"""
Unit tests for _parse_time_expression().

All tests use a fixed reference date of 2026-03-19 (Thursday) to
guarantee deterministic date math regardless of when the tests run.
"""

from datetime import date

import pytest

from packages.query_engine.pipeline import _parse_time_expression

TODAY = date(2026, 3, 19)  # Thursday, weekday=3


# ── Absolute expressions ───────────────────────────────────────────────────────

def test_today():
    r = _parse_time_expression("today", TODAY)
    assert r is not None
    assert r.start == "2026-03-19"
    assert r.end == "2026-03-20"
    assert r.label == "today"


def test_yesterday():
    r = _parse_time_expression("yesterday", TODAY)
    assert r is not None
    assert r.start == "2026-03-18"
    assert r.end == "2026-03-19"
    assert r.label == "yesterday"


def test_plain_year():
    r = _parse_time_expression("2024", TODAY)
    assert r is not None
    assert r.start == "2024-01-01"
    assert r.end == "2025-01-01"
    assert r.label == "2024"


def test_quarter_explicit():
    r = _parse_time_expression("q1 2025", TODAY)
    assert r is not None
    assert r.start == "2025-01-01"
    assert r.end == "2025-04-01"
    assert r.label == "Q1 2025"


def test_quarter_q4():
    r = _parse_time_expression("q4 2024", TODAY)
    assert r is not None
    assert r.start == "2024-10-01"
    assert r.end == "2025-01-01"
    assert r.label == "Q4 2024"


# ── Relative expressions ───────────────────────────────────────────────────────

def test_last_7_days():
    r = _parse_time_expression("last 7 days", TODAY)
    assert r is not None
    assert r.start == "2026-03-12"
    assert r.end == "2026-03-20"
    assert "7" in r.label


def test_last_30_days():
    r = _parse_time_expression("last 30 days", TODAY)
    assert r is not None
    assert r.start == "2026-02-17"
    assert r.end == "2026-03-20"


def test_last_1_day():
    r = _parse_time_expression("last 1 day", TODAY)
    assert r is not None
    assert r.start == "2026-03-18"
    assert r.end == "2026-03-20"


def test_last_week():
    r = _parse_time_expression("last week", TODAY)
    assert r is not None
    assert r.start == "2026-03-09"  # Monday of last week
    assert r.end == "2026-03-16"   # Monday of this week (exclusive)


def test_this_week():
    r = _parse_time_expression("this week", TODAY)
    assert r is not None
    assert r.start == "2026-03-16"  # Monday of current week
    assert r.end == "2026-03-23"   # Monday of next week (exclusive)


def test_last_month():
    r = _parse_time_expression("last month", TODAY)
    assert r is not None
    assert r.start == "2026-02-01"
    assert r.end == "2026-03-01"
    assert r.label == "last month"


def test_this_month():
    r = _parse_time_expression("this month", TODAY)
    assert r is not None
    assert r.start == "2026-03-01"
    assert r.end == "2026-03-20"  # today + 1 day
    assert r.label == "this month"


def test_last_quarter_from_q1():
    # TODAY is in Q1 2026 → last quarter is Q4 2025
    r = _parse_time_expression("last quarter", TODAY)
    assert r is not None
    assert r.start == "2025-10-01"
    assert r.end == "2026-01-01"
    assert "Q4" in r.label and "2025" in r.label


def test_this_quarter():
    # TODAY is 2026-03-19 → Q1 2026
    r = _parse_time_expression("this quarter", TODAY)
    assert r is not None
    assert r.start == "2026-01-01"
    assert r.end == "2026-04-01"
    assert "Q1" in r.label and "2026" in r.label


def test_last_year():
    r = _parse_time_expression("last year", TODAY)
    assert r is not None
    assert r.start == "2025-01-01"
    assert r.end == "2026-01-01"
    assert r.label == "2025"


def test_this_year():
    r = _parse_time_expression("this year", TODAY)
    assert r is not None
    assert r.start == "2026-01-01"
    assert r.end == "2026-03-20"  # today + 1 day
    assert r.label == "2026"


# ── Edge cases ─────────────────────────────────────────────────────────────────

def test_unknown_expression_returns_none():
    r = _parse_time_expression("some random phrase", TODAY)
    assert r is None


def test_none_input():
    from packages.query_engine.pipeline import _resolve_time
    assert _resolve_time(None) is None


def test_assumption_is_human_readable():
    r = _parse_time_expression("last month", TODAY)
    assert r is not None
    assert "2026-02" in r.assumption or "February" in r.assumption


def test_start_before_end():
    """Start must always be before end for every expression type."""
    expressions = [
        "today", "yesterday", "last 7 days", "last week", "this week",
        "last month", "this month", "last quarter", "this quarter",
        "last year", "this year", "q2 2025", "2023",
    ]
    for expr in expressions:
        r = _parse_time_expression(expr, TODAY)
        assert r is not None, f"Expected result for '{expr}'"
        assert r.start < r.end, f"start >= end for '{expr}': {r.start} >= {r.end}"
