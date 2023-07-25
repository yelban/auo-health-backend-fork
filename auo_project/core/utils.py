from datetime import date, datetime, time
from random import randrange
from typing import Union

import dateutil.parser
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
    return f"{s[0:4]}{wildcard * (len(s) - 6)}{s[-2:]}"


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


def get_hr_type(n):
    if not n:
        return n
    if n >= 90:
        return 2
    elif n < 50:
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


def safe_parse_dt(s):
    try:
        return dateutil.parser.parse(s)
    except Exception as e:
        print(e)
        return None


def get_date(text):
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except:
        return None


def get_time(text):
    try:
        return datetime.strptime(text, "%H:%M").time()
    except:
        return None


def get_datetime(text):
    try:
        return datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
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


def get_measure_strength(max_slop, max_amp_value):
    if max_slop is None or max_amp_value is None:
        return None
    if max_slop > 199 and max_amp_value > 34:
        return 2
    elif max_slop < 100 and max_amp_value < 10:
        return 0
    else:
        return 1


def get_measure_width(range_length, max_amp_value):
    if range_length is None or max_amp_value is None:
        return None
    if range_length / 0.2 < 15 and max_amp_value < 10:
        return 0
    elif range_length / 0.2 > 24 and max_amp_value > 34:
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
