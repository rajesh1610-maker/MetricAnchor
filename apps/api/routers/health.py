"""Health check endpoint."""

from __future__ import annotations

import sys
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from config import get_settings

router = APIRouter(tags=["health"])

_START_TIME = datetime.now(timezone.utc)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    uptime_seconds: int
    llm_provider: str
    llm_model: str
    llm_live: bool
    python_version: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description=(
        "Returns API health status and runtime configuration. "
        "`llm_live=false` means the API key is missing or is the test stub — "
        "the pipeline will use rule-based parsing and templated answers."
    ),
)
async def health() -> HealthResponse:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    llm_live = bool(settings.llm_api_key and settings.llm_api_key not in ("", "test-key"))
    return HealthResponse(
        status="ok",
        service="metricanchor-api",
        version="0.3.0",
        timestamp=now.isoformat(),
        uptime_seconds=int((now - _START_TIME).total_seconds()),
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
        llm_live=llm_live,
        python_version=sys.version.split()[0],
    )
