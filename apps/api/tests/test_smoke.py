"""Smoke tests — verify the API starts and all core routes respond correctly."""

import pytest
from httpx import ASGITransport, AsyncClient


def _clear_singletons():
    from config import get_settings
    from db import reset_engine
    from deps import get_query_engine
    get_settings.cache_clear()
    get_query_engine.cache_clear()
    reset_engine()


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{data_dir}/smoke.db")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    _clear_singletons()
    yield
    _clear_singletons()


@pytest.fixture
async def client():
    from db import init_db
    from main import create_app
    await init_db()
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_health_returns_ok(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "metricanchor-api"
    assert "timestamp" in body
    assert "version" in body


async def test_datasets_list_returns_200(client):
    response = await client.get("/api/datasets")
    assert response.status_code == 200
    assert "datasets" in response.json()


async def test_semantic_models_list_returns_200(client):
    response = await client.get("/api/semantic_models")
    assert response.status_code == 200
    assert "semantic_models" in response.json()


async def test_questions_list_returns_200(client):
    response = await client.get("/api/questions")
    assert response.status_code == 200
    assert "questions" in response.json()


async def test_openapi_schema_is_served(client):
    response = await client.get("/api/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "MetricAnchor API"
