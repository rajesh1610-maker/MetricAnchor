# MetricAnchor — User Personas

**Version:** 1.0 (Phase 0 — Discovery)
**Last Updated:** 2026-03-19

---

## Overview

MetricAnchor serves two distinct user types who interact with the system at different layers of abstraction. Both personas have been grounded in realistic job contexts and real pain points. Neither persona is hypothetical filler — every product decision in V1 maps to at least one of them.

---

## Persona 1: Maya — The Business Analyst Who Owns Her Data

**Role:** Senior Marketing Analyst, mid-size e-commerce company (~200 employees)
**Tech comfort:** Advanced spreadsheet user, knows a bit of SQL, uses Tableau and Looker but does not administer them, comfortable running local tools with a README
**Age:** 34
**Location:** Works remotely

### Background
Maya's team runs a weekly revenue review. Every Monday morning she has a list of 10–15 ad-hoc questions that the pre-built Looker dashboards don't answer. She used to file requests with the data team and wait 3–5 days. Last year the data team was cut to 2 people. Now she tries to write her own SQL but regularly gets wrong answers because the column names and business definitions live only in her head and in a Confluence doc that's 18 months out of date.

She heard about AI tools for data analysis. She tried ChatGPT with a CSV upload. It gave her an answer with no way to verify it. She didn't know if the revenue number included returns or not. She stopped trusting it.

### Goals
- Get answers to ad-hoc data questions without waiting for an analyst.
- Trust the answers she gets — she is presenting to the CMO, so she cannot afford to show wrong numbers.
- Understand what "revenue" means in the context of each report so she can explain it to stakeholders.
- Build up a library of reliable metrics her team can reuse.

### Pain Points
- Business definitions are tribal knowledge. "Revenue" means different things to sales, finance, and marketing.
- AI tools feel like black boxes. She can't verify what they did.
- Setting up data tools feels like an IT project. She doesn't have admin rights to install things on her work machine — but she can run Docker.
- She spends 30–45 minutes per question chasing down column names, double-checking filters, and validating outputs.

### How She Uses MetricAnchor
1. Uploads her weekly CSV export from the company's order management system.
2. Reviews the auto-generated schema profile to confirm column names and types look right.
3. Defines her team's metric definitions once ("revenue = order_total where status not in ('cancelled', 'returned')").
4. Asks questions in plain English every Monday morning.
5. Before presenting a number to her CMO, she clicks "Show SQL" and double-checks the filters.
6. When an answer looks off, she clicks "Report a problem" and notes what she expected.

### Jobs to Be Done
- When I have a new data question, I want to get an answer in under 5 minutes so I can stay in flow instead of waiting on the data team.
- When I show a number to my CMO, I want to be able to explain exactly how it was calculated so I don't look unprepared.
- When I define what "active customer" means, I want every future answer to use that same definition automatically.

### Frustration Signals
- "I just need to know what our refund rate was last quarter, why is this so hard?"
- "I got a different number from the AI than from Looker and I don't know which one to trust."
- "My manager asked me to break down revenue by channel and I've been staring at this for an hour."

### Success Looks Like
Maya uploads a file, defines 5–6 metrics, and runs her entire Monday morning Q&A in under 30 minutes — with SQL visible for each answer. She stops filing data requests for routine questions.

---

## Persona 2: Dev — The Analytics Engineer Who Builds and Extends

**Role:** Analytics Engineer / Backend Developer, startup (Series B, ~80 engineers)
**Tech comfort:** Python, SQL, dbt, Git, Docker, REST APIs, comfortable reading source code
**Age:** 28
**Location:** Works in a hybrid office

### Background
Dev has been building internal analytics tools for two years. His company's data stack is dbt + BigQuery + Metabase. He's seen the promise of AI-powered analytics tools but has been burned by vendor lock-in and black-box behavior. He's specifically frustrated that most AI analytics products:
- Don't let you inspect what the AI is actually doing.
- Use proprietary semantic model formats you can't version-control.
- Fail silently when the LLM generates bad SQL.
- Are too expensive for internal tooling experiments.

He discovered MetricAnchor on GitHub. He wants to fork it, extend it, and potentially run it as an internal analytics tool. He's also interested in contributing back to the project.

### Goals
- Run a trustworthy AI analytics layer on top of CSV or Parquet files for internal use.
- Edit semantic models in code (YAML) and version-control them.
- Inspect generated SQL and LLM prompts when something goes wrong.
- Extend connectors to support new data sources.
- Contribute to the OSS project and build public portfolio visibility.

### Pain Points
- Most AI analytics tools are black boxes — no way to see the prompt, the plan, or the intermediate steps.
- Vendor semantic model formats are proprietary and can't be versioned in Git.
- LLM tools fail silently — they return a result even when the SQL is wrong.
- Bad OSS documentation makes contribution painful.
- Tools with poor test coverage are scary to extend.

### How He Uses MetricAnchor
1. Clones the repo and runs `docker-compose up` to explore the architecture.
2. Reads `docs/architecture.md` and the FastAPI source to understand the query pipeline.
3. Edits `semantic_models/retail_sales.yml` to add a custom computed metric.
4. Runs `metricanchor validate` to check the YAML is valid.
5. Asks a question in the UI and uses the "Developer View" toggle to see the full LLM prompt and response.
6. Writes a pytest integration test for the new metric.
7. Opens a GitHub issue proposing a Postgres connector and starts a discussion.

### Jobs to Be Done
- When I onboard to a new analytics tool, I want to read the architecture in one sitting so I can understand how to extend it.
- When the AI gives a wrong answer, I want to inspect the prompt, the SQL plan, and the execution log so I can fix the root cause.
- When I define a new metric, I want to write it in YAML and commit it to Git like any other piece of infrastructure.
- When I contribute a PR, I want clear contribution guidelines and a CI pipeline that catches issues before review.

### Frustration Signals
- "This tool doesn't have a single test. How do I know what I'm breaking?"
- "I want to add a Postgres connector but the connector interface isn't documented anywhere."
- "The LLM is clearly hallucinating a column name that doesn't exist and the tool just returns a query error with no explanation."
- "The semantic model format is some proprietary JSON blob. I can't version-control this properly."

### Success Looks Like
Dev forks MetricAnchor, adds a connector for a new data source, writes tests, and submits a PR in under 2 hours. The CONTRIBUTING.md and test setup were clear enough that he didn't have to ask anyone for help. He mentions the project in his personal blog post.

---

## Persona Comparison

| Dimension | Maya (Citizen Developer) | Dev (Analytics Engineer) |
|---|---|---|
| SQL fluency | Basic | Advanced |
| Primary interface | Web UI | CLI + code editor + UI |
| Key feature needed | Clean answers + trust signals | Inspectability + extensibility |
| Semantic model editing | Via UI form | Via YAML + code editor |
| LLM prompt visibility | Does not need to see | Wants full access |
| Feedback mechanism | "Report a problem" button | GitHub issue + direct YAML edit |
| Onboarding expectation | 5 min, no setup friction | 15 min with README + CONTRIBUTING.md |
| Failure tolerance | Low — wrong answer = broken trust | Moderate — can debug, but hates silent failures |
| OSS contribution intent | No | Yes |

---

## Anti-Personas (Who We Are Not Building For)

### The Enterprise Data Administrator
Needs SSO, RBAC, audit logs, compliance controls, and multi-tenant isolation. MetricAnchor V1 is not designed for enterprise deployment. A future roadmap item can address this.

### The Data Scientist Running Complex ML
MetricAnchor is an analytics Q&A tool, not a Jupyter notebook replacement. It does not support arbitrary Python execution, model training, or complex statistical analysis beyond SQL aggregations.

### The Non-Technical Executive Who Wants a Dashboard
MetricAnchor requires some initial setup (defining semantic models). A pure end-user who wants a beautiful pre-built dashboard with zero configuration is better served by a traditional BI tool. MetricAnchor is for people willing to invest 30 minutes in setup to get trustworthy ad-hoc answers.
