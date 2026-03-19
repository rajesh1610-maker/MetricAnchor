"""
DuckDB-backed query engine.

Registers uploaded files as persistent views in a DuckDB database file,
then runs SQL against them. Thread-safe via a module-level lock.
"""

from __future__ import annotations

import asyncio
import re
import threading
from pathlib import Path

import duckdb

from .profiler import DatasetProfile, profile_dataset


class QueryEngine:
    """Wraps a persistent DuckDB connection for dataset registration and querying."""

    _lock: threading.Lock = threading.Lock()

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._conn: duckdb.DuckDBPyConnection | None = None

    # ── Internal sync methods (run inside asyncio.to_thread) ─────────────────

    def _connect(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = duckdb.connect(self._db_path)
        return self._conn

    def _register_sync(self, view_name: str, file_path: str) -> DatasetProfile:
        with self._lock:
            conn = self._connect()
            safe_view = f'"{view_name}"'
            conn.execute(
                f"CREATE OR REPLACE VIEW {safe_view} AS SELECT * FROM '{file_path}'"
            )
            return profile_dataset(conn, view_name)

    def _run_sync(self, sql: str) -> tuple[list[str], list[list]]:
        with self._lock:
            conn = self._connect()
            result = conn.execute(sql)
            columns = [desc[0] for desc in result.description]  # type: ignore[union-attr]
            rows = result.fetchall()
            return columns, [list(row) for row in rows]

    def _sample_sync(self, view_name: str, limit: int, offset: int) -> tuple[list[str], list[list]]:
        safe_view = f'"{view_name}"'
        sql = f"SELECT * FROM {safe_view} LIMIT {limit} OFFSET {offset}"
        return self._run_sync(sql)

    def _restore_sync(self, view_name: str, file_path: str) -> None:
        """Re-register a view without re-profiling (used on server restart)."""
        if not Path(file_path).exists():
            return
        with self._lock:
            conn = self._connect()
            safe_view = f'"{view_name}"'
            conn.execute(
                f"CREATE OR REPLACE VIEW {safe_view} AS SELECT * FROM '{file_path}'"
            )

    # ── Public async API ──────────────────────────────────────────────────────

    async def register_dataset(self, view_name: str, file_path: str) -> DatasetProfile:
        """Register a CSV/Parquet file as a DuckDB view and return its profile."""
        return await asyncio.to_thread(self._register_sync, view_name, file_path)

    async def sample_rows(
        self, view_name: str, limit: int = 100, offset: int = 0
    ) -> tuple[list[str], list[list]]:
        """Return (columns, rows) for the first N rows of a dataset."""
        return await asyncio.to_thread(self._sample_sync, view_name, limit, offset)

    async def run(self, sql: str) -> tuple[list[str], list[list]]:
        """Execute arbitrary SQL and return (columns, rows)."""
        return await asyncio.to_thread(self._run_sync, sql)

    async def restore_view(self, view_name: str, file_path: str) -> None:
        """Re-register a view after a server restart without re-profiling."""
        await asyncio.to_thread(self._restore_sync, view_name, file_path)


# ── Name sanitisation helper ──────────────────────────────────────────────────

def sanitize_view_name(filename: str) -> str:
    """Turn a filename into a valid, lowercase DuckDB view name."""
    stem = Path(filename).stem
    name = re.sub(r"[^a-zA-Z0-9_]", "_", stem)
    name = re.sub(r"_+", "_", name).strip("_").lower()
    return name or "dataset"
