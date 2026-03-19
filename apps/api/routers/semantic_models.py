"""Semantic model endpoints — CRUD, validation, and YAML export."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from schemas.semantic_model import (
    SemanticModelCreate,
    SemanticModelListResponse,
    SemanticModelResponse,
    SemanticModelUpdate,
    ValidationResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from services.semantic_model_service import SemanticModelService

router = APIRouter(prefix="/semantic_models", tags=["semantic_models"])


def _service(db: AsyncSession = Depends(get_session)) -> SemanticModelService:
    return SemanticModelService(db=db)


@router.get(
    "",
    response_model=SemanticModelListResponse,
    summary="List semantic models",
)
async def list_semantic_models(
    dataset_id: str | None = Query(None, description="Filter by dataset ID"),
    svc: SemanticModelService = Depends(_service),
):
    models = await svc.list(dataset_id=dataset_id)
    return SemanticModelListResponse(semantic_models=models, total=len(models))


@router.post(
    "",
    response_model=SemanticModelResponse,
    status_code=201,
    summary="Create a semantic model",
)
async def create_semantic_model(
    payload: SemanticModelCreate,
    svc: SemanticModelService = Depends(_service),
):
    """
    Create a new semantic model for a dataset.

    The `definition` field must conform to the MetricAnchor semantic model schema.
    Validation is run before saving. Invalid models are rejected with a 422 response.
    """
    try:
        return await svc.create(payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from None


@router.get(
    "/{model_id}",
    response_model=SemanticModelResponse,
    summary="Get a semantic model",
)
async def get_semantic_model(
    model_id: str,
    svc: SemanticModelService = Depends(_service),
):
    model = await svc.get(model_id)
    if model is None:
        raise HTTPException(status_code=404, detail=f"Semantic model '{model_id}' not found.")
    return model


@router.put(
    "/{model_id}",
    response_model=SemanticModelResponse,
    summary="Update a semantic model",
)
async def update_semantic_model(
    model_id: str,
    payload: SemanticModelUpdate,
    svc: SemanticModelService = Depends(_service),
):
    try:
        model = await svc.update(model_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from None

    if model is None:
        raise HTTPException(status_code=404, detail=f"Semantic model '{model_id}' not found.")
    return model


@router.delete(
    "/{model_id}",
    status_code=204,
    summary="Delete a semantic model",
)
async def delete_semantic_model(
    model_id: str,
    svc: SemanticModelService = Depends(_service),
):
    deleted = await svc.delete(model_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Semantic model '{model_id}' not found.")


@router.post(
    "/validate",
    response_model=ValidationResponse,
    summary="Validate a semantic model definition without saving",
)
async def validate_semantic_model(
    definition: dict,
    svc: SemanticModelService = Depends(_service),
):
    """
    Validate a semantic model definition against the JSON schema and semantic rules.
    Returns validation errors and warnings without persisting anything.
    """
    return await svc.validate(definition)


@router.get(
    "/{model_id}/export",
    response_class=PlainTextResponse,
    summary="Export a semantic model as YAML",
)
async def export_semantic_model(
    model_id: str,
    svc: SemanticModelService = Depends(_service),
):
    yaml_text = await svc.export_yaml(model_id)
    if yaml_text is None:
        raise HTTPException(status_code=404, detail=f"Semantic model '{model_id}' not found.")
    return PlainTextResponse(yaml_text, media_type="text/yaml")
