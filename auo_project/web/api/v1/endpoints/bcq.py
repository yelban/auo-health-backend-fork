from itertools import chain
from typing import Any, Dict, List, Optional

import requests
from fastapi import APIRouter, HTTPException, Query

from auo_project import schemas
from auo_project.core.config import settings


def get_age_group(age: int) -> Optional[int]:
    if age < 0:
        return None
    elif age < 45:
        return 0
    elif age < 60:
        return 1
    else:
        return 2


def get_full_questions():
    return {
        1: "雖然沒有感冒，我喉嚨中會有痰。",
        2: "我會覺得手心、腳掌心或身體會熱熱的。",
        3: "我會覺得自己怕冷、手腳冰冷或需穿比較多的衣服。",
        4: "我會覺得頭重、頭昏不舒服。",
        5: "我會覺得疲倦或無力不想動。",
        6: "我會覺得口中黏黏的或口水黏稠。",
        7: "我會覺得身體或下半身重重的。",
        8: "突然站起來時，我會覺得眼前發黑。",
        9: "我會覺得疲倦不想說話或沒力氣說話。",
        10: "我的舌頭或口腔會破。",
        11: "我會覺得眼睛乾澀，或看東西不清楚。",
        12: "我的胸、腹部或四肢會悶痛不舒服。",
        13: "我的胸、腹部或四肢會刺痛不舒服。",
        14: "我會覺得睡眠時間夠，但仍想睡覺或睡不飽。",
        15: "我會覺得氣不夠，需要深呼吸。",
        16: "我的身體或手腳會有麻木感。",
        17: "我會覺得胸口悶悶或緊緊的，好像有東西壓著。",
        18: "我會耳鳴。",
        19: "我的皮膚會無故出現瘀血烏青。",
        20: "我的皮膚會乾燥、龜裂、變厚或變硬。",
        21: "我的身體或四肢會看到扭曲變形的血管（靜脈曲張）。",
        22: "我會感到腰部、膝蓋或足跟酸軟、疼痛、無力或發冷。",
        23: "沒有劇烈運動時，我會抽筋。",
        24: "我會覺得呼吸深度短淺或喘。",
        25: "我的身體側面或兩側上腹肋骨處（位置見右圖中打×範圍）會有悶、脹或疼痛的感覺。",
        26: "我會口渴、嘴巴乾、嘴唇乾燥龜裂，且喝水後很快又口渴。",
        27: "我的四肢、身體、臉部或眼睛周圍會浮腫。",
        28: "平躺時我的呼吸會變喘。",
        29: "我的臉頰會發紅。(部位請見附圖)",
        30: "我會覺得喉嚨乾，但嘴巴或嘴唇不會乾燥。",
        31: "姿勢改變時，我會覺得天旋地轉。",
        32: "我覺得我的聽力減退。",
        33: "我吹到風會不舒服。",
        34: "我的舌苔會厚厚或黏黏的。",
        35: "我會覺得身體或頭面突然一陣熱熱的。",
        36: "我會喜歡喝溫熱的東西。",
        37: "沒有劇烈運動時，我的腰部會容易扭傷。",
        38: "除了早上第一次解尿外，我的小便顏色深黃或茶色。",
        39: "我的小便量少。",
        40: "我的大便乾硬。",
        41: "我的大便不成形。",
        42: "我會覺得嘴巴淡淡的沒有味道。",
        43: "沒有喝很多水，我仍覺得小便量多。",
        44: "我在天亮前會因拉肚子而起床。",
    }


def get_api_response():
    res = requests.get(
        f"{settings.BCQ_MODEL_API_URL}/api/v1.0/items_info",
    )
    if res.status_code == 200:
        return res.json()
    else:
        print(f"error: {res.text}")
        return get_mock_api_response()


def get_mock_api_response():
    return {
        "status": "OK",
        "message": "",
        "data": {
            "itemsInfo": {
                "M-0-yang_hsu": [5, 15, 17, 24, 22],
                "M-0-ying_hsu": [26, 11, 8, 4, 16],
                "M-0-tang_yu": [5, 12, 13, 14],
                "M-1-yang_hsu": [24, 33, 22, 3, 5],
                "M-1-ying_hsu": [32, 11, 26, 38, 39],
                "M-1-tang_yu": [5, 14, 12, 6],
                "M-2-yang_hsu": [15, 42, 22, 17, 28],
                "M-2-ying_hsu": [11, 38, 26, 8, 39],
                "M-2-tang_yu": [5, 6, 20, 14],
                "F-0-yang_hsu": [15, 22, 5, 24, 17],
                "F-0-ying_hsu": [26, 8, 11, 4, 31],
                "F-0-tang_yu": [14, 5, 12, 17],
                "F-1-yang_hsu": [24, 17, 15, 33, 22],
                "F-1-ying_hsu": [11, 26, 35, 4, 31],
                "F-1-tang_yu": [14, 17, 12, 7],
                "F-2-yang_hsu": [22, 17, 15, 24, 5],
                "F-2-ying_hsu": [11, 18, 16, 23, 26],
                "F-2-tang_yu": [12, 16, 5, 7],
            },
        },
    }


def transform_api_response(items_info):
    return {
        "M0": {
            "yang": items_info["M-0-yang_hsu"],
            "yin": items_info["M-0-ying_hsu"],
            "phlegm": items_info["M-0-tang_yu"],
        },
        "M1": {
            "yang": items_info["M-1-yang_hsu"],
            "yin": items_info["M-1-ying_hsu"],
            "phlegm": items_info["M-1-tang_yu"],
        },
        "M2": {
            "yang": items_info["M-2-yang_hsu"],
            "yin": items_info["M-2-ying_hsu"],
            "phlegm": items_info["M-2-tang_yu"],
        },
        "F0": {
            "yang": items_info["F-0-yang_hsu"],
            "yin": items_info["F-0-ying_hsu"],
            "phlegm": items_info["F-0-tang_yu"],
        },
        "F1": {
            "yang": items_info["F-1-yang_hsu"],
            "yin": items_info["F-1-ying_hsu"],
            "phlegm": items_info["F-1-tang_yu"],
        },
        "F2": {
            "yang": items_info["F-2-yang_hsu"],
            "yin": items_info["F-2-ying_hsu"],
            "phlegm": items_info["F-2-tang_yu"],
        },
    }


def get_option_by_question_id(qid: int) -> List[Dict[str, Any]]:
    if qid <= 22:
        return [
            {"label": "完全不會", "value": 1},
            {"label": "稍微會", "value": 2},
            {"label": "中等程度會", "value": 3},
            {"label": "很會", "value": 4},
            {"label": "最嚴重會", "value": 5},
        ]
    else:
        return [
            {"label": "從來沒有", "value": 1},
            {"label": "偶爾有", "value": 2},
            {"label": "一半有一半沒有", "value": 3},
            {"label": "常常有", "value": 4},
            {"label": "一直都有", "value": 5},
        ]


router = APIRouter()


@router.get("/questions", response_model=schemas.BCQQuestionList)
def get_questions(
    age: int = Query(title="年齡", gt=0, description="年齡必須大於0"),
    sex: str = Query(title="生理性別: 男:M;女:F"),
) -> Any:
    """
    Get BCQ questions by age and sex.
    """
    age_group = None
    if age < 45:
        age_group = 0
    elif age < 60:
        age_group = 1
    else:
        age_group = 2

    if sex not in ("M", "F"):
        raise HTTPException(status_code=422, detail="sex allow M and F only.")
    api_response = get_api_response()
    questions = get_full_questions()
    question_mapping = transform_api_response(api_response["data"]["itemsInfo"])
    question_by_profile = question_mapping[f"{sex}{age_group}"]
    flat_uniq_questions = sorted(set(chain.from_iterable(question_by_profile.values())))
    output_questions = [
        {
            "id": q_id,
            "question": questions[q_id],
            "options": get_option_by_question_id(q_id),
        }
        for q_id in flat_uniq_questions
    ]

    return schemas.BCQQuestionList(data=output_questions)


@router.get("/questions/json")
def get_questions_json() -> Any:
    """
    Get BCQ questions json.
    """
    age_ranges = {
        0: "45歲以下",
        1: "45-60歲",
        2: "60歲以上",
    }
    age_groups = [0, 1, 2]
    sex_groups = ["M", "F"]
    sex_label_map = {"M": "男", "F": "女"}
    output_result = []
    api_response = get_api_response()
    for age_group in age_groups:
        for sex in sex_groups:
            questions = get_full_questions()
            question_mapping = transform_api_response(api_response["data"]["itemsInfo"])
            question_by_profile = question_mapping[f"{sex}{age_group}"]
            flat_uniq_questions = sorted(
                set(chain.from_iterable(question_by_profile.values())),
            )
            output_questions = [
                {
                    "id": q_id,
                    "question": questions[q_id],
                    "options": get_option_by_question_id(q_id),
                }
                for q_id in flat_uniq_questions
            ]
            output_result.append(
                {
                    "age_group": age_group,
                    "age_range": age_ranges[age_group],
                    "sex": sex,
                    "sex_label": sex_label_map[sex],
                    "data": output_questions,
                },
            )
    return output_result


@router.post("/type/inference", response_model=schemas.BCQTypeInferenceOuput)
def inference_type_by_bcq(
    bcq_input: schemas.BCQTypeInferenceInput,
) -> Any:
    """
    Inference BCQ type by BCQ data.
    """
    from random import choice, random

    # TODO: design error handling for calling api

    sex = bcq_input.sex
    age_group = get_age_group(bcq_input.age)

    api_response = get_api_response()
    question_mapping = transform_api_response(api_response["data"]["itemsInfo"])
    question_by_profile = question_mapping[f"{sex}{age_group}"]
    flat_uniq_questions = sorted(set(chain.from_iterable(question_by_profile.values())))
    if len(bcq_input.answers) != len(flat_uniq_questions):
        raise HTTPException(
            status_code=422,
            detail="answers length must be equal to the number of questions.",
        )
    if sorted(list(map(int, bcq_input.answers.keys()))) != flat_uniq_questions:
        raise HTTPException(
            status_code=422,
            detail=f"answers keys must be equal to the question ids: {flat_uniq_questions}",
        )

    payload = {
        "individuals": [
            {
                "id": bcq_input.user_id,
                "yang_hsu_items": [
                    bcq_input.answers.get(str(qid))
                    for qid in question_by_profile["yang"]
                ],
                "ying_hsu_items": [
                    bcq_input.answers.get(str(qid))
                    for qid in question_by_profile["yin"]
                ],
                "tang_yu_items": [
                    bcq_input.answers.get(str(qid))
                    for qid in question_by_profile["phlegm"]
                ],
                "gender": bcq_input.sex,
                "age": bcq_input.age,
                "height": bcq_input.height,
                "weight": bcq_input.weight,
            },
        ],
    }
    print("payload", payload)
    res = requests.post(
        f"{settings.BCQ_MODEL_API_URL}/api/v1.0/inference/",
        json=payload,
    )

    mock_api_response = schemas.BCQTypeInferenceOuput(
        yang_type=choice([0, 1, 2]),
        yin_type=choice([0, 1, 2]),
        phlegm_type=choice([0, 1, 2]),
        yang_score=round(random(), 3),
        yin_score=round(random(), 3),
        phlegm_score=round(random(), 3),
    )

    print("res", res.status_code, res.json())

    if res.status_code != 200:
        return mock_api_response
    else:
        status = res.json().get("status")
        data = res.json()["data"]
        results = data["results"]
        if len(results) != 1:
            print("error: length is not the 1")
            return mock_api_response

        if status != "OK":
            print(f"error: status is not OK but {status}")
            return mock_api_response

        bcq_type_map = {
            "Normal": 0,
            "Possible": 1,
            "Confirmed": 2,
        }
        api_response = schemas.BCQTypeInferenceOuput(
            yang_type=bcq_type_map.get(results[0]["yang_hsu"], 0),
            yin_type=bcq_type_map.get(results[0]["ying_hsu"], 0),
            phlegm_type=bcq_type_map.get(results[0]["tang_yu"], 0),
            yang_score=round(results[0]["yang_hsu_score"], 3),
            yin_score=round(results[0]["ying_hsu_score"], 3),
            phlegm_score=round(results[0]["tang_yu_score"], 3),
        )
        return api_response
