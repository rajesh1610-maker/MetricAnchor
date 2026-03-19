"""
Column-level data profiler using DuckDB.

Computes null %, distinct count, min/max for numeric/date columns,
and sample values for categorical columns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import duckdb


# DuckDB type name fragments → category
_NUMERIC = {"INT", "FLOAT", "DOUBLE", "DECIMAL", "NUMERIC", "REAL", "HUGEINT", "UBIGINT"}
_DATE = {"DATE", "TIMESTAMP", "TIME", "INTERVAL"}
_BOOL = {"BOOL", "BOOLEAN"}


def _categorise(dtype: str) -> tuple[bool, bool, bool]:
    """Return (is_numeric, is_date, is_bool) for a DuckDB type string."""
    upper = dtype.upper()
    is_numeric = any(t in upper for t in _NUMERIC)
    is_date = any(t in upper for t in _DATE)
    is_bool = any(t in upper for t in _BOOL)
    return is_numeric, is_date, is_bool


def _safe(col: str) -> str:
    """Quote a column name for use in SQL."""
    return f'"{col}"'


@dataclass
class ColumnProfile:
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
    sample_values: list[str] = field(default_factory=list)


@dataclass
class DatasetProfile:
    row_count: int
    column_count: int
    columns: list[ColumnProfile]


def profile_dataset(conn: duckdb.DuckDBPyConnection, view_name: str) -> DatasetProfile:
    """Compute a full profile of a registered DuckDB view."""
    safe_view = f'"{view_name}"'

    # Schema
    schema_rows = conn.execute(f"DESCRIBE {safe_view}").fetchall()
    # DuckDB DESCRIBE → (column_name, column_type, null, key, default, extra)

    # Total row count
    total = conn.execute(f"SELECT COUNT(*) FROM {safe_view}").fetchone()[0]  # type: ignore[index]

    columns: list[ColumnProfile] = []

    for row in schema_rows:
        col_name: str = row[0]
        col_type: str = row[1]
        is_numeric, is_date, is_bool = _categorise(col_type)
        safe_col = _safe(col_name)

        # Null count + distinct count in one pass
        stats = conn.execute(
            f"SELECT COUNT(*) - COUNT({safe_col}), COUNT(DISTINCT {safe_col}) FROM {safe_view}"
        ).fetchone()
        null_count: int = stats[0]  # type: ignore[index]
        distinct_count: int = stats[1]  # type: ignore[index]
        null_pct = round(null_count / total * 100, 1) if total > 0 else 0.0

        min_value: str | None = None
        max_value: str | None = None

        if is_numeric or is_date:
            minmax = conn.execute(
                f"SELECT MIN({safe_col}), MAX({safe_col}) FROM {safe_view}"
            ).fetchone()
            min_value = str(minmax[0]) if minmax[0] is not None else None  # type: ignore[index]
            max_value = str(minmax[1]) if minmax[1] is not None else None  # type: ignore[index]

        # Sample values: up to 5 distinct non-null values
        sample_rows = conn.execute(
            f"SELECT DISTINCT {safe_col} FROM {safe_view} "
            f"WHERE {safe_col} IS NOT NULL LIMIT 5"
        ).fetchall()
        sample_values = [str(r[0]) for r in sample_rows]

        columns.append(
            ColumnProfile(
                name=col_name,
                data_type=col_type,
                null_count=null_count,
                null_pct=null_pct,
                distinct_count=distinct_count,
                is_numeric=is_numeric,
                is_date=is_date,
                is_bool=is_bool,
                min_value=min_value,
                max_value=max_value,
                sample_values=sample_values,
            )
        )

    return DatasetProfile(row_count=total, column_count=len(columns), columns=columns)
