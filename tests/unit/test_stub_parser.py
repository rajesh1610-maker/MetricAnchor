"""
Unit tests for _parse_stub().

Validates question-type detection, time-expression extraction,
candidate-term collection, explicit group-by detection, and limit parsing.
All tests use the minimal_model fixture (orders dataset).
"""

import pytest

from packages.query_engine.pipeline import _parse_stub


# ── Question type detection ────────────────────────────────────────────────────

def test_metric_lookup_default(minimal_model):
    r = _parse_stub("What is revenue?", minimal_model)
    assert r.question_type == "metric_lookup"


def test_ranking_top_n(minimal_model):
    r = _parse_stub("Show me the top 5 products by revenue", minimal_model)
    assert r.question_type == "ranking"
    assert r.limit == 5


def test_ranking_top_10(minimal_model):
    r = _parse_stub("top 10 customers", minimal_model)
    assert r.question_type == "ranking"
    assert r.limit == 10


def test_trend_over_time(minimal_model):
    r = _parse_stub("Show revenue over time", minimal_model)
    assert r.question_type == "trend"


def test_trend_monthly(minimal_model):
    r = _parse_stub("monthly order count", minimal_model)
    assert r.question_type == "trend"


def test_trend_by_month(minimal_model):
    r = _parse_stub("revenue by month", minimal_model)
    assert r.question_type == "trend"


def test_comparison_vs(minimal_model):
    r = _parse_stub("compare revenue vs last year", minimal_model)
    assert r.question_type == "comparison"


def test_breakdown_by_dimension(minimal_model):
    r = _parse_stub("revenue by product_category", minimal_model)
    assert r.question_type == "breakdown"


def test_breakdown_per_dimension(minimal_model):
    r = _parse_stub("revenue per product_category", minimal_model)
    assert r.question_type == "breakdown"


# ── Time expression extraction ─────────────────────────────────────────────────

def test_last_month(minimal_model):
    r = _parse_stub("revenue last month", minimal_model)
    assert r.time_expression == "last month"


def test_last_7_days(minimal_model):
    r = _parse_stub("orders last 7 days", minimal_model)
    assert r.time_expression == "last 7 days"


def test_last_quarter(minimal_model):
    r = _parse_stub("revenue last quarter", minimal_model)
    assert r.time_expression == "last quarter"


def test_this_year(minimal_model):
    r = _parse_stub("revenue this year", minimal_model)
    assert r.time_expression == "this year"


def test_plain_year(minimal_model):
    r = _parse_stub("revenue in 2024", minimal_model)
    assert r.time_expression == "2024"


def test_no_time_expression(minimal_model):
    r = _parse_stub("total revenue", minimal_model)
    assert r.time_expression is None


# ── Candidate term extraction ──────────────────────────────────────────────────

def test_metric_name_extracted(minimal_model):
    r = _parse_stub("What is revenue?", minimal_model)
    assert "revenue" in r.candidate_terms


def test_metric_alias_extracted(minimal_model):
    r = _parse_stub("Show me total sales", minimal_model)
    assert "sales" in r.candidate_terms


def test_dimension_alias_extracted(minimal_model):
    r = _parse_stub("revenue by category", minimal_model)
    assert "category" in r.candidate_terms


def test_synonym_phrase_extracted(minimal_model):
    r = _parse_stub("best selling products", minimal_model)
    assert "best selling" in r.candidate_terms


def test_no_false_positives(minimal_model):
    r = _parse_stub("What happened in Q1?", minimal_model)
    # "q1" should not match metric/dimension names in minimal_model
    for t in r.candidate_terms:
        assert t in {"revenue", "order_count", "product_category", "order_date",
                     "sales", "total revenue", "orders", "order volume", "category",
                     "date", "best selling", "by product"}


# ── Explicit group-by detection ────────────────────────────────────────────────

def test_explicit_group_by_dimension_name(minimal_model):
    r = _parse_stub("revenue by product_category", minimal_model)
    assert "product_category" in r.explicit_group_by


def test_explicit_group_by_alias(minimal_model):
    r = _parse_stub("revenue by category", minimal_model)
    assert "product_category" in r.explicit_group_by


def test_no_group_by_when_absent(minimal_model):
    r = _parse_stub("total revenue", minimal_model)
    assert r.explicit_group_by == []


# ── Sort direction ─────────────────────────────────────────────────────────────

def test_sort_desc_by_default(minimal_model):
    r = _parse_stub("top 5 products by revenue", minimal_model)
    assert r.sort_direction == "desc"


def test_sort_asc_for_bottom(minimal_model):
    r = _parse_stub("bottom 5 products", minimal_model)
    assert r.sort_direction == "asc"


# ── raw_question preserved ─────────────────────────────────────────────────────

def test_raw_question_preserved(minimal_model):
    q = "What is total revenue last month?"
    r = _parse_stub(q, minimal_model)
    assert r.raw_question == q
