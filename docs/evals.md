# MetricAnchor Evaluation Guide

The eval suite measures the pipeline's accuracy on deterministic questions against the seed=42 sample datasets. No LLM, no network, no running server required — all tests use the stub mode and run in under 1 second.

---

## Running Evals

### pytest (recommended for CI)

```bash
# From the repo root
apps/api/.venv/bin/python3 -m pytest evals/test_evals.py -v

# Filter to one dataset
apps/api/.venv/bin/python3 -m pytest evals/test_evals.py -v -k "retail"

# Or via make
make test          # runs unit + integration + evals together
```

### Standalone runner (human-readable report)

```bash
apps/api/.venv/bin/python3 -m evals.runner

# Filter dataset
apps/api/.venv/bin/python3 -m evals.runner --dataset retail_sales

# Save report
apps/api/.venv/bin/python3 -m evals.runner --output my_report.json
```

### Via CLI

```bash
apps/api/.venv/bin/python3 -m cli.main eval run
apps/api/.venv/bin/python3 -m cli.main eval run --dataset support_tickets
```

---

## Prerequisites

The sample CSVs must exist before running evals:

```bash
make generate-data
# or: python3 sample_data/generate.py
```

This creates three files deterministically (seed=42):
- `sample_data/retail_sales.csv` — 774 rows
- `sample_data/support_tickets.csv` — 256 rows
- `sample_data/saas_funnel.csv` — 320 rows

---

## Eval Case Format

Cases are defined in `evals/cases.py` as `EvalCase` dataclasses:

```python
EvalCase(
    id="retail_total_revenue",
    dataset="retail_sales",       # maps to semantic model + CSV
    question="What is total revenue?",

    # Chart type assertion
    expected_chart="metric",

    # SQL fragment assertions (case-insensitive)
    sql_must_contain=["SUM", "revenue"],
    sql_must_not_contain=["DROP", "DELETE"],

    # Row count assertions
    row_count=1,                  # exact
    # row_count_min=2,            # or range
    # row_count_max=5,

    # Column presence assertions
    columns=["revenue"],

    # Value assertions
    value_checks=[
        ValueCheck("revenue", "approx", 208222.95, tolerance=0.01),
        ValueCheck("revenue", "all_positive"),
    ],
)
```

### Value Check Operators

| Operator | Assertion |
|----------|-----------|
| `approx` | `math.isclose(actual, expected, rel_tol=tolerance)` |
| `==` | exact equality |
| `sum` | sum of all values in the column ≈ expected |
| `first_value` | first row value == expected (string comparison) |
| `all_positive` | all non-null values ≥ 0 |
| `gte` | first value ≥ expected |
| `lte` | first value ≤ expected |

---

## Current Eval Cases

### Retail Sales (`retail_sales.csv`, 774 rows)

| ID | Question | Expected chart |
|----|----------|---------------|
| `retail_total_revenue` | What is total revenue? | metric (KPI) |
| `retail_revenue_by_region` | revenue by region | bar |
| `retail_top5_products` | top 5 products by revenue | bar |
| `retail_order_count` | total orders | metric (KPI) |
| `retail_revenue_by_channel` | revenue by channel | bar |

### Support Tickets (`support_tickets.csv`, 256 rows)

| ID | Question | Expected chart |
|----|----------|---------------|
| `support_total_tickets` | total tickets | metric (KPI) |
| `support_by_priority` | tickets by priority | bar |
| `support_tickets_by_category` | tickets by category | bar |
| `support_by_team` | tickets by team | bar |

### SaaS Funnel (`saas_funnel.csv`, 320 rows)

| ID | Question | Expected chart |
|----|----------|---------------|
| `funnel_total_signups` | total signups | metric (KPI) |
| `funnel_conversions` | total conversions | metric (KPI) |
| `funnel_by_channel` | signups by acquisition_channel | bar |
| `funnel_by_plan` | signups by plan | bar |

---

## Ground Truth Values (seed=42)

### Retail Sales
- Total rows: **774**
- Total revenue: **$208,222.95**
- Total margin: **$71,605.26**
- Margin rate: **34.39%**
- Top product: **Electronics** (~$81,710)
- Regions: North, South, East, West (4 rows)
- Channels: Online, In-store, Wholesale, Partner (4 rows)
- Products: Electronics, Apparel, Home, Sports, Beauty (5 rows)

### Support Tickets
- Total rows: **256**
- Priorities: P1, P2, P3 (3 rows)
- SLA breach rate: **~31.1%** (of resolved tickets)
- Average CSAT: **~3.38**
- Average resolution: **~24.2 hours**

### SaaS Funnel
- Total signups: **320**
- Converted: **~131** (~40.9%)
- Churned: **~21** (~16% of converted)
- Active MRR: **~$14,260**
- Channels: Organic, Paid, Referral, Social (varies)
- Plans: Starter, Pro, Enterprise (3 rows)

---

## Adding New Eval Cases

1. Add a new `EvalCase` to `evals/cases.py` in the appropriate list.
2. Determine the correct question phrasing by checking the semantic model's metric/dimension aliases in `examples/<dataset>/semantic_model.yml`.
3. Run the case to verify it passes:
   ```bash
   apps/api/.venv/bin/python3 -m pytest evals/test_evals.py -v -k "my_new_case_id"
   ```
4. If values drift (e.g. after regenerating data), re-run `python3 sample_data/generate.py` and update the `ValueCheck` expectations.

**Tips:**
- Use exact metric/dimension names or known aliases from the semantic model — the stub LLM only resolves terms it recognises.
- Prefer `approx` over `==` for floating-point values; use `tolerance=0.01` (1%) unless you need tighter bounds.
- Use `row_count_min`/`row_count_max` instead of exact `row_count` for dimensions whose cardinality may vary (e.g. dates).

---

## Live Evals (against running API)

For end-to-end validation including the real database, seed the API first:

```bash
make up && make seed     # start services and seed demo data
pytest tests/test_demo_questions.py -v

# Filter to one dataset
pytest tests/test_demo_questions.py -v -k "retail"
```

Live evals test the full stack: file upload → DuckDB registration → semantic model creation → question pipeline → HTTP response. They auto-skip if the API is not reachable.

---

## CI Integration

The offline eval suite (`evals/test_evals.py`) requires no external services and is safe to run in CI:

```yaml
# GitHub Actions example
- name: Generate sample data
  run: python3 sample_data/generate.py

- name: Run test suite
  run: make test
  # Runs: tests/unit/ + tests/integration/ + evals/test_evals.py
```

Exit code is non-zero if any eval case fails.

---

## Report Format (`evals/last_run.json`)

After each run, the runner writes `evals/last_run.json`:

```json
{
  "timestamp": "2026-03-19T12:00:00",
  "total": 13,
  "passed": 13,
  "failed": 0,
  "pass_rate": 1.0,
  "cases": [
    {
      "id": "retail_total_revenue",
      "dataset": "retail_sales",
      "question": "What is total revenue?",
      "passed": true,
      "failures": [],
      "duration_ms": 18
    }
  ]
}
```
