from uuid import UUID

from pydantic import BaseModel, Field

from auo_project.models.recipe_parameter_model import RecipeParameterBase


class RecipeBasicParameterInput(BaseModel):
    p001: str = Field(title="計畫編號")
    p002: str = Field(title="判讀醫師")
    p003: str = Field(title="檢測單位")
    p004: str = Field(title="檢測人員")
    p005: str = Field(title="檢測日期")
    p006: str = Field(title="問卷收案日期")
    p007: str = Field(title="脈診量測時間")
    p008: str = Field(title="脈波通過率")
    s001: str = Field(title="教育程度")
    s002: str = Field(title="習慣用語")
    s003: str = Field(title="婚姻狀況")
    # s004: str = Field(title="生活作息")
    s005: str = Field(title="主要工作/上課時間")
    s006: str = Field(title="經常熬夜")
    s007: str = Field(title="每週運動超過30分鐘次數")
    s008: str = Field(title="精神壓力")
    # s009: str = Field(title="飲食習慣")
    s010: str = Field(title="喜歡口味")
    s011: str = Field(title="每週食用冰品頻率")
    s012: str = Field(title="每週食用油炸食物頻率")
    s013: str = Field(title="喜歡的咖啡因飲品")
    s014: str = Field(title="每週飲用含咖啡因飲品頻率")
    # s015: str = Field(title="個人史")
    s016: str = Field(title="抽菸頻率")
    s017: str = Field(title="每週喝酒頻率")
    s018: str = Field(title="每週嚼檳榔頻率")
    # s019: str = Field(title="自我評量")
    s020: str = Field(title="對健康狀態打分")
    s021: str = Field(title="自覺健康狀態")
    s022: str = Field(title="節律標記")
    # s023: str = Field(title="量測當日生活及身體狀況")
    s024: str = Field(title="是否熬夜")
    s025: str = Field(title="睡眠時間")
    s026: str = Field(title="距最近1次用餐時間")
    s027: str = Field(title="最近1次進食食物溫度")
    s028: str = Field(title="前4小時內是否飲用咖啡因飲品")
    s029: str = Field(title="前4小時內是否食用含酒精飲食")
    s030: str = Field(title="前4小時內是否有運動")
    s031: str = Field(title="前4小時內最近1次運動時數")
    s032: str = Field(title="今日是否有感冒症狀")
    s033: str = Field(title="距離已感冒的天數")
    s034: str = Field(title="24小時內是否服用藥物")
    s035: str = Field(title="接種幾次COVID-19疫苗")
    s036: str = Field(title="感染幾次COVID-19")
    s037: str = Field(title="確診COVID-19距離測量日天數")
    # s038: str = Field(title="女性專屬問項")
    s039: str = Field(title="是否仍有月經")
    s040: str = Field(title="距離上次月經天數")
    s041: str = Field(title="幾歲停經")
    s042: str = Field(title="目前是否懷孕")
    s043: str = Field(title="目前懷孕週數")
    # s044: str = Field(title="心情溫度計")
    s045: str = Field(title="總分")
    s046: str = Field(title="有自殺想法")


class RecipeAnalyticalParamsInput(BaseModel):
    a001: str = Field(title="檢測日期")
    a002: str = Field(title="介入因子")
    a003: str = Field(title="生理性別")
    a004: str = Field(title="年齡")
    a005: str = Field(title="身高")
    a006: str = Field(title="體重")
    a007: str = Field(title="BMI")
    a008: str = Field(title="疾病史")
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
    a024: str = Field(title="因上述疾病三個月內持續用藥")
    a025: str = Field(title="BCQ得分（正規化）")
    a026: str = Field(title="BCQ得分")
    a027: str = Field(title="二十八脈")
    a028: str = Field(title="血壓")
    a029: str = Field(title="血型")
    a030: str = Field(title="居住縣/市")
    # a031: str = Field(title="匹茲堡睡眠量表")
    a032: str = Field(title="總分")
    a033: str = Field(title="睡眠品質")
    a034: str = Field(title="睡眠潛伏期")
    a035: str = Field(title="睡眠總時數")
    a036: str = Field(title="睡眠效率")
    a037: str = Field(title="睡眠障礙")
    a038: str = Field(title="安眠藥物使用")
    a039: str = Field(title="日間功能障礙")


class RecipeParameterBaseRead(RecipeParameterBase):
    id: UUID


class RecipeParameterRead(RecipeParameterBaseRead):
    pass


class RecipeParameterCreate(RecipeParameterBase):
    pass


class RecipeParameterUpdate(BaseModel):
    value: str = None
