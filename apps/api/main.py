"""MetricAnchor API — entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from db import get_session, init_db
from deps import get_query_engine
from routers import datasets, health, questions, semantic_models
from services.ingest import IngestService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    # Ensure data directories exist
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    (Path(settings.data_dir) / "uploads").mkdir(exist_ok=True)

    # Initialise SQLite tables
    await init_db()

    # Re-register all dataset views in DuckDB after restart
    engine = get_query_engine()
    async for db in get_session():
        svc = IngestService(db=db, engine=engine)
        await svc.restore_all_views()
        break

    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="MetricAnchor API",
        description=(
            "Trust-first AI analytics copilot. "
            "Every answer shows its SQL, assumptions, term mappings, and confidence."
        ),
        version="0.2.0",
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
