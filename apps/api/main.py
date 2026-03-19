"""MetricAnchor API — entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from db import init_db
from routers import datasets, health, questions, semantic_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise database tables on startup."""
    await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="MetricAnchor API",
        description=(
            "Trust-first AI analytics copilot. "
            "Every answer shows its SQL, assumptions, term mappings, and confidence."
        ),
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(datasets.router, prefix="/api")
    app.include_router(semantic_models.router, prefix="/api")
    app.include_router(questions.router, prefix="/api")

    return app


app = create_app()
