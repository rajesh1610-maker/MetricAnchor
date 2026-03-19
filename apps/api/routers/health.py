"""Health check endpoint."""

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
async def health():
    return {
        "status": "ok",
        "service": "metricanchor-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
    }
