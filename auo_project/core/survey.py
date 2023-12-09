""" 一個收案編號會對到多個問卷、量測資料，理論上是一對一 """

import json
import re
from datetime import date, datetime, time, timedelta
from functools import partial
from typing import List, Union
from uuid import UUID

import pandas as pd
import pydash as py_
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from auo_project import crud, schemas
from auo_project.core.constants import SEX_TYPE_LABEL, ParameterType
from auo_project.core.recipe import find_all_component_names, get_parameters
from auo_project.core.utils import (
    get_age,
    get_bmi,
    get_date,
    get_datetime,
    safe_divide,
    safe_float,
    safe_int,
)
from auo_project.db.session import SessionLocal


class SurveyAnswer(BaseModel):
    survey_at: datetime
    proj_num: str = None
    number: str
    gender: str = None
    height: float = None
    weight: float = None
    disease: list = None
    age: int = None
    birth_date: date = None
    a003: str = None
    a004: str = None
    a005: str = None
    a006: str = None
    a007: str = None
    a008: List[str] = None
    a024: str = None
    a025: dict = None
    a028: str = None
    a029: str = None
    a030: str = None
    a031: dict = None
    a032: str = None
    a033: str = None
    a034: str = None
    a035: str = None
    a036: str = None
    a037: str = None
    a038: str = None
    a039: str = None
    a040: str = None
    a040_other: str = None

    p001: str = None
    s001: str = None
    s001_other: str = None
    s002: str = None
    s002_other: str = None
    s003: str = None
    s005: str = None
    office_hours: tuple = None
    s006: int = None
    s007: int = None
    s008: int = None
    s010: List[str] = None
    s011: int = None
    s012: int = None
    s013: List[str] = None
    s014: int = None
    s016: str = None
    s017: int = None
    s018: int = None
    s020: int = None
    s021: str = None
    # s024: str = None  # 此問卷沒有：是否熬夜
    s025: str = None
    s026: str = None  # 額外計算
    s027: str = None
    s028: str = None
    s029: str = None
    s030: str = None
    s031: str = None
    s032: str = None
    s033: str = None
    s034: str = None
    s035: str = None
    s036: str = None
    s037: str = None
    s039: str = None
    s040: str = None
    s041: str = None
    s042: str = None
    s043: str = None
    # s044: int = None
    s045: str = None

    a026c056001: str = None  # a026:c056:001
    a026c056002: str = None  # a026:c056:002

    # TODO: fixme
    eat_at: datetime = None
    symptom_from: datetime = None
    covid_from: datetime = None
    menstruation_from: datetime = None

    # blood_pressure:
    sbp: int = None
    dbp: int = None
    hr: int = None


class SingletonSurveyResult:
    _instance = None
    survey_result = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # self.survey_result = await process_qa()
        pass

    async def get_result(self) -> List[SurveyAnswer]:
        if self.survey_result is None:
            self.survey_result = await process_qa()
        return self.survey_result


survey_instance = SingletonSurveyResult()

# unit: hour
def get_time_duration(
    start: Union[str, datetime, time],
    end: Union[str, datetime, time],
):
    if isinstance(start, time):
        start = datetime(1900, 1, 1, start.hour, start.minute, start.second)
    if isinstance(end, time):
        end = datetime(1900, 1, 1, end.hour, end.minute, end.second)
    if isinstance(start, (datetime)) and isinstance(end, (datetime)):
        return (end - start).seconds / 3600

    try:
        start_time = datetime.strptime(start, "%H:%M")
        end_time = datetime.strptime(end, "%H:%M")
        return (end_time - start_time).seconds / 3600
    except:
        return None


def get_days_range(start, end):
    try:
        return (end - start).days
    except:
        return None


def get_eat_to_measure_diff_hours(eat_at_time: datetime, measure_time: datetime):
    try:
        eat_at_time = eat_at_time.replace(year=1900, month=1, day=1)
        measure_time = measure_time.replace(year=1900, month=1, day=1)
        return (measure_time - eat_at_time).seconds / 3600
    except Exception as e:
        print(e)
        return None


def get_blood_pressure_option(sbp: int, dbp: int):
    if sbp is None or dbp is None:
        return None
    if sbp < 90 and dbp < 60:
        return "c029:005"
    elif sbp < 130 and dbp < 85:
        return "c029:001"
    elif sbp >= 130 and sbp < 140 and dbp < 90:
        return "c029:002"
    elif sbp >= 140 and sbp < 160 and dbp < 100:
        return "c029:003"
    elif sbp >= 160 and dbp >= 100:
        return "c029:004"
    return None


def get_blood_pressure(measure_info):
    return get_blood_pressure_option(measure_info.sbp, measure_info.dbp)


def get_p008_pass_rate(option):
    m = re.search(r"c001:00([0-9])", option)
    if m:
        return int(m.group(1)) * 10
    return 0


def handle_s033_options(days: int):
    if isinstance(days, int) is False:
        return None
    elif days < 1:
        return "c035:001"
    elif days >= 1 and days < 4:
        return "c035:002"
    elif days >= 4 and days < 7:
        return "c035:003"
    elif days >= 7:
        return "c035:004"


def handle_s037_options(days: int):
    if isinstance(days, int) is False:
        return None
    elif days < 31:
        return "c049:001"
    elif days >= 31 and days < 91:
        return "c049:002"
    elif days >= 91 and days < 181:
        return "c049:003"
    elif days >= 181:
        return "c049:004"


def handle_s040_options(days: int):
    if isinstance(days, (int, float)) is False:
        return None
    elif days < 7:
        return "c036:001"
    elif days >= 7 and days < 15:
        return "c036:002"
    elif days >= 15 and days < 22:
        return "c036:003"
    elif days >= 22 and days < 29:
        return "c036:004"


def extract_number(text):
    p = re.compile("([0-9\.]+)")
    return list(map(lambda x: float(x), p.findall(text)))


def get_range_options_value(value, options):
    # TODO: design ascending (default) / descending
    range_options = [extract_number(options["label"]) for options in options]
    if all(map(lambda x: x == 2, list(map(lambda x: len(x), range_options)))):
        for idx, range_option in enumerate(range_options):
            if range_option[0] <= value <= range_option[1]:
                return options[idx]["value"]
    elif (
        len(range_options[0]) == 1
        and len(range_options[-1]) == 1
        and all(map(lambda x: x == 2, list(map(len, range_options[1:-1]))))
    ):
        if value <= range_options[0][0]:
            return options[0]["value"]
        elif value >= range_options[-1][0]:
            return options[-1]["value"]
        else:
            for idx, range_option in enumerate(range_options[1:-1]):
                if range_option[0] <= value <= range_option[1]:
                    return options[idx + 1]["value"]
    else:
        for idx, range_option in enumerate(range_options):
            if len(range_options[idx]) == 1 and idx == 0:
                if value < range_option[0]:
                    return options[idx]["value"]
            elif len(range_options[idx]) == 2:
                if range_option[0] <= value <= range_option[1]:
                    return options[idx]["value"]
            elif len(range_options[idx]) == 1 and idx == len(range_options) - 1:
                if value >= range_option[0]:
                    return options[idx]["value"]

    return None


def handle_multi_choices(text):
    if pd.isnull(text):
        return []
    return text.split("\n")


def process_text(text):
    """否（請回答 C ） -> 否"""
    if pd.isnull(text):
        return ""
    if text == "此選項已刪除":
        return ""
    return re.sub(r"\(.+\)$", "", text.strip().replace("（", "(").replace("）", ")"))


def process_text2(text):
    """大學(專) -> 大學（專）"""
    if pd.isnull(text):
        return ""
    return text.strip().replace("(", "（").replace(")", "）")


class AUOInternalSurveyHandler:
    def __init__(self) -> None:
        self.qa_df = None
        self.question_mapping_df = None

    def get_qa_df(self):
        if self.qa_df is None:
            self.qa_df = pd.read_csv(
                "STANDARD_wZN8X_中醫診斷現代化研究問卷_202306151458_648b2702784da.xlsx - 「sheet1」的副本.csv",
            )
            # col index 1: 請填入您的收案編號
            self.qa_df = self.qa_df[self.qa_df.iloc[:, 1].notnull()]
        return self.qa_df

    def get_question_mapping_df(self):
        if self.question_mapping_df is None:
            self.question_mapping_df = pd.read_csv(
                "STANDARD_wZN8X_中醫診斷現代化研究問卷_202306151458_648b2702784da.xlsx - question_mapping.csv",
            )
            self.question_mapping_df = self.question_mapping_df[
                self.question_mapping_df.question_id.notnull()
            ].sort_values("question_number")
        return self.question_mapping_df

    def get_question_mapping(self):
        question_mapping_df = self.get_question_mapping_df()
        question_mapping_records = question_mapping_df[
            ["question_id", "question_number"]
        ].to_dict("records")
        question_mapping = (
            py_.chain(question_mapping_records)
            .group_by(lambda x: x["question_id"])
            .map_values(lambda x: sorted([e["question_number"] for e in x]))
            .value()
        )
        return question_mapping


# TODO: check if need to get measure time
class QAHandler:
    def __init__(self, survey_name: str) -> None:
        self.file_handler = AUOSurveyFileHandler(survey_name=survey_name)

        self.parameter_dict = None
        self.disease_options_dict = None
        self.special_function_map = None
        self.speical_post_function_map = None

    async def process(self):
        db_session = SessionLocal()
        p_types = [
            ParameterType.primary,
            ParameterType.secondary,
            ParameterType.analytical,
        ]

        parameter_dict = await get_parameters(
            db_session=db_session,
            p_types=p_types,
            process_child_parent=False,
        )

        disease_options_dict = await get_disease_dict(db_session=db_session)
        # {'心臟血管疾病': {'category_id': 'd001', 'category_name': '心臟血管疾病', 'mapping': {'全部': '000', '高血壓': '001', '心律不整': '002', '冠狀動脈疾病': '003', '心瓣膜疾病': '004', '心臟衰竭': '005', '雷

        # the key order is important
        special_function_map = {
            "number": process_number,
            "p001": process_p001,
            "s001_other": process_s001_other,
            "s002_other": process_s002_other,
            "s003_other": process_s003_other,
            "a040_other": process_a040_other,
            "a003": partial(process_a003, parameter_dict=parameter_dict),
            "a008": partial(process_a008, disease_options_dict=disease_options_dict),
            "s045": partial(process_s045, parameter_dict=parameter_dict),
            "a025": process_a025,
            "a031": partial(process_a031, parameter_dict=parameter_dict),
            "a005": partial(process_a005, parameter_dict=parameter_dict),
            "a006": partial(process_a006, parameter_dict=parameter_dict),
            "s005": partial(
                process_s005,
                parameter_dict=parameter_dict,
            ),  # TODO 9. 生活作息
            "s025": partial(process_s025, parameter_dict=parameter_dict),
            "s026": process_s026,  # TODO: all null 3. 請問您量測脈診、舌診前最近一次用餐的時間？
            "s031": partial(process_s031, parameter_dict=parameter_dict),
            "s041": partial(process_s041, parameter_dict=parameter_dict),
            "s043": partial(process_s043, parameter_dict=parameter_dict),
            "a028": process_a028,
            "hr": process_hr,
        }

        speical_post_function_map = {
            "a004": partial(process_a004, parameter_dict=parameter_dict),
            # TODO: fix me a006 is weight but confuse with bmi
            "a006": partial(process_a007, parameter_dict=parameter_dict),
            "s033": process_s033,
            "s037": process_s037,
            "s040": process_s040,
        }

        all_rows = {
            "basic": [],
            "stop2": [],
            "stop3": [],
            "stop4": [],
            "stop6": [],
        }

        self.parameter_dict = parameter_dict
        self.disease_options_dict = disease_options_dict
        self.special_function_map = special_function_map
        self.speical_post_function_map = speical_post_function_map

        for all_rows_key in all_rows.keys():
            print("all_rows_key", all_rows_key)
            df = self.file_handler.get_qa_df(key=all_rows_key)
            question_mapping = self.file_handler.get_qa_mapping(key=all_rows_key)
            for _, row in df.iterrows():
                processed_row = self.process_single_row_new(
                    row=row,
                    question_mapping=question_mapping,
                )
                if processed_row is not None:
                    all_rows[all_rows_key].append(processed_row)

        # merge basic, stop2, stop3, stop4, stop6 by number
        merged_rows_dict = {}
        for all_rows_key in all_rows.keys():
            for row in all_rows[all_rows_key]:
                merged_rows_dict.setdefault(row["number"], {})
                survey_at = row["survey_at"]
                merged_rows_dict[row["number"]].update(row)
                if row["survey_at"] > survey_at:
                    merged_rows_dict[row["number"]]["survey_at"] = survey_at

        return list(merged_rows_dict.values())

    async def get_survey_result(self) -> List[SurveyAnswer]:
        rows = await self.process()
        rows = py_.order_by(rows, ["survey_at"])
        survey_result = [SurveyAnswer(**row) for row in rows]
        return survey_result

    def process_single_row_new(
        self,
        row,
        question_mapping,
    ):
        parameter_dict = self.parameter_dict
        special_function_map = self.special_function_map

        answer = {}
        answer["survey_at"] = get_datetime(row["填答時間"])
        if answer["survey_at"] is None:
            print(
                f"number {answer.get('number')} survey_at error: {answer['survey_at']}",
            )
            return
        for question_id, indices in question_mapping.items():
            speicial_func = special_function_map.get(question_id)
            if speicial_func:
                result = speicial_func(values=row[indices])
                for key, val in result.items():
                    answer[key] = val

            else:
                if not question_id:
                    continue
                parameter = parameter_dict.get(question_id)
                if not parameter:
                    continue

                component_names = find_all_component_names(parameter)
                if "input" in component_names:
                    answer[question_id] = safe_int(row[indices[0]])
                else:
                    top_level_option_length = len(parameter["subField"]["options"])
                    for i in range(top_level_option_length):
                        options = py_.get(
                            parameter_dict,
                            f"{question_id}.subField.options.{i}.subField.options",
                            [],
                        )
                        if options == []:
                            options = py_.get(
                                parameter_dict,
                                f"{question_id}.subField.options",
                                [],
                            )
                        # not include disease
                        multiple_choices_qid = ["s010", "s013"]
                        if question_id in multiple_choices_qid:
                            answers = (
                                row[indices[0]].split("\n")
                                if isinstance(row[indices[0]], str)
                                else []
                            )
                            answer[question_id] = []
                            for option in options:
                                if option["label"] in answers:
                                    answer[question_id].append(option["value"])
                        else:
                            for option in options:
                                if option["label"] == row[indices[0]]:
                                    answer[question_id] = option["value"]
                                elif isinstance(row[indices[0]], str) and option[
                                    "label"
                                ] == process_text(row[indices[0]]):
                                    answer[question_id] = option["value"]
                                elif isinstance(row[indices[0]], str) and option[
                                    "label"
                                ] == process_text2(row[indices[0]]):
                                    answer[question_id] = option["value"]

                    options = py_.get(
                        parameter_dict,
                        f"{question_id}.subField.options",
                        [],
                    )
                    for option in options:
                        if option["label"] == row[indices[0]]:
                            answer[question_id] = option["value"]

        for question_id, indices in question_mapping.items():
            speicial_post_func = self.speical_post_function_map.get(question_id)
            if speicial_post_func:
                result = speicial_post_func(values=row[indices], answer=answer)
                for key, val in result.items():
                    answer[key] = val

        return answer


def get_question_mapping(question_mapping_df):
    question_mapping_records = question_mapping_df[
        ["question_id", "column_index"]
    ].to_dict("records")
    question_mapping = (
        py_.chain(question_mapping_records)
        .group_by(lambda x: x["question_id"])
        .map_values(lambda x: sorted([e["column_index"] for e in x]))
        .value()
    )
    return question_mapping


class AUOSurveyFileHandler:
    def __init__(self, survey_name: str) -> None:
        qa_basic_df = pd.read_excel(f"{survey_name}收案資料.xlsx", sheet_name=0)
        qa_stop2_df = pd.read_excel(f"{survey_name}收案資料.xlsx", sheet_name=1)
        qa_stop3_df = pd.read_excel(f"{survey_name}收案資料.xlsx", sheet_name=2)
        qa_stop4_df = pd.read_excel(f"{survey_name}收案資料.xlsx", sheet_name=3)
        qa_stop6_df = pd.read_excel(f"{survey_name}收案資料.xlsx", sheet_name=5)

        qa_mapping_basic_df = pd.read_excel("問卷題號對照.xlsx", sheet_name=0)
        qa_mapping_stop2_df = pd.read_excel("問卷題號對照.xlsx", sheet_name=1)
        qa_mapping_stop3_df = pd.read_excel("問卷題號對照.xlsx", sheet_name=2)
        qa_mapping_stop4_df = pd.read_excel("問卷題號對照.xlsx", sheet_name=3)
        qa_mapping_stop6_df = pd.read_excel("問卷題號對照.xlsx", sheet_name=5)

        self.qa_basic_df = qa_basic_df[qa_basic_df.iloc[:, 0].notnull()]
        self.qa_stop2_df = qa_stop2_df
        self.qa_stop3_df = qa_stop3_df
        self.qa_stop4_df = qa_stop4_df
        self.qa_stop6_df = qa_stop6_df

        self.qa_mapping_basic_df = qa_mapping_basic_df
        self.qa_mapping_stop2_df = qa_mapping_stop2_df
        self.qa_mapping_stop3_df = qa_mapping_stop3_df
        self.qa_mapping_stop4_df = qa_mapping_stop4_df
        self.qa_mapping_stop6_df = qa_mapping_stop6_df

        self.qa_mapping_basic = get_question_mapping(qa_mapping_basic_df)
        self.qa_mapping_stop2 = get_question_mapping(qa_mapping_stop2_df)
        self.qa_mapping_stop3 = get_question_mapping(qa_mapping_stop3_df)
        self.qa_mapping_stop4 = get_question_mapping(qa_mapping_stop4_df)
        self.qa_mapping_stop6 = get_question_mapping(qa_mapping_stop6_df)

    def get_qa_df(self, key):
        return getattr(self, f"qa_{key}_df")

    def get_qa_mapping(self, key):
        return getattr(self, f"qa_mapping_{key}")


qa_df = pd.read_csv(
    "STANDARD_wZN8X_中醫診斷現代化研究問卷_202306151458_648b2702784da.xlsx - 「sheet1」的副本.csv",
)
# col index 1: 請填入您的收案編號
qa_df = qa_df[qa_df.iloc[:, 1].notnull()]
question_mapping_df = pd.read_csv(
    "STANDARD_wZN8X_中醫診斷現代化研究問卷_202306151458_648b2702784da.xlsx - question_mapping.csv",
)
question_mapping_df = question_mapping_df[
    question_mapping_df.question_id.notnull()
].sort_values("question_number")

question_mapping_records = question_mapping_df[
    ["question_id", "question_number"]
].to_dict("records")
question_mapping = (
    py_.chain(question_mapping_records)
    .group_by(lambda x: x["question_id"])
    .map_values(lambda x: sorted([e["question_number"] for e in x]))
    .value()
)


def process_p001(values):
    return {"proj_num": values[0]}


def process_s005(values, parameter_dict):
    result = {}
    question_id = process_s005.__name__.split("_")[-1]
    work_type = values[0]
    start = values[1]
    end = values[2]
    if isinstance(start, (datetime, time)):
        start = start.strftime("%H:%M")
    elif pd.isnull(start):
        start = None
    if isinstance(end, (datetime, time)):
        end = end.strftime("%H:%M")
    elif pd.isnull(end):
        end = None

    result["office_hours"] = (start, end)

    options = py_.get(
        parameter_dict,
        f"{question_id}.subField.options.1.subField.options",
        [],
    )
    for option in options:
        if option["label"] == work_type:
            result[question_id] = option["value"]
        elif option["label"] == process_text(work_type):
            result[question_id] = option["value"]
        elif option["label"] in str(work_type):
            # 有固定的工作或上學時間者 in 有固定的工作或上學時間者，請續填答下題A-B
            result[question_id] = option["value"]

    return result


def process_s025(values, parameter_dict):
    result = {}
    question_id = process_s025.__name__.split("_")[-1]
    sleep_at = values[0]
    wake_up_at = values[1]
    # if isinstance(sleep_at, str) and isinstance(wake_up_at, str):
    result["sleep_duration"] = get_time_duration(wake_up_at, sleep_at)
    options = py_.get(
        parameter_dict,
        f"{question_id}.subField.options",
        [],
    )
    if result["sleep_duration"] < 6:
        result["s025"] = options[1]["value"]
    elif result["sleep_duration"] >= 6:
        result["s025"] = options[2]["value"]
    else:
        result["s025"] = options[0]["value"]
    return result


def process_s026(values):
    result = {}
    eat_at = values[0]
    if isinstance(eat_at, time):
        result["eat_at"] = datetime(
            year=1900,
            month=1,
            day=1,
            hour=eat_at.hour,
            minute=eat_at.minute,
        )
    elif isinstance(eat_at, datetime):
        result["eat_at"] = eat_at
    elif isinstance(eat_at, str) and ":" in eat_at:
        result["eat_at"] = datetime.strptime(eat_at, "%H:%M")
    elif pd.isnull(eat_at):
        result["eat_at"] = None
    else:
        result["eat_at"] = None
    # TODO: s026
    return result


def process_s031(values, parameter_dict):
    result = {}
    question_id = process_s031.__name__.split("_")[-1]
    exercise_from = values[0]
    exercise_to = values[1]
    exercise_duration_minute = get_time_duration(exercise_from, exercise_to)
    exercise_duration = (
        exercise_duration_minute * 60 if exercise_duration_minute else None
    )

    # breakpoint()

    options = py_.get(
        parameter_dict,
        f"{question_id}.subField.options.1.subField.options",
        [],
    )
    if exercise_duration is None:
        result["s031"] = None
    elif exercise_duration < 30:
        result["s031"] = options[0]["value"]
    elif exercise_duration >= 30 and exercise_duration < 60:
        result["s031"] = options[1]["value"]
    elif exercise_duration >= 60:
        result["s031"] = options[2]["value"]
    return result


def process_s033(values, **kwargs):
    result = {}
    symptom_from = values[0]
    if pd.isnull(symptom_from):
        result["symptom_from"] = None
    elif isinstance(symptom_from, datetime):
        result["symptom_from"] = symptom_from
    elif isinstance(symptom_from, str) and "-" in symptom_from:
        result["symptom_from"] = datetime.strptime(symptom_from, "%Y-%m-%d")
    elif isinstance(symptom_from, str) and "/" in symptom_from:
        result["symptom_from"] = datetime.strptime(symptom_from, "%Y/%m/%d")
    else:
        result["symptom_from"] = None
    # TODO: calculate symptom with survey at / measure time
    if result["symptom_from"]:
        result["s033"] = handle_s033_options(
            get_days_range(result["symptom_from"], py_.get(kwargs, "answer.survey_at")),
        )
    return result


def process_s037(values, **kwargs):
    result = {}
    covid_from = values[0]
    if pd.isnull(covid_from):
        result["covid_from"] = None
    elif isinstance(covid_from, datetime):
        result["covid_from"] = covid_from
    elif isinstance(covid_from, str) and "-" in covid_from:
        result["covid_from"] = datetime.strptime(covid_from, "%Y-%m-%d")
    elif isinstance(covid_from, str) and "/" in covid_from:
        result["covid_from"] = datetime.strptime(covid_from, "%Y/%m/%d")
    else:
        result["covid_from"] = None

    survey_at = py_.get(kwargs, "answer.survey_at")
    if isinstance(result["covid_from"], datetime) and isinstance(survey_at, datetime):
        diff_days = get_days_range(survey_at, result["covid_from"])
        result["s037"] = handle_s037_options(diff_days)

    return result


def process_s040(values, **kwargs):
    result = {}
    menstruation_from = values[0]
    if pd.isnull(menstruation_from):
        result["menstruation_from"] = None
    elif isinstance(menstruation_from, datetime):
        result["menstruation_from"] = menstruation_from
    elif isinstance(menstruation_from, str) and "-" in menstruation_from:
        result["menstruation_from"] = datetime.strptime(menstruation_from, "%Y-%m-%d")
    elif isinstance(menstruation_from, str) and "/" in menstruation_from:
        result["menstruation_from"] = datetime.strptime(menstruation_from, "%Y/%m/%d")
    else:
        result["menstruation_from"] = None
    # TODO: calculate menstruation with survey at / measure time
    if result["menstruation_from"]:
        result["s040"] = handle_s040_options(
            get_days_range(
                result["menstruation_from"],
                py_.get(kwargs, "answer.survey_at"),
            ),
        )
    return result


def process_s041(values, parameter_dict):
    question_id = process_s041.__name__.split("_")[-1]
    options = py_.get(
        parameter_dict,
        f"{question_id}.subField.options.1.subField.options",
        [],
    )
    result = {}
    stop_menstruation_year_ago = safe_int(values[0])
    if isinstance(stop_menstruation_year_ago, int) is False:
        result["s041"] = None
    elif stop_menstruation_year_ago < 1:
        result["s041"] = options[0]["value"]
    elif stop_menstruation_year_ago >= 1 and stop_menstruation_year_ago < 3:
        result["s041"] = options[1]["value"]
    elif stop_menstruation_year_ago >= 3 and stop_menstruation_year_ago < 5:
        result["s041"] = options[2]["value"]
    elif stop_menstruation_year_ago >= 5:
        result["s041"] = options[3]["value"]
    return result


def process_s043(values, parameter_dict):
    result = {}
    question_id = process_s043.__name__.split("_")[-1]
    pregnant_month = safe_int(values[0])
    options = py_.get(
        parameter_dict,
        f"{question_id}.subField.options.1.subField.options",
        [],
    )
    if pregnant_month is None:
        result[question_id] = None
    elif pregnant_month < 12:
        result[question_id] = options[0]["value"]
    elif pregnant_month >= 12 and pregnant_month < 24:
        result[question_id] = options[1]["value"]
    elif pregnant_month >= 24:
        result[question_id] = options[2]["value"]
    return result


def process_a028(values):
    result = {}
    question_id = process_a028.__name__.split("_")[-1]
    sbp = values[0]
    dbp = values[1]
    if isinstance(sbp, (int, float)):
        result["sbp"] = sbp
    if isinstance(dbp, (int, float)):
        result["dbp"] = dbp
    if isinstance(sbp, (int, float)) and isinstance(dbp, (int, float)):
        result[question_id] = get_blood_pressure_option(sbp, dbp)
    return result


def process_number(values):
    result = {}
    result["number"] = values[0].upper()
    return result


def process_sbp(values):
    result = {}
    result["sbp"] = safe_int(values[0])
    return result


def process_dbp(values):
    result = {}
    result["dbp"] = safe_int(values[0])
    return result


def process_hr(values):
    result = {}
    result["hr"] = safe_int(values[0])
    return result


def process_a003(values, parameter_dict):
    question_id = process_a003.__name__.split("_")[-1]
    options = parameter_dict[question_id]["subField"]["options"]
    result = {}
    for option in options:
        if option["label"] == values[0]:
            result["gender"] = option["label"]
            result[question_id] = option["value"]
    return result


def process_a004(values, parameter_dict, **kwargs):
    survey_at = py_.get(kwargs, ".answer.survey_at")
    result = {}
    question_id = process_a004.__name__.split("_")[-1]
    options = py_.get(
        parameter_dict,
        f"{question_id}.subField.options.1.subField.options",
        [],
    )
    result["birth_date"] = get_date(values[0])
    result["age"] = get_age(survey_at, result["birth_date"])
    if isinstance(result["age"], int):
        result[question_id] = get_range_options_value(result["age"], options)
    return result


def process_a005(values, parameter_dict):
    result = {}
    question_id = process_a005.__name__.split("_")[-1]
    result["height"] = safe_int(values[0])
    # TODO: get from question options
    options = py_.get(
        parameter_dict,
        f"{question_id}.subField.options.1.subField.options",
        [],
    )
    range_options = [extract_number(options["label"]) for options in options]
    if result["height"] < range_options[0][0]:
        result["a005"] = options[0]["value"]
    elif (
        result["height"] >= range_options[1][0]
        and result["height"] <= range_options[1][1]
    ):
        result["a005"] = options[1]["value"]
    elif (
        result["height"] >= range_options[2][0]
        and result["height"] <= range_options[2][1]
    ):
        result["a005"] = options[2]["value"]
    elif (
        result["height"] >= range_options[3][0]
        and result["height"] <= range_options[3][1]
    ):
        result["a005"] = options[3]["value"]
    elif result["height"] >= range_options[4][0]:
        result["a005"] = options[4]["value"]
    return result


def process_a006(values, parameter_dict):
    result = {}
    question_id = process_a006.__name__.split("_")[-1]
    result["weight"] = safe_float(values[0])
    options = py_.get(
        parameter_dict,
        f"{question_id}.subField.options.1.subField.options",
        [],
    )
    # TODO: get from question options
    result["a006"] = get_range_options_value(result["weight"], options)
    return result


def process_a007(values, parameter_dict, **kwargs):
    answer = py_.get(kwargs, ".answer")
    result = {}
    question_id = process_a007.__name__.split("_")[-1]
    if isinstance(answer["height"], (int, float)) and isinstance(
        answer["weight"],
        (int, float),
    ):
        bmi = safe_divide(answer["weight"], (answer["height"] / 100) ** 2)
        result["bmi"] = round(bmi, 2)
        options = py_.get(
            parameter_dict,
            f"{question_id}.subField.options.1.subField.options",
            [],
        )
        result["a007"] = get_range_options_value(result["bmi"], options)
    return result


def process_disease_old(row, indices, disease_options_dict):
    # order: "三個月內您是否經醫師確定診斷有罹患下列疾病", "心臟血管疾病", "呼吸系統疾病", "消化系統疾病", "內分泌及代謝疾病", "腎泌尿系統疾病", "神經系統疾病", "身心科疾病", "皮膚及皮下組織疾病", "骨骼肌肉系統及結締組織之疾病", "耳之疾病", "婦科疾病", "血液及造血器官疾病", "癌症", "先天性疾病"
    if pd.isnull(row[indices[0]]) or row[indices[0]] == "" or row[indices[0]] == "無":
        disease_info = disease_options_dict["健康人"]
        return [
            {
                "category_id": disease_info["category_id"],
                "category_name": disease_info["category_name"],
                "value": disease_info["mapping"]["無疾病"],
                "label": "無疾病",
            },
        ]
    # check d001 ~ d014 (index: 29-42)
    result = []
    for idx in indices[1 : 1 + 14]:
        disease_name = row.index[idx]
        if isinstance(row[idx], str) is False:
            continue
        disease_answers = handle_multi_choices(row[idx])
        if disease_name in disease_options_dict:
            disease_info = disease_options_dict[disease_name]
            disease_options = disease_info["mapping"]
            for disease_answer in disease_answers:
                if disease_answer in disease_options:
                    result.append(
                        {
                            "category_id": disease_info["category_id"],
                            "category_name": disease_info["category_name"],
                            "value": disease_options[disease_answer],
                            "label": disease_answer,
                        },
                    )
        else:
            raise Exception(f"not exist disease name: {disease_name}")

    return result


def process_s001_other(values):
    result = {}
    result["s001_other"] = values[0]
    if pd.isnull(values[0]):
        result["s001_other"] = None
    return result


def process_s002_other(values):
    result = {}
    result["s002_other"] = values[0]
    if pd.isnull(values[0]):
        result["s002_other"] = None
    return result


def process_s003_other(values):
    result = {}
    result["s003_other"] = values[0]
    if pd.isnull(values[0]):
        result["s003_other"] = None
    return result


def process_a040_other(values):
    result = {}
    result["a040_other"] = values[0]
    if pd.isnull(values[0]):
        result["a040_other"] = None
    return result


def process_disease(values, disease_options_dict):
    # order: "三個月內您是否經醫師確定診斷有罹患下列疾病", "心臟血管疾病", "呼吸系統疾病", "消化系統疾病", "內分泌及代謝疾病", "腎泌尿系統疾病", "神經系統疾病", "身心科疾病", "皮膚及皮下組織疾病", "骨骼肌肉系統及結締組織之疾病", "耳之疾病", "婦科疾病", "血液及造血器官疾病", "癌症", "先天性疾病"
    if pd.isnull(values[0]) or values[0] == "" or values[0] == "無":
        disease_info = disease_options_dict["健康人"]
        return [
            {
                "category_id": disease_info["category_id"],
                "category_name": disease_info["category_name"],
                "value": disease_info["mapping"]["無疾病"],
                "label": "無疾病",
            },
        ]
    # check d001 ~ d014 (index: 29-42)
    result = []
    for idx in range(1, 1 + 14):
        # 您是否罹患下列呼吸系統疾病？
        # breakpoint()
        question_name = values.index[idx]
        m = re.search(r"您是否罹患下列(\w+疾病)？", question_name)
        if m is None:
            continue
        disease_name = m.group(1)
        if disease_name in (
            "心臟血管系統疾病",
            "內分泌及代謝系統疾病",
            "身心科系統疾病",
            "皮膚及皮下組織系統疾病",
        ):
            disease_name = disease_name.replace("系統", "")
        if disease_name == "骨骼肌肉系統及結締組織系統疾病":
            disease_name = "骨骼肌肉系統及結締組織之疾病"
        if disease_name == "婦科之疾病":
            disease_name = "婦科疾病"
        if disease_name == "血液及造血器官之疾病":
            disease_name = "血液及造血器官疾病"
        if disease_name == "癌症疾病":
            disease_name = "癌症"

        if isinstance(values[idx], str) is False:
            continue
        disease_answers = handle_multi_choices(values[idx])
        if disease_name in disease_options_dict:
            disease_info = disease_options_dict[disease_name]
            disease_options = disease_info["mapping"]
            for disease_answer in disease_answers:
                if disease_answer in disease_options:
                    result.append(
                        {
                            "category_id": disease_info["category_id"],
                            "category_name": disease_info["category_name"],
                            "value": disease_options[disease_answer],
                            "label": disease_answer,
                        },
                    )
        else:
            raise Exception(f"not exist disease name: {disease_name}")

    return result


def process_a008(values, disease_options_dict):
    disease_answer = process_disease(values, disease_options_dict)
    return {
        "disease": disease_answer,
        "a008": [
            f"{disease['category_id']}:{disease['value']}" for disease in disease_answer
        ],
    }


def process_mind(answers):
    # 不需要有「6. 有過自殺的念頭」
    if len(answers) != 5:
        raise Exception("心情溫度計應有 5 題")
    option_scores = {"完全沒有": 0, "輕微": 1, "中等程度": 2, "厲害": 3, "非常厲害": 4}
    score = 0
    for answer in answers:
        score += option_scores.get(answer, 0)
    return score


def process_s045(values, parameter_dict):
    question_id = process_s045.__name__.split("_")[-1]
    options = py_.get(
        parameter_dict,
        f"{question_id}.subField.options.1.subField.options",
        [],
    )
    bsrs5 = process_mind(values)
    s045_answer = None
    if isinstance(bsrs5, int):
        if bsrs5 >= 0 and bsrs5 <= 5:
            s045_answer = options[0]["value"]
        elif bsrs5 >= 6 and bsrs5 <= 9:
            s045_answer = options[1]["value"]
        elif bsrs5 >= 10 and bsrs5 <= 14:
            s045_answer = options[2]["value"]
        elif bsrs5 >= 15 and bsrs5 <= 19:
            s045_answer = options[3]["value"]
    return {"s045": s045_answer}


def convert_bcq_score_to_pct(bcq_type: str, score: int):
    score_range_dict = {
        "score_yang": (19, 95),
        "score_yin": (19, 95),
        "score_phlegm": (16, 80),
        "score_yang_head": (4, 20),
        "score_yang_chest": (4, 20),
        "score_yang_limbs": (4, 20),
        "score_yang_abdomen": (4, 20),
        "score_yang_surface": (3, 15),
        "score_yin_head": (6, 30),
        "score_yin_limbs": (4, 20),
        "score_yin_gt": (4, 20),
        "score_yin_surface": (3, 15),
        "score_yin_abdomen": (2, 10),
        "score_phlegm_trunk": (5, 25),
        "score_phlegm_surface": (5, 25),
        "score_phlegm_head": (3, 15),
        "score_phlegm_gt": (3, 15),
    }
    if bcq_type not in score_range_dict:
        raise ValueError("bcq_type must be one of {}".format(score_range_dict.keys()))
    score_range = score_range_dict[bcq_type]
    normalized_score = round(
        (score - score_range[0]) * 100 / (score_range[1] - score_range[0]),
    )
    if normalized_score < 0:
        return 0
    return normalized_score


def get_bcq_type_result(
    score_or_pct: str,
    has_yang_weak: bool,
    has_yin_weak: bool,
    has_phlegm_weak: bool,
) -> dict:
    if score_or_pct not in ("score", "pct"):
        raise ValueError("score_or_pct must be 'score' or 'pct'")
    qid = "a026:c056:001" if score_or_pct == "score" else "a026:c056:002"
    result = {}
    if has_yang_weak and has_yin_weak and has_phlegm_weak:
        result[qid] = "c039:007"
    elif has_yang_weak and has_yin_weak:
        result[qid] = "c039:004"
    elif has_yang_weak and has_phlegm_weak:
        result[qid] = "c039:005"
    elif has_yin_weak and has_phlegm_weak:
        result[qid] = "c039:006"
    elif has_yang_weak:
        result[qid] = "c039:001"
    elif has_yin_weak:
        result[qid] = "c039:002"
    elif has_phlegm_weak:
        result[qid] = "c039:003"
    else:
        result[qid] = "c039:008"
    return result


def process_a025(values):
    result = {}
    bcq_result, has_bcq = process_bcq(values)
    result["a025"] = bcq_result if has_bcq else None
    result["a026c056001"] = bcq_result["a026:c056:001"] if has_bcq else None
    result["a026c056002"] = bcq_result["a026:c056:002"] if has_bcq else None
    return result


def process_bcq(values):
    # Q1-Q44
    if len(values) != 44:
        raise Exception("bcq questions number is 44")

    bcq_questions = values

    # TODO: check validation rule
    has_bcq = False if any(map(lambda x: pd.isnull(x), bcq_questions)) else True
    has_yang_weak = False
    has_yin_weak = False
    has_phlegm_weak = False

    min_yang_weak_score = 31
    min_yin_weak_score = 30
    min_phlegm_weak_score = 27

    has_yang_weak_by_pct = False
    has_yin_weak_by_pct = False
    has_phlegm_weak_by_pct = False

    min_yang_weak_pct = 14
    min_yin_weak_pct = 14
    min_phlegm_weak_pct = 17

    yang_questions = "3,5,8,9,15,16,17,22,23,24,28,31,33,36,37,41,42,43,44".split(",")
    yin_questions = "2,4,8,10,11,16,18,20,23,26,29,30,31,32,35,37,38,39,40".split(",")
    phlegm_questions = "1,4,5,6,7,12,13,14,16,17,19,20,21,25,27,34".split(",")

    if len(yang_questions) + len(yin_questions) + len(phlegm_questions) != 54:
        raise Exception("total bcq questions number is 54")

    factor_questions = {
        "yang_head_questions": "5,8,9,31".split(","),
        "yang_chest_questions": "15,17,24,28".split(","),
        "yang_limbs_questions": "16,22,23,37".split(","),
        "yang_abdomen_questions": "41,42,43,44".split(","),
        "yang_surface_questions": "3,33,36".split(","),
        "yin_head_questions": "4,8,11,18,31,32".split(","),
        "yin_limbs_questions": "16,20,23,37".split(","),
        "yin_gt_questions": "10,26,30,40".split(","),
        "yin_surface_questions": "2,29,35".split(","),
        "yin_abdomen_questions": "38,39".split(","),
        "phlegm_trunk_questions": "12,13,16,17,25".split(","),
        "phlegm_surface_questions": "7,19,20,21,27".split(","),
        "phlegm_head_questions": "4,5,14".split(","),
        "phlegm_gt_questions": "1,6,34".split(","),
    }

    yang_weak_score = 0
    yin_weak_score = 0
    phlegm_weak_score = 0

    for question_order in yang_questions:
        score = get_bcq_score(bcq_questions[int(question_order) - 1])
        yang_weak_score += score
    for question_order in yin_questions:
        score = get_bcq_score(bcq_questions[int(question_order) - 1])
        yin_weak_score += score
    for question_order in phlegm_questions:
        score = get_bcq_score(bcq_questions[int(question_order) - 1])
        phlegm_weak_score += score

    if yang_weak_score >= min_yang_weak_score:
        has_yang_weak = True
    if yin_weak_score >= min_yin_weak_score:
        has_yin_weak = True
    if phlegm_weak_score >= min_phlegm_weak_score:
        has_phlegm_weak = True

    yang_weak_pct = convert_bcq_score_to_pct("score_yang", yang_weak_score) or 0
    yin_weak_pct = convert_bcq_score_to_pct("score_yin", yin_weak_score) or 0
    phlegm_weak_pct = convert_bcq_score_to_pct("score_phlegm", phlegm_weak_score) or 0
    if yang_weak_pct >= min_yang_weak_pct:
        has_yang_weak_by_pct = True
    if yin_weak_pct >= min_yin_weak_pct:
        has_yin_weak_by_pct = True
    if phlegm_weak_pct >= min_phlegm_weak_pct:
        has_phlegm_weak_by_pct = True

    bcq_result = {
        "has_yang_weak": has_yang_weak,
        "score_yang": yang_weak_score,
        "has_yin_weak": has_yin_weak,
        "score_yin": yin_weak_score,
        "has_phlegm_weak": has_phlegm_weak,
        "score_phlegm": phlegm_weak_score,
    }
    for name, question_numbers in factor_questions.items():
        for question_order in question_numbers:
            key = "score_" + name.replace("_questions", "")
            bcq_result.setdefault(key, 0)
            bcq_result[key] += get_bcq_score(bcq_questions[int(question_order) - 1])

    percentage_result = {}
    for key in bcq_result.keys():
        if key.startswith("score_"):
            percentage_key = key.replace("score_", "percentage_")
            percentage_result[percentage_key] = convert_bcq_score_to_pct(
                bcq_type=key,
                score=bcq_result[key],
            )

    bcq_result = {**bcq_result, **percentage_result}

    bcq_by_score_result = get_bcq_type_result(
        "score",
        has_yang_weak,
        has_yin_weak,
        has_phlegm_weak,
    )
    bcq_by_pct_result = get_bcq_type_result(
        "pct",
        has_yang_weak_by_pct,
        has_yin_weak_by_pct,
        has_phlegm_weak_by_pct,
    )
    bcq_result = {**bcq_result, **bcq_by_score_result, **bcq_by_pct_result}

    return bcq_result, has_bcq


def process_psqi(values):
    sleep_result = {}
    sleep_questions = values

    sleep_quality_option_scores1 = {"非常好": 0, "好": 1, "不好": 2, "非常不好": 3}
    sleep_quality_option_scores2 = {"極好": 0, "好": 1, "中等程度好": 2, "不好": 3}
    # old: sleep_option_scores = {"從未發生": 0, "每周少於1次": 1, "每周1-2次": 2, "每周3次或以上": 3}
    sleep_option_scores = {"從未發生": 0, "每週少於 1 次": 1, "每週 1-2 次": 2, "每週 3 次或以上": 3}
    sleep_option_scores2 = {"完全沒有困擾": 0, "只有很少困擾": 1, "有些困擾": 2, "有很大的困擾": 3}

    # 睡眠品質
    # TODO: 這邊台北收案結果和選項不同
    a033_questions = 19  # old is 18
    sleep_result["a033_answer"] = sleep_questions[int(a033_questions) - 1]
    if pd.isnull(sleep_result["a033_answer"]):
        sleep_result["a033_answer"] = None
    sleep_result["a033_score"] = sleep_quality_option_scores1.get(
        sleep_questions[int(a033_questions) - 1],
    )
    if sleep_result["a033_score"] is None:
        sleep_result["a033_score"] = sleep_quality_option_scores2.get(
            sleep_questions[int(a033_questions) - 1],
        )

    # 睡眠潛伏期 incubation period 過去一個月來，您在上床後，通常躺多久才能入睡？
    def get_sleep_incubation_period_part_b_score(minute: int):
        if minute <= 15:
            return 0
        elif minute <= 30:
            return 1
        elif minute <= 60:
            return 2
        else:
            return 3

    def get_sleep_incubation_period_score(score_a: int, score_b: int):
        score = score_a or 0 + score_b or 0
        if score == 0:
            return 0
        elif score <= 2:
            return 1
        elif score <= 4:
            return 2
        elif score <= 6:
            return 3

    def process_a035(a035_start_answer, a035_end_answer):
        today = datetime.now()
        start = None
        end = None
        if isinstance(a035_start_answer, time):
            start = datetime(
                1900,
                1,
                1,
                a035_start_answer.hour,
                a035_start_answer.minute,
            )
        elif isinstance(a035_start_answer, datetime):
            start = a035_start_answer

        if isinstance(a035_end_answer, time):
            end = datetime(1900, 1, 1, a035_end_answer.hour, a035_end_answer.minute)
        elif isinstance(a035_end_answer, datetime):
            end = a035_end_answer

        if isinstance(start, datetime) and isinstance(end, datetime):
            sleep_hour = (end - start).seconds / 3600
            return sleep_hour

        if (
            isinstance(a035_start_answer, str) and isinstance(a035_end_answer, str)
        ) is False:
            return None
        else:
            try:
                start_dt = today.replace(
                    hour=int(a035_start_answer.split(":")[0]),
                    minute=int(a035_start_answer.split(":")[1]),
                    second=0,
                    microsecond=0,
                )
                end_dt = timedelta(days=1) + today.replace(
                    hour=int(a035_end_answer.split(":")[0]),
                    minute=int(a035_end_answer.split(":")[1]),
                    second=0,
                    microsecond=0,
                )
                sleep_hour = (end_dt - start_dt).seconds / 3600
                return sleep_hour
            except Exception as e:
                print("error", e, a035_start_answer, a035_end_answer)

    a034_score = 0

    # Part A - 無法在 30 分鐘內入睡
    a034_part_a_questions = 5
    a034_part_a_answer = sleep_questions[a034_part_a_questions - 1]
    a034_part_a_score = sleep_option_scores.get(a034_part_a_answer)

    # Part B - 上床後通常多久可以睡著
    a034_part_b_questions = 2
    a034_part_b_answer = sleep_questions[a034_part_b_questions - 1]
    a034_part_b_score = get_sleep_incubation_period_part_b_score(a034_part_b_answer)

    a034_score = get_sleep_incubation_period_score(a034_part_a_score, a034_part_b_score)
    sleep_result["a034_score"] = a034_score

    # 睡眠時數
    # sleep_hours_questions
    def get_sleep_hours_score(hour: float) -> int:
        if hour is None:
            return None
        elif hour >= 7:
            return 0
        elif hour >= 6:
            return 1
        elif hour >= 5:
            return 2
        elif hour < 5:
            return 3

    a035_questions = "1,3".split(",")
    a035_start_question, a035_end_question = a035_questions
    a035_start_answer = sleep_questions[int(a035_start_question) - 1]
    a035_end_answer = sleep_questions[int(a035_end_question) - 1]
    sleep_hour = process_a035(a035_start_answer, a035_end_answer)
    a035_score = get_sleep_hours_score(sleep_hour)
    sleep_result["a035_score"] = a035_score

    # 睡眠效率
    def get_sleep_efficiency(pct: float):
        if pct is None:
            return None
        elif pct >= 0.85:
            return 0
        elif pct >= 0.75:
            return 1
        elif pct >= 0.65:
            return 2
        elif pct >= 0:
            return 3

    a036_questions = 4
    a036_answer = sleep_questions[a036_questions - 1]
    a036_score = get_sleep_efficiency(safe_divide(a036_answer, sleep_hour))
    sleep_result["a036_score"] = a036_score

    # 睡眠困擾
    # TODO: check formula
    def get_sleep_disturbance_score(count):
        if count == 0:
            return 0
        elif count <= 9:
            return 1
        elif count <= 18:
            return 2
        elif count <= 27:
            return 3

    a037_count = 0
    # TODO: check: https://bestmade.com.tw/blogs/news/psqi-sleep-test
    # 5. 過去一個月來，您的睡眠有多少次受到下列干擾？
    a037_questions = "5,6,7,8,9,10,11,12,13,14".split(",")
    for a037_question in a037_questions:
        if sleep_questions[int(a037_question) - 1] != "從未發生":
            a037_count += 1
    a037_score = get_sleep_disturbance_score(a037_count)
    sleep_result["a037_score"] = a037_score

    a037_other_question = 15
    sleep_result["a037_other"] = sleep_questions[int(a037_other_question) - 1]

    # 安眠藥物使用
    a038_question = 16
    a038_score = sleep_option_scores.get(sleep_questions[int(a038_question) - 1])
    sleep_result["a038_score"] = a038_score

    # 白天功能運作
    # TODO: check formula
    a039_question = "17,18".split(",")
    # 保持清醒
    a039_part_a_score = sleep_option_scores.get(
        sleep_questions[int(a039_question[0]) - 1],
    )
    # 做事熱忱
    a039_part_b_score = sleep_option_scores2.get(
        sleep_questions[int(a039_question[1]) - 1],
    )
    if a039_part_a_score is not None and a039_part_b_score is not None:
        a039_score = a039_part_a_score + a039_part_b_score
        a039_score_normalized_map = {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3}
        a038_score_normalized = a039_score_normalized_map.get(a039_score, 0)
        sleep_result["a039_score"] = a038_score_normalized
    else:
        sleep_result["a039_score"] = None

    sleep_result["a032_score"] = sum(
        [sleep_result.get(f"a0{a0num}_score", 0) or 0 for a0num in range(33, 40)],
    )

    for key, val in sleep_result.items():
        if pd.isnull(val):
            sleep_result[key] = None

    return sleep_result


def process_a031(values, parameter_dict):
    result = {}
    sleep_result = process_psqi(values)
    result["a031"] = sleep_result

    options = py_.get(
        parameter_dict,
        f"a032.subField.options.1.subField.options",
        [],
    )
    if sleep_result["a032_score"] > 5:
        result["a032"] = "c046:001"
    else:
        result["a032"] = "c046:002"

    for a0num in range(33, 40):
        options = py_.get(
            parameter_dict,
            f"a0{a0num}.subField.options.1.subField.options",
            [],
        )
        result[f"a0{a0num}"] = py_.get(
            options,
            f'{sleep_result[f"a0{a0num}_score"]}.value',
        )
    return result


def get_bcq_score(option):
    option_score = {"完全不會": 1, "稍微會": 2, "中等程度會": 3, "很會": 4, "最嚴重會": 5}
    # TODO: check correction
    option_score2 = {"從來沒有": 1, "偶爾有": 2, "一半有一半沒有": 3, "時常有": 4, "一直都有": 5}
    if option_score.get(option):
        return option_score.get(option)
    elif option_score2.get(option):
        return option_score2.get(option)
    else:
        return 0


def match_option(answer, parameter_dict):
    pass


def process_single_row(row, parameter_dict, disease_options_dict):
    answer = {}
    answer["survey_at"] = get_datetime(row["填答時間"])
    # answer["p006"] = answer["survey_at"]
    # index starts from 1
    for question_id, indices in question_mapping.items():
        if question_id == "p001":  # 計畫編號，和脈診量測資料的 proj_num 不一致，目前不可用
            # answer["p001"] = row[indices[0]]
            answer["proj_num"] = row[indices[0]]
        elif question_id == "number":
            answer["number"] = row[indices[0]]
        elif question_id == "a008":  # 疾病史
            answer["disease"] = process_disease_old(row, indices, disease_options_dict)
            answer["a008"] = [
                f"{disease['category_id']}:{disease['value']}"
                for disease in answer["disease"]
            ]
        elif question_id == "s045":  # 心情溫度計
            answer["s045"] = process_mind(row[indices])
            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            bsrs5 = process_mind(row[indices])
            if isinstance(bsrs5, int):
                if bsrs5 >= 0 and bsrs5 <= 5:
                    answer["s045"] = options[0]["value"]
                elif bsrs5 >= 6 and bsrs5 <= 9:
                    answer["s045"] = options[1]["value"]
                elif bsrs5 >= 10 and bsrs5 <= 14:
                    answer["s045"] = options[2]["value"]
                elif bsrs5 >= 15 and bsrs5 <= 19:
                    answer["s045"] = options[3]["value"]

        elif question_id == "a025":  # BCQ體質量表
            bcq_result, has_bcq = process_bcq(row[indices])
            answer["a025"] = bcq_result if has_bcq else None
            answer["a026c056001"] = bcq_result["a026:c056:001"] if has_bcq else None
            answer["a026c056002"] = bcq_result["a026:c056:002"] if has_bcq else None
        elif question_id == "a031":  # 匹茲堡睡眠品質量表
            sleep_result = process_psqi(row[indices])

            answer["a031"] = sleep_result

            options = py_.get(
                parameter_dict,
                f"a032.subField.options.1.subField.options",
                [],
            )
            if sleep_result["a032_score"] > 5:
                answer["a032"] = "c046:001"
            else:
                answer["a032"] = "c046:002"

            for a0num in range(33, 40):
                options = py_.get(
                    parameter_dict,
                    f"a0{a0num}.subField.options.1.subField.options",
                    [],
                )
                answer[f"a0{a0num}"] = py_.get(
                    options,
                    f'{sleep_result[f"a0{a0num}_score"]}.value',
                )

        elif question_id == "a003":  # 生理性別
            options = parameter_dict["a003"]["subField"]["options"]
            for option in options:
                if option["label"] == row[indices[0]]:
                    answer["gender"] = option["label"]
                    answer["a003"] = option["value"]
        elif question_id == "a004":  # 年齡
            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            answer["birth_date"] = get_date(row[indices[0]])
            answer["age"] = get_age(answer["survey_at"], answer["birth_date"])
            if isinstance(answer["age"], int):
                answer["a004"] = get_range_options_value(answer["age"], options)
        elif question_id == "a005":  # 身高
            answer["height"] = safe_int(row[indices[0]])
            # TODO: get from question options
            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            range_options = [extract_number(options["label"]) for options in options]
            if answer["height"] < range_options[0][0]:
                answer["a005"] = options[0]["value"]
            elif (
                answer["height"] >= range_options[1][0]
                and answer["height"] <= range_options[1][1]
            ):
                answer["a005"] = options[1]["value"]
            elif (
                answer["height"] >= range_options[2][0]
                and answer["height"] <= range_options[2][1]
            ):
                answer["a005"] = options[2]["value"]
            elif (
                answer["height"] >= range_options[3][0]
                and answer["height"] <= range_options[3][1]
            ):
                answer["a005"] = options[3]["value"]
            elif answer["height"] >= range_options[4][0]:
                answer["a005"] = options[4]["value"]
            # TODO: fixme
            # answer["a005"] = get_range_options_value(answer["height"], options)
        elif question_id == "a006":  # 體重
            answer["weight"] = safe_int(row[indices[0]])
            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            # TODO: get from question options
            answer["a006"] = get_range_options_value(answer["weight"], options)

            # TODO: refactor: BMI a007
            if isinstance(answer["height"], int) and isinstance(answer["weight"], int):
                bmi = safe_divide(answer["weight"], (answer["height"] / 100) ** 2)
                answer["bmi"] = round(bmi, 2)
                options = py_.get(
                    parameter_dict,
                    "a007.subField.options.1.subField.options",
                    [],
                )
                answer["a007"] = get_range_options_value(answer["bmi"], options)

        elif question_id == "a024":  # 因上述疾病三個月內持續用藥
            # TODO: check rule
            """
            system:
                c040	001	無因疾病而持續使用藥物
                c040	002	有疾病，但無持續使用藥物
                c040	003	有疾病，且有持續使用藥物
            survey:
                無
                有，請繼續回答下列題目(題項為A-N)
            """
            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            if row[indices[0]] == "無上述疾病":
                answer["a024"] = "c040:001"
            elif row[indices[0]] == "無持續使用藥物":
                answer["a024"] = "c040:002"
            elif row[indices[0]] == "有持續使用藥物，請繼續回答下列題目(題項為A-K)":
                answer["a024"] = "c040:003"
        elif question_id == "a029":  # 血型
            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            for option in options:
                if option["label"] == row[indices[0]]:
                    answer["a029"] = option["value"]
        elif question_id == "s001":  # 教育程度
            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            for option in options:
                if option["label"] == row[indices[0]]:
                    answer["s001"] = option["value"]
            if "大學(專)" == row[indices[0]]:
                answer["s001"] = options[5]["value"]

        elif question_id == "s003":  # 婚姻狀況
            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            for option in options:
                if option["label"] == row[indices[0]]:
                    answer["s003"] = option["value"]
                elif "或" in option["label"] and row[indices[0]] in option["label"]:
                    answer["s003"] = option["value"]

        elif question_id == "s005":  # 主要工作/上課時間
            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            for option in options:
                if option["label"] == row[indices[0]]:
                    answer[question_id] = option["value"]
                elif option["label"] == process_text(row[indices[0]]):
                    answer[question_id] = option["value"]
            if question_id in answer:
                answer["office_hours"] = (row[indices[1]], row[indices[2]])

        elif question_id == "s025":  # 睡眠時間
            sleep_at = row[indices[0]]
            wake_up_at = row[indices[1]]
            if isinstance(sleep_at, str) and isinstance(wake_up_at, str):
                answer["sleep_duration"] = get_time_duration(wake_up_at, sleep_at)
                options = py_.get(
                    parameter_dict,
                    f"{question_id}.subField.options",
                    [],
                )
                if answer["sleep_duration"] < 6:
                    answer["s025"] = options[1]["value"]
                elif answer["sleep_duration"] >= 6:
                    answer["s025"] = options[2]["value"]
                else:
                    answer["s025"] = options[0]["value"]

        elif question_id == "s026":  # 距最近1次用餐時間 range
            eat_at = row[indices[0]]
            answer["eat_at"] = (
                datetime.strptime(eat_at, "%H:%M")
                if isinstance(row[indices[0]], str) and ":" in row[indices[0]]
                else None
            )
            # TODO: calculate eat with measure time

        elif question_id == "s030":  # 前4小時內是否有運動
            """
            c016	001	無
            c016	002	有，前2小時內
            c016	003	有，前2-4小時內
            """

            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            if process_text(row[indices[0]]) == "無":
                answer["s030"] = options[0]["value"]
            # 問卷只有問有無，和選項不同，因此都指定 c016:002
            elif process_text(row[indices[0]]) == "有":
                answer["s030"] = options[1]["value"]

        elif question_id == "s031":  # 運動時數
            exercise_from = row[indices[0]]
            exercise_to = row[indices[1]]
            exercise_duration_minute = get_time_duration(exercise_from, exercise_to)
            exercise_duration = (
                exercise_duration_minute * 60 if exercise_duration_minute else None
            )
            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            if exercise_duration is None:
                answer["a031"] = None
            elif exercise_duration < 30:
                answer["s031"] = options[0]["value"]
            elif exercise_duration >= 30 and exercise_duration < 60:
                answer["s031"] = options[1]["value"]
            elif exercise_duration >= 60:
                answer["s031"] = options[2]["value"]

        elif question_id == "s033":  # 距離已感冒的天數
            symptom_from = row[indices[0]]
            answer["symptom_from"] = (
                datetime.strptime(symptom_from, "%Y-%m-%d")
                if isinstance(row[indices[0]], str) and "-" in row[indices[0]]
                else None
            )
            # TODO: calculate symptom with survey at / measure time

        elif question_id == "s037":  # 確診COVID-19距離測量日天數
            answer["covid_from"] = (
                datetime.strptime(row[indices[0]], "%Y-%m-%d")
                if isinstance(row[indices[0]], str) and "-" in row[indices[0]]
                else None
            )

        elif question_id == "s040":  # 距離上次月經天數
            answer["menstruation_from"] = (
                datetime.strptime(row[indices[0]], "%Y-%m-%d")
                if isinstance(row[indices[0]], str) and "-" in row[indices[0]]
                else None
            )
            # TODO: calculate menstruation with survey at / measure time

        elif question_id == "s041":  # 幾歲停經
            stop_menstruation_year_ago = safe_int(row[indices[0]])
            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            if isinstance(stop_menstruation_year_ago, int) is False:
                answer["s041"] = None
            elif stop_menstruation_year_ago < 1:
                answer["s041"] = options[0]["value"]
            elif stop_menstruation_year_ago >= 1 and stop_menstruation_year_ago < 3:
                answer["s041"] = options[1]["value"]
            elif stop_menstruation_year_ago >= 3 and stop_menstruation_year_ago < 5:
                answer["s041"] = options[2]["value"]
            elif stop_menstruation_year_ago >= 5:
                answer["s041"] = options[3]["value"]

        elif question_id == "s043":  # 懷孕週數
            pregnant_month = safe_int(row[indices[0]])
            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            if pregnant_month is None:
                answer[question_id] = None
            elif pregnant_month < 12:
                answer[question_id] = options[0]["value"]
            elif pregnant_month >= 12 and pregnant_month < 24:
                answer[question_id] = options[1]["value"]
            elif pregnant_month >= 24:
                answer[question_id] = options[2]["value"]

        elif question_id == "a030":  # 居住縣/市
            options = py_.get(
                parameter_dict,
                f"{question_id}.subField.options.1.subField.options",
                [],
            )
            for option in options:
                if option["label"] == row[indices[0]]:
                    answer["a030"] = option["value"]

        else:
            if not question_id:
                continue
            parameter = parameter_dict.get(question_id)
            if not parameter:
                continue

            component_names = find_all_component_names(parameter)
            if "input" in component_names:
                answer[question_id] = safe_int(row[indices[0]])
            else:
                top_level_option_length = len(parameter["subField"]["options"])
                for i in range(top_level_option_length):
                    options = py_.get(
                        parameter_dict,
                        f"{question_id}.subField.options.{i}.subField.options",
                        [],
                    )
                    # not include disease
                    multiple_choices_qid = ["s010", "s013"]
                    if question_id in multiple_choices_qid:
                        answers = (
                            row[indices[0]].split("\n")
                            if isinstance(row[indices[0]], str)
                            else []
                        )
                        answer[question_id] = []
                        for option in options:
                            if option["label"] in answers:
                                answer[question_id].append(option["value"])
                    else:
                        for option in options:
                            if option["label"] == row[indices[0]]:
                                answer[question_id] = option["value"]

                options = py_.get(
                    parameter_dict,
                    f"{question_id}.subField.options",
                    [],
                )
                for option in options:
                    if option["label"] == row[indices[0]]:
                        answer[question_id] = option["value"]

    return answer


async def get_disease_dict(db_session):
    values = await crud.measure_disease_option.get_all(db_session=db_session)
    transformed = (
        py_.chain(values)
        .group_by("category_name")
        .map_values(
            lambda value: {
                "category_id": value[0].category_id,
                "category_name": value[0].category_name,
                "mapping": {f"{e.label}": e.value for e in value},
            },
        )
        .value()
    )
    return transformed


async def process_qa():
    db_session = SessionLocal()
    p_types = [ParameterType.primary, ParameterType.secondary, ParameterType.analytical]

    parameter_dict = await get_parameters(
        db_session=db_session,
        p_types=p_types,
        process_child_parent=False,
    )

    disease_options_dict = await get_disease_dict(db_session=db_session)
    # {'心臟血管疾病': {'category_id': 'd001', 'category_name': '心臟血管疾病', 'mapping': {'全部': '000', '高血壓': '001', '心律不整': '002', '冠狀動脈疾病': '003', '心瓣膜疾病': '004', '心臟衰竭': '005', '雷諾氏病': '006', '心臟病': '007'}}, '呼吸系統疾病': {'category_id': 'd002', 'category_name': '呼吸系統疾病', 'mapping': {'全部': '000', '過敏性鼻炎': '001', '慢性鼻竇炎': '002', '氣喘': '003', '慢性支氣管肺炎': '004', '肺氣腫': '005', '支氣管擴張症': '006', '肺結核': '007'}}, '消化系統疾病': {'category_id': 'd003', 'category_name': '消化系統疾病', 'mapping': {'全部': '000', '胃食道逆流': '001', '胃炎': '002', '消化道潰瘍': '003', '腸胃機能性障礙': '004', '便秘': '005', '大腸激躁症候群': '006', '潰瘍性結腸炎': '007', '克隆氏症': '008', '痔瘡': '009', '肝炎帶原': '010', '慢性肝炎': '011', '肝硬化': '012', '膽結石': '013', '膽囊炎': '014', '慢性胰臟炎': '015'}}, '內分泌及代謝疾病': {'category_id': 'd004', 'category_name': '內分泌及代謝疾病', 'mapping': {'全部': '000', '糖尿病': '001', '高血脂症': '002', '高尿酸': '003', '痛風': '004', '甲狀腺機能亢進症': '005', '甲狀腺機能低下症': '006', '副甲狀腺機能低下症': '007', '副甲狀腺功能亢進症': '008', '腎上腺病變引發內分泌障礙': '009', '腦下垂體病變引發內分泌障礙': '010'}}, '腎泌尿系統疾病': {'category_id': 'd005', 'category_name': '腎泌尿系統疾病', 'mapping': {'全部': '000', '慢性腎臟病': '001', '慢性腎炎': '002', '間質性膀胱炎': '003', '泌尿道感染': '004', '攝護腺肥大': '005', '慢性攝護腺炎': '006', '尿路結石': '007', '尿失禁': '008'}}, '神經系統疾病': {'category_id': 'd006', 'category_name': '神經系統疾病', 'mapping': {'全部': '000', '睡眠障礙': '001', '偏頭痛': '002', '眩暈症': '003', '巴金森氏症': '004', '癲癇': '005', '重症肌無力': '006', '中風': '007', '腦血管疾病': '008', '自律神經失調症': '009', '多發性硬化症': '010', '脊髓損傷': '011'}}, '身心科疾病': {'category_id': 'd007', 'category_name': '身心科疾病', 'mapping': {'全部': '000', '焦慮症': '001', '憂鬱症': '002', '恐慌症': '003', '躁鬱症': '004', '思覺失調症': '005'}}, '皮膚及皮下組織疾病': {'category_id': 'd008', 'category_name': '皮膚及皮下組織疾病', 'mapping': {'全部': '000', '異位性皮膚炎': '001', '濕疹': '002', '蕁麻疹': '003', '脂漏性皮膚炎': '004', '乾癬': '005', '紅皮症': '006'}}, '骨骼肌肉系統及結締組織之疾病': {'category_id': 'd009', 'category_name': '骨骼肌肉系統及結締組織之疾病', 'mapping': {'全部': '000', '關節炎': '001', '骨質疏鬆': '002', '慢性骨髓炎': '003', '僵直性脊椎炎': '004', '硬皮症': '005', '紅斑性狼瘡': '006', '類風濕性關節炎': '007', '乾燥症': '008', '皮肌炎': '009', '多發性肌炎': '010'}}, '耳之疾病': {'category_id': 'd010', 'category_name': '耳之疾病', 'mapping': {'全部': '000', '耳鳴': '001', '中耳炎': '002', '內耳前庭病變': '003'}}, '婦科疾病': {'category_id': 'd011', 'category_name': '婦科疾病', 'mapping': {'全部': '000', '子宮內膜異位症': '001', '子宮肌瘤': '002', '陰道炎': '003', '慢性盆腔炎': '004', '月經不調': '005', '痛經症': '006', '多囊性卵巢症候群': '007', '高泌乳素血症': '008', '更年期症候群': '009'}}, '血液及造血器官疾病': {'category_id': 'd012', 'category_name': '血液及造血器官疾病', 'mapping': {'全部': '000', '缺鐵性貧血': '001', '地中海型貧血': '002', '再生不良性貧血': '003', '骨髓造血不良症候群': '004', '多發性骨髓瘤': '005', '白血病': '006', '淋巴瘤': '007', '紫斑症': '008', '持續性血液凝固障礙（血友病）': '009', '血小板過多症': '010'}}, '癌症': {'category_id': 'd013', 'category_name': '癌症', 'mapping': {'全部': '000', '大腸癌': '001', '肝癌': '002', '胃癌': '003', '口腔癌': '004', '食道癌': '005', '攝護腺癌': '006', '膀胱癌': '007', '肺癌': '008', '甲狀腺癌': '009', '皮膚癌': '010', '白血病': '011', '非何杰金氏淋巴瘤': '012', '乳癌': '013', '子宮體癌': '014', '子宮頸癌': '015', '卵巢癌': '016', '其他癌症': '017'}}, '先天性疾病': {'category_id': 'd014', 'category_name': '先天性疾病', 'mapping': {'全部': '000', '先天性心臟病': '001', '先天代謝異常': '002', '其他先天性疾病': '003'}}, '健康人': {'category_id': 'd015', 'category_name': '健康人', 'mapping': {'無疾病': '000'}}}

    rows = []
    for idx, row in qa_df.iterrows():
        # print(idx)
        processed_row = process_single_row(
            row,
            parameter_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
        # print(processed_row)
        rows.append(processed_row)

    await db_session.close()
    return rows


async def get_survey_result() -> List[SurveyAnswer]:
    rows = await survey_instance.get_result()
    survey_result = [SurveyAnswer(**row) for row in rows]
    return survey_result


async def save_old_survey_result():
    db_session = SessionLocal()
    survey_result_list = await get_survey_result()
    # 內測問卷
    survey_id = "398ec64b-5ee2-48f6-ba9a-d86f69d2d578"

    print("survey_result_list", len(survey_result_list))
    for survey_result in survey_result_list:
        value = json.dumps(jsonable_encoder(survey_result), ensure_ascii=False)
        # print("value", value)
        survey_result_in = schemas.MeasureSurveyResultCreate(
            survey_id=survey_id,
            number=survey_result.number,
            subject_id=None,
            measure_id=None,
            value=value,
            survey_at=survey_result.survey_at,
        )
        await crud.measure_survey_result.create(
            db_session=db_session,
            obj_in=survey_result_in,
        )


async def save_survey_result():
    db_session = SessionLocal()

    org = await crud.org.get_by_name(db_session=db_session, name="tph")
    survey_list = []
    survey_name_list = ["台北站問卷", "金門站問卷"]
    # survey_name_list = ["台北站問卷"]
    for survey_name in survey_name_list:
        survey = await crud.measure_survey.get_by_name(
            db_session=db_session,
            name=survey_name,
        )
        if survey is None:
            survey = await crud.measure_survey.create(
                db_session=db_session,
                obj_in=schemas.MeasureSurveyCreate(name=survey_name, org_id=org.id),
            )
        survey_list.append(survey)

    for idx, survey_name in enumerate(survey_name_list):
        qa_handler = QAHandler(survey_name=survey_name)
        survey_result_list = await qa_handler.get_survey_result()

        survey_id = survey_list[idx].id
        print("survey_result_list", len(survey_result_list))
        for survey_result in survey_result_list:

            value = json.dumps(jsonable_encoder(survey_result), ensure_ascii=False)

            subject_id = None
            measure_id = None
            print("survey_result.number", survey_result.number)
            if survey_result.number.upper() in ("KA014"):
                continue
            subject = await crud.subject.get_by_number_and_org_id(
                db_session=db_session,
                org_id=org.id,
                number=survey_result.number,
            )
            if subject is None:
                continue
            subject_id = subject.id
            measure = await crud.measure_info.get_closest_by_survey_at(
                db_session=db_session,
                subject_id=subject_id,
                survey_at=survey_result.survey_at,
            )
            if subject is not None and measure is not None:
                if abs((measure.measure_time - survey_result.survey_at).days) > 7:
                    print("ignore diff day more than 7 days")
                    continue

                sex_type_label_map = {
                    value: key for key, value in SEX_TYPE_LABEL.items()
                }
                sex_value = sex_type_label_map.get(survey_result.gender)
                subject_in = schemas.SubjectUpdate(
                    birth_date=survey_result.birth_date,
                    sex=sex_value,
                )
                subject = await crud.subject.update(
                    db_session=db_session,
                    obj_current=subject,
                    obj_new=subject_in.dict(exclude_none=True),
                )

                measure_id = measure.id
                measure_in = schemas.MeasureInfoUpdate(
                    sex=sex_value,
                    age=get_age(measure.measure_time, survey_result.birth_date),
                    height=survey_result.height,
                    weight=survey_result.weight,
                    bmi=get_bmi(survey_result.height, survey_result.weight),
                    sbp=survey_result.sbp,
                    dbp=survey_result.dbp,
                )
                await crud.measure_info.update(
                    db_session=db_session,
                    obj_current=measure,
                    obj_new=measure_in.dict(exclude_none=True),
                )
            else:
                print(f"cannot find subject/measure number {survey_result.number}")

            survey_result_in = schemas.MeasureSurveyResultCreate(
                survey_id=survey_id,
                number=survey_result.number,
                subject_id=subject_id,
                measure_id=measure_id,
                value=value,
                survey_at=survey_result.survey_at,
            )

            exist_survey_result = (
                await crud.measure_survey_result.get_by_number_survey_at(
                    db_session=db_session,
                    number=survey_result.number,
                    survey_at=survey_result.survey_at,
                )
            )
            if exist_survey_result:
                await crud.measure_survey_result.remove(
                    db_session=db_session,
                    id=exist_survey_result.id,
                )
            await crud.measure_survey_result.create(
                db_session=db_session,
                obj_in=survey_result_in,
            )

    await save_bcq_score_new(org_id=org.id)


async def save_bcq_score():
    from auo_project import schemas

    db_session = SessionLocal()
    survey_result = await get_survey_result()
    survey_dict_by_number = {x.number: x for x in survey_result}
    survey_number_list = [x.number for x in survey_result if x.a025]
    print("survey_number_list", survey_number_list)
    measures = await crud.measure_info.get_by_numbers(
        db_session=db_session,
        list_ids=survey_number_list,
        relations=["bcq"],
    )
    measure_id_number_dict = {measure.id: measure.number for measure in measures}
    measure_bcqs = [
        {
            "input": schemas.BCQCreate(
                **survey_dict_by_number.get(
                    measure_id_number_dict.get(measure.id),
                ).a025,
                measure_id=measure.id,
            ),
            "exist_bcq": measure.bcq,
            "measure_id": measure.id,
        }
        for measure in measures
    ]
    await db_session.close()
    for measure_bcq in measure_bcqs:
        if measure_bcq["exist_bcq"]:
            await crud.measure_bcq.remove(
                db_session=db_session,
                id=measure_bcq["exist_bcq"].id,
            )
        await crud.measure_bcq.create(
            db_session=db_session,
            obj_in=measure_bcq["input"],
        )
        measure = await crud.measure_info.get(
            db_session=db_session,
            id=measure_bcq["measure_id"],
        )
        await crud.measure_info.update(
            db_session=db_session,
            obj_current=measure,
            obj_new=schemas.MeasureInfoUpdate(has_bcq=True),
        )


async def save_bcq_score_new(org_id: UUID):
    db_session = SessionLocal()
    survey_result = await crud.measure_survey_result.get_by_org_id(
        db_session=db_session,
        org_id=org_id,
    )
    measure_id_survey_dict = {x.measure_id: x for x in survey_result}
    survey_number_list = [x.number for x in survey_result if x.value.get("a025")]
    survey_measure_id_list = [
        x.measure_id for x in survey_result if x.value.get("a025")
    ]
    print("survey_number_list", survey_number_list)
    measures = await crud.measure_info.get_by_ids(
        db_session=db_session,
        list_ids=survey_measure_id_list,
        relations=["bcq"],
    )
    print(f"measures length: {len(measures)}")
    measure_id_number_dict = {measure.id: measure.number for measure in measures}
    measure_bcqs = [
        {
            "input": schemas.BCQCreate(
                **measure_id_survey_dict.get(measure.id).value.get("a025"),
                measure_id=measure.id,
            ),
            "exist_bcq": measure.bcq,
            "measure_id": measure.id,
            "number": measure_id_number_dict.get(measure.id),
        }
        for measure in measures
        if measure_id_survey_dict.get(measure.id).value.get("a025")
    ]

    for measure_bcq in measure_bcqs:
        db_session = SessionLocal()
        print(
            'measure_bcq["measure_id"]',
            measure_bcq["measure_id"],
            measure_bcq["number"],
        )
        if measure_bcq["exist_bcq"]:
            await crud.measure_bcq.remove(
                db_session=db_session,
                id=measure_bcq["exist_bcq"].id,
            )
        await db_session.flush()
        await crud.measure_bcq.create(
            db_session=db_session,
            obj_in=measure_bcq["input"],
        )
        await db_session.close()

        db_session = SessionLocal()
        measure = await crud.measure_info.get(
            db_session=db_session,
            id=measure_bcq["measure_id"],
        )

        await crud.measure_info.update(
            db_session=db_session,
            obj_current=measure,
            obj_new=schemas.MeasureInfoUpdate(has_bcq=True),
        )

        await db_session.commit()
        await db_session.close()
