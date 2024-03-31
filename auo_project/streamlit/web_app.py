# https://github.com/streamlit/streamlit/issues/3218
import pydantic

pydantic.class_validators._FUNCS.clear()

import os

import streamlit as st
from auo_project.streamlit import (
    decrypt_file,
    decrypt_zip,
    download,
    download2,
    download_six_sec,
    encrypt_zip,
    update_formula,
)

DIR = os.path.dirname(os.path.realpath(__file__))
st.set_page_config(
    page_title="AUO Health Tools",
    initial_sidebar_state="auto",
)


def main():
    page_names_to_funcs = {
        "解密壓縮檔": decrypt_zip.page,
        "加密壓縮檔": encrypt_zip.page,
        "解密單檔": decrypt_file.page,
        "下載並解密壓縮檔": download.page,
        "下載壓縮檔": download2.page,
        "設定公式": update_formula.page,
        "下載六秒資料": download_six_sec.page,
    }

    selected_page = st.sidebar.selectbox("請選擇功能", page_names_to_funcs.keys())
    page_names_to_funcs[selected_page]()


if __name__ == "__main__":
    main()
