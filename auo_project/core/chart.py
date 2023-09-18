from math import ceil, floor
from random import randint, uniform
from statistics import mean, quantiles, stdev

import numpy as np
import pydash as py_
from fastapi import HTTPException

from auo_project.core.utils import is_disease_match, normalize_parameter_name


def get_data_range():
    range_dict = {
        "h1": (0, 60),
        "t1": (0, 10),
        "h1/t1": (0, 4),
        "PR": (20, 100),
        "w1": (0, 1),
        "w1/t": (0, 1.2),
        "t1/t": (0, 0.5),
        "PW": (0, 0.3),
        "PWCV": (0.0, 0.12),
        "A0": (0, 7000),
        "cn": (0, 1),
    }
    for i in range(1, 12):
        range_dict[f"cn:c{i}"] = (0, 1)
        range_dict[f"cncv:c{i}"] = (0, 1)
        range_dict[f"pn:p{i}"] = (0, 1)
        range_dict[f"pncv:p{i}"] = (0, 1)

    return range_dict


def get_data_range_from_data(data):
    if not data:
        return [0, 0]
    min_value = floor(min([e["y"][0] for e in data]))
    max_value = (
        ceil(max([e["y"][-1] for e in data]) * 1.2)
        if max([e["y"][-1] for e in data]) >= 1
        else max([e["y"][-1] for e in data]) * 1.2
    )
    if min_value < 0:
        min_value = min_value * 1.2
    else:
        min_value = min_value * 0.8
    data_range = [min_value, max_value]
    return data_range


def get_data_by_column(column, n=100):
    data_range_dict = get_data_range()
    data_range = data_range_dict.get(column, (0, 100))
    min_adjust = (data_range[1] - data_range[0]) / 2 - (
        data_range[1] - data_range[0]
    ) * randint(5, 40) / 100
    max_adjust = (data_range[1] - data_range[0]) / 2 + (
        data_range[1] - data_range[0]
    ) * randint(5, 40) / 100
    data_list = np.random.normal(
        (min_adjust + max_adjust) / 2,
        (data_range[1] - data_range[0]) * 0.05,
        300,
    ).tolist()
    return data_list


def get_data_by_column_low_std(column, n=100):
    data_range_dict = get_data_range()
    data_range = data_range_dict.get(column, (0, 100))
    mean_val = (data_range[0] + data_range[1]) / 2 + (data_range[1] - data_range[0]) * (
        randint(5, 20) / 100
    ) * (randint(0, 10) % 2 == 0 and 1 or -1)
    data_list = np.random.normal(
        mean_val,
        (data_range[1] - data_range[0]) * 0.05,
        300,
    ).tolist()
    return data_list


def get_random_data(min, max):
    return uniform(min, max)


def get_box_plot_data(data_list):
    if len(data_list) == 0:
        return [0] * 5
    elif len(data_list) < 2:
        return [data_list[0]] * 5
    q1, q2, q3 = quantiles(data_list, n=4)
    lower = q1 - 1.5 * (q3 - q1)
    upper = q3 + 1.5 * (q3 - q1)
    min_val = min(data_list)
    if lower < min_val:
        lower = min_val
    max_val = max(data_list)
    if upper > max_val:
        upper = max_val
    return [lower, q1, q2, q3, upper]


def get_mean_and_std(data_list):
    if len(data_list) < 2:
        return [0, 0]
    return [mean(data_list), stdev(data_list)]


def get_filters():
    output = []
    six = {
        "type": "six_pulse",
        "options": [
            {"label": "左寸", "value": "l_cu"},
            {"label": "左關", "value": "l_qu"},
            {"label": "左尺", "value": "l_ch"},
            {"label": "右寸", "value": "r_cu"},
            {"label": "右關", "value": "r_qu"},
            {"label": "右尺", "value": "r_ch"},
        ],
    }

    time_domains = "h1,t1,h1/t1,PR,w1,w1/t,t1/t,PW,PWCV".split(",")
    domain = {
        "type": "domains",
        "options": [
            {
                "label": "時域",
                "value": "time_domain",
                "options": [
                    {"label": domain, "value": domain} for domain in time_domains
                ],
            },
            {
                "label": "頻域",
                "value": "freq_domain",
                "options": [
                    {"label": "A0", "value": "A0"},
                    {
                        "label": "CN",
                        "value": "cn",
                        "options": [
                            {"label": f"C{e}", "value": f"cn:c{e}"}
                            for e in range(1, 12)
                        ],
                    },
                    {
                        "label": "CNCV",
                        "value": "cncv",
                        "options": [
                            {"label": f"C{e}", "value": f"cncv:c{e}"}
                            for e in range(1, 12)
                        ],
                    },
                    {
                        "label": "PN",
                        "value": "pn",
                        "options": [
                            {"label": f"P{e}", "value": f"pn:p{e}"}
                            for e in range(1, 12)
                        ],
                    },
                    {
                        "label": "PNCV",
                        "value": "pncv",
                        "options": [
                            {"label": f"P{e}", "value": f"pncv:p{e}"}
                            for e in range(1, 12)
                        ],
                    },
                ],
            },
        ],
    }

    statistic = {
        "type": "statistics",
        "options": [
            {"label": "平均值", "value": "mean"},
            {"label": "標準差", "value": "std"},
            {"label": "變異數", "value": "cv"},
        ],
    }
    output.append(six)
    output.append(domain)
    output.append(statistic)

    return output


def get_chart_type1_data(x_options, y, z, z_options, sdata):
    time_domains_dict = {
        e: "time_domain" for e in "h1,t1,h1/t1,PR,w1,w1/t,t1/t,PW,PWCV".split(",")
    }
    freq_domains = [
        f"{freq_type}:{freq_type[0]}{e}"
        for e in range(1, 12)
        for freq_type in ["cn", "cncv", "pn", "pncv"]
    ] + ["A0"]
    freq_domains_dict = {e: "freq_domain" for e in freq_domains}
    domain_map = {
        **time_domains_dict,
        **freq_domains_dict,
    }
    if y not in domain_map:
        raise HTTPException(status_code=400, detail=f"y {y} not found")

    # TODO: check z is valid

    data = []

    for x_option in x_options:
        for z_option in z_options:
            match_data = [
                e["y"]
                for e in sdata
                if e["y"] is not None
                and e["x"] == x_option
                and (
                    py_.get(e, normalize_parameter_name(z)) == z_option["value"]
                    or is_disease_match(e, z, z_option["value"])
                )
            ]

            statistics_data = get_box_plot_data(match_data)
            data.append(
                {
                    "x": x_option,
                    # [lower, q1, q2, q3, upper]
                    "y": statistics_data,
                    "z": z_option["label"],
                },
            )
    domain_last = y
    if domain_last in time_domains_dict or domain_last == "A0":
        return_domain = [domain_map.get(domain_last), domain_last]
    else:
        return_domain = [
            domain_map.get(domain_last),
            domain_last.split(":")[0],
            domain_last,
        ]

    data_range = get_data_range_from_data(data)
    return {
        "y": {"domain": return_domain},
        "z": z,
        "data": data,
        "data_range": data_range,
    }


def get_chart_type2_data(x, x_options, domain_last, six_pulse, z, z_options, sdata):
    time_domains_dict = {
        e: "time_domain" for e in "h1,t1,h1/t1,PR,w1,w1/t,t1/t,PW,PWCV".split(",")
    }
    freq_domains = [
        f"{freq_type}:{freq_type[0]}{e}"
        for e in range(1, 12)
        for freq_type in ["cn", "cncv", "pn", "pncv"]
    ] + ["A0"]
    freq_domains_dict = {e: "freq_domain" for e in freq_domains}
    domain_map = {
        **time_domains_dict,
        **freq_domains_dict,
    }
    if domain_last not in domain_map:
        raise HTTPException(status_code=400, detail=f"y {domain_last} not found")

    # TODO: check z is valid

    data = []
    for x_option in x_options:
        for z_option in z_options:
            match_data = [
                e["y"]
                for e in sdata
                if e["y"] is not None
                and (
                    e["x"] == x_option.get("value")
                    or is_disease_match(e, x, x_option.get("value"))
                )
                and (
                    py_.get(e, normalize_parameter_name(z)) == z_option["value"]
                    or is_disease_match(e, z, z_option["value"])
                )
                and e["hand_position"] == six_pulse
            ]
            statistics_data = get_box_plot_data(match_data)
            data.append(
                {
                    "x": x_option.get("label"),
                    # [lower, q1, q2, q3, upper]
                    "y": statistics_data,
                    "z": z_option["label"],
                },
            )
    if domain_last in time_domains_dict or domain_last == "A0":
        return_domain = [domain_map.get(domain_last), domain_last]
    else:
        return_domain = [
            domain_map.get(domain_last),
            domain_last.split(":")[0],
            domain_last,
        ]

    data_range = get_data_range_from_data(data)
    return {
        "x": x,
        "y": {"six_pulse": six_pulse, "domain": return_domain},
        "z": z,
        "data": data,
        "data_range": data_range,
    }


def get_chart_type3_data(x_options, six_pulse, statistics, z, z_options, sdata):
    data = []
    data_range = [0, 0]
    for x_option in x_options:
        for z_option in z_options:
            match_data = [
                py_.get(e, x_option.lower())
                for e in sdata
                if py_.get(e, x_option.lower()) is not None
                and (
                    py_.get(e, normalize_parameter_name(z)) == z_option["value"]
                    or is_disease_match(e, z, z_option["value"])
                )
            ]
            mean_val, std_val = get_mean_and_std(match_data)

            data.append(
                {
                    "x": x_option,
                    # mean-std, mean, mean+std
                    "y": {
                        "y": round(mean_val, 2),
                        "yMin": round(mean_val - std_val, 2),
                        "yMax": round(mean_val + std_val, 2),
                        "yStd": round(std_val, 2),
                    },
                    "z": z_option["label"],
                },
            )

            data_range[0] = min(data_range[0], data[-1]["y"]["yMin"])
            data_range[1] = max(data_range[1], data[-1]["y"]["yMax"])

    # data_range_dict = get_data_range()

    new_data = (
        py_.chain(data)
        .group_by("z")
        .map(
            lambda val, key: {
                "label": key,
                "data": [o["y"] for o in val],
                "x": [o["x"] for o in val],
            },
        )
        .value()
    )
    labels = x_options

    if data_range[0] < 0:
        data_range[0] = data_range[0] * 1.2
    data_range[1] = data_range[1] * 1.2

    return {
        "y": {"six_pulse": six_pulse, "statistics": statistics},
        "z": z,
        "data": {"labels": labels, "datasets": new_data},
        "data_range": data_range,
    }
