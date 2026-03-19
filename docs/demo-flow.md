# Demo Flow

A step-by-step walkthrough of the full MetricAnchor user journey using the included sample datasets. Use this when demoing to stakeholders, onboarding new contributors, or recording a screen walkthrough.

**Time:** ~5 minutes end-to-end.
**Prerequisites:** Docker Desktop installed and running.

---

## Setup (one time)

```bash
git clone https://github.com/your-username/metricanchor.git
cd metricanchor

# Copy env config — no API key required for stub mode
cp .env.example .env

# Start both services
make up

# Generate the sample CSVs and load them into the running API
make generate-data
make seed
```

You should see:
```
Seeding demo datasets and semantic models...
  retail_sales     → uploaded (774 rows) ✓
  support_tickets  → uploaded (256 rows) ✓
  saas_funnel      → uploaded (320 rows) ✓
  retail_sales     semantic model created ✓
  support_tickets  semantic model created ✓
  saas_funnel      semantic model created ✓
```

Open http://localhost:3000.

---

## Step 1 — Explore a Dataset

1. Click **Datasets** in the navigation bar.
2. Select **retail_sales**.
3. The **Schema Profile** panel shows:
   - Column names, inferred types, null rates, distinct counts
   - Sample values for each column (first 5 rows)
4. Notice the dataset has 774 rows and 9 columns including `order_total`, `product_category`, `region`, `channel`, `status`.

> **What to point out:** MetricAnchor profiles the schema automatically on upload — no configuration needed.

---

## Step 2 — Inspect the Semantic Model

1. Click **Semantic Models** in the navigation bar.
2. Select the **retail_sales** model.
3. Review the defined metrics:
   - `revenue` — `SUM(order_total)` filtered to `status = 'completed'`
   - `order_count` — `COUNT(DISTINCT order_id)` filtered to `status = 'completed'`
   - `aov` — average order value
   - `margin` — `SUM(margin_amount)`
4. Review dimensions: `product_category`, `region`, `channel`, `order_date`.

> **What to point out:** Semantic models are plain YAML files, version-controllable alongside your code. The "revenue" definition tells the system exactly what "revenue" means for this data — every answer will use it.

---

## Step 3 — Ask a Simple Question

1. Click **Ask** in the navigation bar.
2. Select **retail_sales** from the dataset dropdown.
3. Type: `What is total revenue?`
4. Hit **Ask** (or press Enter).

**Expected result:**

- A single metric card showing `$208,222.95`
- Confidence badge: **High**
- SQL panel shows:
  ```sql
  SELECT SUM(order_total) AS revenue
  FROM retail_sales
  WHERE status = 'completed'
  ```
- Assumptions: *(none — no time range or ambiguous terms)*
- Term mappings: `revenue → SUM(order_total) WHERE status = 'completed'`

> **What to point out:** Every answer shows its SQL, term mappings, and confidence. Nothing is a black box.

---

## Step 4 — Ask a Breakdown Question

1. Still on the Ask page with **retail_sales** selected.
2. Type: `revenue by region`
3. Hit **Ask**.

**Expected result:**

- A bar chart with 4 bars (North, South, East, West)
- The chart auto-selects based on the number of result rows and question type
- SQL panel shows a `GROUP BY region` query
- Confidence: **High** (region is a defined dimension)

---

## Step 5 — Ask a Ranking Question

1. Type: `top 5 products by revenue`
2. Hit **Ask**.

**Expected result:**

- Bar chart with 5 bars (Electronics at the top, ~$81,710)
- SQL includes `ORDER BY revenue DESC LIMIT 5`
- Confidence: **High**

---

## Step 6 — Ask a Time-Range Question

1. Type: `revenue last quarter`
2. Hit **Ask**.

**Expected result:**

- A metric card (or bar chart if grouped by another dimension)
- Assumptions panel shows: *"'last quarter' interpreted as Q4 2025 (2025-10-01 to 2025-12-31)"*
- SQL includes a `WHERE order_date >= '2025-10-01' AND order_date < '2026-01-01'` clause

> **What to point out:** Time expressions are parsed at query time and always surfaced as assumptions. The user can verify the interpretation before trusting the number.

---

## Step 7 — Toggle Developer Mode

1. On the Ask page, press **Cmd+Shift+D** (macOS) or **Ctrl+Shift+D** (Windows/Linux).
2. The developer panel appears below the result, showing:
   - The full LLM prompt sent to the model (in stub mode, the stub logic that ran)
   - The raw model response
   - All intermediate parsing results

> **What to point out:** Analytics engineers (Persona 2 / Dev) can see exactly what the system did and why. This makes it debuggable and trustworthy.

---

## Step 8 — Switch to Support Tickets

1. Change the dataset selector to **support_tickets**.
2. Type: `tickets by priority`
3. Hit **Ask**.

**Expected result:**

- Bar chart: P1, P2, P3 buckets with ticket counts
- SQL: `SELECT priority, COUNT(*) AS ticket_count FROM support_tickets GROUP BY priority`

---

## Step 9 — Demonstrate Low Confidence

1. Still on **support_tickets**.
2. Type something ambiguous: `how are we doing?`
3. Hit **Ask**.

**Expected result:**

- Confidence: **Low** or **Clarification needed**
- The system surfaces that it cannot map any recognised metric or dimension from the question
- No SQL is run with undefined terms
- The UI shows a plain-English explanation of what was ambiguous

> **What to point out:** The system fails gracefully and honestly. It does not invent an answer.

---

## Step 10 — Flag an Answer

1. After any result, click the **Report a problem** button (thumbs down or flag icon).
2. A modal appears asking what was wrong.
3. Submit feedback.

The feedback is recorded in SQLite and retrievable via `GET /api/questions/{id}/feedback`.

---

## Demo Variants

### Live LLM mode
Set `LLM_API_KEY=sk-...` in `.env`, restart (`make down && make up`), and ask the same questions. SQL quality improves significantly. The trust output structure is identical — only the SQL generation step changes.

### CLI demo
```bash
# Check status
apps/api/.venv/bin/python3 -m cli.main status

# Ask from the terminal
apps/api/.venv/bin/python3 -m cli.main ask <dataset_id> "revenue by region"
apps/api/.venv/bin/python3 -m cli.main ask <dataset_id> "top 5 products" --provenance

# Run the eval suite
apps/api/.venv/bin/python3 -m cli.main eval run
```

### SaaS Funnel dataset
Try: `total signups`, `signups by acquisition_channel`, `signups by plan`.

---

## Teardown

```bash
make down       # stops containers, preserves data volume
# or
make clean-data # stops containers and removes the data volume (asks for confirmation)
```
