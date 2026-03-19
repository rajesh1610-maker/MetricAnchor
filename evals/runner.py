"""
Eval runner — executes EvalCases against the pipeline and records pass/fail.

Usage:
    python -m evals.runner [--dataset retail_sales|support_tickets|saas_funnel]

Requires:
    - sample CSVs in sample_data/ (run: python3 sample_data/generate.py)
    - semantic model YAMLs in examples/*/semantic_model.yml

No API key needed — uses stub LLM throughout.
"""

from __future__ import annotations

import argparse
import asyncio
import math
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.cases import ALL_CASES, EvalCase, ValueCheck  # noqa: E402
from packages.query_engine.engine import QueryEngine  # noqa: E402
from packages.query_engine.pipeline import execute_pipeline  # noqa: E402


# ── Stub LLM ───────────────────────────────────────────────────────────────────

class StubLLM:
    is_stub = True

    async def complete(self, messages, json_mode=False):
        return ""

    async def complete_json(self, messages):
        return {}


class StubSettings:
    llm_provider = "openai"
    llm_api_key = "test-key"
    llm_model = "stub"
    llm_base_url = ""
    llm_max_tokens = 512


# ── Result dataclass ───────────────────────────────────────────────────────────

@dataclass
class CaseResult:
    case_id: str
    dataset: str
    question: str
    passed: bool
    failures: list[str] = field(default_factory=list)
    duration_ms: int = 0
    sql: str = ""


# ── Engine registry ────────────────────────────────────────────────────────────

async def _build_engines(tmp_dir: str) -> dict[str, tuple[QueryEngine, dict]]:
    """Build one engine + model_def per dataset."""
    import yaml

    datasets = {
        "retail_sales": ("retail_sales.csv", "retail_sales"),
        "support_tickets": ("support_tickets.csv", "support_tickets"),
        "saas_funnel": ("saas_funnel.csv", "saas_funnel"),
    }

    result = {}
    for key, (csv_name, model_dir) in datasets.items():
        csv_path = ROOT / "sample_data" / csv_name
        model_path = ROOT / "examples" / model_dir / "semantic_model.yml"

        if not csv_path.exists():
            print(f"  SKIP {key}: {csv_path} not found")
            continue
        if not model_path.exists():
            print(f"  SKIP {key}: {model_path} not found")
            continue

        db_path = str(Path(tmp_dir) / f"{key}.duckdb")
        engine = QueryEngine(db_path)
        await engine.register_dataset(key, str(csv_path))
        model_def = yaml.safe_load(model_path.read_text())
        result[key] = (engine, model_def)
        print(f"  Loaded {key}")

    return result


# ── Assertion logic ────────────────────────────────────────────────────────────

def _col_idx(columns: list[str], name: str) -> int | None:
    for i, c in enumerate(columns):
        if c.lower() == name.lower():
            return i
    return None


def _col_values(result, col: str) -> list:
    idx = _col_idx(result.columns, col)
    if idx is None:
        return []
    return [row[idx] for row in result.rows]


def _run_assertions(pipeline_result, case: EvalCase) -> list[str]:
    failures = []

    if pipeline_result.error:
        return [f"Pipeline error: {pipeline_result.error}"]

    # Chart type
    if case.expected_chart and pipeline_result.chart_type != case.expected_chart:
        failures.append(
            f"chart_type: expected '{case.expected_chart}', got '{pipeline_result.chart_type}'"
        )

    # SQL
    if not pipeline_result.sql:
        failures.append("No SQL returned")
    else:
        sql_upper = pipeline_result.sql.upper()
        for fragment in case.sql_must_contain:
            if fragment.upper() not in sql_upper:
                failures.append(f"SQL missing '{fragment}'")
        for fragment in case.sql_must_not_contain:
            if fragment.upper() in sql_upper:
                failures.append(f"SQL contains forbidden '{fragment}'")

    # Row count
    if case.row_count is not None and pipeline_result.row_count != case.row_count:
        failures.append(
            f"row_count: expected {case.row_count}, got {pipeline_result.row_count}"
        )
    if case.row_count_min is not None and pipeline_result.row_count < case.row_count_min:
        failures.append(
            f"row_count {pipeline_result.row_count} < min {case.row_count_min}"
        )
    if case.row_count_max is not None and pipeline_result.row_count > case.row_count_max:
        failures.append(
            f"row_count {pipeline_result.row_count} > max {case.row_count_max}"
        )

    # Columns present
    for col in case.columns:
        if _col_idx(pipeline_result.columns, col) is None:
            failures.append(
                f"Expected column '{col}' not in result. Got: {pipeline_result.columns}"
            )

    # Value checks
    for check in case.value_checks:
        values = _col_values(pipeline_result, check.column)
        if not values:
            failures.append(
                f"Column '{check.column}' not found or empty"
            )
            continue

        if check.operator == "approx":
            got = float(values[0])
            if not math.isclose(got, float(check.value), rel_tol=check.tolerance):
                failures.append(
                    f"{check.column}: expected ≈{check.value} ±{check.tolerance*100:.0f}%, got {got}"
                )
        elif check.operator == "==":
            if values[0] != check.value:
                failures.append(f"{check.column}: expected {check.value}, got {values[0]}")
        elif check.operator == "sum":
            total = sum(float(v) for v in values if v is not None)
            if not math.isclose(total, float(check.value), rel_tol=check.tolerance):
                failures.append(
                    f"{check.column} sum: expected {check.value}, got {total}"
                )
        elif check.operator == "all_positive":
            bad = [v for v in values if v is not None and float(v) < 0]
            if bad:
                failures.append(f"{check.column}: found negative values: {bad[:3]}")
        elif check.operator == "gte":
            if float(values[0]) < float(check.value):
                failures.append(f"{check.column}: expected >= {check.value}, got {values[0]}")
        elif check.operator == "lte":
            if float(values[0]) > float(check.value):
                failures.append(f"{check.column}: expected <= {check.value}, got {values[0]}")

    # Confidence
    if case.expected_confidence and pipeline_result.confidence != case.expected_confidence:
        failures.append(
            f"confidence: expected '{case.expected_confidence}', got '{pipeline_result.confidence}'"
        )

    return failures


# ── Main runner ────────────────────────────────────────────────────────────────

async def run_evals(filter_dataset: str | None = None) -> list[CaseResult]:
    llm = StubLLM()
    settings = StubSettings()

    with tempfile.TemporaryDirectory() as tmp_dir:
        print("Loading datasets...")
        engines = await _build_engines(tmp_dir)
        print()

        results: list[CaseResult] = []
        cases = [c for c in ALL_CASES if filter_dataset is None or c.dataset == filter_dataset]

        for case in cases:
            if case.dataset not in engines:
                results.append(CaseResult(
                    case_id=case.id,
                    dataset=case.dataset,
                    question=case.question,
                    passed=False,
                    failures=[f"Dataset '{case.dataset}' not loaded (missing CSV or model)"],
                ))
                continue

            engine, model_def = engines[case.dataset]
            start = time.monotonic()
            try:
                pipeline_result = await execute_pipeline(
                    question=case.question,
                    view_name=case.dataset,
                    model_definition=model_def,
                    engine=engine,
                    llm=llm,
                    settings=settings,
                )
                failures = _run_assertions(pipeline_result, case)
                sql = pipeline_result.sql or ""
            except Exception as exc:
                failures = [f"Exception: {exc}"]
                sql = ""

            duration_ms = int((time.monotonic() - start) * 1000)
            results.append(CaseResult(
                case_id=case.id,
                dataset=case.dataset,
                question=case.question,
                passed=not failures,
                failures=failures,
                duration_ms=duration_ms,
                sql=sql,
            ))

    return results


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MetricAnchor eval suite")
    parser.add_argument("--dataset", help="Filter to a specific dataset", default=None)
    args = parser.parse_args()

    results = asyncio.run(run_evals(filter_dataset=args.dataset))

    # Import report here to avoid circular imports
    from evals.report import print_report, write_report

    print_report(results)
    write_report(results)
