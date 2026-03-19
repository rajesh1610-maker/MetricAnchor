# Good First Issues

A curated list of well-scoped, beginner-friendly issues for new contributors.

Each issue has a clear problem statement, success criteria, and pointers to the relevant code. None require deep domain knowledge — just curiosity and a working dev environment.

---

## Before you start

1. Read [CONTRIBUTING.md](../CONTRIBUTING.md) — especially the local setup and PR checklist sections.
2. Comment on the issue to claim it (so two people don't duplicate effort).
3. Open a draft PR early — you can ask questions there.

---

## Tier 1 — No code changes required

These contributions have impact and require zero Python or TypeScript.

---

### GFI-01: Add an example semantic model for a new domain

**Label:** `good first issue`, `semantic-model`, `docs`

**Problem:** MetricAnchor ships with three demo datasets (retail sales, support tickets, SaaS funnel). Each one has a matching semantic model that defines what "revenue," "open ticket," or "conversion" means. More example models help new users understand the format and give them a head start for their own data.

**What to do:**
1. Think of a domain you know well (e-commerce, HR, finance, logistics, healthcare, etc.).
2. Create a sample CSV with 200–500 rows (no real PII).
3. Write a `semantic_model.yml` for it following `examples/retail_sales/semantic_model.yml`.
4. Validate it: `apps/api/.venv/bin/python3 -m packages.semantic_model.validator examples/<your_name>/semantic_model.yml`
5. Add a short `README.md` with 3–5 example questions the model answers.
6. Open a PR.

**Files to create:** `examples/<domain>/semantic_model.yml`, `examples/<domain>/README.md`, `sample_data/<domain>.csv`

**Success criteria:** `make validate` passes; the example questions return sensible answers.

---

### GFI-02: Fix a documentation typo or gap

**Label:** `good first issue`, `docs`

**Problem:** Docs bit-rot. Links break, code examples drift out of sync, and setup steps develop subtle errors over time.

**What to do:** Read through any file in `docs/`, `README.md`, or `CONTRIBUTING.md`. Fix anything that is wrong, unclear, or could be improved. Small PRs are fine — one-line fixes are welcome.

**Files:** Anything in `docs/`, `README.md`, `CONTRIBUTING.md`

**Success criteria:** The change makes the docs more accurate or easier to follow.

---

### GFI-03: Add missing eval cases

**Label:** `good first issue`, `tests`, `evals`

**Problem:** The eval suite currently has 13 cases across three datasets. Many useful questions are not covered — for example, time-range questions, ranking questions, and questions that should return clarification rather than an answer.

**What to do:**
1. Read `evals/cases.py` and `docs/evals.md`.
2. Choose one or more questions not currently covered.
3. Add `EvalCase` entries to `evals/cases.py`.
4. Verify they pass: `apps/api/.venv/bin/python3 -m pytest evals/test_evals.py -v -k "<your_case_id>"`

**Files:** `evals/cases.py`

**Success criteria:** New cases pass in CI; they test something not already covered.

---

## Tier 2 — Small code changes

These require writing Python or TypeScript but are well-scoped and isolated.

---

### GFI-04: Add `--json` flag to the `profile` CLI command

**Label:** `good first issue`, `cli`

**Problem:** The `metricanchor profile <dataset_id>` command outputs a Rich table, which is great for humans but hard to pipe into other tools. A `--json` flag would make it scriptable.

**What to do:**
1. Read `cli/main.py`, specifically the `profile` command.
2. Add an `--json / --no-json` option using `typer.Option`.
3. If `--json` is set, print the profile as JSON (`json.dumps(...)`) instead of a Rich table.

**Files:** `cli/main.py`

**Tests:** Add a test in `tests/unit/` that checks the profile output format (mock the API call).

**Success criteria:** `metricanchor profile <id> --json | jq .columns` works correctly.

---

### GFI-05: Add `row_count` to the dataset list API response

**Label:** `good first issue`, `api`

**Problem:** `GET /api/datasets` returns dataset metadata but omits `row_count`. Users need to click into a dataset to see how many rows it has. Including it in the list response saves a round-trip.

**What to do:**
1. Read `apps/api/schemas/` and `apps/api/routers/datasets.py`.
2. Add `row_count: int | None` to the `DatasetListItem` response schema.
3. Populate it from the `Dataset` ORM model (it's already stored).
4. Add a test.

**Files:** `apps/api/schemas/datasets.py`, `apps/api/routers/datasets.py`

**Tests:** Add or update a test in `apps/api/tests/` that checks the list response includes `row_count`.

**Success criteria:** `GET /api/datasets` response includes `row_count` for each dataset; existing tests still pass.

---

### GFI-06: Surface the `X-Request-ID` in API error responses

**Label:** `good first issue`, `api`, `observability`

**Problem:** The API injects a `X-Request-ID` header in every response. But when the API returns a 422 or 500, the request ID is only in the header — not in the JSON body. Including it in error responses makes it much easier to correlate client-side errors with server logs.

**What to do:**
1. Read `apps/api/main.py` — specifically the `request_id_and_logging` middleware.
2. For non-2xx responses that return JSON, inject `"request_id"` into the response body.
3. Handle edge cases: responses that are not JSON (e.g., streaming) should not be modified.

**Files:** `apps/api/main.py`

**Tests:** Add a test that triggers a 422 (e.g., invalid upload) and checks the response body contains `request_id`.

**Success criteria:** `curl -s -X POST http://localhost:8000/api/datasets -F "bad=payload" | jq .request_id` returns a value.

---

### GFI-07: Add `--provenance` output to the `ask` CLI command

**Label:** `good first issue`, `cli`

**Problem:** The `metricanchor ask` command shows the answer and SQL. There is a `--provenance` flag placeholder in `cli/main.py` but it doesn't output the term mappings and assumptions sections yet.

**What to do:**
1. Read `cli/main.py` — the `ask` command — and `apps/api/schemas/questions.py`.
2. When `--provenance` is set, print the `term_mappings` and `assumptions` fields from the API response using Rich panels.

**Files:** `cli/main.py`

**Tests:** Functional test or docstring example showing expected output.

**Success criteria:** `metricanchor ask <id> "revenue by region" --provenance` prints term mappings and assumptions below the result table.

---

## Tier 3 — Moderate complexity

These are self-contained but require reading more of the codebase.

---

### GFI-08: Add a `DISTINCT` option to metric expressions

**Label:** `good first issue`, `semantic-model`, `query-engine`

**Problem:** Some metrics need `COUNT(DISTINCT column)` rather than `COUNT(column)`. The semantic model has no way to express this — users have to write `COUNT(DISTINCT order_id)` directly in the `expression` field. A `distinct: true` field on metric expressions would make the intent explicit and validate the column reference.

**What to do:**
1. Read `packages/semantic_model/schema.json` and `examples/retail_sales/semantic_model.yml`.
2. Add an optional `distinct: bool` field to the metric schema.
3. Update the validator to check that if `distinct: true`, the expression references a single column (not a `SUM(...)` or complex expression).
4. Update the resolver to use the `distinct` flag when generating SQL.

**Files:** `packages/semantic_model/schema.json`, `packages/semantic_model/validator.py`, `packages/semantic_model/resolver.py`

**Tests:** Add validation tests for valid and invalid uses of `distinct: true`.

**Success criteria:** `distinct: true` is accepted by the validator; `COUNT(DISTINCT ...)` appears in the generated SQL; invalid uses produce clear error messages.

---

### GFI-09: Add a `--dataset` filter to `metricanchor datasets` list

**Label:** `good first issue`, `cli`

**Problem:** Once a user has many uploaded datasets, `metricanchor datasets` lists them all. A `--filter <name>` flag would let users search by dataset name.

**What to do:**
1. Read `cli/main.py` and `GET /api/datasets` in `apps/api/routers/datasets.py`.
2. Add `--filter` option to the `datasets` CLI command; pass it as a `?name=` query parameter.
3. If the API doesn't support `?name=` filtering yet, add it.

**Files:** `cli/main.py`, `apps/api/routers/datasets.py`

**Tests:** Unit test for the CLI filtering; API test for the query parameter.

**Success criteria:** `metricanchor datasets --filter retail` shows only datasets whose name contains "retail".

---

### GFI-10: Warn when a semantic model references a column that doesn't exist in the dataset

**Label:** `good first issue`, `semantic-model`, `api`

**Problem:** The semantic model validator checks the YAML structure but has no way to know whether the columns referenced (`expression: SUM(order_total)`, `column: region`) actually exist in the uploaded CSV. The `POST /api/semantic_models` endpoint has access to both the model and the dataset profile — it could emit a warning if a column reference doesn't match any profiled column.

**What to do:**
1. Read `apps/api/routers/semantic_models.py` and `apps/api/services/`.
2. After creating a semantic model, load the associated dataset's column profile.
3. Extract column references from the model (metric expressions and dimension `column` fields).
4. Compare against the profiled columns (case-insensitive).
5. Return any mismatches as `warnings` in the response (non-fatal — model is still created).

**Files:** `apps/api/routers/semantic_models.py` or a new service

**Tests:** Test that uploading a model with an invalid column reference returns a warning (but succeeds).

**Success criteria:** Creating a model with `expression: SUM(nonexistent_column)` returns `{"warnings": ["metric 'revenue' references column 'nonexistent_column' which was not found in the dataset profile"]}`.
