"""
Integration tests for the trust-first analytics pipeline.

Uses real DuckDB + SQLite. LLM is bypassed (api_key = "test-key"),
so the stub question parser and answer formatter are used — deterministic
and offline.
"""

from __future__ import annotations

import io

import pytest
from httpx import ASGITransport, AsyncClient

# ── Fixtures (same pattern as other test modules) ──────────────────────────────

ORDERS_CSV = """\
order_id,order_total,status,order_date,product_category
1,100.0,completed,2026-01-15,Electronics
2,200.0,completed,2026-01-20,Apparel
3,50.0,completed,2026-02-05,Electronics
4,300.0,cancelled,2026-01-10,Apparel
5,75.0,completed,2026-02-10,Electronics
"""

ORDERS_MODEL = {
    "name": "orders",
    "dataset": "orders",
    "description": "Order analytics",
    "grain": "one row = one order",
    "time_column": "order_date",
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
        },
        {
            "name": "order_date",
            "column": "order_date",
            "description": "Order date",
            "is_date": True,
            "aliases": ["date"],
        },
    ],
}


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
    from main import create_app

    from db import init_db

    await init_db()
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# ── Helpers ────────────────────────────────────────────────────────────────────


async def _setup_dataset_and_model(client: AsyncClient) -> tuple[str, str]:
    """Upload ORDERS_CSV and create ORDERS_MODEL. Returns (dataset_id, model_id)."""
    upload = await client.post(
        "/api/datasets",
        files={"file": ("orders.csv", io.BytesIO(ORDERS_CSV.encode()), "text/csv")},
    )
    assert upload.status_code == 201, upload.text
    dataset_id = upload.json()["id"]

    model = await client.post(
        "/api/semantic_models",
        json={
            "dataset_id": dataset_id,
            "name": "orders",
            "definition": ORDERS_MODEL,
        },
    )
    assert model.status_code == 201, model.text
    model_id = model.json()["id"]

    return dataset_id, model_id


# ── Basic pipeline tests ───────────────────────────────────────────────────────


async def test_ask_question_returns_201_with_trust_fields(client):
    dataset_id, _ = await _setup_dataset_and_model(client)

    response = await client.post(
        "/api/questions",
        json={"question": "What is the total revenue?", "dataset_id": dataset_id},
    )
    assert response.status_code == 201
    body = response.json()

    # Core fields
    assert body["question"] == "What is the total revenue?"
    assert body["dataset_id"] == dataset_id

    # Trust fields must be present
    assert "sql" in body
    assert "semantic_mappings" in body
    assert "assumptions" in body
    assert "caveats" in body
    assert "confidence" in body
    assert "confidence_note" in body
    assert "provenance" in body

    # SQL must not be empty and should reference the view
    assert body["sql"]
    assert "orders" in body["sql"].lower()

    # Should have resolved revenue
    assert any(m["resolved_name"] == "revenue" for m in body["semantic_mappings"])


async def test_ask_question_executes_sql_and_returns_rows(client):
    dataset_id, _ = await _setup_dataset_and_model(client)

    response = await client.post(
        "/api/questions",
        json={"question": "What is the revenue?", "dataset_id": dataset_id},
    )
    assert response.status_code == 201
    body = response.json()

    # Revenue should be sum of completed orders: 100+200+50+75 = 425
    assert body["row_count"] >= 1
    assert body["columns"] == ["revenue"]
    assert body["rows"][0][0] == pytest.approx(425.0)


async def test_ask_question_breakdown_groups_by_dimension(client):
    dataset_id, _ = await _setup_dataset_and_model(client)

    response = await client.post(
        "/api/questions",
        json={
            "question": "Show revenue by product_category",
            "dataset_id": dataset_id,
        },
    )
    assert response.status_code == 201
    body = response.json()

    assert body["row_count"] == 2  # Electronics + Apparel
    assert "product_category" in body["columns"]
    assert "revenue" in body["columns"]
    # Chart should be bar for categorical breakdown
    assert body["chart_type"] == "bar"


async def test_ask_question_sql_always_shown(client):
    """Even if the answer is empty, SQL must be present in the response."""
    dataset_id, _ = await _setup_dataset_and_model(client)

    response = await client.post(
        "/api/questions",
        json={"question": "revenue", "dataset_id": dataset_id},
    )
    assert response.status_code == 201
    assert response.json()["sql"]


async def test_ask_question_confidence_field_is_valid(client):
    dataset_id, _ = await _setup_dataset_and_model(client)

    response = await client.post(
        "/api/questions",
        json={"question": "total revenue", "dataset_id": dataset_id},
    )
    body = response.json()
    assert body["confidence"] in ("high", "medium", "low", "clarification_needed")


async def test_ask_question_without_semantic_model_returns_error(client):
    """A dataset with no semantic model should get a clear error in the response."""
    upload = await client.post(
        "/api/datasets",
        files={"file": ("nomodel.csv", io.BytesIO(ORDERS_CSV.encode()), "text/csv")},
    )
    assert upload.status_code == 201
    dataset_id = upload.json()["id"]

    response = await client.post(
        "/api/questions",
        json={"question": "What is revenue?", "dataset_id": dataset_id},
    )
    # Still returns 201 — the pipeline always returns a structured result
    assert response.status_code == 201
    body = response.json()
    assert body["error"] is not None
    assert "semantic model" in body["error"].lower()


async def test_ask_question_with_invalid_dataset_returns_422(client):
    from db import init_db

    await init_db()

    response = await client.post(
        "/api/questions",
        json={"question": "What is revenue?", "dataset_id": "no-such-dataset"},
    )
    assert response.status_code == 422


async def test_ask_question_with_time_range_adds_assumption(client):
    dataset_id, _ = await _setup_dataset_and_model(client)

    response = await client.post(
        "/api/questions",
        json={"question": "What was revenue last month?", "dataset_id": dataset_id},
    )
    assert response.status_code == 201
    body = response.json()

    # Should have a time-range assumption
    assumptions = body["assumptions"]
    assert any("last month" in a.lower() or "interpreted" in a.lower() for a in assumptions)
    # SQL should contain a date filter
    assert body["sql"] and "order_date" in body["sql"]


async def test_provenance_contains_pipeline_steps(client):
    dataset_id, _ = await _setup_dataset_and_model(client)

    response = await client.post(
        "/api/questions",
        json={"question": "revenue", "dataset_id": dataset_id},
    )
    body = response.json()
    provenance = body["provenance"]
    assert provenance is not None
    step_names = [s["step"] for s in provenance.get("steps", [])]
    assert "question_parser" in step_names
    assert "semantic_mapper" in step_names
    assert "sql_generator" in step_names
    assert "execution_engine" in step_names


# ── History / persistence tests ────────────────────────────────────────────────


async def test_list_questions_returns_asked_questions(client):
    dataset_id, _ = await _setup_dataset_and_model(client)

    await client.post(
        "/api/questions",
        json={"question": "revenue", "dataset_id": dataset_id},
    )
    await client.post(
        "/api/questions",
        json={"question": "total sales", "dataset_id": dataset_id},
    )

    response = await client.get("/api/questions")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["questions"]) == 2


async def test_list_questions_filters_by_dataset_id(client):
    dataset_id, _ = await _setup_dataset_and_model(client)

    await client.post(
        "/api/questions",
        json={"question": "revenue", "dataset_id": dataset_id},
    )

    # Filter by this dataset
    r1 = await client.get(f"/api/questions?dataset_id={dataset_id}")
    assert r1.json()["total"] == 1

    # Filter by non-existent dataset
    r2 = await client.get("/api/questions?dataset_id=ds-99")
    assert r2.json()["total"] == 0


async def test_get_question_by_id(client):
    dataset_id, _ = await _setup_dataset_and_model(client)

    created = await client.post(
        "/api/questions",
        json={"question": "revenue", "dataset_id": dataset_id},
    )
    question_id = created.json()["id"]

    response = await client.get(f"/api/questions/{question_id}")
    assert response.status_code == 200
    assert response.json()["id"] == question_id
    assert response.json()["sql"]


async def test_get_question_not_found_returns_404(client):
    response = await client.get("/api/questions/no-such-id")
    assert response.status_code == 404


# ── Feedback tests ─────────────────────────────────────────────────────────────


async def test_submit_feedback_returns_201(client):
    dataset_id, _ = await _setup_dataset_and_model(client)

    created = await client.post(
        "/api/questions",
        json={"question": "revenue", "dataset_id": dataset_id},
    )
    question_id = created.json()["id"]

    fb = await client.post(
        f"/api/questions/{question_id}/feedback",
        json={"feedback_type": "correct", "note": "Spot on!"},
    )
    assert fb.status_code == 201
    body = fb.json()
    assert body["question_id"] == question_id
    assert body["feedback_type"] == "correct"
    assert body["note"] == "Spot on!"


async def test_submit_feedback_on_missing_question_returns_404(client):
    response = await client.post(
        "/api/questions/no-such-id/feedback",
        json={"feedback_type": "wrong"},
    )
    assert response.status_code == 404


async def test_submit_invalid_feedback_type_returns_422(client):
    dataset_id, _ = await _setup_dataset_and_model(client)

    created = await client.post(
        "/api/questions",
        json={"question": "revenue", "dataset_id": dataset_id},
    )
    question_id = created.json()["id"]

    fb = await client.post(
        f"/api/questions/{question_id}/feedback",
        json={"feedback_type": "bad_value"},
    )
    assert fb.status_code == 422
