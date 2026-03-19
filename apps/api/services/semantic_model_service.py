"""
SemanticModelService — CRUD and validation for semantic models.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from packages.semantic_model import SemanticModelValidator

from models import SemanticModel
from schemas.semantic_model import (
    SemanticModelCreate,
    SemanticModelListResponse,
    SemanticModelResponse,
    SemanticModelUpdate,
    ValidationResponse,
)

_validator = SemanticModelValidator()


class SemanticModelService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── CRUD ───────────────────────────────────────────────────────────────────

    async def create(self, payload: SemanticModelCreate) -> SemanticModelResponse:
        result = _validator.validate(payload.definition)
        if not result.valid:
            raise ValueError(f"Invalid semantic model: {'; '.join(result.errors)}")

        model = SemanticModel(
            dataset_id=payload.dataset_id,
            name=payload.name,
            definition=payload.definition,
        )
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return _to_response(model)

    async def list(self, dataset_id: str | None = None) -> list[SemanticModelResponse]:
        stmt = select(SemanticModel).order_by(SemanticModel.created_at.desc())
        if dataset_id:
            stmt = stmt.where(SemanticModel.dataset_id == dataset_id)
        result = await self._db.execute(stmt)
        return [_to_response(m) for m in result.scalars().all()]

    async def get(self, model_id: str) -> SemanticModelResponse | None:
        result = await self._db.execute(
            select(SemanticModel).where(SemanticModel.id == model_id)
        )
        m = result.scalar_one_or_none()
        return _to_response(m) if m else None

    async def get_for_dataset(self, dataset_id: str) -> SemanticModelResponse | None:
        """Return the most recent semantic model for a dataset, or None."""
        result = await self._db.execute(
            select(SemanticModel)
            .where(SemanticModel.dataset_id == dataset_id)
            .order_by(SemanticModel.updated_at.desc())
            .limit(1)
        )
        m = result.scalar_one_or_none()
        return _to_response(m) if m else None

    async def update(
        self, model_id: str, payload: SemanticModelUpdate
    ) -> SemanticModelResponse | None:
        result = await self._db.execute(
            select(SemanticModel).where(SemanticModel.id == model_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None

        validation = _validator.validate(payload.definition)
        if not validation.valid:
            raise ValueError(f"Invalid semantic model: {'; '.join(validation.errors)}")

        model.definition = payload.definition
        model.name = payload.definition.get("name", model.name)
        await self._db.commit()
        await self._db.refresh(model)
        return _to_response(model)

    async def delete(self, model_id: str) -> bool:
        result = await self._db.execute(
            select(SemanticModel).where(SemanticModel.id == model_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._db.delete(model)
        await self._db.commit()
        return True

    # ── Validation ─────────────────────────────────────────────────────────────

    async def validate(self, definition: dict) -> ValidationResponse:
        result = _validator.validate(definition)
        return ValidationResponse(
            valid=result.valid,
            errors=result.errors,
            warnings=result.warnings,
        )

    # ── Export ─────────────────────────────────────────────────────────────────

    async def export_yaml(self, model_id: str) -> str | None:
        response = await self.get(model_id)
        if response is None:
            return None
        return yaml.dump(response.definition, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _to_response(m: SemanticModel) -> SemanticModelResponse:
    return SemanticModelResponse(
        id=m.id,
        dataset_id=m.dataset_id,
        name=m.name,
        definition=m.definition,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )
