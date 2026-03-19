"""FastAPI dependency providers."""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

_api_dir = Path(__file__).resolve().parent
_repo_root = _api_dir.parents[1] if len(_api_dir.parents) > 1 else _api_dir
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from packages.query_engine import QueryEngine

from config import get_settings


@lru_cache
def get_query_engine() -> QueryEngine:
    """Singleton QueryEngine — one DuckDB connection per process."""
    settings = get_settings()
    db_path = str(Path(settings.data_dir) / "analytics.duckdb")
    return QueryEngine(db_path=db_path)
