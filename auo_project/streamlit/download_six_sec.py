import csv
from io import StringIO
from itertools import zip_longest

from sqlalchemy import create_engine

import streamlit as st
from auo_project.core.config import settings


def safe_float(value):
    try:
        return float(value)
    except ValueError:
        return value


def page():
    if "run_button" in st.session_state and st.session_state.run_button == True:
        st.session_state.disabled = True
    else:
        st.session_state.disabled = False

    st.write("請輸入單人單次網址")
    url = st.text_input("網址", "", disabled=st.session_state.disabled)
    if url == "":
        st.stop()

    password = st.text_input("密碼", "", disabled=st.session_state.disabled)

    if st.button("確認", disabled=st.session_state.disabled, key="run_button"):
        if password == "":
            st.write("請輸入密碼")
            st.stop()

        elif password == settings.STREAMLIT_PASSWORD and url != "":
            measure_id = url.split("/")[-1]

            engine = create_engine(
                settings.DATABASE_URI,
                connect_args={"connect_timeout": 10},
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=0,
                pool_timeout=10,
            )
            conn = engine.raw_connection()
            print("measure_id", measure_id)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    select
                        raw_data.measure_id,
                        infos.number,
                        infos.measure_time,
                        raw_data.six_sec_l_cu,
                        raw_data.six_sec_l_qu,
                        raw_data.six_sec_l_ch,
                        raw_data.six_sec_r_cu,
                        raw_data.six_sec_r_qu,
                        raw_data.six_sec_r_ch
                    from measure.raw_data
                    inner join measure.infos on raw_data.measure_id = infos.id
                    where raw_data.measure_id = %s
                            """,
                    (measure_id,),
                )
                record = cursor.fetchone()
                if record is None:
                    st.write(f"找不到資料（檢測編號 {measure_id}）")
                    st.stop()

            conn.close()
            st.session_state.disabled = True

            csv_output = StringIO()
            csv_writer = csv.writer(
                csv_output,
                delimiter=",",
                quoting=csv.QUOTE_NONNUMERIC,
            )
            csv_writer.writerow(
                [
                    "measure_id",
                    "number",
                    "measure_time",
                    "six_sec_l_cu",
                    "six_sec_l_qu",
                    "six_sec_l_ch",
                    "six_sec_r_cu",
                    "six_sec_r_qu",
                    "six_sec_r_ch",
                ],
            )
            six_sec_l_cu = (
                map(safe_float, record[3].strip("\r\n").split("\n"))
                if record[3]
                else []
            )
            six_sec_l_qu = (
                map(safe_float, record[4].strip("\r\n").split("\n"))
                if record[4]
                else []
            )
            six_sec_l_ch = (
                map(safe_float, record[5].strip("\r\n").split("\n"))
                if record[5]
                else []
            )
            six_sec_r_cu = (
                map(safe_float, record[6].strip("\r\n").split("\n"))
                if record[6]
                else []
            )
            six_sec_r_qu = (
                map(safe_float, record[7].strip("\r\n").split("\n"))
                if record[7]
                else []
            )
            six_sec_r_ch = (
                map(safe_float, record[8].strip("\r\n").split("\n"))
                if record[8]
                else []
            )
            points_it = zip_longest(
                six_sec_l_cu,
                six_sec_l_qu,
                six_sec_l_ch,
                six_sec_r_cu,
                six_sec_r_qu,
                six_sec_r_ch,
                fillvalue="",
            )
            for idx, points in enumerate(points_it):
                if idx == 0:
                    csv_writer.writerow([str(record[0]), record[1], record[2], *points])
                else:
                    csv_writer.writerow(["", "", "", *points])

            st.download_button(
                label="下載 CSV 檔",
                data=csv_output.getvalue(),
                file_name=f"six_sec_{record[1]}_{record[2]}.csv",
            )

            st.session_state.disabled = False

        else:
            st.write("密碼錯誤")
            # st.stop()
            return
