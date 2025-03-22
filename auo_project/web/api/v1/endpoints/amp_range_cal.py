from io import StringIO

import pandas as pd
from sqlalchemy import create_engine

from auo_project.core.config import settings


def get_all_amp_range(data):
    if data is None:
        return (0, 0)
    file = StringIO(data)
    names = ("amp", "depth", "slope", "static")
    df = pd.read_csv(file, names=names, sep="\t", header=None)
    for c in names:
        df.loc[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna()
    df = df.assign(depth=df.depth / 0.2)
    return (df.amp[df.amp > 0].min(), df.amp.max())


def safe_float(x):
    try:
        return float(x)
    except:
        return 0


def get_six_sec_amp_range(data):
    if data is None:
        return (0, 0)
    points = [safe_float(x) for x in data.split("\n")]
    return (min(points), max(points))


def update_result(result, data, name):
    if data[0] < result[name]["min"]:
        result[name]["min"] = data[0]
    if data[1] > result[name]["max"]:
        result[name]["max"] = data[1]
    return result


counter = 0
result = {
    "six_sec_l_cu": {"min": 1000, "max": 0},
    "six_sec_l_qu": {"min": 1000, "max": 0},
    "six_sec_l_ch": {"min": 1000, "max": 0},
    "six_sec_r_cu": {"min": 1000, "max": 0},
    "six_sec_r_qu": {"min": 1000, "max": 0},
    "six_sec_r_ch": {"min": 1000, "max": 0},
    "all_sec_analyze_raw_l_cu": {"min": 1000, "max": 0},
    "all_sec_analyze_raw_l_qu": {"min": 1000, "max": 0},
    "all_sec_analyze_raw_l_ch": {"min": 1000, "max": 0},
    "all_sec_analyze_raw_r_cu": {"min": 1000, "max": 0},
    "all_sec_analyze_raw_r_qu": {"min": 1000, "max": 0},
    "all_sec_analyze_raw_r_ch": {"min": 1000, "max": 0},
}


engine = create_engine(
    settings.DATABASE_URI,
    connect_args={"connect_timeout": 10},
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=0,
    pool_timeout=10,
)
conn = engine.raw_connection()
with conn.cursor(name="name_of_cursor") as cursor:
    cursor.itersize = 100
    cursor.execute("select * from measure.raw_data")
    for row in cursor:
        print(f"counter: {counter}")

        counter += 1
        six_sec_l_cu_range = get_six_sec_amp_range(row[1])
        six_sec_l_qu_range = get_six_sec_amp_range(row[2])
        six_sec_l_ch_range = get_six_sec_amp_range(row[3])
        six_sec_r_cu_range = get_six_sec_amp_range(row[4])
        six_sec_r_qu_range = get_six_sec_amp_range(row[5])
        six_sec_r_ch_range = get_six_sec_amp_range(row[6])
        all_sec_analyze_raw_l_cu_range = get_all_amp_range(row[7])
        all_sec_analyze_raw_l_qu_range = get_all_amp_range(row[8])
        all_sec_analyze_raw_l_ch_range = get_all_amp_range(row[9])
        all_sec_analyze_raw_r_cu_range = get_all_amp_range(row[10])
        all_sec_analyze_raw_r_qu_range = get_all_amp_range(row[11])
        all_sec_analyze_raw_r_ch_range = get_all_amp_range(row[12])

        update_result(result, six_sec_l_cu_range, "six_sec_l_cu")
        update_result(result, six_sec_l_qu_range, "six_sec_l_qu")
        update_result(result, six_sec_l_ch_range, "six_sec_l_ch")
        update_result(result, six_sec_r_cu_range, "six_sec_r_cu")
        update_result(result, six_sec_r_qu_range, "six_sec_r_qu")
        update_result(result, six_sec_r_ch_range, "six_sec_r_ch")
        update_result(
            result,
            all_sec_analyze_raw_l_cu_range,
            "all_sec_analyze_raw_l_cu",
        )
        update_result(
            result,
            all_sec_analyze_raw_l_qu_range,
            "all_sec_analyze_raw_l_qu",
        )
        update_result(
            result,
            all_sec_analyze_raw_l_ch_range,
            "all_sec_analyze_raw_l_ch",
        )
        update_result(
            result,
            all_sec_analyze_raw_r_cu_range,
            "all_sec_analyze_raw_r_cu",
        )
        update_result(
            result,
            all_sec_analyze_raw_r_qu_range,
            "all_sec_analyze_raw_r_qu",
        )
        update_result(
            result,
            all_sec_analyze_raw_r_ch_range,
            "all_sec_analyze_raw_r_ch",
        )


print(result)
