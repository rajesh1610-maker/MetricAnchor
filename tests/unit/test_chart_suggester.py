"""
Unit tests for _suggest_chart().

Verifies chart type routing across all combinations of
question_type, dimension count, metric count, date dimensions,
and row count.
"""

import pytest

from packages.query_engine.pipeline import _suggest_chart
from packages.query_engine.pipeline_types import TermMapping


def _metric(name: str) -> TermMapping:
    return TermMapping(
        phrase=name, resolved_name=name, resolved_type="metric",
        resolved_to=f"metric:{name}", via="exact", confidence=1.0,
    )


def _dim(name: str, is_date: bool = False) -> TermMapping:
    return TermMapping(
        phrase=name, resolved_name=name, resolved_type="dimension",
        resolved_to=f"dimension:{name}", via="exact", confidence=1.0,
    )


def _model_with_dims(*dims):
    """Build a minimal model dict with the given dimension dicts."""
    return {"dimensions": list(dims)}


def _date_dim_dict(name: str) -> dict:
    return {"name": name, "column": name, "is_date": True}


def _cat_dim_dict(name: str) -> dict:
    return {"name": name, "column": name}


# ── No dimensions → KPI card ───────────────────────────────────────────────────

def test_metric_kpi_no_dims():
    model = _model_with_dims()
    result = _suggest_chart("metric_lookup", [_metric("revenue")], [], model, 1)
    assert result == "metric"


def test_metric_kpi_even_multi_metrics():
    model = _model_with_dims()
    result = _suggest_chart("metric_lookup", [_metric("revenue"), _metric("margin")], [], model, 1)
    assert result == "metric"


# ── Too many rows or dims → table ──────────────────────────────────────────────

def test_table_for_many_rows():
    model = _model_with_dims(_cat_dim_dict("region"))
    result = _suggest_chart("breakdown", [_metric("revenue")], [_dim("region")], model, 30)
    assert result == "table"


def test_table_for_multiple_dims():
    model = _model_with_dims(_cat_dim_dict("region"), _cat_dim_dict("product"))
    result = _suggest_chart(
        "breakdown",
        [_metric("revenue")],
        [_dim("region"), _dim("product")],
        model,
        5,
    )
    assert result == "table"


# ── One date dimension → line ──────────────────────────────────────────────────

def test_line_for_date_dim():
    model = _model_with_dims(_date_dim_dict("order_date"))
    result = _suggest_chart("metric_lookup", [_metric("revenue")], [_dim("order_date")], model, 12)
    assert result == "line"


def test_line_for_trend_question_type():
    # Even with a non-date dim, trend question_type → line
    model = _model_with_dims(_cat_dim_dict("region"))
    result = _suggest_chart("trend", [_metric("revenue")], [_dim("region")], model, 10)
    assert result == "line"


# ── Ranking → bar ──────────────────────────────────────────────────────────────

def test_bar_for_ranking():
    model = _model_with_dims(_cat_dim_dict("product"))
    result = _suggest_chart("ranking", [_metric("revenue")], [_dim("product")], model, 5)
    assert result == "bar"


# ── Single cat dim + single metric → bar ──────────────────────────────────────

def test_bar_single_cat_dim_single_metric():
    model = _model_with_dims(_cat_dim_dict("region"))
    result = _suggest_chart("breakdown", [_metric("revenue")], [_dim("region")], model, 4)
    assert result == "bar"


# ── Single cat dim + multiple metrics → grouped_bar ───────────────────────────

def test_grouped_bar_multi_metric():
    model = _model_with_dims(_cat_dim_dict("region"))
    result = _suggest_chart(
        "breakdown",
        [_metric("revenue"), _metric("margin")],
        [_dim("region")],
        model,
        4,
    )
    assert result == "grouped_bar"


# ── Boundary: exactly 25 rows should still render as bar/line ─────────────────

def test_25_rows_not_table():
    model = _model_with_dims(_cat_dim_dict("region"))
    result = _suggest_chart("breakdown", [_metric("revenue")], [_dim("region")], model, 25)
    assert result != "table"


def test_26_rows_is_table():
    model = _model_with_dims(_cat_dim_dict("region"))
    result = _suggest_chart("breakdown", [_metric("revenue")], [_dim("region")], model, 26)
    assert result == "table"
