"""
Eval case definitions — ground-truth assertions for deterministic questions.

Each case specifies a question, the dataset, and what the pipeline MUST
produce. Cases are entirely offline: they run against the seed=42 CSVs
using the stub LLM, so they never touch an external API.

Values are derived from sample_data/generate.py with SEED=42.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValueCheck:
    """Assert something about a specific column in the result."""
    column: str
    operator: str   # "approx" | "==" | "sum" | "gte" | "lte" | "all_positive"
    value: Any = None
    tolerance: float = 0.01  # relative tolerance for "approx"


@dataclass
class EvalCase:
    """A single evaluation case."""
    id: str
    dataset: str          # "retail_sales" | "support_tickets" | "saas_funnel"
    question: str
    expected_chart: str | None = None
    sql_must_contain: list[str] = field(default_factory=list)
    sql_must_not_contain: list[str] = field(default_factory=list)
    row_count: int | None = None
    row_count_min: int | None = None
    row_count_max: int | None = None
    columns: list[str] = field(default_factory=list)
    value_checks: list[ValueCheck] = field(default_factory=list)
    expected_confidence: str | None = None   # high | medium | low
    notes: str = ""


# ── Retail Sales (seed=42: 774 rows, total_revenue=208222.95) ─────────────────

RETAIL_CASES: list[EvalCase] = [
    EvalCase(
        id="retail_total_revenue",
        dataset="retail_sales",
        question="What is total revenue?",
        expected_chart="metric",
        sql_must_contain=["SUM", "revenue"],
        row_count=1,
        columns=["revenue"],
        value_checks=[
            ValueCheck("revenue", "approx", 208222.95, tolerance=0.01),
        ],
    ),
    EvalCase(
        id="retail_revenue_by_region",
        dataset="retail_sales",
        question="revenue by region",
        expected_chart="bar",
        sql_must_contain=["region", "GROUP BY"],
        row_count=4,
        columns=["region", "revenue"],
        value_checks=[
            ValueCheck("revenue", "sum", 208222.95, tolerance=0.01),
            ValueCheck("revenue", "all_positive"),
        ],
    ),
    EvalCase(
        id="retail_top5_products",
        dataset="retail_sales",
        question="top 5 products by revenue",
        expected_chart="bar",
        sql_must_contain=["LIMIT 5", "product"],
        row_count=5,
        columns=["product", "revenue"],
        notes="Electronics should be #1 at ~81,710",
    ),
    EvalCase(
        id="retail_order_count",
        dataset="retail_sales",
        question="total orders",
        expected_chart="metric",
        sql_must_contain=["COUNT"],
        row_count=1,
        columns=["order_count"],
        value_checks=[
            ValueCheck("order_count", "approx", 774, tolerance=0.05),
        ],
    ),
    EvalCase(
        id="retail_revenue_by_channel",
        dataset="retail_sales",
        question="revenue by channel",
        expected_chart="bar",
        sql_must_contain=["channel", "GROUP BY"],
        row_count_min=2,
        row_count_max=5,
        columns=["channel", "revenue"],
    ),
]

# ── Support Tickets (seed=42: 256 rows, 222 resolved, SLA breach rate≈31.1%) ──

SUPPORT_CASES: list[EvalCase] = [
    EvalCase(
        id="support_total_tickets",
        dataset="support_tickets",
        question="total tickets",
        expected_chart="metric",
        sql_must_contain=["COUNT"],
        row_count=1,
        columns=["ticket_count"],
        value_checks=[
            ValueCheck("ticket_count", "approx", 256, tolerance=0.05),
        ],
    ),
    EvalCase(
        id="support_by_priority",
        dataset="support_tickets",
        question="tickets by priority",
        expected_chart="bar",
        sql_must_contain=["priority", "GROUP BY"],
        row_count=3,
        columns=["priority", "ticket_count"],
        value_checks=[
            ValueCheck("ticket_count", "all_positive"),
        ],
    ),
    EvalCase(
        id="support_tickets_by_category",
        dataset="support_tickets",
        question="tickets by category",
        expected_chart="bar",
        sql_must_contain=["category", "GROUP BY"],
        row_count_min=2,
        row_count_max=10,
        columns=["category", "ticket_count"],
        value_checks=[
            ValueCheck("ticket_count", "all_positive"),
        ],
    ),
    EvalCase(
        id="support_by_team",
        dataset="support_tickets",
        question="tickets by team",
        expected_chart="bar",
        sql_must_contain=["team", "GROUP BY"],
        row_count_min=2,
        row_count_max=10,
        columns=["team", "ticket_count"],
    ),
]

# ── SaaS Funnel (seed=42: 320 signups, 131 converted, MRR≈14260) ─────────────

FUNNEL_CASES: list[EvalCase] = [
    EvalCase(
        id="funnel_total_signups",
        dataset="saas_funnel",
        question="total signups",
        expected_chart="metric",
        sql_must_contain=["COUNT"],
        row_count=1,
        columns=["signups"],
        value_checks=[
            ValueCheck("signups", "approx", 320, tolerance=0.05),
        ],
    ),
    EvalCase(
        id="funnel_conversions",
        dataset="saas_funnel",
        question="total conversions",
        expected_chart="metric",
        row_count=1,
        columns=["conversions"],
        value_checks=[
            ValueCheck("conversions", "approx", 131, tolerance=0.10),
        ],
    ),
    EvalCase(
        id="funnel_by_channel",
        dataset="saas_funnel",
        question="signups by acquisition_channel",
        expected_chart="bar",
        sql_must_contain=["acquisition_channel", "GROUP BY"],
        row_count_min=2,
        row_count_max=8,
        columns=["acquisition_channel", "signups"],
        value_checks=[
            ValueCheck("signups", "all_positive"),
        ],
    ),
    EvalCase(
        id="funnel_by_plan",
        dataset="saas_funnel",
        question="signups by plan",
        expected_chart="bar",
        sql_must_contain=["plan", "GROUP BY"],
        row_count_min=2,
        row_count_max=5,
        columns=["plan", "signups"],
    ),
]

ALL_CASES: list[EvalCase] = RETAIL_CASES + SUPPORT_CASES + FUNNEL_CASES
