from io import StringIO
from typing import List

import pandas as pd
import pydash as py_

from auo_project import schemas

surface_disease_content = """
tongue_tip	tongue_color	tongue_shap	tongue_status1	tongue_status2	tongue_coating_color	tongue_coating_status	surface_disease
紅	淡紅	正常	正常	榮舌	白	薄	心火上炎
    青	老	正常	榮舌	白	薄	肝膽兩經邪氣盛
    青	瘦薄	正常	榮舌	白	滑、光剝	傷寒直中肝腎陰證
    青、紫	正常	正常	榮舌	灰黑	滑	痰飲內停或寒濕內阻
    青、紫	正常	正常	榮舌	白	厚、膩、滑	停飲
    青、紫	正常	正常	榮舌	白	薄	寒邪直中
    紅	正常	正常	榮舌	黃	薄	實熱
    紅	正常	正常	榮舌	白	燥	胃津已傷
    紅	正常	萎軟	榮舌	白	燥	熱灼陰傷
    紅	正常	強硬	榮舌	白	薄	熱入心包
    紅	正常	正常	榮舌	白	薄	熱證
    紅	正常	正常	榮舌	黃	腐、膩	脾胃濕熱壅滯
    紅	正常	正常	榮舌	灰黑	燥	熱熾傷津或陰虛火旺
    紅	正常	正常	榮舌	白	厚、膩、燥	濕邪困遏，陽氣不伸
    紅	正常	正常	榮舌	白	光剝、燥	胃陰虛
    紅	芒刺	正常	榮舌	白	薄	營分有熱
    紅	芒刺	正常	榮舌	黃	燥	氣分熱盛
    紅	芒刺	正常	榮舌	黃	薄	胃腸熱盛
    紅	裂紋	正常	榮舌	白	燥	熱盛傷津
    紅	裂紋	正常	榮舌	白	少	氣陰兩虛
    紅	裂紋	正常	榮舌	白	光剝	氣陰兩虛
    紅	嫩	正常	榮舌	白	光剝	陰虛火旺
    紅	瘦薄	正常	枯舌	白	光剝、燥	腎陰欲竭
    紅、絳	正常	短縮	榮舌	灰黑	燥	熱病傷津
    紅、絳	正常	短縮	榮舌	白	光剝、燥	熱病傷津
    紅、絳	瘦薄	正常	榮舌	白	燥	陰虛火旺
    淡白	正常	正常	榮舌	白	滑	大腸陽氣虛
    淡白	正常	正常	榮舌	白	燥	肺臟火旺
    淡白	正常	萎軟	榮舌	白	薄	氣血俱虛
    淡白	正常	吐弄	榮舌	白	薄	虛象
    淡白	正常	短縮	榮舌	白	滑	寒凝經脈
    淡白	正常	正常	榮舌	白	薄	寒證
    淡白	正常	正常	榮舌	灰黑	滑	痰飲內停或寒濕內阻
    淡白	正常	正常	榮舌	白	厚	痰熱
    淡白	正常	正常	榮舌	白	花剝、滑	脾胃陽氣不足
    淡白	正常	正常	榮舌	白	光剝	氣血兩虛
    淡白	胖大、嫩	正常	榮舌	白	薄	肺與大腸精氣虛
    淡白	胖大、嫩	正常	榮舌	黃	滑	陽虛水濕不化
    淡白	胖大、嫩、齒痕	正常	榮舌	白	薄	脾氣虛
    淡白	裂紋	正常	榮舌	白	薄	氣血兩虛
    淡白	裂紋、胖大	正常	榮舌	白	膩	脾虛濕浸
    淡白	瘦薄	正常	榮舌	白	薄	氣血兩虛
    淡紅	正常	顫動	榮舌	白	薄	血虛生風
    淡紅	正常	顫動	榮舌	白	厚	酒精中毒
    淡紅	正常	正常	榮舌	白	厚、膩	里寒兼濕
    淡紅	正常	正常	榮舌	白	滑	寒濕襲表
    淡紅	正常	正常	榮舌	白	光剝	脾陽虛衰
    淡紅	正常	正常	榮舌	黃	滑	濕熱
    淡紅	正常	正常	榮舌	灰黑	滑	痰飲寒濕
    淡紅	正常	正常	榮舌	灰黑	燥	陰虛火旺
    淡紅	正常	正常	榮舌	灰黑	膩	濕熱
    淡紅	正常	正常	榮舌	灰黑	少	陰虛
    淡紅	正常	正常	榮舌	灰黑	花剝	陰虛
    淡紅	正常	正常	榮舌	白	滑、膩	寒濕束表
    淡紅	正常	正常	榮舌	白	花剝、燥	氣陰兩傷
    淡紅	正常	正常	榮舌	白	光剝、燥	氣陰兩虛
    淡紅	胖大	短縮	榮舌	白	膩	痰濕阻閉
    淡紅	裂紋	正常	榮舌	白	少	氣陰兩虛
    淡紅	裂紋	正常	榮舌	白	光剝	氣陰兩虛
    紫	正常	正常	榮舌	灰黑	薄	瘀血
    紫	正常	顫動	榮舌	白	薄	熱極生風
    紫	芒刺	正常	榮舌	白	薄	血分熱毒盛
    紫、紅	正常	正常	榮舌	白	燥	瘀熱
    紫、紅	正常	吐弄	榮舌	白	薄	熱毒攻心
    紫、淡白	正常	正常	榮舌	白	薄	寒凝血瘀 / 陽陽虛生寒
    紫、絳	正常	正常	榮舌	白	滑	熱傳營血
    紫、絳	正常	正常	榮舌	白	薄	血分熱毒
    紫、絳	正常	顫動	榮舌	灰黑	薄	肝風內動
    絳	正常	正常	榮舌	白	燥	邪入營血
    絳	正常	正常	榮舌	白	光剝	胃陰大傷
    絳	正常	正常	枯舌	白	薄	胃陰已涸
    絳	正常	正常	榮舌	白	薄	飲食中風寒 / 熱積涼飲
    絳	正常	正常	榮舌	白	厚	內夾宿食，中風寒
    絳	正常	正常	榮舌	白	厚、膩、燥	表里合邪
    絳	正常	正常	榮舌	黃	厚、膩、燥	邪熱內結
    絳	正常	萎軟	榮舌	白	薄	陰虧已極
    絳	正常	強硬	榮舌	白	薄	熱入心包
    絳	正常	正常	榮舌	灰黑	燥	熱熾傷津或陰虛火旺
    絳	正常	正常	榮舌	白	光剝、燥	胃陰虛
    絳	朱點	正常	榮舌	白	薄	熱毒乘心
    絳	裂紋	正常	榮舌	白	薄	胃火傷津
    絳	裂紋	正常	榮舌	白	燥	熱盛傷津
    絳	瘦薄	正常	枯舌	白	光剝、燥	腎陰欲竭
"""

surface_disease_records = pd.read_csv(
    StringIO(surface_disease_content),
    sep="\t",
).to_dict("records")


def get_surface_disease_records():
    return surface_disease_records


def get_tongue_summary(
    tongue_info: schemas.MeasureAdvancedTongue2UpdateInput,
    tongue_sympotms: List[schemas.MeasureTongueSymptom],
):
    summary_components = [
        ("舌尖", ["tongue_tip"], ""),
        ("舌", ["tongue_color", "tongue_shap"], ""),
        ("苔", ["tongue_coating_color", "tongue_coating_status"], ""),
        ("舌態", ["tongue_status1"], ""),
        ("舌神", ["tongue_status2"], ""),
        ("舌下脈絡", ["tongue_coating_bottom"], ""),
    ]
    normal_symptoms = py_.filter_(tongue_sympotms, lambda x: x.is_normal)
    normal_symptom_dict = (
        py_.chain(normal_symptoms)
        .group_by("item_id")
        .map_values(lambda values: [e.symptom_id for e in values])
        .value()
    )

    # show the symptom of the summary
    special_rules = {
        "tongue_coating_color": {
            "tongue_coating_color": ["白"],
            "tongue_coating_status": [
                "少",
                "厚",
                "腐",
                "膩",
                "潤",
                "燥",
                "花剝",
                "光剝",
            ],
        },
    }
    special_rules_match = py_.map_values(
        special_rules,
        lambda rule: py_.chain(rule)
        .map_values(
            lambda value, key: len(py_.intersection(py_.get(tongue_info, key), value))
            > 0,
        )
        .values()
        .every()
        .value(),
    )

    tongue_summary_list = []
    for prefix, items, suffix in summary_components:
        abnormal_symptoms_list = []
        for item in items:
            symptoms = getattr(tongue_info, item, [])

            if special_rules_match.get(item) is True:
                sub_abnormal_symptoms = symptoms
            else:
                sub_abnormal_symptoms = py_.difference(
                    symptoms,
                    normal_symptom_dict.get(item, []),
                )
            abnormal_symptoms_list.extend(sub_abnormal_symptoms)
        if abnormal_symptoms_list:
            tongue_summary_list.append(
                f"{prefix}{'、'.join(abnormal_symptoms_list)}{suffix}",
            )

    # 證型 disease
    disease_list = []
    for key in tongue_info.__fields__.keys():
        if key.endswith("_disease_map"):
            disease_map = getattr(tongue_info, key, {})
            disease_list.extend(py_.flatten(disease_map.values()))
    uniq_disease_list = list(set(disease_list))
    if uniq_disease_list:
        tongue_summary_list.append(f"一般會有{'、'.join(uniq_disease_list)}的傾向")

    def process_symptom_id_list(content: str):
        if isinstance(content, str):
            return content.split("、")
        return []

    records = get_surface_disease_records()
    records = [
        {
            "tongue_tip": process_symptom_id_list(record["tongue_tip"]),
            "tongue_color": process_symptom_id_list(record["tongue_color"]),
            "tongue_shap": process_symptom_id_list(record["tongue_shap"]),
            "tongue_coating_color": process_symptom_id_list(
                record["tongue_coating_color"],
            ),
            "tongue_coating_status": process_symptom_id_list(
                record["tongue_coating_status"],
            ),
            "tongue_status1": process_symptom_id_list(record["tongue_status1"]),
            "tongue_status2": process_symptom_id_list(record["tongue_status2"]),
            # "tongue_coating_bottom": process_symptom_id_list(
            #     record["tongue_coating_bottom"]
            # ),
            "surface_disease": record["surface_disease"],
        }
        for record in records
    ]

    surface_summary_list = []
    for record in records:
        condition_match = []
        for item_id, symptom_id_list in record.items():
            if item_id == "surface_disease":
                continue

            selected_symptoms = getattr(tongue_info, item_id, [])
            match = sorted(selected_symptoms) == sorted(symptom_id_list)
            condition_match.append(match)

        if all(condition_match):
            surface_summary_list.append(record["surface_disease"])
            break
    if surface_summary_list:
        tongue_summary_list.append(f"可能有{'、'.join(surface_summary_list)}的情況")

    tongue_summary = "，".join(tongue_summary_list)
    tongue_summary = tongue_summary and tongue_summary + "。"

    return tongue_summary
