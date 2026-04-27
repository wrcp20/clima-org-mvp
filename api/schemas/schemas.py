from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator


class SurveyCreate(BaseModel):
    title: str
    campaign_date: date


class SurveyStatusUpdate(BaseModel):
    status: str

    @model_validator(mode="after")
    def validate_status(self):
        valid = {"draft", "active", "closed"}
        if self.status not in valid:
            raise ValueError(f"status must be one of {valid}")
        return self


class SurveyRead(BaseModel):
    id: UUID
    title: str
    status: str
    campaign_date: date
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenGenerateRequest(BaseModel):
    department: str
    count: int

    @model_validator(mode="after")
    def validate_count(self):
        if self.count < 1 or self.count > 500:
            raise ValueError("count must be between 1 and 500")
        return self


class TokenGenerateResponse(BaseModel):
    tokens: list[str]
    department: str
    count: int


class SurveySubmitRequest(BaseModel):
    answers: dict[str, int]

    @model_validator(mode="after")
    def validate_answers(self):
        required = {f"q{i}" for i in range(1, 29)}
        missing = required - self.answers.keys()
        if missing:
            raise ValueError(f"Missing answer keys: {sorted(missing)}")
        for q in [f"q{i}" for i in range(1, 23)]:   # q1-q22 MBI: 0-6
            if not 0 <= self.answers[q] <= 6:
                raise ValueError(f"{q} must be between 0 and 6")
        for q in [f"q{i}" for i in range(23, 29)]:  # q23-q28 climate: 1-5
            if not 1 <= self.answers[q] <= 5:
                raise ValueError(f"{q} must be between 1 and 5")
        return self


class ScoreRead(BaseModel):
    id: UUID
    survey_id: UUID
    department: str
    exhaustion_score: int
    depersonalization_score: int
    personal_achievement_score: int
    climate_score: float
    risk_level: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DepartmentAggregation(BaseModel):
    department: str
    avg_exhaustion: float
    avg_depersonalization: float
    avg_achievement: float
    avg_climate: float
    count: int
    dominant_risk: str


class AlertRead(BaseModel):
    id: UUID
    department: str
    score_type: str
    value: float
    threshold: float
    triggered_at: datetime
    seen: bool

    model_config = {"from_attributes": True}


class ResponseSummary(BaseModel):
    department: str
    response_count: int
