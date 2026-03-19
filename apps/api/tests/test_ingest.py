"""
Integration tests for the dataset ingestion layer.
Uses real DuckDB (temp file) and real SQLite.

Note: httpx.ASGITransport does not fire FastAPI's lifespan events,
so we call init_db() explicitly in fixtures before each test.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

MINIMAL_CSV = (
    b"id,name,amount,created_at\n"
    b"1,Alice,100.5,2025-01-01\n"
    b"2,Bob,200.0,2025-01-02\n"
    b"3,,300.0,2025-01-03\n"
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _clear_singletons():
    from config import get_settings
    from db import reset_engine
    from deps import get_query_engine
    get_settings.cache_clear()
    get_query_engine.cache_clear()
    reset_engine()


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """Fresh temp dirs + fresh singletons for every test."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{data_dir}/test.db")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "524288000")
    _clear_singletons()
    yield
    _clear_singletons()


@pytest.fixture
async def client():
    from db import init_db
    from main import create_app

    await init_db()  # ASGITransport skips lifespan, so we do this manually
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def tiny_limit_client(tmp_path, monkeypatch):
    """Client with a 10-byte upload limit for size-limit tests."""
    data_dir = tmp_path / "tiny"
    data_dir.mkdir()
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{data_dir}/test.db")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "10")
    _clear_singletons()

    from db import init_db
    from main import create_app

    await init_db()
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    _clear_singletons()


# ── Upload tests ───────────────────────────────────────────────────────────────

async def test_upload_csv_returns_201_with_profile(client):
    response = await client.post(
        "/api/datasets",
        files={"file": ("retail_sales.csv", MINIMAL_CSV, "text/csv")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "retail_sales"
    assert body["file_format"] == "csv"
    assert body["row_count"] == 3
    assert body["column_count"] == 4
    assert body["profile"] is not None
    assert len(body["profile"]["columns"]) == 4


async def test_upload_csv_profile_computes_null_pct(client):
    response = await client.post(
        "/api/datasets",
        files={"file": ("sales.csv", MINIMAL_CSV, "text/csv")},
    )
    assert response.status_code == 201
    columns = {c["name"]: c for c in response.json()["profile"]["columns"]}
    # "name" column has one null → 33.3 %
    assert columns["name"]["null_count"] == 1
    assert columns["name"]["null_pct"] == pytest.approx(33.3, abs=0.1)


async def test_upload_csv_profile_has_distinct_counts(client):
    response = await client.post(
        "/api/datasets",
        files={"file": ("sales.csv", MINIMAL_CSV, "text/csv")},
    )
    columns = {c["name"]: c for c in response.json()["profile"]["columns"]}
    assert columns["id"]["distinct_count"] == 3
    assert columns["amount"]["distinct_count"] == 3


async def test_upload_csv_numeric_column_has_min_max(client):
    response = await client.post(
        "/api/datasets",
        files={"file": ("sales.csv", MINIMAL_CSV, "text/csv")},
    )
    columns = {c["name"]: c for c in response.json()["profile"]["columns"]}
    assert columns["amount"]["min_value"] is not None
    assert columns["amount"]["max_value"] is not None


async def test_upload_csv_profile_has_sample_values(client):
    response = await client.post(
        "/api/datasets",
        files={"file": ("sales.csv", MINIMAL_CSV, "text/csv")},
    )
    columns = {c["name"]: c for c in response.json()["profile"]["columns"]}
    assert len(columns["name"]["sample_values"]) >= 1


async def test_upload_unsupported_type_returns_415(client):
    response = await client.post(
        "/api/datasets",
        files={"file": ("data.xlsx", b"fake xlsx", "application/vnd.ms-excel")},
    )
    assert response.status_code == 415
    assert "parquet" in response.json()["detail"].lower()


async def test_upload_oversized_file_returns_413(tiny_limit_client):
    response = await tiny_limit_client.post(
        "/api/datasets",
        files={"file": ("big.csv", MINIMAL_CSV, "text/csv")},
    )
    assert response.status_code == 413


# ── List / detail tests ────────────────────────────────────────────────────────

async def test_list_datasets_initially_empty(client):
    response = await client.get("/api/datasets")
    assert response.status_code == 200
    assert response.json() == {"datasets": [], "total": 0}


async def test_list_datasets_shows_uploaded_dataset(client):
    await client.post(
        "/api/datasets",
        files={"file": ("sales.csv", MINIMAL_CSV, "text/csv")},
    )
    response = await client.get("/api/datasets")
    body = response.json()
    assert body["total"] == 1
    assert body["datasets"][0]["name"] == "sales"


async def test_get_dataset_returns_full_profile(client):
    upload = await client.post(
        "/api/datasets",
        files={"file": ("sales.csv", MINIMAL_CSV, "text/csv")},
    )
    dataset_id = upload.json()["id"]
    response = await client.get(f"/api/datasets/{dataset_id}")
    assert response.status_code == 200
    assert response.json()["id"] == dataset_id
    assert response.json()["profile"]["row_count"] == 3


async def test_get_dataset_not_found_returns_404(client):
    response = await client.get("/api/datasets/does-not-exist")
    assert response.status_code == 404


# ── Sample rows tests ──────────────────────────────────────────────────────────

async def test_get_rows_returns_columns_and_data(client):
    upload = await client.post(
        "/api/datasets",
        files={"file": ("sales.csv", MINIMAL_CSV, "text/csv")},
    )
    dataset_id = upload.json()["id"]
    response = await client.get(f"/api/datasets/{dataset_id}/rows")
    assert response.status_code == 200
    body = response.json()
    assert body["columns"] == ["id", "name", "amount", "created_at"]
    assert body["total_returned"] == 3
    assert len(body["rows"]) == 3


async def test_get_rows_respects_limit(client):
    upload = await client.post(
        "/api/datasets",
        files={"file": ("sales.csv", MINIMAL_CSV, "text/csv")},
    )
    dataset_id = upload.json()["id"]
    response = await client.get(f"/api/datasets/{dataset_id}/rows?limit=1")
    assert response.json()["total_returned"] == 1


async def test_get_rows_not_found_returns_404(client):
    response = await client.get("/api/datasets/no-such-id/rows")
    assert response.status_code == 404
