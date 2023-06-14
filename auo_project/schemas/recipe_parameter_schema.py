from uuid import UUID

from pydantic import BaseModel, Field

from auo_project.models.recipe_parameter_model import RecipeParameterBase


class RecipeBasicParameterInput(BaseModel):
    p001: str = Field(title="計畫編號", example="all")
    p002: str = Field(title="判讀醫師", example="all")
    p003: str = Field(title="檢測單位", example="all")
    p004: str = Field(title="檢測人員", example="all")
    p005: str = Field(title="檢測日期", example="all")
    p006: str = Field(title="問卷收案日期", example="all")
    p007: str = Field(title="脈診量測時間", example="all")
    p008: str = Field(title="脈波通過率", example="all")
    s001: str = Field(title="教育程度", example="all")
    s002: str = Field(title="習慣用語", example="all")
    s003: str = Field(title="婚姻狀況", example="all")
    # s004: str = Field(title="生活作息", example="all")
    s005: str = Field(title="主要工作/上課時間", example="all")
    s006: str = Field(title="經常熬夜", example="all")
    s007: str = Field(title="每週運動超過30分鐘次數", example="all")
    s008: str = Field(title="精神壓力", example="all")
    # s009: str = Field(title="飲食習慣", example="all")
    s010: str = Field(title="喜歡口味", example="all")
    s011: str = Field(title="每週食用冰品頻率", example="all")
    s012: str = Field(title="每週食用油炸食物頻率", example="all")
    s013: str = Field(title="喜歡的咖啡因飲品", example="all")
    s014: str = Field(title="每週飲用含咖啡因飲品頻率", example="all")
    # s015: str = Field(title="個人史", example="all")
    s016: str = Field(title="抽菸頻率", example="all")
    s017: str = Field(title="每週喝酒頻率", example="all")
    s018: str = Field(title="每週嚼檳榔頻率", example="all")
    # s019: str = Field(title="自我評量", example="all")
    s020: str = Field(title="對健康狀態打分", example="all")
    s021: str = Field(title="自覺健康狀態", example="all")
    s022: str = Field(title="節律標記", example="all")
    # s023: str = Field(title="量測當日生活及身體狀況", example="all")
    s024: str = Field(title="是否熬夜", example="all")
    s025: str = Field(title="睡眠時間", example="all")
    s026: str = Field(title="距最近1次用餐時間", example="all")
    s027: str = Field(title="最近1次進食食物溫度", example="all")
    s028: str = Field(title="前4小時內是否飲用咖啡因飲品", example="all")
    s029: str = Field(title="前4小時內是否食用含酒精飲食", example="all")
    s030: str = Field(title="前4小時內是否有運動", example="all")
    s031: str = Field(title="前4小時內最近1次運動時數", example="all")
    s032: str = Field(title="今日是否有感冒症狀", example="all")
    s033: str = Field(title="距離已感冒的天數", example="all")
    s034: str = Field(title="24小時內是否服用藥物", example="all")
    s035: str = Field(title="接種幾次COVID-19疫苗", example="all")
    s036: str = Field(title="感染幾次COVID-19", example="all")
    s037: str = Field(title="確診COVID-19距離測量日天數", example="all")
    # s038: str = Field(title="女性專屬問項", example="all")
    s039: str = Field(title="是否仍有月經", example="all")
    s040: str = Field(title="距離上次月經天數", example="all")
    s041: str = Field(title="幾歲停經", example="all")
    s042: str = Field(title="目前是否懷孕", example="all")
    s043: str = Field(title="目前懷孕週數", example="all")
    # s044: str = Field(title="心情溫度計", example="all")
    s045: str = Field(title="總分", example="all")
    s046: str = Field(title="有自殺想法", example="all")


class RecipeAnalyticalParamsInput(BaseModel):
    a001: str = Field(title="檢測日期", example="all")
    a002: str = Field(title="介入因子", example="all")
    a003: str = Field(title="生理性別", example="c023:000")
    a004: str = Field(title="年齡", example="all")
    a005: str = Field(title="身高", example="all")
    a006: str = Field(title="體重", example="all")
    a007: str = Field(title="BMI", example="all")
    a008: str = Field(title="疾病史", example="all")
    # a009: str = Field(title="正常人")
    # a010: str = Field(title="心臟血管疾病")
    # a011: str = Field(title="呼吸系統疾病")
    # a012: str = Field(title="消化系統疾病")
    # a013: str = Field(title="內分泌及代謝疾病")
    # a014: str = Field(title="腎泌尿系統疾病")
    # a015: str = Field(title="神經系統疾病")
    # a016: str = Field(title="身心科疾病")
    # a017: str = Field(title="皮膚及皮下組織疾病")
    # a018: str = Field(title="骨骼肌肉系統及結締組織之疾病")
    # a019: str = Field(title="耳之疾病")
    # a020: str = Field(title="婦科疾病")
    # a021: str = Field(title="血液及造血器官疾病")
    # a022: str = Field(title="癌症")
    # a023: str = Field(title="先天性疾病")
    a024: str = Field(title="因上述疾病三個月內持續用藥", example="all")
    a025: str = Field(title="BCQ得分（正規化）", example="c056:001")
    a026: str = Field(title="BCQ得分", example="all")
    a027: str = Field(title="二十八脈", example="all")
    a028: str = Field(title="血壓", example="all")
    a029: str = Field(title="血型", example="all")
    a030: str = Field(title="居住縣/市", example="all")
    # a031: str = Field(title="匹茲堡睡眠量表")
    a032: str = Field(title="匹茲堡睡眠量表-總分", example="c046:000")
    a033: str = Field(title="匹茲堡睡眠量表-睡眠品質", example="all")
    a034: str = Field(title="匹茲堡睡眠量表-睡眠潛伏期", example="all")
    a035: str = Field(title="匹茲堡睡眠量表-睡眠總時數", example="all")
    a036: str = Field(title="匹茲堡睡眠量表-睡眠效率", example="all")
    a037: str = Field(title="匹茲堡睡眠量表-睡眠障礙", example="all")
    a038: str = Field(title="匹茲堡睡眠量表-安眠藥物使用", example="all")
    a039: str = Field(title="匹茲堡睡眠量表-日間功能障礙", example="all")


class RecipeAllParameterInput(RecipeBasicParameterInput, RecipeAnalyticalParamsInput):
    pass


class RecipeParameterBaseRead(RecipeParameterBase):
    id: UUID


class RecipeParameterRead(RecipeParameterBaseRead):
    pass


class RecipeParameterCreate(RecipeParameterBase):
    pass


class RecipeParameterUpdate(BaseModel):
    value: str = None
