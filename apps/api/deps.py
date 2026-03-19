"""FastAPI dependency providers."""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.query_engine import QueryEngine

from config import get_settings


@lru_cache
def get_query_engine() -> QueryEngine:
    """Singleton QueryEngine — one DuckDB connection per process."""
    settings = get_settings()
    db_path = str(Path(settings.data_dir) / "analytics.duckdb")
    return QueryEngine(db_path=db_path)
