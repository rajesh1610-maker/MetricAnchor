"""
Eval report generator.

Prints a pass/fail summary to stdout and writes a JSON report file.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def print_report(results) -> None:
    """Print a human-readable pass/fail report to stdout."""
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]

    print("\n" + "═" * 65)
    print(f"  MetricAnchor Eval Report — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 65)

    # Per-dataset summary
    datasets = sorted({r.dataset for r in results})
    for ds in datasets:
        ds_results = [r for r in results if r.dataset == ds]
        ds_pass = sum(1 for r in ds_results if r.passed)
        ds_total = len(ds_results)
        icon = "" if ds_pass == ds_total else ""
        print(f"  {icon}  {ds}: {ds_pass}/{ds_total}")

    print()

    # Failures
    if failed:
        print(f"  FAILURES ({len(failed)}):")
        print()
        for r in failed:
            print(f"  ✗  [{r.dataset}] {r.case_id}")
            print(f"     Q: {r.question}")
            for f in r.failures:
                print(f"     - {f}")
            if r.sql:
                print(f"     SQL: {r.sql[:120]}{'...' if len(r.sql) > 120 else ''}")
            print()

    # Overall
    total = len(results)
    print("─" * 65)
    score = f"{len(passed)}/{total}"
    status = "ALL PASSED" if not failed else f"{len(failed)} FAILED"
    avg_ms = sum(r.duration_ms for r in results) // max(len(results), 1)
    print(f"  Result: {score}  |  {status}  |  avg {avg_ms}ms/case")
    print("═" * 65 + "\n")


def write_report(results, path: str | None = None) -> Path:
    """Write a JSON report to evals/last_run.json."""
    if path is None:
        out_path = ROOT / "evals" / "last_run.json"
    else:
        out_path = Path(path)

    passed = [r for r in results if r.passed]
    report = {
        "timestamp": datetime.now().isoformat(),
        "total": len(results),
        "passed": len(passed),
        "failed": len(results) - len(passed),
        "pass_rate": len(passed) / max(len(results), 1),
        "cases": [
            {
                "id": r.case_id,
                "dataset": r.dataset,
                "question": r.question,
                "passed": r.passed,
                "failures": r.failures,
                "duration_ms": r.duration_ms,
            }
            for r in results
        ],
    }

    out_path.write_text(json.dumps(report, indent=2))
    print(f"  Report written to: {out_path}")
    return out_path
