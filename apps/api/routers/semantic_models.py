"""Semantic model endpoints. (Stub for Phase 1; implemented in Phase 3.)"""

from fastapi import APIRouter

router = APIRouter(prefix="/semantic_models", tags=["semantic_models"])


@router.get("", summary="List semantic models")
async def list_semantic_models():
    return {"semantic_models": [], "message": "Semantic models are implemented in Phase 3."}


@router.post("", summary="Create a semantic model", status_code=202)
async def create_semantic_model():
    return {"message": "Semantic model creation is implemented in Phase 3."}
