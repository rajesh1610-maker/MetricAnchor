"""
Unit tests for _generate_sql().

Validates SELECT, WHERE, GROUP BY, ORDER BY, and LIMIT clauses
across a range of metric/dimension/time/limit combinations.
"""

import pytest

from packages.query_engine.pipeline import _generate_sql
from packages.query_engine.pipeline_types import TermMapping, TimeRange
from packages.semantic_model.resolver import SemanticResolver


def _metric(name: str, via: str = "exact") -> TermMapping:
    return TermMapping(
        phrase=name, resolved_name=name, resolved_type="metric",
        resolved_to=f"metric:{name}", via=via, confidence=1.0,
    )


def _dim(name: str, via: str = "exact") -> TermMapping:
    return TermMapping(
        phrase=name, resolved_name=name, resolved_type="dimension",
        resolved_to=f"dimension:{name}", via=via, confidence=1.0,
    )


def _time(start: str, end: str) -> TimeRange:
    return TimeRange(
        start=start, end=end,
        label="last month",
        assumption=f"Interpreted 'last month' as {start} to {end}.",
    )


# ── SELECT clause ──────────────────────────────────────────────────────────────

def test_select_single_metric(retail_model):
    resolver = SemanticResolver(retail_model)
    sql, _ = _generate_sql(
        view_name="retail_sales",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[],
        model=retail_model,
        time_range=None,
        limit=None,
        sort_direction="desc",
        resolver=resolver,
    )
    assert "SELECT" in sql
    assert "revenue" in sql.lower()
    assert "SUM" in sql


def test_select_dimension_and_metric(retail_model):
    resolver = SemanticResolver(retail_model)
    sql, _ = _generate_sql(
        view_name="retail_sales",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[_dim("region")],
        model=retail_model,
        time_range=None,
        limit=None,
        sort_direction="desc",
        resolver=resolver,
    )
    assert '"region"' in sql or "region" in sql
    assert "revenue" in sql.lower()


def test_select_from_view_name(retail_model):
    resolver = SemanticResolver(retail_model)
    sql, _ = _generate_sql(
        view_name="my_view",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[],
        model=retail_model,
        time_range=None,
        limit=None,
        sort_direction="desc",
        resolver=resolver,
    )
    assert '"my_view"' in sql


# ── WHERE clause ───────────────────────────────────────────────────────────────

def test_where_time_range_applied(retail_model):
    resolver = SemanticResolver(retail_model)
    sql, assumptions = _generate_sql(
        view_name="retail_sales",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[],
        model=retail_model,
        time_range=_time("2026-01-01", "2026-02-01"),
        limit=None,
        sort_direction="desc",
        resolver=resolver,
    )
    assert "WHERE" in sql
    assert "2026-01-01" in sql
    assert "2026-02-01" in sql


def test_where_business_rules_applied(minimal_model):
    # minimal_model has a business rule: status = 'completed'
    resolver = SemanticResolver(minimal_model)
    sql, _ = _generate_sql(
        view_name="orders",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[],
        model=minimal_model,
        time_range=None,
        limit=None,
        sort_direction="desc",
        resolver=resolver,
    )
    # Business rules should appear in WHERE or metric FILTER
    assert "completed" in sql


def test_where_no_time_no_rules(retail_model):
    resolver = SemanticResolver(retail_model)
    sql, _ = _generate_sql(
        view_name="retail_sales",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[],
        model=retail_model,
        time_range=None,
        limit=None,
        sort_direction="desc",
        resolver=resolver,
    )
    assert "WHERE" not in sql


# ── GROUP BY ───────────────────────────────────────────────────────────────────

def test_group_by_dimension(retail_model):
    resolver = SemanticResolver(retail_model)
    sql, _ = _generate_sql(
        view_name="retail_sales",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[_dim("region")],
        model=retail_model,
        time_range=None,
        limit=None,
        sort_direction="desc",
        resolver=resolver,
    )
    assert "GROUP BY" in sql
    assert '"region"' in sql


def test_no_group_by_when_no_dims(retail_model):
    resolver = SemanticResolver(retail_model)
    sql, _ = _generate_sql(
        view_name="retail_sales",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[],
        model=retail_model,
        time_range=None,
        limit=None,
        sort_direction="desc",
        resolver=resolver,
    )
    assert "GROUP BY" not in sql


# ── ORDER BY ───────────────────────────────────────────────────────────────────

def test_order_by_metric_desc(retail_model):
    resolver = SemanticResolver(retail_model)
    sql, _ = _generate_sql(
        view_name="retail_sales",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[_dim("region")],
        model=retail_model,
        time_range=None,
        limit=None,
        sort_direction="desc",
        resolver=resolver,
    )
    assert "ORDER BY" in sql
    assert "DESC" in sql


def test_order_by_metric_asc(retail_model):
    resolver = SemanticResolver(retail_model)
    sql, _ = _generate_sql(
        view_name="retail_sales",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[_dim("region")],
        model=retail_model,
        time_range=None,
        limit=None,
        sort_direction="asc",
        resolver=resolver,
    )
    assert "ORDER BY" in sql
    assert "ASC" in sql


# ── LIMIT ──────────────────────────────────────────────────────────────────────

def test_limit_applied(retail_model):
    resolver = SemanticResolver(retail_model)
    sql, _ = _generate_sql(
        view_name="retail_sales",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[_dim("region")],
        model=retail_model,
        time_range=None,
        limit=10,
        sort_direction="desc",
        resolver=resolver,
    )
    assert "LIMIT 10" in sql


def test_no_limit_when_none(retail_model):
    resolver = SemanticResolver(retail_model)
    sql, _ = _generate_sql(
        view_name="retail_sales",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[_dim("region")],
        model=retail_model,
        time_range=None,
        limit=None,
        sort_direction="desc",
        resolver=resolver,
    )
    assert "LIMIT" not in sql


# ── Assumptions ────────────────────────────────────────────────────────────────

def test_time_range_assumption_included(retail_model):
    resolver = SemanticResolver(retail_model)
    _, assumptions = _generate_sql(
        view_name="retail_sales",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[],
        model=retail_model,
        time_range=_time("2026-01-01", "2026-02-01"),
        limit=None,
        sort_direction="desc",
        resolver=resolver,
    )
    assert any("2026-01-01" in a or "last month" in a for a in assumptions)


def test_no_time_column_assumption_when_time_given():
    # A model without time_column should produce a note, not crash
    model_no_time = {
        "name": "x",
        "dataset": "x",
        "metrics": [{"name": "revenue", "expression": "SUM(amount)", "aliases": []}],
        "dimensions": [],
    }
    resolver = SemanticResolver(model_no_time)
    sql, assumptions = _generate_sql(
        view_name="x",
        resolved_metrics=[_metric("revenue")],
        resolved_dimensions=[],
        model=model_no_time,
        time_range=_time("2026-01-01", "2026-02-01"),
        limit=None,
        sort_direction="desc",
        resolver=resolver,
    )
    # Should not raise; should note that time filter was skipped
    assert any("time" in a.lower() for a in assumptions)
