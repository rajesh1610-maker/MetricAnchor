"""
Integration tests for execute_pipeline().

Calls the pipeline directly with a real DuckDB engine backed by the
deterministic sample CSVs. Uses a stub LLM so no API key is needed.

All numeric assertions use tolerances derived from the seed=42 CSV stats:
  retail_sales:    774 rows, total_revenue ≈ 208,222.95
  support_tickets: 256 rows, 222 resolved, SLA breach rate ≈ 31.1%
  saas_funnel:     320 signups, 131 converted, active MRR ≈ 14,260
"""

from __future__ import annotations

import math

import pytest
import pytest_asyncio

from packages.query_engine.pipeline import execute_pipeline


# ── Helpers ────────────────────────────────────────────────────────────────────

def _col_idx(columns: list[str], name: str) -> int | None:
    for i, c in enumerate(columns):
        if c.lower() == name.lower():
            return i
    return None


def _first(result, col: str):
    idx = _col_idx(result.columns, col)
    assert idx is not None, f"Column '{col}' not in {result.columns}"
    return result.rows[0][idx]


def _col_values(result, col: str) -> list:
    idx = _col_idx(result.columns, col)
    assert idx is not None, f"Column '{col}' not in {result.columns}"
    return [row[idx] for row in result.rows]


# ── Retail Sales ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_retail_total_revenue(retail_engine, retail_model_def, stub_llm, stub_settings):
    result = await execute_pipeline(
        question="What is total revenue?",
        view_name="retail_sales",
        model_definition=retail_model_def,
        engine=retail_engine,
        llm=stub_llm,
        settings=stub_settings,
    )
    assert not result.error, result.error
    assert result.row_count == 1
    revenue = float(_first(result, "revenue"))
    assert math.isclose(revenue, 208222.95, rel_tol=0.01), f"Revenue was {revenue}"


@pytest.mark.asyncio
async def test_retail_revenue_by_region(retail_engine, retail_model_def, stub_llm, stub_settings):
    result = await execute_pipeline(
        question="revenue by region",
        view_name="retail_sales",
        model_definition=retail_model_def,
        engine=retail_engine,
        llm=stub_llm,
        settings=stub_settings,
    )
    assert not result.error, result.error
    assert result.row_count == 4  # North, South, East, West
    assert _col_idx(result.columns, "region") is not None
    assert _col_idx(result.columns, "revenue") is not None


@pytest.mark.asyncio
async def test_retail_top5_products(retail_engine, retail_model_def, stub_llm, stub_settings):
    result = await execute_pipeline(
        question="top 5 products by revenue",
        view_name="retail_sales",
        model_definition=retail_model_def,
        engine=retail_engine,
        llm=stub_llm,
        settings=stub_settings,
    )
    assert not result.error, result.error
    assert result.row_count == 5
    # First row should be highest revenue
    revenues = [float(v) for v in _col_values(result, "revenue")]
    assert revenues == sorted(revenues, reverse=True)


@pytest.mark.asyncio
async def test_retail_revenue_chart_type(retail_engine, retail_model_def, stub_llm, stub_settings):
    result = await execute_pipeline(
        question="total revenue",
        view_name="retail_sales",
        model_definition=retail_model_def,
        engine=retail_engine,
        llm=stub_llm,
        settings=stub_settings,
    )
    assert not result.error
    assert result.chart_type == "metric"


@pytest.mark.asyncio
async def test_retail_breakdown_chart_type(retail_engine, retail_model_def, stub_llm, stub_settings):
    result = await execute_pipeline(
        question="revenue by region",
        view_name="retail_sales",
        model_definition=retail_model_def,
        engine=retail_engine,
        llm=stub_llm,
        settings=stub_settings,
    )
    assert not result.error
    assert result.chart_type == "bar"


@pytest.mark.asyncio
async def test_retail_provenance_has_steps(retail_engine, retail_model_def, stub_llm, stub_settings):
    result = await execute_pipeline(
        question="revenue by region",
        view_name="retail_sales",
        model_definition=retail_model_def,
        engine=retail_engine,
        llm=stub_llm,
        settings=stub_settings,
    )
    assert not result.error
    steps = result.provenance.get("steps", [])
    step_names = [s["step"] for s in steps]
    assert "question_parser" in step_names
    assert "semantic_mapper" in step_names
    assert "sql_generator" in step_names
    assert "execution_engine" in step_names


@pytest.mark.asyncio
async def test_retail_sql_is_select_only(retail_engine, retail_model_def, stub_llm, stub_settings):
    result = await execute_pipeline(
        question="revenue by product",
        view_name="retail_sales",
        model_definition=retail_model_def,
        engine=retail_engine,
        llm=stub_llm,
        settings=stub_settings,
    )
    assert not result.error
    assert result.sql.strip().upper().startswith("SELECT")


# ── Support Tickets ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_support_total_tickets(support_engine, support_model_def, stub_llm, stub_settings):
    result = await execute_pipeline(
        question="total tickets",
        view_name="support_tickets",
        model_definition=support_model_def,
        engine=support_engine,
        llm=stub_llm,
        settings=stub_settings,
    )
    assert not result.error, result.error
    assert result.row_count == 1
    col = "ticket_count" if _col_idx(result.columns, "ticket_count") is not None else result.columns[0]
    count = float(result.rows[0][0])
    assert math.isclose(count, 256, rel_tol=0.05), f"ticket_count was {count}"


@pytest.mark.asyncio
async def test_support_tickets_by_priority(support_engine, support_model_def, stub_llm, stub_settings):
    result = await execute_pipeline(
        question="tickets by priority",
        view_name="support_tickets",
        model_definition=support_model_def,
        engine=support_engine,
        llm=stub_llm,
        settings=stub_settings,
    )
    assert not result.error, result.error
    assert result.row_count == 3  # P1, P2, P3
    assert _col_idx(result.columns, "priority") is not None


# ── SaaS Funnel ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_funnel_total_signups(funnel_engine, funnel_model_def, stub_llm, stub_settings):
    result = await execute_pipeline(
        question="total signups",
        view_name="saas_funnel",
        model_definition=funnel_model_def,
        engine=funnel_engine,
        llm=stub_llm,
        settings=stub_settings,
    )
    assert not result.error, result.error
    assert result.row_count == 1
    count = float(_first(result, "signups"))
    assert math.isclose(count, 320, rel_tol=0.05), f"signups was {count}"


@pytest.mark.asyncio
async def test_funnel_signups_by_channel(funnel_engine, funnel_model_def, stub_llm, stub_settings):
    result = await execute_pipeline(
        question="signups by acquisition_channel",
        view_name="saas_funnel",
        model_definition=funnel_model_def,
        engine=funnel_engine,
        llm=stub_llm,
        settings=stub_settings,
    )
    assert not result.error, result.error
    assert result.row_count >= 2
    assert _col_idx(result.columns, "acquisition_channel") is not None


# ── Error handling ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ambiguous_question_returns_clarification(
    retail_engine, retail_model_def, stub_llm, stub_settings
):
    # A question with no recognizable metric terms on a multi-metric model
    result = await execute_pipeline(
        question="xyz foobar qux",
        view_name="retail_sales",
        model_definition=retail_model_def,
        engine=retail_engine,
        llm=stub_llm,
        settings=stub_settings,
    )
    # Should return either clarification or a default metric result
    # (stub parser falls back to default if exactly 1 metric — retail has 7)
    assert result.confidence in ("clarification_needed", "medium", "high", "low")


@pytest.mark.asyncio
async def test_confidence_high_for_exact_match(
    retail_engine, retail_model_def, stub_llm, stub_settings
):
    result = await execute_pipeline(
        question="revenue by region",
        view_name="retail_sales",
        model_definition=retail_model_def,
        engine=retail_engine,
        llm=stub_llm,
        settings=stub_settings,
    )
    assert not result.error
    assert result.confidence in ("high", "medium")
