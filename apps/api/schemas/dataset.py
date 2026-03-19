"""Pydantic request/response schemas for dataset endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ColumnProfileSchema(BaseModel):
    name: str
    data_type: str
    null_count: int
    null_pct: float
    distinct_count: int
    is_numeric: bool
    is_date: bool
    is_bool: bool
    min_value: str | None = None
    max_value: str | None = None
    sample_values: list[str] = []


class DatasetProfileSchema(BaseModel):
    row_count: int
    column_count: int
    columns: list[ColumnProfileSchema]


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    original_filename: str
    file_format: str
    row_count: int | None = None
    column_count: int | None = None
    profile: DatasetProfileSchema | None = None
    created_at: datetime


class DatasetListResponse(BaseModel):
    datasets: list[DatasetResponse]
    total: int


class RowsResponse(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    total_returned: int
