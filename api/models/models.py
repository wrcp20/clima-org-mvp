from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, UniqueConstraint
from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class Employee(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    token_hash: str = Field(unique=True, index=True)
    department: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Survey(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    status: str = Field(default="draft")
    campaign_date: date
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Response(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("survey_id", "token_hash"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    survey_id: UUID = Field(foreign_key="survey.id")
    token_hash: str = Field(foreign_key="employee.token_hash")
    department: str
    answers: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class Score(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    survey_id: UUID = Field(foreign_key="survey.id")
    token_hash: str = Field(foreign_key="employee.token_hash")
    department: str
    exhaustion_score: int
    depersonalization_score: int
    personal_achievement_score: int
    climate_score: float
    risk_level: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Alert(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    department: str
    score_type: str
    value: float
    threshold: float
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    seen: bool = Field(default=False)
