"""Pydantic request/response schemas for semantic model endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class FilterDef(BaseModel):
    column: str
    operator: str
    value: Any = None


class MetricDef(BaseModel):
    name: str
    description: str = ""
    expression: str
    filters: list[FilterDef] = []
    aliases: list[str] = []
    format: str = "number"
    unit: str = ""
    default_aggregation: str = "sum"


class DimensionDef(BaseModel):
    name: str
    column: str
    description: str = ""
    aliases: list[str] = []
    values: list[str] = []
    is_date: bool = False


class EntityDef(BaseModel):
    name: str
    column: str
    description: str = ""
    aliases: list[str] = []


class SynonymDef(BaseModel):
    phrase: str
    maps_to: str


class BusinessRuleDef(BaseModel):
    name: str
    description: str = ""
    filter: str
    applies_to: list[str] = []


class ExclusionDef(BaseModel):
    description: str
    filter: str = ""


class SemanticModelCreate(BaseModel):
    dataset_id: str
    name: str
    definition: dict  # The full model dict (matches the YAML schema)


class SemanticModelUpdate(BaseModel):
    definition: dict


class ValidationResponse(BaseModel):
    valid: bool
    errors: list[str] = []
    warnings: list[str] = []


class SemanticModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dataset_id: str
    name: str
    definition: dict
    created_at: datetime
    updated_at: datetime


class SemanticModelListResponse(BaseModel):
    semantic_models: list[SemanticModelResponse]
    total: int
