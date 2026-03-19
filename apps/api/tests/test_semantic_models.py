"""
Integration tests for semantic model CRUD, validation, and YAML export.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

VALID_DEFINITION = {
    "name": "retail_sales",
    "dataset": "retail_sales",
    "description": "Retail order analytics",
    "time_column": "order_date",
    "grain": "one row = one order",
    "metrics": [
        {
            "name": "revenue",
            "description": "Total completed order value",
            "expression": "SUM(order_total)",
            "filters": [{"column": "status", "operator": "=", "value": "completed"}],
            "aliases": ["sales", "total revenue"],
            "format": "currency",
        }
    ],
    "dimensions": [
        {
            "name": "product_category",
            "column": "product_category",
            "description": "Product category",
            "aliases": ["category"],
        }
    ],
}

INVALID_DEFINITION_NO_METRICS = {
    "name": "broken",
    "dataset": "retail_sales",
    "metrics": [],  # minItems: 1 — fails
}

INVALID_DEFINITION_BAD_SYNONYM = {
    "name": "broken",
    "dataset": "retail_sales",
    "metrics": [{"name": "revenue", "expression": "SUM(order_total)"}],
    "synonyms": [{"phrase": "sales", "maps_to": "metric:no_such_metric"}],
}


# ── Fixtures ───────────────────────────────────────────────────────────────────

def _clear_singletons():
    from config import get_settings
    from db import reset_engine
    get_settings.cache_clear()
    reset_engine()


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{data_dir}/test.db")
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


# ── Create tests ───────────────────────────────────────────────────────────────

async def test_create_valid_model_returns_201(client):
    response = await client.post(
        "/api/semantic_models",
        json={"dataset_id": "ds-1", "name": "retail_sales", "definition": VALID_DEFINITION},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "retail_sales"
    assert body["dataset_id"] == "ds-1"
    assert body["definition"]["metrics"][0]["name"] == "revenue"


async def test_create_invalid_model_returns_422(client):
    response = await client.post(
        "/api/semantic_models",
        json={"dataset_id": "ds-1", "name": "broken", "definition": INVALID_DEFINITION_NO_METRICS},
    )
    assert response.status_code == 422


async def test_create_model_with_bad_synonym_returns_422(client):
    response = await client.post(
        "/api/semantic_models",
        json={"dataset_id": "ds-1", "name": "broken", "definition": INVALID_DEFINITION_BAD_SYNONYM},
    )
    assert response.status_code == 422
    assert "no_such_metric" in response.json()["detail"]


# ── List / detail tests ────────────────────────────────────────────────────────

async def test_list_returns_empty_initially(client):
    response = await client.get("/api/semantic_models")
    assert response.status_code == 200
    assert response.json() == {"semantic_models": [], "total": 0}


async def test_list_returns_created_model(client):
    await client.post(
        "/api/semantic_models",
        json={"dataset_id": "ds-1", "name": "retail_sales", "definition": VALID_DEFINITION},
    )
    response = await client.get("/api/semantic_models")
    assert response.json()["total"] == 1


async def test_list_filters_by_dataset_id(client):
    await client.post(
        "/api/semantic_models",
        json={"dataset_id": "ds-1", "name": "retail_sales", "definition": VALID_DEFINITION},
    )
    response = await client.get("/api/semantic_models?dataset_id=ds-1")
    assert response.json()["total"] == 1

    response = await client.get("/api/semantic_models?dataset_id=ds-99")
    assert response.json()["total"] == 0


async def test_get_returns_full_definition(client):
    created = await client.post(
        "/api/semantic_models",
        json={"dataset_id": "ds-1", "name": "retail_sales", "definition": VALID_DEFINITION},
    )
    model_id = created.json()["id"]

    response = await client.get(f"/api/semantic_models/{model_id}")
    assert response.status_code == 200
    assert response.json()["id"] == model_id


async def test_get_not_found_returns_404(client):
    response = await client.get("/api/semantic_models/no-such-id")
    assert response.status_code == 404


# ── Update tests ───────────────────────────────────────────────────────────────

async def test_update_model_succeeds(client):
    created = await client.post(
        "/api/semantic_models",
        json={"dataset_id": "ds-1", "name": "retail_sales", "definition": VALID_DEFINITION},
    )
    model_id = created.json()["id"]

    updated_def = {**VALID_DEFINITION, "description": "Updated description"}
    response = await client.put(
        f"/api/semantic_models/{model_id}",
        json={"definition": updated_def},
    )
    assert response.status_code == 200
    assert response.json()["definition"]["description"] == "Updated description"


async def test_update_with_invalid_definition_returns_422(client):
    created = await client.post(
        "/api/semantic_models",
        json={"dataset_id": "ds-1", "name": "retail_sales", "definition": VALID_DEFINITION},
    )
    model_id = created.json()["id"]

    response = await client.put(
        f"/api/semantic_models/{model_id}",
        json={"definition": INVALID_DEFINITION_NO_METRICS},
    )
    assert response.status_code == 422


# ── Validation endpoint tests ──────────────────────────────────────────────────

async def test_validate_valid_definition_returns_valid_true(client):
    response = await client.post("/api/semantic_models/validate", json=VALID_DEFINITION)
    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["errors"] == []


async def test_validate_invalid_definition_returns_valid_false(client):
    response = await client.post(
        "/api/semantic_models/validate", json=INVALID_DEFINITION_NO_METRICS
    )
    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert len(response.json()["errors"]) > 0


# ── Delete tests ───────────────────────────────────────────────────────────────

async def test_delete_model_returns_204(client):
    created = await client.post(
        "/api/semantic_models",
        json={"dataset_id": "ds-1", "name": "retail_sales", "definition": VALID_DEFINITION},
    )
    model_id = created.json()["id"]

    response = await client.delete(f"/api/semantic_models/{model_id}")
    assert response.status_code == 204

    response = await client.get(f"/api/semantic_models/{model_id}")
    assert response.status_code == 404


# ── YAML export tests ──────────────────────────────────────────────────────────

async def test_export_yaml_returns_valid_yaml(client):
    created = await client.post(
        "/api/semantic_models",
        json={"dataset_id": "ds-1", "name": "retail_sales", "definition": VALID_DEFINITION},
    )
    model_id = created.json()["id"]

    response = await client.get(f"/api/semantic_models/{model_id}/export")
    assert response.status_code == 200
    assert "revenue" in response.text
    assert "SUM(order_total)" in response.text
