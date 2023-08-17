from collections import Counter
from datetime import datetime
from io import BytesIO, StringIO
from os.path import abspath, dirname
from os.path import join as joinpath
from os.path import realpath
from pathlib import Path
from typing import BinaryIO, List, Union
from uuid import UUID
from zipfile import ZipFile

import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.azure import (
    blob_service,
    download_zip_file,
    internet_blob_service,
    upload_internet_file,
)
from auo_project.core.config import settings
from auo_project.core.constants import (
    LOW_PASS_RATE_THRESHOLD,
    FileStatusType,
    UploadStatusType,
)
from auo_project.core.security import decrypt
from auo_project.core.utils import get_age, safe_divide, safe_substract
from auo_project.db.session import SessionLocal

conn_args = {}
if settings.DATABASE_SSL_REQURED:
    conn_args["ssl"] = "require"

engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    echo=settings.DATABASE_ECHO,
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_POOL_SIZE + 5,
    connect_args=conn_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


resolved = lambda x: realpath(abspath(x))


def badpath(path, base):
    # joinpath will ignore base if path is absolute
    return not resolved(joinpath(base, path)).startswith(base)


def badlink(info, base):
    # Links are interpreted relative to the directory containing the link
    tip = resolved(joinpath(base, dirname(info.name)))
    return badpath(info.linkname, base=tip)


def decrypt_file(input_file):
    if input_file.suffix != ".txt":
        return
    if "decrypted" in input_file.name:
        return

    # 從檔案讀取初始向量與密文
    with open(input_file, "rb") as f:
        # iv = f.read(16)  # 讀取 16 位元組的初始向量
        ciphered_data = f.read()  # 讀取其餘的密文

    original_data = decrypt(
        settings.TXT_FILE_AES_KEY,
        settings.TXT_FILE_AES_IV,
        ciphered_data,
    )
    return original_data


def parse_content(content):
    result = {}
    field_counter = Counter()
    split_lines = content.split("\n")
    for line in split_lines:
        pairs = line.strip().split(":", 1)
        if len(pairs) == 2:
            field, value = pairs
            if value == "NA":
                value = None
            field_counter.update({f"{field.lower()}": 1})
            result[field.lower()] = value
        elif len(pairs) > 2:
            raise Exception("invalid line with extra :")
    most_common = field_counter.most_common()
    if len(most_common) > 0 and most_common[0][1] > 1:
        raise Exception(f"duplicated field name: {most_common[0][0]}")
    return result


def clean_extra_comma(content):
    new_content = []
    split_lines = content.split("\n")
    for line in split_lines:
        new_content.append(line.strip(","))
    return "\n".join(new_content)


def is_valid_file(file_info):
    # single file limit 10MB
    if file_info.file_size > 20 * 1024**2:
        raise Exception(f"{file_info.filename} file size should not exceed 20 MB")

    base = resolved("/tmp")
    if badpath(file_info.filename, base):
        raise Exception(f"{file_info.filename} is blocked (illegal path)")
    # TODO: improve security
    # https://stackoverflow.com/questions/10060069/safely-extract-zip-or-tar-using-python
    # elif file_info.issym() and badlink(file_info, base):
    #     raise Exception(
    #         f"{file_info.filename} is blocked: Hard link to {file_info.linkname}"
    #     )
    # elif file_info.islnk() and badlink(file_info, base):
    #     raise Exception(f"{file_info.filename} is blocked: Symlink to {file_info.linkname}")
    return file_info


def data_integrity_check(result_dict):
    # 同欄位在不同檔案的一致性
    return result_dict


# TODO: rename mean_prop_range prefix to static_mean_prop_range
def get_mean_prop_range_123(infos_analyze, hand, position):
    keys = [f"static_mean_range_{i}_{hand}_{position}" for i in (1, 2, 3)]
    values = [
        hasattr(infos_analyze, key) and getattr(infos_analyze, key) for key in keys
    ]

    default_value = {
        f"mean_prop_range_1_{hand}_{position}": None,
        f"mean_prop_range_2_{hand}_{position}": None,
        f"mean_prop_range_3_{hand}_{position}": None,
        f"mean_prop_range_max_{hand}_{position}": None,
    }

    if not all([v is not None for v in values]):
        return default_value

    total = sum(values)
    result = dict(
        [
            (
                f"mean_prop_range_{i+1}_{hand}_{position}",
                int(safe_divide(values[i], total) * 100),
            )
            for i in range(3)
        ],
    )
    result[f"mean_prop_range_max_{hand}_{position}"] = values.index(max(values))
    return result


def get_range_idx(v, values):
    if v < values[0]:
        # TODO
        # raise Exception("max depth should not less than start", v, values)
        print("max depth should not less than start", v, values)
    elif v < values[1]:
        return 0
    elif v < values[2]:
        return 1
    elif v <= values[3]:
        return 2
    else:
        # raise Exception("max depth should not more than end", v, values)
        print("max depth should not more than end", v, values)
    return


def get_max_amp_depth_of_range(infos_analyze, hand, position):
    default_value = {f"max_amp_depth_of_range_{hand}_{position}": None}
    # 未來可能調整算法，目前為 3:4:3
    start_end_keys = [
        f"static_range_start_{hand}_{position}",
        f"static_range_end_{hand}_{position}",
    ]
    start_end_values = [
        hasattr(infos_analyze, key) and getattr(infos_analyze, key)
        for key in start_end_keys
    ]
    static_range_1_3_adjust = (
        start_end_values[0] + (start_end_values[1] - start_end_values[0]) * 3 / 10
        if all([x is not None for x in start_end_values])
        else None
    )
    static_range_2_3_adjust = (
        start_end_values[0] + (start_end_values[1] - start_end_values[0]) * 7 / 10
        if all([x is not None for x in start_end_values])
        else None
    )
    values = [
        start_end_values[0],
        static_range_1_3_adjust,
        static_range_2_3_adjust,
        start_end_values[1],
    ]
    max_value = getattr(infos_analyze, f"static_max_amp_{hand}_{position}")

    if not all([v is not None for v in values]) or max_value is None:
        return default_value

    return {
        f"max_amp_depth_of_range_{hand}_{position}": get_range_idx(max_value, values),
    }


def cal_extra_measure_info(infos_analyze):
    hands = ["l", "r"]
    positions = ["cu", "qu", "ch"]
    result = {}
    for hand in hands:
        for position in positions:
            result = {
                **result,
                **get_mean_prop_range_123(infos_analyze, hand, position),
                **get_max_amp_depth_of_range(infos_analyze, hand, position),
            }
    return result


def read_statistics_txt(content) -> List[schemas.FileStatistics]:
    # skip header
    lines = content.split("\r\n")[1:]
    columns = [
        "statistic",
        "id",
        "hand",
        "position",
        "a0",
        "c1",
        "c2",
        "c3",
        "c4",
        "c5",
        "c6",
        "c7",
        "c8",
        "c9",
        "c10",
        "c11",
        "p1",
        "p2",
        "p3",
        "p4",
        "p5",
        "p6",
        "p7",
        "p8",
        "p9",
        "p10",
        "p11",
        "h1",
        "t1",
        "t",
        "pw",
        "w1",
        "w1_div_t",
        "h1_div_t1",
        "t1_div_t",
        "hr",
        "pass_num",
        "all_num",
        "pass_rate",
    ]
    result = []
    for line in lines:
        if not line:
            continue
        parts = line.strip(",").split(",")
        if len(parts) < 4:
            raise Exception(
                f"statistics.txt each line should be more than 4 columns but only {len(parts)}.",
            )
        result.append(schemas.FileStatistics(**dict(zip(columns[: len(parts)], parts))))
    return result


def read_file(zip_file: Union[BytesIO, str]):
    # TODO: detect //, \\, ..
    txt_filename_list_format_dict = {
        "infos.txt": schemas.FileInfos,
        "infos_analyze.txt": schemas.FileInfosAnalyze,
        "report.txt": schemas.FileReport,
        "BCQ.txt": schemas.FileBCQ,
    }

    # TODO: implement
    def validate_6s_file():
        pass

    def validate_all_s_all_raw_file():
        pass

    def validate_all_s_all_static_file():
        pass

    def validate_all_s_analyze_raw_file():
        pass

    validates_6s = {
        "6s_cu.txt": {"validate": validate_6s_file, "transform": ""},
        "6s_qu.txt": {"validate": validate_6s_file, "transform": ""},
        "6s_ch.txt": {"validate": validate_6s_file, "transform": ""},
    }
    validates_all_s = {
        "all_raw_cu.txt": {"validate": validate_all_s_all_raw_file, "transform": ""},
        "all_raw_ch.txt": {"validate": validate_all_s_all_raw_file, "transform": ""},
        "all_raw_qu.txt": {"validate": validate_all_s_all_raw_file, "transform": ""},
        "all_static_cu.txt": {
            "validate": validate_all_s_all_static_file,
            "transform": "",
        },
        "all_static_ch.txt": {
            "validate": validate_all_s_all_static_file,
            "transform": "",
        },
        "all_static_qu.txt": {
            "validate": validate_all_s_all_static_file,
            "transform": "",
        },
        "analyze_raw_Cu.txt": {
            "validate": validate_all_s_analyze_raw_file,
            "transform": "",
        },
        "analyze_raw_Qu.txt": {
            "validate": validate_all_s_analyze_raw_file,
            "transform": "",
        },
        "analyze_raw_Ch.txt": {
            "validate": validate_all_s_analyze_raw_file,
            "transform": "",
        },
    }
    validates_raw_data = {
        "6s": validates_6s,
        "all_s": validates_all_s,
    }
    txt_raw_file_dict = {
        "Left": validates_raw_data,
        "Right": validates_raw_data,
    }

    statistics_file = "statistics.csv"
    image_file_list = ["T_up.jpg", "T_down.jpg"]
    version_file = "ver.ini"

    allowd_filename_list = (
        list(txt_filename_list_format_dict.keys())
        + list(validates_6s.keys())
        + list(validates_all_s.keys())
        + [statistics_file]
        + image_file_list
        + [version_file]
    )

    checked_file_list = []
    result_dict = {"error_msg": ""}
    with ZipFile(zip_file, mode="r") as measure_zip:
        infolist = measure_zip.infolist()
        for file_info in infolist:
            if not file_info.is_dir():
                file_info = is_valid_file(file_info)
                checked_file_list.append(file_info)

        for file_info in checked_file_list:
            file_name_p = Path(file_info.filename)
            file_name = file_name_p.name
            print(file_name)
            if file_name in allowd_filename_list:
                with measure_zip.open(file_info.filename, mode="r") as f:
                    content = f.read()

                if file_name_p.suffix == ".txt":
                    decrypted_data = decrypt(
                        settings.TXT_FILE_AES_KEY,
                        settings.TXT_FILE_AES_IV,
                        content,
                    )
                    decoded_data = decrypted_data.decode("utf8")
                    schema_in = txt_filename_list_format_dict.get(file_name)
                    if schema_in:
                        try:
                            dict_obj = parse_content(decoded_data)
                            # TODO: check provided columns
                            result_dict[file_name] = schema_in(**dict_obj)
                        except Exception as e:
                            result_dict["error_msg"] += f"{file_name}:{e};"
                    elif file_name in validates_6s or file_name in validates_all_s:
                        df = pd.read_csv(StringIO(decoded_data), header=None, sep="\t")
                        side = None
                        if "Left" in str(file_name_p):
                            side = "left"
                        elif "Right" in str(file_name_p):
                            side = "right"
                        else:
                            result_dict["error_msg"] += f"invalid side: {file_name_p};"
                        result_dict[f"{side}/{file_name}"] = df

                elif file_name == statistics_file:
                    result_dict[file_name] = read_statistics_txt(
                        content=content.decode("utf8"),
                    )

                elif file_name in image_file_list:
                    result_dict[file_name] = BytesIO(content)

                elif file_name == "ver.ini":
                    decrypted_data = decrypt(
                        settings.TXT_FILE_AES_KEY,
                        settings.TXT_FILE_AES_IV,
                        content,
                    )
                    decoded_data = decrypted_data.decode("utf8")
                    result_dict[file_name] = decoded_data

        return result_dict


async def process_file(
    file: models.File,
    zip_file: BinaryIO,
    overwrite: bool,
    db_session: AsyncSession = None,
):
    result_dict = {}
    try:
        result_dict = read_file(zip_file)
    except Exception as e:
        print("file error: ", e)
        return {"error_msg": result_dict.get("error_msg", str(e))}

    if not result_dict:
        print("no result")
        return

    if result_dict.get("error_msg"):
        print("file error: ", result_dict["error_msg"])
        return {"error_msg": result_dict["error_msg"]}

    checked = data_integrity_check(result_dict)
    if not checked:
        raise Exception("checked error")

    # check subject exists
    db_session = db_session or SessionLocal()
    infos = result_dict.get("infos.txt")
    infos_analyze = result_dict.get("infos_analyze.txt")
    report = result_dict.get("report.txt")
    bcq = result_dict.get("BCQ.txt", {})
    ver = result_dict.get("ver.ini")

    subject = await crud.subject.get_by_sid_and_proj_num(
        db_session=db_session,
        sid=infos.id,
        proj_num=report.proj_num if report else None,
    )
    if not subject:
        subject_in = schemas.SubjectCreate(
            sid=infos.id,
            name=infos.name,
            birth_date=infos.birth_date,
            sex=infos.sex,
            last_measure_time=infos.measure_time,
            proj_num=report.proj_num if report else None,
            number=infos.number,
            is_active=True,
        )
        subject = await crud.subject.create(db_session=db_session, obj_in=subject_in)
    else:
        subject_in = schemas.SubjectUpdate(
            birth_date=infos.birth_date,
            sex=infos.sex,
            last_measure_time=max(infos.measure_time, subject.last_measure_time)
            if subject.last_measure_time
            else infos.measure_time,
            number=infos.number,
        )
        subject = await crud.subject.update(
            db_session=db_session,
            obj_current=subject,
            obj_new=subject_in,
        )

    # TODO: check sid + measure_time as unique key ok
    measure_info = await crud.measure_info.get_exist_measure(
        db_session=db_session,
        sid=subject.sid,
        measure_time=infos.measure_time,
    ) or await crud.measure_info.get_by_file_id(db_session=db_session, file_id=file.id)

    extra_info = schemas.MeasureInfoExtraInfo(**cal_extra_measure_info(infos_analyze))

    has_low_pass_rate = False
    if "statistics.csv" in result_dict:
        records = result_dict["statistics.csv"]
        for record in records:
            # TODO: check definition of low pass rate
            if (
                record.pass_rate is not None
                and record.pass_rate < LOW_PASS_RATE_THRESHOLD
            ):
                has_low_pass_rate = True

    age = get_age(infos.measure_time, infos.birth_date) or get_age(
        infos.measure_time,
        subject.birth_date,
    )

    bmi = None
    if isinstance(infos.height, float) and isinstance(infos.weight, float):
        bmi = safe_divide(infos.weight, (infos.height / 100) ** 2)

    if measure_info:
        print(f"measure exist: {measure_info.id}")
    if overwrite and measure_info:
        print("start deleting...")
        await db_session.delete(measure_info)
        await db_session.commit()
        # await crud.measure_info.remove(db_session=db_session, id=measure_info.id)
        print("deleted")
    if not measure_info or overwrite:
        measure_info_in = schemas.MeasureInfoCreate(
            subject_id=subject.id,
            file_id=file.id,
            org_id=file.owner.org_id,
            uid=infos.uid,
            number=infos.name,
            has_measure=True,
            has_bcq="BCQ.txt" in result_dict,
            has_tongue="T_up.jpg" in result_dict or "T_down.jpg" in result_dict,
            has_memo=False,
            has_low_pass_rate=has_low_pass_rate,
            measure_time=infos.measure_time,
            measure_operator=infos.measure_operator,
            mean_prop_range_1_l_cu=extra_info.mean_prop_range_1_l_cu,
            mean_prop_range_2_l_cu=extra_info.mean_prop_range_2_l_cu,
            mean_prop_range_3_l_cu=extra_info.mean_prop_range_3_l_cu,
            mean_prop_range_1_l_qu=extra_info.mean_prop_range_1_l_qu,
            mean_prop_range_2_l_qu=extra_info.mean_prop_range_2_l_qu,
            mean_prop_range_3_l_qu=extra_info.mean_prop_range_3_l_qu,
            mean_prop_range_1_l_ch=extra_info.mean_prop_range_1_l_ch,
            mean_prop_range_2_l_ch=extra_info.mean_prop_range_2_l_ch,
            mean_prop_range_3_l_ch=extra_info.mean_prop_range_3_l_ch,
            mean_prop_range_1_r_cu=extra_info.mean_prop_range_1_r_cu,
            mean_prop_range_2_r_cu=extra_info.mean_prop_range_2_r_cu,
            mean_prop_range_3_r_cu=extra_info.mean_prop_range_3_r_cu,
            mean_prop_range_1_r_qu=extra_info.mean_prop_range_1_r_qu,
            mean_prop_range_2_r_qu=extra_info.mean_prop_range_2_r_qu,
            mean_prop_range_3_r_qu=extra_info.mean_prop_range_3_r_qu,
            mean_prop_range_1_r_ch=extra_info.mean_prop_range_1_r_ch,
            mean_prop_range_2_r_ch=extra_info.mean_prop_range_2_r_ch,
            mean_prop_range_3_r_ch=extra_info.mean_prop_range_3_r_ch,
            # TODO: check how to change
            mean_prop_range_max_l_cu=extra_info.max_amp_depth_of_range_l_cu,
            mean_prop_range_max_l_qu=extra_info.max_amp_depth_of_range_l_qu,
            mean_prop_range_max_l_ch=extra_info.max_amp_depth_of_range_l_ch,
            mean_prop_range_max_r_cu=extra_info.max_amp_depth_of_range_r_cu,
            mean_prop_range_max_r_qu=extra_info.max_amp_depth_of_range_r_qu,
            mean_prop_range_max_r_ch=extra_info.max_amp_depth_of_range_r_ch,
            max_amp_depth_of_range_l_cu=extra_info.max_amp_depth_of_range_l_cu,
            max_amp_depth_of_range_l_qu=extra_info.max_amp_depth_of_range_l_qu,
            max_amp_depth_of_range_l_ch=extra_info.max_amp_depth_of_range_l_ch,
            max_amp_depth_of_range_r_cu=extra_info.max_amp_depth_of_range_r_cu,
            max_amp_depth_of_range_r_qu=extra_info.max_amp_depth_of_range_r_qu,
            max_amp_depth_of_range_r_ch=extra_info.max_amp_depth_of_range_r_ch,
            max_amp_value_l_cu=infos_analyze.max_amp_value_l_cu,
            max_amp_value_l_qu=infos_analyze.max_amp_value_l_qu,
            max_amp_value_l_ch=infos_analyze.max_amp_value_l_ch,
            max_amp_value_r_cu=infos_analyze.max_amp_value_r_cu,
            max_amp_value_r_qu=infos_analyze.max_amp_value_r_qu,
            max_amp_value_r_ch=infos_analyze.max_amp_value_r_ch,
            irregular_hr_l_cu=infos.irregular_hr_l_cu,
            irregular_hr_l_qu=infos.irregular_hr_l_qu,
            irregular_hr_l_ch=infos.irregular_hr_l_ch,
            irregular_hr_r_cu=infos.irregular_hr_r_cu,
            irregular_hr_r_qu=infos.irregular_hr_r_qu,
            irregular_hr_r_ch=infos.irregular_hr_r_ch,
            irregular_hr_l=any(
                [
                    infos.irregular_hr_l_cu,
                    infos.irregular_hr_l_qu,
                    infos.irregular_hr_l_ch,
                ],
            ),
            irregular_hr_type_l=None,
            irregular_hr_r=any(
                [
                    infos.irregular_hr_r_cu,
                    infos.irregular_hr_r_qu,
                    infos.irregular_hr_r_ch,
                ],
            ),
            irregular_hr_type_r=None,
            irregular_hr=any(
                [
                    infos.irregular_hr_l_cu,
                    infos.irregular_hr_l_qu,
                    infos.irregular_hr_l_ch,
                    infos.irregular_hr_r_cu,
                    infos.irregular_hr_r_qu,
                    infos.irregular_hr_r_ch,
                ],
            ),
            max_slope_value_l_cu=infos_analyze.max_slop_l_cu,
            max_slope_value_l_qu=infos_analyze.max_slop_l_qu,
            max_slope_value_l_ch=infos_analyze.max_slop_l_ch,
            max_slope_value_r_cu=infos_analyze.max_slop_r_cu,
            max_slope_value_r_qu=infos_analyze.max_slop_r_qu,
            max_slope_value_r_ch=infos_analyze.max_slop_r_ch,
            strength_l_cu=infos.strength_l_cu,
            strength_l_qu=infos.strength_l_qu,
            strength_l_ch=infos.strength_l_ch,
            strength_r_cu=infos.strength_r_cu,
            strength_r_qu=infos.strength_r_qu,
            strength_r_ch=infos.strength_r_ch,
            range_length_l_cu=infos.range_length_l_cu,
            range_length_l_qu=infos.range_length_l_qu,
            range_length_l_ch=infos.range_length_l_ch,
            range_length_r_cu=infos.range_length_r_cu,
            range_length_r_qu=infos.range_length_r_qu,
            range_length_r_ch=infos.range_length_r_ch,
            width_l_cu=None,
            width_l_qu=None,
            width_l_ch=None,
            width_r_cu=None,
            width_r_qu=None,
            width_r_ch=None,
            static_max_amp_l_cu=infos_analyze.static_max_amp_l_cu,
            static_max_amp_l_qu=infos_analyze.static_max_amp_l_qu,
            static_max_amp_l_ch=infos_analyze.static_max_amp_l_ch,
            static_max_amp_r_cu=infos_analyze.static_max_amp_r_cu,
            static_max_amp_r_qu=infos_analyze.static_max_amp_r_qu,
            static_max_amp_r_ch=infos_analyze.static_max_amp_r_ch,
            static_range_start_l_cu=infos_analyze.static_range_start_l_cu,
            static_range_start_l_qu=infos_analyze.static_range_start_l_qu,
            static_range_start_l_ch=infos_analyze.static_range_start_l_ch,
            static_range_start_r_cu=infos_analyze.static_range_start_r_cu,
            static_range_start_r_qu=infos_analyze.static_range_start_r_qu,
            static_range_start_r_ch=infos_analyze.static_range_start_r_ch,
            static_range_end_l_cu=infos_analyze.static_range_end_l_cu,
            static_range_end_l_qu=infos_analyze.static_range_end_l_qu,
            static_range_end_l_ch=infos_analyze.static_range_end_l_ch,
            static_range_end_r_cu=infos_analyze.static_range_end_r_cu,
            static_range_end_r_qu=infos_analyze.static_range_end_r_qu,
            static_range_end_r_ch=infos_analyze.static_range_end_r_ch,
            xingcheng_l_cu=safe_substract(
                infos_analyze.range_end_index_l_cu,
                infos_analyze.range_start_index_l_cu,
            ),
            xingcheng_l_qu=safe_substract(
                infos_analyze.range_end_index_l_qu,
                infos_analyze.range_start_index_l_qu,
            ),
            xingcheng_l_ch=safe_substract(
                infos_analyze.range_end_index_l_ch,
                infos_analyze.range_start_index_l_ch,
            ),
            xingcheng_r_cu=safe_substract(
                infos_analyze.range_end_index_r_cu,
                infos_analyze.range_start_index_r_cu,
            ),
            xingcheng_r_qu=safe_substract(
                infos_analyze.range_end_index_r_qu,
                infos_analyze.range_start_index_r_qu,
            ),
            xingcheng_r_ch=safe_substract(
                infos_analyze.range_end_index_r_ch,
                infos_analyze.range_start_index_r_ch,
            ),
            sex=infos.sex,
            age=age,
            height=infos.height,
            weight=infos.weight,
            bmi=bmi,
            sbp=infos.sbp,
            dbp=infos.dbp,
            judge_time=infos.judge_time,
            judge_dr=infos.judge_dr,
            hr_l=infos.hr_l,
            hr_r=infos.hr_r,
            special_l=infos.special_l,
            special_r=infos.special_r,
            comment=infos.comment,
            memo=None,
            proj_num=report.proj_num if "report.txt" in result_dict else None,
            ver=ver,
            is_active=True,
        )
        measure_info = await crud.measure_info.create(
            db_session=db_session,
            obj_in=measure_info_in,
        )
    else:
        measure_info_in = schemas.MeasureInfoUpdate(
            subject_id=subject.id,
            file_id=file.id,
            org_id=file.owner.org_id,
            uid=infos.uid,
            number=infos.name,
            has_measure=True,
            has_bcq="BCQ.txt" in result_dict,
            has_tongue="T_up.jpg" in result_dict or "T_down.jpg" in result_dict,
            has_low_pass_rate=has_low_pass_rate,
            measure_time=infos.measure_time,
            measure_operator=infos.measure_operator,
            mean_prop_range_1_l_cu=extra_info.mean_prop_range_1_l_cu,
            mean_prop_range_2_l_cu=extra_info.mean_prop_range_2_l_cu,
            mean_prop_range_3_l_cu=extra_info.mean_prop_range_3_l_cu,
            mean_prop_range_1_l_qu=extra_info.mean_prop_range_1_l_qu,
            mean_prop_range_2_l_qu=extra_info.mean_prop_range_2_l_qu,
            mean_prop_range_3_l_qu=extra_info.mean_prop_range_3_l_qu,
            mean_prop_range_1_l_ch=extra_info.mean_prop_range_1_l_ch,
            mean_prop_range_2_l_ch=extra_info.mean_prop_range_2_l_ch,
            mean_prop_range_3_l_ch=extra_info.mean_prop_range_3_l_ch,
            mean_prop_range_1_r_cu=extra_info.mean_prop_range_1_r_cu,
            mean_prop_range_2_r_cu=extra_info.mean_prop_range_2_r_cu,
            mean_prop_range_3_r_cu=extra_info.mean_prop_range_3_r_cu,
            mean_prop_range_1_r_qu=extra_info.mean_prop_range_1_r_qu,
            mean_prop_range_2_r_qu=extra_info.mean_prop_range_2_r_qu,
            mean_prop_range_3_r_qu=extra_info.mean_prop_range_3_r_qu,
            mean_prop_range_1_r_ch=extra_info.mean_prop_range_1_r_ch,
            mean_prop_range_2_r_ch=extra_info.mean_prop_range_2_r_ch,
            mean_prop_range_3_r_ch=extra_info.mean_prop_range_3_r_ch,
            # TODO: check how to change
            mean_prop_range_max_l_cu=extra_info.max_amp_depth_of_range_l_cu,
            mean_prop_range_max_l_qu=extra_info.max_amp_depth_of_range_l_qu,
            mean_prop_range_max_l_ch=extra_info.max_amp_depth_of_range_l_ch,
            mean_prop_range_max_r_cu=extra_info.max_amp_depth_of_range_r_cu,
            mean_prop_range_max_r_qu=extra_info.max_amp_depth_of_range_r_qu,
            mean_prop_range_max_r_ch=extra_info.max_amp_depth_of_range_r_ch,
            max_amp_depth_of_range_l_cu=extra_info.max_amp_depth_of_range_l_cu,
            max_amp_depth_of_range_l_qu=extra_info.max_amp_depth_of_range_l_qu,
            max_amp_depth_of_range_l_ch=extra_info.max_amp_depth_of_range_l_ch,
            max_amp_depth_of_range_r_cu=extra_info.max_amp_depth_of_range_r_cu,
            max_amp_depth_of_range_r_qu=extra_info.max_amp_depth_of_range_r_qu,
            max_amp_depth_of_range_r_ch=extra_info.max_amp_depth_of_range_r_ch,
            max_amp_value_l_cu=infos_analyze.max_amp_value_l_cu,
            max_amp_value_l_qu=infos_analyze.max_amp_value_l_qu,
            max_amp_value_l_ch=infos_analyze.max_amp_value_l_ch,
            max_amp_value_r_cu=infos_analyze.max_amp_value_r_cu,
            max_amp_value_r_qu=infos_analyze.max_amp_value_r_qu,
            max_amp_value_r_ch=infos_analyze.max_amp_value_r_ch,
            irregular_hr_l_cu=infos.irregular_hr_l_cu,
            irregular_hr_l_qu=infos.irregular_hr_l_qu,
            irregular_hr_l_ch=infos.irregular_hr_l_ch,
            irregular_hr_r_cu=infos.irregular_hr_r_cu,
            irregular_hr_r_qu=infos.irregular_hr_r_qu,
            irregular_hr_r_ch=infos.irregular_hr_r_ch,
            irregular_hr_l=any(
                [
                    infos.irregular_hr_l_cu,
                    infos.irregular_hr_l_qu,
                    infos.irregular_hr_l_ch,
                ],
            ),
            irregular_hr_type_l=None,
            irregular_hr_r=any(
                [
                    infos.irregular_hr_r_cu,
                    infos.irregular_hr_r_qu,
                    infos.irregular_hr_r_ch,
                ],
            ),
            irregular_hr_type_r=None,
            irregular_hr=any(
                [
                    infos.irregular_hr_l_cu,
                    infos.irregular_hr_l_qu,
                    infos.irregular_hr_l_ch,
                    infos.irregular_hr_r_cu,
                    infos.irregular_hr_r_qu,
                    infos.irregular_hr_r_ch,
                ],
            ),
            max_slope_value_l_cu=infos_analyze.max_slop_l_cu,
            max_slope_value_l_qu=infos_analyze.max_slop_l_qu,
            max_slope_value_l_ch=infos_analyze.max_slop_l_ch,
            max_slope_value_r_cu=infos_analyze.max_slop_r_cu,
            max_slope_value_r_qu=infos_analyze.max_slop_r_qu,
            max_slope_value_r_ch=infos_analyze.max_slop_r_ch,
            strength_l_cu=infos.strength_l_cu,
            strength_l_qu=infos.strength_l_qu,
            strength_l_ch=infos.strength_l_ch,
            strength_r_cu=infos.strength_r_cu,
            strength_r_qu=infos.strength_r_qu,
            strength_r_ch=infos.strength_r_ch,
            range_length_l_cu=infos.range_length_l_cu,
            range_length_l_qu=infos.range_length_l_qu,
            range_length_l_ch=infos.range_length_l_ch,
            range_length_r_cu=infos.range_length_r_cu,
            range_length_r_qu=infos.range_length_r_qu,
            range_length_r_ch=infos.range_length_r_ch,
            width_l_cu=None,
            width_l_qu=None,
            width_l_ch=None,
            width_r_cu=None,
            width_r_qu=None,
            width_r_ch=None,
            static_max_amp_l_cu=infos_analyze.static_max_amp_l_cu,
            static_max_amp_l_qu=infos_analyze.static_max_amp_l_qu,
            static_max_amp_l_ch=infos_analyze.static_max_amp_l_ch,
            static_max_amp_r_cu=infos_analyze.static_max_amp_r_cu,
            static_max_amp_r_qu=infos_analyze.static_max_amp_r_qu,
            static_max_amp_r_ch=infos_analyze.static_max_amp_r_ch,
            static_range_start_l_cu=infos_analyze.static_range_start_l_cu,
            static_range_start_l_qu=infos_analyze.static_range_start_l_qu,
            static_range_start_l_ch=infos_analyze.static_range_start_l_ch,
            static_range_start_r_cu=infos_analyze.static_range_start_r_cu,
            static_range_start_r_qu=infos_analyze.static_range_start_r_qu,
            static_range_start_r_ch=infos_analyze.static_range_start_r_ch,
            static_range_end_l_cu=infos_analyze.static_range_end_l_cu,
            static_range_end_l_qu=infos_analyze.static_range_end_l_qu,
            static_range_end_l_ch=infos_analyze.static_range_end_l_ch,
            static_range_end_r_cu=infos_analyze.static_range_end_r_cu,
            static_range_end_r_qu=infos_analyze.static_range_end_r_qu,
            static_range_end_r_ch=infos_analyze.static_range_end_r_ch,
            xingcheng_l_cu=safe_substract(
                infos_analyze.range_end_index_l_cu,
                infos_analyze.range_start_index_l_cu,
            ),
            xingcheng_l_qu=safe_substract(
                infos_analyze.range_end_index_l_qu,
                infos_analyze.range_start_index_l_qu,
            ),
            xingcheng_l_ch=safe_substract(
                infos_analyze.range_end_index_l_ch,
                infos_analyze.range_start_index_l_ch,
            ),
            xingcheng_r_cu=safe_substract(
                infos_analyze.range_end_index_r_cu,
                infos_analyze.range_start_index_r_cu,
            ),
            xingcheng_r_qu=safe_substract(
                infos_analyze.range_end_index_r_qu,
                infos_analyze.range_start_index_r_qu,
            ),
            xingcheng_r_ch=safe_substract(
                infos_analyze.range_end_index_r_ch,
                infos_analyze.range_start_index_r_ch,
            ),
            sex=infos.sex,
            age=age,
            height=infos.height,
            weight=infos.weight,
            bmi=bmi,
            sbp=infos.sbp,
            dbp=infos.dbp,
            judge_time=infos.judge_time,
            judge_dr=infos.judge_dr,
            hr_l=infos.hr_l,
            hr_r=infos.hr_r,
            special_l=infos.special_l,
            special_r=infos.special_r,
            comment=infos.comment,
            proj_num=report.proj_num if "report.txt" in result_dict else None,
            ver=ver,
            is_active=True,
        )
        measure_info = await crud.measure_info.update(
            db_session=db_session,
            obj_current=measure_info,
            obj_new=measure_info_in,
        )

    if "BCQ.txt" in result_dict:
        bcq_model = await crud.measure_bcq.get_by_measure_id(
            db_session=db_session,
            measure_id=measure_info.id,
        )
        if bcq_model is None:
            bcq_in = schemas.BCQCreate(
                **bcq.dict(),
                measure_id=measure_info.id,
            )
            bcq = await crud.measure_bcq.create(db_session=db_session, obj_in=bcq_in)

    # tongue
    if "report.txt" in result_dict:
        tongue = await crud.measure_tongue.get_by_measure_id(
            db_session=db_session,
            measure_id=measure_info.id,
        )
        up_img_uri = None
        down_img_uri = None
        if "T_up.jpg" in result_dict:
            obj_path = f"{subject.id}/{measure_info.id}/T_up.jpg"
            up_img_uri = upload_internet_file(
                blob_service_client=internet_blob_service,
                category="image",
                file_path=obj_path,
                object=result_dict["T_up.jpg"],
            )
        if "T_down.jpg" in result_dict:
            obj_path = f"{subject.id}/{measure_info.id}/T_down.jpg"
            down_img_uri = upload_internet_file(
                blob_service_client=internet_blob_service,
                category="image",
                file_path=obj_path,
                object=result_dict["T_down.jpg"],
            )
        if not tongue:
            tongue_in = schemas.MeasureTongueCreate(
                **report.dict(),
                measure_id=measure_info.id,
                up_img_uri=up_img_uri,
                down_img_uri=down_img_uri,
            )
            tongue = await crud.measure_tongue.create(
                db_session=db_session,
                obj_in=tongue_in,
            )

    if "statistics.csv" in result_dict:
        records = result_dict["statistics.csv"]
        for record in records:
            statistic = await crud.measure_statistic.get_by_uniq_keys(
                db_session=db_session,
                measure_id=measure_info.id,
                statistic=record.statistic,
                hand=record.hand,
                position=record.position,
            )
            if not statistic:
                statistic_in = schemas.MeasureStatisticCreate(
                    **record.dict(),
                    measure_id=measure_info.id,
                )
                await crud.measure_statistic.create(
                    db_session=db_session,
                    obj_in=statistic_in,
                )

    def serialize(df):
        if isinstance(df, pd.DataFrame):
            return df.to_csv(sep="\t", index=False, header=None)
        return

    # 6s
    measure_raw = await crud.measure_raw.get_by_measure_id(
        db_session=db_session,
        measure_id=measure_info.id,
    )

    if not measure_raw:
        measure_raw_in = schemas.MeasureRawCreate(
            measure_id=measure_info.id,
            six_sec_l_cu=serialize(result_dict.get("left/6s_cu.txt")),
            six_sec_l_qu=serialize(result_dict.get("left/6s_qu.txt")),
            six_sec_l_ch=serialize(result_dict.get("left/6s_ch.txt")),
            six_sec_r_cu=serialize(result_dict.get("right/6s_cu.txt")),
            six_sec_r_qu=serialize(result_dict.get("right/6s_qu.txt")),
            six_sec_r_ch=serialize(result_dict.get("right/6s_ch.txt")),
            all_sec_analyze_raw_l_cu=serialize(
                result_dict.get("left/analyze_raw_Cu.txt"),
            ),
            all_sec_analyze_raw_l_qu=serialize(
                result_dict.get("left/analyze_raw_Qu.txt"),
            ),
            all_sec_analyze_raw_l_ch=serialize(
                result_dict.get("left/analyze_raw_Ch.txt"),
            ),
            all_sec_analyze_raw_r_cu=serialize(
                result_dict.get("right/analyze_raw_Cu.txt"),
            ),
            all_sec_analyze_raw_r_qu=serialize(
                result_dict.get("right/analyze_raw_Qu.txt"),
            ),
            all_sec_analyze_raw_r_ch=serialize(
                result_dict.get("right/analyze_raw_Ch.txt"),
            ),
        )
        measure_raw = await crud.measure_raw.create(
            db_session=db_session,
            obj_in=measure_raw_in,
        )

    await db_session.close()

    return True


async def get_and_write(
    db_session: AsyncSession,
    file_id: UUID,
    overwrite: bool = True,
):
    file = await crud.file.get(db_session=db_session, id=file_id)
    if not file:
        raise Exception(f"not found file id: {file_id}")

    # download blob
    downloader = download_zip_file(blob_service, file.location)
    zip_file = BytesIO(downloader.readall())
    result = await process_file(file, zip_file, overwrite, db_session)
    # TODO: design error log table
    print("result:", result)
    if result:
        if isinstance(result, dict):
            error_msg = result.get("error_msg", "")
            if error_msg:
                file_in = schemas.FileUpdate(
                    file_status=FileStatusType.success.value,
                    is_valid=False,
                    memo=error_msg,
                )
        else:
            file_in = schemas.FileUpdate(
                file_status=FileStatusType.success.value,
                is_valid=True,
                memo="",
            )
        await crud.file.update(db_session=db_session, obj_current=file, obj_new=file_in)
        is_all_files_success = await crud.upload.is_files_all_success(
            db_session=db_session,
            upload_id=file.upload_id,
        )

        if is_all_files_success:
            display_file_number = await crud.upload.get_display_file_number(
                db_session=db_session,
                upload_id=file.upload_id,
            )
            upload_in = schemas.UploadUpdate(
                upload_status=UploadStatusType.success.value,
                end_to=datetime.utcnow(),
                display_file_number=display_file_number,
            )
            await crud.upload.update(
                db_session=db_session,
                obj_current=file.upload,
                obj_new=upload_in,
            )


async def process_dir(dir: str):
    zip_folder = Path(dir)
    for zip_file in zip_folder.glob("*.zip"):
        await process_file(zip_file, overwrite=False)
