"""
Unit tests for _validate_sql_static().

Verifies the deny-list blocks write/admin keywords while passing
all SELECT variants cleanly.
"""

import pytest

from packages.query_engine.pipeline import _validate_sql_static


# ── Should pass (SELECT only) ──────────────────────────────────────────────────

def test_valid_simple_select():
    assert _validate_sql_static('SELECT revenue FROM "orders"') is None


def test_valid_aggregate():
    assert _validate_sql_static(
        'SELECT SUM(revenue) AS revenue FROM "retail_sales" GROUP BY region'
    ) is None


def test_valid_with_where():
    assert _validate_sql_static(
        "SELECT COUNT(*) FROM \"orders\" WHERE status = 'completed'"
    ) is None


def test_valid_multiline():
    sql = (
        'SELECT\n  region,\n  SUM(revenue) AS revenue\n'
        'FROM "retail_sales"\n'
        "WHERE \"order_date\" >= '2026-01-01'\n"
        "GROUP BY region\nORDER BY revenue DESC\nLIMIT 10"
    )
    assert _validate_sql_static(sql) is None


# ── Should be blocked ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("keyword", [
    "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE",
    "CREATE", "REPLACE", "ATTACH", "DETACH", "PRAGMA",
    "COPY", "EXPORT", "IMPORT", "LOAD", "INSTALL",
])
def test_blocked_keyword(keyword):
    sql = f"{keyword} TABLE orders"
    result = _validate_sql_static(sql)
    assert result is not None
    assert keyword.lower() in result.lower() or keyword in result


def test_blocked_case_insensitive():
    assert _validate_sql_static("drop table orders") is not None
    assert _validate_sql_static("Drop Table orders") is not None


def test_error_message_mentions_keyword():
    result = _validate_sql_static("DELETE FROM orders WHERE 1=1")
    assert result is not None
    assert "DELETE" in result or "delete" in result.lower()


def test_word_boundary_respected():
    # 'CREATED_AT' contains 'CREATE' but as part of an identifier — should pass
    # (Note: the regex uses \b word boundaries, so "CREATED_AT" should NOT match)
    assert _validate_sql_static('SELECT created_at FROM "orders"') is None
