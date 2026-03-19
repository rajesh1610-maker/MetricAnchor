"""
IngestService — file upload, validation, profiling, and persistence.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from packages.query_engine import QueryEngine, sanitize_view_name

from config import get_settings
from models import Dataset
from schemas.dataset import ColumnProfileSchema, DatasetProfileSchema, DatasetResponse

_ALLOWED_EXTENSIONS = {".csv", ".parquet"}


class UploadValidationError(Exception):
    def __init__(self, message: str, status_code: int = 422):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class IngestService:
    def __init__(self, db: AsyncSession, engine: QueryEngine) -> None:
        self._db = db
        self._engine = engine

    async def upload(self, file: UploadFile) -> DatasetResponse:
        settings = get_settings()

        # ── 1. Validate file type ───────────────────────────────────────────
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in _ALLOWED_EXTENSIONS:
            raise UploadValidationError(
                f"Unsupported file type '{suffix}'. Upload a .csv or .parquet file.",
                status_code=415,
            )

        # ── 2. Read and validate file size ──────────────────────────────────
        contents = await file.read()
        if len(contents) > settings.max_upload_bytes:
            mb = settings.max_upload_bytes // 1_048_576
            raise UploadValidationError(
                f"File exceeds the {mb} MB upload limit.", status_code=413
            )

        # ── 3. Save to disk ─────────────────────────────────────────────────
        dataset_id = str(uuid.uuid4())
        upload_dir = Path(settings.data_dir) / "uploads" / dataset_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        original_filename = file.filename or f"upload{suffix}"
        file_path = upload_dir / original_filename
        file_path.write_bytes(contents)

        # ── 4. Register in DuckDB and compute profile ───────────────────────
        # Use sanitized name; CREATE OR REPLACE VIEW handles duplicates cleanly.
        view_name = sanitize_view_name(original_filename)
        profile = await self._engine.register_dataset(view_name, str(file_path))

        # ── 5. Persist metadata in SQLite ───────────────────────────────────
        column_schemas = [
            ColumnProfileSchema(
                name=c.name,
                data_type=c.data_type,
                null_count=c.null_count,
                null_pct=c.null_pct,
                distinct_count=c.distinct_count,
                is_numeric=c.is_numeric,
                is_date=c.is_date,
                is_bool=c.is_bool,
                min_value=c.min_value,
                max_value=c.max_value,
                sample_values=c.sample_values,
            )
            for c in profile.columns
        ]

        profile_schema = DatasetProfileSchema(
            row_count=profile.row_count,
            column_count=profile.column_count,
            columns=column_schemas,
        )

        dataset = Dataset(
            id=dataset_id,
            name=view_name,
            original_filename=original_filename,
            file_path=str(file_path),
            file_format=suffix.lstrip("."),
            row_count=profile.row_count,
            column_count=profile.column_count,
            profile=profile_schema.model_dump(),
        )
        self._db.add(dataset)
        await self._db.commit()
        await self._db.refresh(dataset)

        return _to_response(dataset)

    async def list_datasets(self) -> list[DatasetResponse]:
        result = await self._db.execute(
            select(Dataset).order_by(Dataset.created_at.desc())
        )
        return [_to_response(d) for d in result.scalars().all()]

    async def get_dataset(self, dataset_id: str) -> DatasetResponse | None:
        result = await self._db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        dataset = result.scalar_one_or_none()
        return _to_response(dataset) if dataset else None

    async def get_rows(
        self, dataset_id: str, limit: int = 100, offset: int = 0
    ) -> tuple[list[str], list[list]] | None:
        result = await self._db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        dataset = result.scalar_one_or_none()
        if dataset is None:
            return None
        return await self._engine.sample_rows(dataset.name, limit=limit, offset=offset)

    async def restore_all_views(self) -> None:
        """Re-register all dataset views in DuckDB after a server restart."""
        result = await self._db.execute(select(Dataset))
        for dataset in result.scalars().all():
            await self._engine.restore_view(dataset.name, dataset.file_path)


def _to_response(d: Dataset) -> DatasetResponse:
    profile = DatasetProfileSchema(**d.profile) if d.profile else None
    return DatasetResponse(
        id=d.id,
        name=d.name,
        original_filename=d.original_filename,
        file_format=d.file_format,
        row_count=d.row_count,
        column_count=d.column_count,
        profile=profile,
        created_at=d.created_at,
    )
