from typing import Any, Dict, List
from uuid import UUID

from pydantic import BaseModel, Field, validator

from auo_project.models.measure_bcq_model import BCQBase


class BCQRead(BCQBase):
    id: UUID


class BCQCreate(BCQBase):
    pass


class BCQUpdate(BCQBase):
    pass


class QuestionItem(BaseModel):
    id: int
    question: str
    options: List[Dict[str, Any]]


class BCQQuestionList(BaseModel):
    data: List[QuestionItem]


class BCQTypeInferenceInput(BaseModel):
    user_id: str
    age: float = Field(gt=0, title="年齡（可以有小數點）", example=30)
    sex: str = Field(min_length=1, max_length=1, title="生理性別: M/F", example="M")
    height: float = Field(gt=0, title="身高 cm", example=170.5)
    weight: float = Field(gt=0, title="體重 kg", example=60.3)
    answers: Dict[str, int] = Field(
        example={
            "4": 1,
            "5": 1,
            "8": 1,
            "11": 1,
            "12": 1,
            "13": 1,
            "14": 1,
            "15": 1,
            "16": 1,
            "17": 1,
            "22": 1,
            "24": 1,
            "26": 1,
        },
    )

    @validator("age", pre=True)
    def validate_age(cls, v):
        if v < 0:
            raise ValueError("age must be positive")
        return v

    @validator("sex", pre=True)
    def validate_sex(cls, v):
        if v not in ["M", "F"]:
            raise ValueError("sex must be M or F")
        return v

    @validator("answers", pre=True)
    def validate_answers(cls, v):
        if not all(isinstance(v, int) and v >= 1 and v <= 5 for v in v.values()):
            raise ValueError("answer must be 1-5")
        return v


class BCQTypeInferenceOuput(BaseModel):
    yang_type: int = Field(title="陽虛; 0: 正常; 1: 傾向; 2: 具有體質")
    yin_type: int = Field(title="陰虛; 0: 正常; 1: 傾向; 2: 具有體質")
    phlegm_type: int = Field(title="痰瘀; 0: 正常; 1: 傾向; 2: 具有體質")
    yang_score: float = Field(title="陽虛得分")
    yin_score: float = Field(title="陰虛得分")
    phlegm_score: float = Field(title="痰瘀得分")
