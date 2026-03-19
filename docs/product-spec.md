# MetricAnchor — Product Specification

**Version:** 1.0 (Phase 0 — Discovery)
**Last Updated:** 2026-03-19
**Status:** Draft

---

## 1. Problem Statement

Business teams drown in dashboards but still can't answer simple questions about their data. They either wait days for an analyst to write a SQL query, or they misuse tools that give confident but wrong answers.

The core problem has three layers:

1. **Access gap.** Most business users cannot write SQL, but their questions are inherently data questions. BI tools help with pre-built dashboards but fail at ad-hoc questions.
2. **Trust gap.** AI-generated answers feel like black boxes. When the AI says "revenue is $2.3M," users can't verify whether it used the right date range, the right definition of revenue, or the right table. One wrong answer destroys trust in the entire system.
3. **Alignment gap.** Business concepts (e.g., "active customer," "churned," "net revenue") differ from raw database column names. No tool bridges this gap cleanly without either huge implementation overhead (traditional BI semantic layers) or fragile prompt engineering (raw LLM chatbots).

MetricAnchor solves all three by combining a lightweight semantic layer with a trust-first AI copilot — every answer shows the SQL, the business-term mappings, the assumptions made, and the confidence level.

---

## 2. Target Users

### Primary: Citizen Developer / Business Analyst
A non-technical or semi-technical user who owns a dataset (CSV, Parquet) and has questions about it. They are comfortable with spreadsheets, may know a bit of SQL, but cannot maintain a data pipeline or write complex queries reliably.

**Examples:** Operations manager, marketing analyst, sales ops lead, small business owner, product manager running their own data.

### Secondary: Analytics Engineer / Developer
A technically skilled user who wants to extend MetricAnchor: edit YAML semantic models, inspect generated SQL, wire up new connectors, write tests, and contribute to the OSS project.

**Examples:** Data engineer, backend developer, analytics engineer, ML engineer experimenting with grounded AI.

---

## 3. User Journeys

### Journey 1: Citizen Developer — First Use
1. Download and run MetricAnchor locally (`docker-compose up`).
2. Upload a CSV file (e.g., retail_sales.csv).
3. MetricAnchor auto-profiles the schema: column names, data types, sample values, null rates.
4. User defines business terms in plain English: "revenue = sum of order_total where status = 'completed'."
5. User types a question: "What was my revenue last month by product category?"
6. MetricAnchor generates SQL, runs it against DuckDB, and returns a table and chart.
7. Every answer shows: the SQL used, the business terms applied, any assumptions (e.g., "I assumed 'last month' = February 2026"), and a confidence note.
8. User clicks "This answer is wrong" and provides feedback.
9. MetricAnchor surfaces the relevant semantic model definition for editing.

### Journey 2: Analytics Engineer — Semantic Model Editing
1. Clone the repo. Run `docker-compose up`.
2. Open `semantic_models/retail_sales.yml` in a code editor.
3. Edit metric definitions, add filters, add computed dimensions.
4. Run `metricanchor validate` to check the YAML against the JSON schema.
5. Ask a question in the UI; see the updated metric definition applied.
6. Run `pytest` to confirm tests pass.
7. Open a pull request to share the semantic model improvements.

### Journey 3: Developer — Extending a Connector
1. Read `docs/connectors.md`.
2. Implement the `BaseConnector` interface in Python.
3. Register the connector in `connectors/__init__.py`.
4. Add an integration test.
5. Submit PR with connector, tests, and documentation.

---

## 4. Main Pain Points Addressed

| Pain Point | How MetricAnchor Addresses It |
|---|---|
| "I don't know if the AI answer is correct." | Every response shows the SQL, term mappings, assumptions, and confidence note. Nothing is hidden. |
| "I have to wait for an analyst for simple questions." | Upload a file and ask in natural language. No analyst required for well-defined metrics. |
| "Our 'revenue' definition changes depending on who you ask." | Semantic models encode the canonical definition once. All answers use the same definition. |
| "BI tools require days to set up." | MetricAnchor runs with `docker-compose up` in under 5 minutes. |
| "LLM tools hallucinate column names and table structures." | MetricAnchor grounds the LLM against the real schema and semantic model before generating SQL. |
| "I can't extend or trust a closed-source tool." | Fully open-source. Every layer is inspectable: schema profiles, SQL generation, YAML models, query execution. |

---

## 5. Product Principles

1. **Trust is the feature.** Every AI answer must be inspectable. If we cannot show why we gave an answer, we should not show the answer.
2. **Local-first by default.** Data never leaves the user's machine unless they explicitly configure an external LLM or database.
3. **Minimal magic.** No black-box embeddings that the user cannot audit. Prefer transparent grounding (schema context, YAML models) over invisible retrieval.
4. **Progressive disclosure.** Citizen developers see clean answers. Developers can always drill down to the raw SQL, the prompt, the plan.
5. **Fail loudly and helpfully.** When the system cannot answer confidently, say so clearly and explain why. A confident wrong answer is worse than an honest "I'm not sure."
6. **OSS-first developer experience.** The repo should be a learning resource. Tests, documentation, and architecture decisions should be easy to read and contribute to.
7. **Separation of concerns.** Semantic modeling, LLM orchestration, query execution, and UI are distinct layers with clean interfaces. Each layer is testable and replaceable.

---

## 6. V1 Scope

### In Scope for V1

**Data ingestion**
- Upload CSV and Parquet files via the UI or CLI.
- Auto-profile schema: column names, types, sample values, null rates, distinct counts.
- Store file metadata in SQLite.

**Semantic modeling**
- Define metrics, dimensions, and filters in YAML.
- JSON schema validation for semantic models.
- UI editor (basic) for metric definitions.
- CLI command: `metricanchor validate`.

**Natural language Q&A**
- Ask questions in plain English.
- Generate SQL using an LLM grounded against the schema and semantic model.
- Execute SQL against DuckDB.
- Return: result table, bar/line chart (auto-selected), generated SQL, business-term mappings, assumptions, confidence note.

**Trust and explainability**
- Show generated SQL for every answer.
- Show which semantic model definitions were applied.
- Show assumptions (e.g., date range interpretation).
- Confidence indicator: high / medium / low / unsure.
- "Report a problem" button tied to the specific question and SQL.

**Feedback loop**
- User can flag an answer as incorrect.
- System records the question, SQL, and flag in SQLite.
- Developer can review and fix the semantic model.

**LLM abstraction**
- Support OpenAI API (gpt-4o and gpt-3.5-turbo class).
- Support Anthropic API (claude-3-5-sonnet).
- Support any OpenAI-compatible local model (Ollama, LM Studio).
- Configurable via environment variable or config file.

**Developer experience**
- Docker + docker-compose: single command to run.
- CLI: upload, validate, ask, export.
- REST API: documented with OpenAPI.
- pytest suite covering core services.
- Playwright smoke tests for the UI.
- CONTRIBUTING.md with clear setup and PR instructions.

### Out of Scope for V1

- Multi-tenancy, SSO, RBAC, billing.
- Direct connections to production databases (Postgres, Snowflake, BigQuery) — file uploads only.
- Streaming responses from LLM.
- Scheduled refreshes or data pipelines.
- Complex visualization beyond bar, line, and table.
- Public cloud deployment playbooks.
- Fine-tuning or custom model training.
- Mobile or native app.
- Collaboration features (shared workspaces, comments).

---

## 7. Demo Scenarios

### Demo 1: Retail Sales Analytics

**Dataset:** `retail_sales.csv`
Columns: `order_id`, `order_date`, `customer_id`, `product_category`, `product_name`, `quantity`, `unit_price`, `order_total`, `status`, `region`

**Semantic model defines:**
- `revenue` = SUM(order_total) WHERE status = 'completed'
- `active_customer` = customer with at least 1 completed order in the last 90 days
- `aov` (average order value) = revenue / COUNT(DISTINCT order_id)

**Demo questions:**
1. "What was revenue by product category last quarter?"
2. "Which region has the most active customers?"
3. "What is the average order value for electronics vs. apparel?"
4. "Show me the top 10 customers by total revenue this year."
5. "Has revenue grown month over month this year?"

**Trust demonstration:** For question 1, the UI shows:
- SQL: `SELECT product_category, SUM(order_total) AS revenue FROM retail_sales WHERE status = 'completed' AND order_date >= '2025-10-01' AND order_date < '2026-01-01' GROUP BY product_category ORDER BY revenue DESC`
- Term mapping: "revenue → SUM(order_total) WHERE status='completed' (from semantic model)"
- Assumption: "'last quarter' interpreted as Q4 2025 (Oct–Dec)"
- Confidence: High

---

### Demo 2: Support Ticket Analytics

**Dataset:** `support_tickets.csv`
Columns: `ticket_id`, `created_at`, `resolved_at`, `customer_tier`, `issue_category`, `priority`, `status`, `assigned_agent`, `csat_score`, `resolution_time_hours`

**Semantic model defines:**
- `open_ticket` = ticket WHERE status IN ('open', 'pending')
- `avg_resolution_time` = AVG(resolution_time_hours) WHERE status = 'resolved'
- `csat` = AVG(csat_score) WHERE csat_score IS NOT NULL
- `high_priority_ticket` = ticket WHERE priority = 'P1' OR priority = 'P2'

**Demo questions:**
1. "How many open tickets do we have right now by category?"
2. "What is our average resolution time for enterprise customers vs. free tier?"
3. "Which agent resolves tickets fastest on average?"
4. "What is our CSAT score trend over the last 6 months?"
5. "What percentage of high-priority tickets are still open?"

**Trust demonstration:** For question 5, the UI shows:
- SQL with CTE breaking down total high-priority tickets vs. open ones
- Assumption: "'high-priority' defined as priority IN ('P1','P2') per semantic model"
- Confidence: High
- Notes: "CSAT score is null for 12% of tickets; those rows are excluded from CSAT calculations but included in ticket counts."

---

### Demo 3: SaaS Funnel Analytics

**Dataset:** `saas_funnel.csv`
Columns: `user_id`, `signup_date`, `trial_start_date`, `trial_end_date`, `converted_date`, `plan`, `mrr`, `churned_date`, `acquisition_channel`, `company_size`

**Semantic model defines:**
- `active_subscriber` = user WHERE converted_date IS NOT NULL AND churned_date IS NULL
- `churned_user` = user WHERE churned_date IS NOT NULL
- `mrr` = SUM(mrr) WHERE active_subscriber
- `trial_to_paid_rate` = COUNT(converted_date) / COUNT(trial_start_date)
- `churn_rate` = COUNT(churned_date) / COUNT(converted_date) over a rolling 30-day window

**Demo questions:**
1. "What is our current MRR by plan tier?"
2. "What is our trial-to-paid conversion rate by acquisition channel?"
3. "How many users churned last month, and what was their average tenure?"
4. "Which company size segment has the highest churn rate?"
5. "Show me MRR growth over the last 12 months."

**Trust demonstration:** For question 3, the UI shows:
- Two-part SQL: one query for churn count, one for average tenure calculation
- Term mapping: "churned user → churned_date IS NOT NULL; tenure = days between signup_date and churned_date"
- Assumption: "'last month' = February 2026"
- Confidence: Medium — note: "tenure calculation assumes signup_date is not null; 3% of rows have null signup_date and are excluded"

---

## 8. Success Metrics

### Product Quality
- A first-time user can upload a CSV and get a correct, inspectable answer within 10 minutes of starting the app.
- At least 80% of questions about the three demo datasets return correct SQL on first attempt (measured by automated test harness).
- The UI renders trust information (SQL, assumptions, confidence) for 100% of AI-generated answers.

### Developer Experience
- `docker-compose up` works on a clean Mac and Linux machine with no additional configuration.
- Test suite runs in under 60 seconds.
- A new contributor can set up a local dev environment following CONTRIBUTING.md in under 20 minutes.

### OSS Community Readiness
- The repo has a complete README, CONTRIBUTING.md, CODE_OF_CONDUCT.md, and issue templates.
- All public APIs are documented in OpenAPI.
- All semantic model fields are documented in JSON schema with descriptions.

---

## 9. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM generates incorrect SQL despite grounding | High | High | Show SQL always; let user flag; add test harness with known-good Q&A pairs |
| DuckDB memory limits on large files | Medium | Medium | Add file size warning at upload; document 500MB practical limit for V1 |
| YAML semantic model is too verbose for non-technical users | Medium | Medium | Provide UI editor as primary path; YAML is secondary for developers |
| Local LLM (Ollama) quality is poor for SQL generation | High | Medium | Document known limitations; default to cloud LLM; test against both |
| Users misinterpret confidence indicators | Low | Medium | Add tooltip explanations; document what confidence levels mean |
