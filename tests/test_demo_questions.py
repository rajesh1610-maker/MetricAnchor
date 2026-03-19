"""
Evaluation harness for demo dataset questions.

Runs each question in examples/*/questions.yml against a live API
(seeded with sample_data/*.csv) and asserts the expected outputs.

Usage:
    # Seed first (API must be running):
    python scripts/seed_demo.py

    # Run evals:
    pytest tests/test_demo_questions.py -v

    # Run one dataset only:
    pytest tests/test_demo_questions.py -v -k "retail"

Environment:
    METRICANCHOR_API_URL  – override base URL (default: http://localhost:8000)

Skip condition:
    If the API is not reachable, all tests are skipped automatically.
"""

import math
import os
from pathlib import Path
from typing import Any

import httpx
import pytest
import yaml

ROOT = Path(__file__).parent.parent
EXAMPLES = ROOT / "examples"
API_URL = os.getenv("METRICANCHOR_API_URL", "http://localhost:8000")

# ── Helpers ───────────────────────────────────────────────────────────────────

def _api_available() -> bool:
    try:
        r = httpx.get(f"{API_URL}/api/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def _find_dataset(client: httpx.Client, filename: str) -> str | None:
    resp = client.get("/api/datasets", timeout=10)
    resp.raise_for_status()
    for ds in resp.json().get("datasets", []):
        if ds["original_filename"] == filename:
            return ds["id"]
    return None


def _ask(client: httpx.Client, dataset_id: str, question: str) -> dict:
    resp = client.post(
        "/api/questions",
        json={"question": question, "dataset_id": dataset_id},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def _col_index(columns: list[str], name: str) -> int | None:
    for i, c in enumerate(columns):
        if c.lower() == name.lower():
            return i
    return None


def _get_col_values(result: dict, col: str) -> list[Any]:
    idx = _col_index(result["columns"], col)
    if idx is None:
        return []
    return [row[idx] for row in result["rows"]]


def _assert_value_check(result: dict, check: dict) -> None:
    col = check["column"]
    op = check["operator"]
    expected = check.get("value")
    tolerance = check.get("tolerance", 0.01)

    values = _get_col_values(result, col)
    assert values, f"Column '{col}' not found or empty. Columns: {result['columns']}"

    if op == "==":
        assert values[0] == expected or math.isclose(
            float(values[0]), float(expected), rel_tol=0.001
        ), f"{col}: expected {expected}, got {values[0]}"

    elif op == "approx":
        assert math.isclose(
            float(values[0]), float(expected), abs_tol=tolerance
        ), f"{col}: expected ≈{expected} ±{tolerance}, got {values[0]}"

    elif op == "sum":
        total = sum(float(v) for v in values if v is not None)
        assert math.isclose(
            total, float(expected), rel_tol=0.001
        ), f"{col} sum: expected {expected}, got {total}"

    elif op == "first_value":
        assert str(values[0]) == str(expected), (
            f"{col}: expected first value '{expected}', got '{values[0]}'"
        )

    elif op == "all_positive":
        assert all(v is None or float(v) >= 0 for v in values), (
            f"{col}: expected all non-negative, got {values}"
        )


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def api_client():
    if not _api_available():
        pytest.skip("API not reachable — run 'make up && python scripts/seed_demo.py' first")
    return httpx.Client(base_url=API_URL)


def _load_cases(dataset_csv: str) -> list[tuple[str, str, dict]]:
    """Return (dataset_csv, question_id, spec) tuples for parametrize."""
    dataset_name = Path(dataset_csv).stem
    questions_yml = EXAMPLES / dataset_name / "questions.yml"
    if not questions_yml.exists():
        return []
    data = yaml.safe_load(questions_yml.read_text())
    return [(dataset_csv, q["id"], q) for q in data.get("questions", [])]


RETAIL_CASES = _load_cases("retail_sales.csv")
TICKETS_CASES = _load_cases("support_tickets.csv")
FUNNEL_CASES = _load_cases("saas_funnel.csv")


# ── Test classes ──────────────────────────────────────────────────────────────

def _run_question_test(api_client: httpx.Client, dataset_csv: str, spec: dict) -> None:
    """Core assertion logic shared by all three test classes."""
    dataset_id = _find_dataset(api_client, dataset_csv)
    if not dataset_id:
        pytest.skip(f"Dataset '{dataset_csv}' not seeded — run scripts/seed_demo.py")

    result = _ask(api_client, dataset_id, spec["question"])

    # Must not be a hard error
    assert not result.get("error"), (
        f"Pipeline error: {result['error']}\nQuestion: {spec['question']}"
    )

    # Chart type
    if expected_chart := spec.get("expected_chart"):
        assert result.get("chart_type") == expected_chart, (
            f"chart_type: expected '{expected_chart}', got '{result.get('chart_type')}'"
        )

    # SQL presence and content
    assert result.get("sql"), "No SQL returned"
    sql = result["sql"].upper()
    for fragment in spec.get("sql_contains", []):
        assert fragment.upper() in sql, (
            f"SQL missing expected fragment '{fragment}'.\nSQL:\n{result['sql']}"
        )
    for fragment in spec.get("sql_excludes", []):
        assert fragment.upper() not in sql, (
            f"SQL contains forbidden fragment '{fragment}'.\nSQL:\n{result['sql']}"
        )

    # Row count
    if row_count := spec.get("result", {}).get("row_count"):
        if isinstance(row_count, dict):
            assert row_count["min"] <= result["row_count"] <= row_count["max"], (
                f"row_count {result['row_count']} not in [{row_count['min']}, {row_count['max']}]"
            )
        else:
            assert result["row_count"] == row_count, (
                f"row_count: expected {row_count}, got {result['row_count']}"
            )

    # Columns present
    for col in spec.get("result", {}).get("columns", []):
        assert _col_index(result["columns"], col) is not None, (
            f"Expected column '{col}' not in result. Got: {result['columns']}"
        )

    # Value assertions
    for check in spec.get("result", {}).get("value_checks", []):
        _assert_value_check(result, check)

    # Confidence
    if expected_conf := spec.get("confidence"):
        assert result.get("confidence") == expected_conf, (
            f"confidence: expected '{expected_conf}', got '{result.get('confidence')}'"
        )


class TestRetailSales:
    @pytest.mark.parametrize("dataset_csv,qid,spec", RETAIL_CASES, ids=[c[1] for c in RETAIL_CASES])
    def test_question(self, api_client, dataset_csv: str, qid: str, spec: dict) -> None:
        _run_question_test(api_client, dataset_csv, spec)


class TestSupportTickets:
    @pytest.mark.parametrize("dataset_csv,qid,spec", TICKETS_CASES, ids=[c[1] for c in TICKETS_CASES])
    def test_question(self, api_client, dataset_csv: str, qid: str, spec: dict) -> None:
        _run_question_test(api_client, dataset_csv, spec)


class TestSaasFunnel:
    @pytest.mark.parametrize("dataset_csv,qid,spec", FUNNEL_CASES, ids=[c[1] for c in FUNNEL_CASES])
    def test_question(self, api_client, dataset_csv: str, qid: str, spec: dict) -> None:
        _run_question_test(api_client, dataset_csv, spec)
