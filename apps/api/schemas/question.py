"""Pydantic schemas for the Q&A endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class QuestionCreate(BaseModel):
    question: str
    dataset_id: str
    model_id: str | None = None  # if omitted, the most recent model for the dataset is used

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("question must not be empty")
        return v


class FeedbackCreate(BaseModel):
    feedback_type: str  # wrong | partial | correct
    note: str | None = None

    @field_validator("feedback_type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        allowed = {"wrong", "partial", "correct"}
        if v not in allowed:
            raise ValueError(f"feedback_type must be one of {allowed}")
        return v


class SemanticMappingSchema(BaseModel):
    phrase: str
    resolved_to: str
    resolved_name: str
    type: str
    via: str


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dataset_id: str
    question: str
    answer: str | None = None
    sql: str | None = None
    columns: list[str] = []
    rows: list[list[Any]] = []
    row_count: int = 0
    chart_type: str | None = None
    semantic_mappings: list[dict] = []
    assumptions: list[str] = []
    caveats: list[str] = []
    confidence: str | None = None
    confidence_note: str | None = None
    clarifying_question: str | None = None
    provenance: dict | None = None
    execution_ms: int | None = None
    error: str | None = None
    created_at: datetime


class QuestionListResponse(BaseModel):
    questions: list[QuestionResponse]
    total: int


class FeedbackResponse(BaseModel):
    id: str
    question_id: str
    feedback_type: str
    note: str | None
    created_at: datetime
