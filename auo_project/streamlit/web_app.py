# https://github.com/streamlit/streamlit/issues/3218
import pydantic

pydantic.class_validators._FUNCS.clear()

import os

import streamlit as st
from auo_project.streamlit import decrypt, encrypt

DIR = os.path.dirname(os.path.realpath(__file__))
st.set_page_config(
    page_title="AUO Health Tools",
    initial_sidebar_state="auto",
)


def main():
    page_names_to_funcs = {
        "解密": decrypt.page,
        "加密": encrypt.page,
    }

    selected_page = st.sidebar.selectbox("請選擇功能", page_names_to_funcs.keys())
    page_names_to_funcs[selected_page]()


if __name__ == "__main__":
    main()
