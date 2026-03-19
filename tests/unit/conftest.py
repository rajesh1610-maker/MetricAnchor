"""
Unit test configuration.

Adds the project root to sys.path so packages/ and apps/api/ are importable
without installation.  No I/O is permitted in unit tests — use mocks or
in-memory fixtures for everything.
"""

import sys
from pathlib import Path

# Project root → makes `packages.*` importable
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ── Shared minimal semantic model ─────────────────────────────────────────────

import pytest


@pytest.fixture
def minimal_model() -> dict:
    """A two-metric, two-dimension model used across multiple unit tests."""
    return {
        "name": "orders",
        "dataset": "orders",
        "description": "Order analytics",
        "grain": "one row per order",
        "time_column": "order_date",
        "metrics": [
            {
                "name": "revenue",
                "description": "Total revenue from completed orders",
                "expression": "SUM(order_total)",
                "filters": [{"column": "status", "operator": "=", "value": "completed"}],
                "aliases": ["sales", "total revenue"],
                "format": "currency",
            },
            {
                "name": "order_count",
                "description": "Number of completed orders",
                "expression": "COUNT(*)",
                "filters": [{"column": "status", "operator": "=", "value": "completed"}],
                "aliases": ["orders", "order volume"],
                "format": "number",
            },
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
                "description": "Date the order was placed",
                "is_date": True,
                "aliases": ["date"],
            },
        ],
        "synonyms": [
            {"phrase": "best selling", "maps_to": "metric:revenue"},
            {"phrase": "by product", "maps_to": "dimension:product_category"},
        ],
        "business_rules": [
            {
                "name": "completed_only",
                "description": "Only count completed orders",
                "filter": "status = 'completed'",
                "applies_to": ["metric:revenue", "metric:order_count"],
            }
        ],
        "caveats": ["Revenue excludes refunds."],
    }


@pytest.fixture
def retail_model() -> dict:
    """Model matching the generated retail_sales.csv schema."""
    return {
        "name": "retail_sales",
        "dataset": "retail_sales",
        "description": "Retail order analytics",
        "grain": "one row per order line",
        "time_column": "order_date",
        "metrics": [
            {
                "name": "revenue",
                "description": "Total gross revenue",
                "expression": "SUM(revenue)",
                "aliases": ["sales", "total_revenue", "gross_revenue"],
                "format": "currency",
            },
            {
                "name": "margin_rate",
                "description": "Gross margin as a percentage of revenue",
                "expression": "SUM(margin) / NULLIF(SUM(revenue), 0) * 100",
                "aliases": ["margin_pct", "profitability"],
                "format": "percent",
            },
            {
                "name": "order_count",
                "description": "Number of orders",
                "expression": "COUNT(*)",
                "aliases": ["orders"],
                "format": "number",
            },
        ],
        "dimensions": [
            {
                "name": "product",
                "column": "product",
                "description": "Product category",
                "aliases": ["category", "product_category"],
                "values": ["Electronics", "Apparel", "Home", "Sports", "Beauty"],
            },
            {
                "name": "region",
                "column": "region",
                "description": "Sales region",
                "aliases": ["geo"],
                "values": ["North", "South", "East", "West"],
            },
            {
                "name": "order_date",
                "column": "order_date",
                "description": "Date of order",
                "aliases": ["date"],
                "is_date": True,
            },
        ],
        "synonyms": [
            {"phrase": "top selling", "maps_to": "metric:revenue"},
            {"phrase": "gross profit", "maps_to": "metric:revenue"},
        ],
        "caveats": ["Revenue is gross; returns are not deducted."],
    }
