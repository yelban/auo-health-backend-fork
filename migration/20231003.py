from io import BytesIO
from typing import BinaryIO
from uuid import UUID

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.azure import blob_service, download_zip_file
from auo_project.core.config import settings
from auo_project.core.constants import MAX_DEPTH_RATIO
from auo_project.core.file import get_max_amp_depth_of_range
from auo_project.core.utils import (
    get_max_amp_value,
    get_measure_strength,
    get_measure_width,
    get_pass_rate_from_statistics,
    safe_divide,
)
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


from auo_project.core.file import data_integrity_check, read_file


async def step1_get_and_write(
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
    zip_file.close()
    print(f"file_id {file_id} result:", result)


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

    subject = await crud.subject.get_by_number_and_org_id(
        db_session=db_session,
        number=infos.number,
        org_id=file.owner.org_id,
    )
    if subject is None:
        return False
    measure_info = await crud.measure_info.get_exist_measure(
        db_session=db_session,
        org_id=file.owner.org_id,
        number=subject.number,
        measure_time=infos.measure_time,
    ) or await crud.measure_info.get_by_file_id(db_session=db_session, file_id=file.id)
    if measure_info is None:
        return False
    measure_raw = await crud.measure_raw.get_by_measure_id(
        db_session=db_session,
        measure_id=measure_info.id,
    )

    if measure_info:
        statistics_records = result_dict.get("statistics.csv", [])
        print(f"measure exist: {measure_info.id}")
        (
            pass_rate_l_cu,
            pass_rate_l_qu,
            pass_rate_l_ch,
            pass_rate_r_cu,
            pass_rate_r_qu,
            pass_rate_r_ch,
        ) = get_pass_rate_from_statistics(statistics_records)
        measure_info_in = schemas.MeasureInfoUpdate(
            select_static_l_cu=infos.select_static_l_cu,
            select_static_l_qu=infos.select_static_l_qu,
            select_static_l_ch=infos.select_static_l_ch,
            select_static_r_cu=infos.select_static_r_cu,
            select_static_r_qu=infos.select_static_r_qu,
            select_static_r_ch=infos.select_static_r_ch,
            pass_rate_l_cu=pass_rate_l_cu,
            pass_rate_l_qu=pass_rate_l_qu,
            pass_rate_l_ch=pass_rate_l_ch,
            pass_rate_r_cu=pass_rate_r_cu,
            pass_rate_r_qu=pass_rate_r_qu,
            pass_rate_r_ch=pass_rate_r_ch,
            max_amp_value_l_cu=get_max_amp_value(
                infos.select_static_l_cu,
                measure_raw.all_sec_analyze_raw_l_cu,
            ),
            max_amp_value_l_qu=get_max_amp_value(
                infos.select_static_l_qu,
                measure_raw.all_sec_analyze_raw_l_qu,
            ),
            max_amp_value_l_ch=get_max_amp_value(
                infos.select_static_l_ch,
                measure_raw.all_sec_analyze_raw_l_ch,
            ),
            max_amp_value_r_cu=get_max_amp_value(
                infos.select_static_r_cu,
                measure_raw.all_sec_analyze_raw_r_cu,
            ),
            max_amp_value_r_qu=get_max_amp_value(
                infos.select_static_r_qu,
                measure_raw.all_sec_analyze_raw_r_qu,
            ),
            max_amp_value_r_ch=get_max_amp_value(
                infos.select_static_r_ch,
                measure_raw.all_sec_analyze_raw_r_ch,
            ),
        )
        measure_info = await crud.measure_info.update(
            db_session=db_session,
            obj_current=measure_info,
            obj_new=measure_info_in,
        )

    await db_session.close()
    zip_file.close()
    del result_dict
    del infos
    del infos_analyze
    del report
    del bcq
    import gc

    gc.collect()

    return True


async def step2_update_calculated_columns(
    db_session,
    measure_id: UUID,
):
    measure_info = await crud.measure_info.get(db_session=db_session, id=measure_id)
    width_value_l_cu = safe_divide(measure_info.range_length_l_cu, 0.2)
    width_value_l_qu = safe_divide(measure_info.range_length_l_qu, 0.2)
    width_value_l_ch = safe_divide(measure_info.range_length_l_ch, 0.2)
    width_value_r_cu = safe_divide(measure_info.range_length_r_cu, 0.2)
    width_value_r_qu = safe_divide(measure_info.range_length_r_qu, 0.2)
    width_value_r_ch = safe_divide(measure_info.range_length_r_ch, 0.2)
    measure_info_in = schemas.MeasureInfoUpdate(
        mean_prop_range_max_l_cu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_l_cu,
            static_range_end_hand_position=measure_info.static_range_end_l_cu,
            static_max_amp_hand_position=measure_info.static_max_amp_l_cu,
            ratio=MAX_DEPTH_RATIO,
        ),
        mean_prop_range_max_l_qu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_l_qu,
            static_range_end_hand_position=measure_info.static_range_end_l_qu,
            static_max_amp_hand_position=measure_info.static_max_amp_l_qu,
            ratio=MAX_DEPTH_RATIO,
        ),
        mean_prop_range_max_l_ch=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_l_ch,
            static_range_end_hand_position=measure_info.static_range_end_l_ch,
            static_max_amp_hand_position=measure_info.static_max_amp_l_ch,
            ratio=MAX_DEPTH_RATIO,
        ),
        mean_prop_range_max_r_cu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_r_cu,
            static_range_end_hand_position=measure_info.static_range_end_r_cu,
            static_max_amp_hand_position=measure_info.static_max_amp_r_cu,
            ratio=MAX_DEPTH_RATIO,
        ),
        mean_prop_range_max_r_qu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_r_qu,
            static_range_end_hand_position=measure_info.static_range_end_r_qu,
            static_max_amp_hand_position=measure_info.static_max_amp_r_qu,
            ratio=MAX_DEPTH_RATIO,
        ),
        mean_prop_range_max_r_ch=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_r_ch,
            static_range_end_hand_position=measure_info.static_range_end_r_ch,
            static_max_amp_hand_position=measure_info.static_max_amp_r_ch,
            ratio=MAX_DEPTH_RATIO,
        ),
        max_amp_depth_of_range_l_cu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_l_cu,
            static_range_end_hand_position=measure_info.static_range_end_l_cu,
            static_max_amp_hand_position=measure_info.static_max_amp_l_cu,
            ratio=MAX_DEPTH_RATIO,
        ),
        max_amp_depth_of_range_l_qu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_l_qu,
            static_range_end_hand_position=measure_info.static_range_end_l_qu,
            static_max_amp_hand_position=measure_info.static_max_amp_l_qu,
            ratio=MAX_DEPTH_RATIO,
        ),
        max_amp_depth_of_range_l_ch=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_l_ch,
            static_range_end_hand_position=measure_info.static_range_end_l_ch,
            static_max_amp_hand_position=measure_info.static_max_amp_l_ch,
            ratio=MAX_DEPTH_RATIO,
        ),
        max_amp_depth_of_range_r_cu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_r_cu,
            static_range_end_hand_position=measure_info.static_range_end_r_cu,
            static_max_amp_hand_position=measure_info.static_max_amp_r_cu,
            ratio=MAX_DEPTH_RATIO,
        ),
        max_amp_depth_of_range_r_qu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_r_qu,
            static_range_end_hand_position=measure_info.static_range_end_r_qu,
            static_max_amp_hand_position=measure_info.static_max_amp_r_qu,
            ratio=MAX_DEPTH_RATIO,
        ),
        max_amp_depth_of_range_r_ch=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_r_ch,
            static_range_end_hand_position=measure_info.static_range_end_r_ch,
            static_max_amp_hand_position=measure_info.static_max_amp_r_ch,
            ratio=MAX_DEPTH_RATIO,
        ),
        strength_l_cu=get_measure_strength(
            measure_info.max_slope_value_l_cu,
            measure_info.max_amp_value_l_cu,
        ),
        strength_l_qu=get_measure_strength(
            measure_info.max_slope_value_l_qu,
            measure_info.max_amp_value_l_qu,
        ),
        strength_l_ch=get_measure_strength(
            measure_info.max_slope_value_l_ch,
            measure_info.max_amp_value_l_ch,
        ),
        strength_r_cu=get_measure_strength(
            measure_info.max_slope_value_r_cu,
            measure_info.max_amp_value_r_cu,
        ),
        strength_r_qu=get_measure_strength(
            measure_info.max_slope_value_r_qu,
            measure_info.max_amp_value_r_qu,
        ),
        strength_r_ch=get_measure_strength(
            measure_info.max_slope_value_r_ch,
            measure_info.max_amp_value_r_ch,
        ),
        width_l_cu=get_measure_width(
            measure_info.range_length_l_cu,
            measure_info.max_amp_value_l_cu,
            measure_info.max_slope_value_l_cu,
        ),
        width_l_qu=get_measure_width(
            measure_info.range_length_l_qu,
            measure_info.max_amp_value_l_qu,
            measure_info.max_slope_value_l_qu,
        ),
        width_l_ch=get_measure_width(
            measure_info.range_length_l_ch,
            measure_info.max_amp_value_l_ch,
            measure_info.max_slope_value_l_ch,
        ),
        width_r_cu=get_measure_width(
            measure_info.range_length_r_cu,
            measure_info.max_amp_value_r_cu,
            measure_info.max_slope_value_r_cu,
        ),
        width_r_qu=get_measure_width(
            measure_info.range_length_r_qu,
            measure_info.max_amp_value_r_qu,
            measure_info.max_slope_value_r_qu,
        ),
        width_r_ch=get_measure_width(
            measure_info.range_length_r_ch,
            measure_info.max_amp_value_r_ch,
            measure_info.max_slope_value_r_ch,
        ),
        width_value_l_cu=round(width_value_l_cu, 1) if width_value_l_cu else None,
        width_value_l_qu=round(width_value_l_qu, 1) if width_value_l_qu else None,
        width_value_l_ch=round(width_value_l_ch, 1) if width_value_l_ch else None,
        width_value_r_cu=round(width_value_r_cu, 1) if width_value_r_cu else None,
        width_value_r_qu=round(width_value_r_qu, 1) if width_value_r_qu else None,
        width_value_r_ch=round(width_value_r_ch, 1) if width_value_r_ch else None,
    )
    measure_info = await crud.measure_info.update(
        db_session=db_session,
        obj_current=measure_info,
        obj_new=measure_info_in,
    )


async def run_all_files():
    from sqlmodel import select

    db_session = SessionLocal()
    result = await db_session.execute(select(models.MeasureInfo.file_id).distinct())
    file_ids = result.scalars().all()
    file_ids = sorted(file_ids)

    error_files = []
    for file_id in file_ids:
        try:
            await step1_get_and_write(db_session, file_id)
        except Exception as e:
            error_files.append((file_id, e))
            await db_session.rollback()
        import gc

        gc.collect()
        # import time
        # time.sleep(1)

    return error_files


# run @ 20231022
async def run_all_measures():
    from sqlmodel import select

    db_session = SessionLocal()
    result = await db_session.execute(select(models.MeasureInfo.id).distinct())
    measure_ids = result.scalars().all()
    for measure_id in measure_ids:
        print("measure_id", measure_id)
        await step2_update_calculated_columns(
            db_session,
            measure_id,
        )


async def update_bcq():
    from sqlalchemy import text

    query = text(
        """
update measure.infos
set has_bcq = true
from measure.bcqs where measure.bcqs.measure_id = measure.infos.id
;
""",
    )
    db_session = SessionLocal()
    await db_session.execute(query)
    await db_session.commit()
    await db_session.close()


# """
# select *
# from measure.infos as a
# inner join measure.infos_bak_20231003 as b on b.id = a.id
# where a.max_amp_value_l_cu != b.max_amp_value_l_cu
# or a.max_amp_value_l_qu != b.max_amp_value_l_qu
# or a.max_amp_value_l_ch != b.max_amp_value_l_ch
# or a.max_amp_value_r_cu != b.max_amp_value_r_cu
# or a.max_amp_value_r_qu != b.max_amp_value_r_qu
# or a.max_amp_value_r_ch != b.max_amp_value_r_ch
# ;"""

# """
# select
# s.number,
# a.measure_time,
# a.max_amp_value_l_cu-b.max_amp_value_l_cu as l_cu_diff,
# a.max_amp_value_l_qu - b.max_amp_value_l_qu as l_qu_diff,
# a.max_amp_value_l_ch - b.max_amp_value_l_ch as l_ch_diff,
# a.max_amp_value_r_cu - b.max_amp_value_r_cu as r_cu_diff,
# a.max_amp_value_r_qu - b.max_amp_value_r_qu as r_qu_diff,
# a.max_amp_value_r_ch - b.max_amp_value_r_ch as r_ch_diff
# from measure.infos as a
# inner join measure.infos_bak_20231003 as b on b.id = a.id
# inner join measure.subjects as s on a.subject_id = s.id
# where a.max_amp_value_l_cu != b.max_amp_value_l_cu
# or a.max_amp_value_l_qu != b.max_amp_value_l_qu
# or a.max_amp_value_l_ch != b.max_amp_value_l_ch
# or a.max_amp_value_r_cu != b.max_amp_value_r_cu
# or a.max_amp_value_r_qu != b.max_amp_value_r_qu
# or a.max_amp_value_r_ch != b.max_amp_value_r_ch
# order by a.measure_time
# """
