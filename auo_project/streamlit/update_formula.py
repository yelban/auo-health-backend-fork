from code_editor import code_editor
from sqlalchemy import create_engine

import streamlit as st
from auo_project.core.config import settings
from auo_project.core.constants import MAX_DEPTH_RATIO


def get_original_formulas():
    max_depth_ratio = MAX_DEPTH_RATIO
    strength_code_string = """def get_custom_strength(max_slop, max_amp_value):
    '''
    max_slop (float): 最大斜率
    max_amp_value (float): 最大振幅
    return (int): 0: 無力, 1: 正常, 2: 有力
    '''
    if max_slop is None or max_amp_value is None:
        return None
    if max_slop > 199 or max_amp_value > 33:
        return 2
    elif max_amp_value < 10:
        return 0
    else:
        return 1
"""
    width_code_string = """def get_custom_width(range_length, max_amp_value, max_slop):
    '''
    range_length (float): 有效範圍長度(單位:mm)
    max_amp_value (float): 最大振幅
    max_slop (float): 最大斜率
    return (int): 0: 大, 1: 正常, 2: 細
    '''
    if range_length is None or max_amp_value is None:
        return None
    if range_length / 0.2 < 25 and (max_amp_value >= 20 or max_slop > 180):
        return 0
    elif range_length / 0.2 < 25 and (max_amp_value < 20 or max_slop < 100):
        return 2
    else:
        return 1
    """
    hr_type_code_string = """def get_custom_hr_type(hr, other_hand_hr):
    '''
    hr (float): 脈率
    other_hand_hr (float): 另一隻手脈率
    return (int): 0: 遲 1: 正常, 2: 數
    '''
    if not hr:
        return hr
    if hr > 90:
        return 2
    elif hr > 85 and other_hand_hr > 90:
        return 2
    elif hr < 60:
        return 0
    return 1
"""
    return {
        "max_depth_ratio": max_depth_ratio,
        "strength_code": strength_code_string,
        "width_code": width_code_string,
        "hr_type_code": hr_type_code_string,
    }


def get_formulas():
    if "password_disabled" in st.session_state:
        st.session_state.password_disabled = False
    if (
        "password_disabled" in st.session_state
        and st.session_state.password_disabled is False
    ):
        password = st.text_input("密碼", "")
        if password == "":
            st.write("請輸入密碼")
            st.stop()
        elif password == settings.STREAMLIT_PASSWORD:
            st.session_state.password_disabled = True

    engine = create_engine(
        settings.DATABASE_URI,
        connect_args={"connect_timeout": 10},
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=0,
        pool_timeout=10,
    )
    conn = engine.raw_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
select max_depth_ratio, strength_code, width_code, hr_type_code from measure.custom_formulas
""",
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return {
        "max_depth_ratio": list(map(int, result[0].split(":"))),
        "strength_code": result[1],
        "width_code": result[2],
        "hr_type_code": result[3],
    }


def save_formula(column_name, code_string):
    engine = create_engine(
        settings.DATABASE_URI,
        connect_args={"connect_timeout": 10},
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=0,
        pool_timeout=10,
    )
    conn = engine.raw_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
update measure.custom_formulas
set {column_name} = %s
""",
        (code_string,),
    )
    conn.commit()
    cursor.close()
    conn.close()


def page():
    if "run_button" in st.session_state and st.session_state.run_button == True:
        st.session_state.disabled = True
    else:
        st.session_state.disabled = False

    st.header("調整單人單次基本分析詳細資料頁面公式（不更改資料庫）")

    original_formula_dict = get_original_formulas()
    if "formula_dict" not in st.session_state:
        st.session_state["formula_dict"] = get_formulas()

    formula_dict = st.session_state["formula_dict"]
    print("formula_dict", formula_dict)
    formula_dict = get_formulas()

    st.subheader("請設定浮中沉比例")
    values = st.slider(
        "",
        0,
        10,
        (
            formula_dict["max_depth_ratio"][0],
            formula_dict["max_depth_ratio"][0] + formula_dict["max_depth_ratio"][1],
        ),
    )
    max_depth_ratio = [values[0], values[1] - values[0], 10 - values[1]]
    st.write("浮中沉比例: ", ":".join(map(str, max_depth_ratio)))
    if st.button("儲存", key="save_button"):
        save_formula("max_depth_ratio", ":".join(map(str, max_depth_ratio)))
    if st.button("重置", key="reset_button"):
        save_formula(
            "max_depth_ratio",
            ":".join(map(str, original_formula_dict["max_depth_ratio"])),
        )
        st.session_state["formula_dict"] = get_formulas()

    st.subheader("請調整「力量」公式")
    strength_code_test_cases = """
print("測試結果: ")
print(get_custom_strength(100, 10))
"""
    custom_btns = [
        {
            "name": "儲存",
            "feather": "Save",
            "hasText": True,
            "commands": [
                "save-state",
                ["response", "saved"],
                [
                    "infoMessage",
                    {
                        "text": "儲存成功",
                        "timeout": 2500,
                        "classToggle": "show",
                    },
                ],
            ],
            "response": "saved",
            "style": {"right": "0.4rem"},
            "alwaysOn": False,
        },
        {
            "name": "重置",
            "feather": "RotateCcw",
            "hasText": True,
            "commands": [
                "reset",
                ["response", "reset"],
                [
                    "infoMessage",
                    {
                        "text": "重置成功",
                        "timeout": 2500,
                        "classToggle": "show",
                    },
                ],
            ],
            "response": "reset",
            "style": {"top": "2rem", "right": "0.4rem"},
            "alwaysOn": False,
        },
    ]
    stength_response_dict = code_editor(
        formula_dict["strength_code"],
        lang="python",
        buttons=custom_btns,
        allow_reset=True,
    )
    print("stength_response_dict", stength_response_dict)
    if (
        stength_response_dict["type"] == "saved"
        and len(stength_response_dict["text"]) != 0
    ):
        # run test
        print(
            'stength_response_dict["text"]',
            len(stength_response_dict["text"]),
            stength_response_dict["text"],
        )
        exec(stength_response_dict["text"] + "\n" + strength_code_test_cases)
        save_formula("strength_code", stength_response_dict["text"])

    if stength_response_dict["type"] == "reset":
        save_formula("strength_code", original_formula_dict["strength_code"])
        # st.session_state["formula_dict"] = get_formulas()

    st.subheader("請調整「大細」公式")
    width_response_dict = code_editor(
        formula_dict["width_code"],
        lang="python",
        buttons=custom_btns,
        allow_reset=True,
    )
    if width_response_dict["type"] == "saved" and len(width_response_dict["text"]) != 0:
        # run test
        print(
            'width_response_dict["text"]',
            len(width_response_dict["text"]),
            width_response_dict["text"],
        )
        # exec(width_response_dict["text"] + "\n" + strength_code_test_cases)
        save_formula("width_code", width_response_dict["text"])

    if width_response_dict["type"] == "reset":
        save_formula("width_code", original_formula_dict["width_code"])
        # st.rerun()

    st.subheader("請調整「脈率類型」公式")
    hr_type_response_dict = code_editor(
        formula_dict["hr_type_code"],
        lang="python",
        buttons=custom_btns,
        allow_reset=True,
    )
    if (
        hr_type_response_dict["type"] == "saved"
        and len(hr_type_response_dict["text"]) != 0
    ):
        # run test
        print(
            'hr_type_response_dict["text"]',
            len(hr_type_response_dict["text"]),
            hr_type_response_dict["text"],
        )
        # exec(hr_type_response_dict["text"] + "\n" + strength_code_test_cases)

        save_formula("hr_type_code", hr_type_response_dict["text"])

    if hr_type_response_dict["type"] == "reset":
        save_formula("hr_type_code", original_formula_dict["hr_type_code"])
        # st.rerun()
