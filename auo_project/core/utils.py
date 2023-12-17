from datetime import date, datetime, time
from io import StringIO
from random import randrange
from typing import Optional, Union

import dateutil.parser
import pandas as pd
import pydash as py_
from dateutil.relativedelta import relativedelta

from auo_project import schemas


def mask_credential_name(s: str):
    wildcard = "*"
    if len(s) == 1:
        return s
    elif len(s) == 2:
        return f"{s[0]}{wildcard}"
    elif len(s) == 3:
        return f"{s[0]}{wildcard*(len(s)-2)}{s[-1]}"
    else:
        return f"{s[0]}{wildcard*(len(s)-3)}{s[-2:]}"


def mask_crediential_sid(s: str):
    wildcard = "*"
    if len(s) <= 1:
        return s
    elif len(s) == 2:
        return f"{s[0]}{wildcard}"
    else:
        one_third_cnt = len(s) // 3
        return f"{s[0:one_third_cnt]}{wildcard * (len(s) - one_third_cnt*2)}{s[-1*one_third_cnt:]}"


def safe_divide(a, b):
    if a is None or b is None:
        return None
    elif b == 0:
        return 0
    return a / b


def safe_substract(a, b):
    if a is None or b is None:
        return None
    return a - b


def get_filters(f):
    return dict([(k, v) for k, v in f.items() if v is not None and v != []])


def get_hr_type(hr, other_hand_hr):
    if not hr:
        return hr
    if hr > 90:
        return 2
    elif hr > 85 and other_hand_hr > 90:
        return 2
    elif hr < 60:
        return 0
    return 1


def compare_x_diff2(a, x):
    """compare a of 1. it's a compatibable function for compare_x_diff"""
    data = []
    cols = [f"{x}{i}" for i in range(1, 12)]
    for c in cols:
        ac = getattr(a, c, 0)
        if ac is not None:
            diff_type = "pos"
            data.append(
                {
                    "x": c.upper(),
                    "pct": ac,
                    "type": diff_type,
                },
            )

    return {
        "data": data,
        "x_field": "x",
        "y_field": "pct",
    }


def compare_x_diff(a, b, x):
    """compare a and b based on b"""
    data = []
    cols = [f"{x}{i}" for i in range(1, 12)]
    for c in cols:
        ac = getattr(a, c, 0)
        bc = getattr(b, c, 0)
        if ac is not None and bc is not None:
            diff_type = "pos" if ac > bc else "neg"
            data.append(
                {
                    "x": c.upper(),
                    "pct": round(safe_divide(abs(ac - bc), bc) * 100),
                    "type": diff_type,
                },
            )

    return {
        "data": data,
        "x_field": "x",
        "y_field": "pct",
    }


def compare_cn_diff(a, b):
    return compare_x_diff(a, b, "c")


def compare_pn_diff(a, b):
    return compare_x_diff(a, b, "p")


def get_pct_cmp_overall_and_standard(cn_dict, cn_means_dict, standard_cn_dict, c_or_p):
    cmp_diff_func = compare_cn_diff if c_or_p == "c" else compare_pn_diff
    return {
        "overall": {
            "l_cu": cmp_diff_func(cn_dict["l_cu"], cn_means_dict["l_cu"]),
            "l_qu": cmp_diff_func(cn_dict["l_qu"], cn_means_dict["l_qu"]),
            "l_ch": cmp_diff_func(cn_dict["l_ch"], cn_means_dict["l_ch"]),
            "r_cu": cmp_diff_func(cn_dict["r_cu"], cn_means_dict["r_cu"]),
            "r_qu": cmp_diff_func(cn_dict["r_qu"], cn_means_dict["r_qu"]),
            "r_ch": cmp_diff_func(cn_dict["r_ch"], cn_means_dict["r_ch"]),
        },
        "standard_value": {
            "l_cu": cmp_diff_func(cn_dict["l_cu"], standard_cn_dict.get("l_cu", {})),
            "l_qu": cmp_diff_func(cn_dict["l_qu"], standard_cn_dict.get("l_qu", {})),
            "l_ch": cmp_diff_func(cn_dict["l_ch"], standard_cn_dict.get("l_ch", {})),
            "r_cu": cmp_diff_func(cn_dict["r_cu"], standard_cn_dict.get("r_cu", {})),
            "r_qu": cmp_diff_func(cn_dict["r_qu"], standard_cn_dict.get("r_qu", {})),
            "r_ch": cmp_diff_func(cn_dict["r_ch"], standard_cn_dict.get("r_ch", {})),
        },
    }


def compare_cn_diff2(a):
    return compare_x_diff2(a, "c")


def compare_pn_diff2(a):
    return compare_x_diff2(a, "p")


def get_pct_cmp_base(cn_dict, c_or_p):
    cmp_diff_func = compare_cn_diff2 if c_or_p == "c" else compare_pn_diff2
    return {
        "overall": {
            "l_cu": cmp_diff_func(cn_dict["l_cu"]),
            "l_qu": cmp_diff_func(cn_dict["l_qu"]),
            "l_ch": cmp_diff_func(cn_dict["l_ch"]),
            "r_cu": cmp_diff_func(cn_dict["r_cu"]),
            "r_qu": cmp_diff_func(cn_dict["r_qu"]),
            "r_ch": cmp_diff_func(cn_dict["r_ch"]),
        },
        "standard_value": {
            "l_cu": cmp_diff_func(cn_dict["l_cu"]),
            "l_qu": cmp_diff_func(cn_dict["l_qu"]),
            "l_ch": cmp_diff_func(cn_dict["l_ch"]),
            "r_cu": cmp_diff_func(cn_dict["r_cu"]),
            "r_qu": cmp_diff_func(cn_dict["r_qu"]),
            "r_ch": cmp_diff_func(cn_dict["r_ch"]),
        },
    }


def get_age(measure_time: datetime, birth_date: Union[datetime, date]):
    if (isinstance(measure_time, datetime) or isinstance(measure_time, date)) and (
        isinstance(birth_date, datetime) or isinstance(birth_date, date)
    ):
        return relativedelta(measure_time, birth_date).years


def switch_strength_value(v):
    if v:
        if str(v) == "0":
            return 2
        elif str(v) == "1":
            return v
        elif str(v) == "2":
            return 0
        else:
            raise ValueError(f"must be null/0/1/2 but got {v}")


def safe_int(v):
    try:
        return int(v)
    except Exception:
        return None


def safe_float(v):
    try:
        return float(v)
    except Exception:
        return None


def safe_parse_dt(s):
    try:
        return dateutil.parser.parse(s)
    except Exception as e:
        print(e)
        return None


def get_date(text):
    if isinstance(text, date):
        return text
    if isinstance(text, datetime):
        return text.date()
    try:
        if "-" in text:
            return datetime.strptime(text, "%Y-%m-%d").date()
        elif "/" in text:
            return datetime.strptime(text, "%Y/%m/%d").date()
    except:
        return None


def get_time(text):
    if isinstance(text, datetime):
        return text.time()
    try:
        return datetime.strptime(text, "%H:%M").time()
    except:
        return None


def get_datetime(text):
    if isinstance(text, datetime):
        return text
    try:
        if "-" in text:
            return datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
        elif "/" in text:
            return datetime.strptime(text, "%Y/%m/%d %H:%M:%S")
    except:
        return None


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    try:
        start = start if isinstance(start, time) else get_time(start)
        end = end if isinstance(end, time) else get_time(end)
        x = x if isinstance(x, time) else get_time(x)
        if start <= end:
            return start <= x <= end
        else:
            return start <= x or x <= end
    except Exception as e:
        print("error", e)


def get_bmi(height: Union[int, float], weight: Union[int, float]) -> Optional[float]:
    bmi = None
    if isinstance(height, (int, float)) and isinstance(weight, (int, float)):
        bmi = safe_divide(weight, (height / 100) ** 2)
    return bmi


def get_measure_strength(max_slop, max_amp_value):
    if max_slop is None or max_amp_value is None:
        return None
    if max_slop > 199 or max_amp_value > 33:
        return 2
    elif max_amp_value < 10:
        return 0
    else:
        return 1


# 大細類型
def get_measure_width(range_length, max_amp_value, max_slop):
    if range_length is None or max_amp_value is None:
        return None
    if range_length / 0.2 < 25 and (max_amp_value >= 20 or max_slop > 180):
        return 0
    elif range_length / 0.2 < 25 and (max_amp_value < 20 or max_slop < 100):
        return 2
    else:
        return 1


def get_mock_bcq():
    return schemas.BCQ(
        exist=randrange(0, 1),
        score_yang=randrange(0, 100),
        score_yin=randrange(0, 100),
        score_phlegm=randrange(0, 100),
        score_yang_head=randrange(0, 100),
        score_yang_chest=randrange(0, 100),
        score_yang_limbs=randrange(0, 100),
        score_yang_abdomen=randrange(0, 100),
        score_yang_surface=randrange(0, 100),
        score_yin_head=randrange(0, 100),
        score_yin_limbs=randrange(0, 100),
        score_yin_gt=randrange(0, 100),
        score_yin_surface=randrange(0, 100),
        score_yin_abdomen=randrange(0, 100),
        score_phlegm_trunk=randrange(0, 100),
        score_phlegm_surface=randrange(0, 100),
        score_phlegm_head=randrange(0, 100),
        score_phlegm_gt=randrange(0, 100),
        percentage_yang=randrange(0, 100),
        percentage_yin=randrange(0, 100),
        percentage_phlegm=randrange(0, 100),
        percentage_yang_head=randrange(0, 100),
        percentage_yang_chest=randrange(0, 100),
        percentage_yang_limbs=randrange(0, 100),
        percentage_yang_abdomen=randrange(0, 100),
        percentage_yang_surface=randrange(0, 100),
        percentage_yin_head=randrange(0, 100),
        percentage_yin_limbs=randrange(0, 100),
        percentage_yin_gt=randrange(0, 100),
        percentage_yin_surface=randrange(0, 100),
        percentage_yin_abdomen=randrange(0, 100),
        percentage_phlegm_trunk=randrange(0, 100),
        percentage_phlegm_surface=randrange(0, 100),
        percentage_phlegm_head=randrange(0, 100),
        percentage_phlegm_gt=randrange(0, 100),
    )


# TODO: check whether filter pass rate
def normalize_parameter_name(name):
    # replace ':' for a026:c056:001 and a026:c056:002
    if isinstance(name, str):
        return name.replace(":", "")


def is_disease_include_option(answer: str, input_option: str) -> bool:
    if answer == input_option:
        return True
    answer_category_id, answer_disease_id = answer.split(":")
    option_category_id, option_disease_id = input_option.split(":")
    # TODO: answer without :000?
    if answer_category_id == option_category_id and (
        answer_disease_id == "000" or option_disease_id == "000"
    ):
        return True
    return False


def is_disease_match(data: dict, qid: str, input_option: Union[str, dict]):
    if qid != "a008":
        return False
    survey_answers = py_.get(data, "a008", [])
    if not survey_answers:
        return False

    if isinstance(input_option, str):
        if any(
            [
                is_disease_include_option(answer, input_option)
                for answer in survey_answers
            ],
        ):
            return True

    elif isinstance(input_option, dict):
        includes = input_option.get("include", [])
        excludes = input_option.get("exclude", [])
        is_all_include = all(
            [
                any(
                    [
                        is_disease_include_option(answer, include_option)
                        for answer in survey_answers
                    ],
                )
                for include_option in includes
            ],
        )
        is_all_exclude = (
            any(
                [
                    any(
                        [
                            is_disease_include_option(answer, exclude_option)
                            for answer in survey_answers
                        ],
                    )
                    for exclude_option in excludes
                ],
            )
            is False
        )
        if is_all_include and is_all_exclude:
            return True
    return False


def get_pass_rate_from_statistics(records) -> tuple:
    pass_rate_l_cu = None
    pass_rate_l_qu = None
    pass_rate_l_ch = None
    pass_rate_r_cu = None
    pass_rate_r_qu = None
    pass_rate_r_ch = None

    for record in records:
        if record.hand == "Left" and record.position == "Cu":
            pass_rate_l_cu = record.pass_rate
        elif record.hand == "Left" and record.position == "Qu":
            pass_rate_l_qu = record.pass_rate
        elif record.hand == "Left" and record.position == "Ch":
            pass_rate_l_ch = record.pass_rate
        elif record.hand == "Right" and record.position == "Cu":
            pass_rate_r_cu = record.pass_rate
        elif record.hand == "Right" and record.position == "Qu":
            pass_rate_r_qu = record.pass_rate
        elif record.hand == "Right" and record.position == "Ch":
            pass_rate_r_ch = record.pass_rate

    return (
        pass_rate_l_cu,
        pass_rate_l_qu,
        pass_rate_l_ch,
        pass_rate_r_cu,
        pass_rate_r_qu,
        pass_rate_r_ch,
    )


def get_max_amp_value(select_static: float, analyze_raw_file_content: str) -> float:
    if (
        select_static is None
        or analyze_raw_file_content is None
        or analyze_raw_file_content == ""
    ):
        return None
    try:
        df = pd.read_csv(StringIO(analyze_raw_file_content), header=None, sep="\t")
        idx_min = (df[3] - select_static).abs().idxmin()
        if pd.isnull(idx_min):
            return None
        found = df.iloc[idx_min, 0]
        return found
    except Exception as e:
        print(f"get_max_amp_value error: {e}")


def get_subject_schema(org_name: str):
    if org_name in ("nricm", "tongue_label"):
        return schemas.SubjectRead
    return schemas.SubjectSecretRead
