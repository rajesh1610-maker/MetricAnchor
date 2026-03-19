# Contributing to MetricAnchor

Thank you for your interest in contributing. MetricAnchor is designed to be a learning resource and a real open-source tool — good contributions at any skill level are welcome.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Development Setup](#development-setup)
- [Local Development Without Docker](#local-development-without-docker)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Reporting Bugs](#reporting-bugs)
- [Proposing Features](#proposing-features)
- [Adding a Connector](#adding-a-connector)
- [Contributing a Semantic Model](#contributing-a-semantic-model)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it. Report violations to the maintainers via a GitHub issue marked `[conduct]`.

---

## Ways to Contribute

You don't need to write code to contribute.

| Type | How |
|---|---|
| Bug report | Open a GitHub issue using the bug report template |
| Feature request | Open a GitHub issue using the feature request template |
| Semantic model | Add a YAML model to `examples/` and open a PR |
| Sample dataset | Add a CSV to `sample_data/` with a matching semantic model |
| Documentation | Edit docs in `docs/` or improve README sections |
| Tests | Add test cases for untested behavior |
| New connector | Implement `BaseConnector` and open a PR |
| Code review | Review open PRs — feedback on design is as valuable as code |

---

## Development Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/)
- [Git](https://git-scm.com/)
- [Make](https://www.gnu.org/software/make/) (pre-installed on macOS and Linux)

### Steps

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/metricanchor.git
cd metricanchor

# 2. Add the upstream remote
git remote add upstream https://github.com/your-username/metricanchor.git

# 3. Copy the environment file and configure your LLM key
cp .env.example .env
# Edit .env — at minimum, set LLM_PROVIDER and LLM_API_KEY

# 4. Start all services
make up

# 5. Verify everything is running
make health

# 6. Run the test suite to confirm your setup works
make test
```

The web UI is at http://localhost:3000 and the API docs are at http://localhost:8000/api/docs.

---

## Local Development Without Docker

### Backend (FastAPI)

```bash
cd apps/api

# Create a virtual environment (Python 3.12 recommended)
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy env and start the dev server
cp ../../.env.example .env
uvicorn main:app --reload --port 8000
```

### Frontend (Next.js)

```bash
cd apps/web

# Install dependencies
npm install

# Start the dev server
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

The web UI will be at http://localhost:3000.

---

## Project Structure

```
metricanchor/
├── apps/
│   ├── api/            # FastAPI backend
│   └── web/            # Next.js frontend
├── packages/
│   ├── semantic_model/ # YAML model format, validator, schema
│   ├── query_engine/   # DuckDB query execution
│   ├── llm_adapter/    # Provider-agnostic LLM abstraction
│   └── shared/         # Shared types and utilities
├── examples/           # Sample semantic models
├── sample_data/        # Demo CSV datasets
├── tests/              # Integration and end-to-end tests
├── docs/               # Architecture, roadmap, guides
└── .github/            # CI, issue templates, PR template
```

**Key design rule:** Each package in `packages/` must be independently importable and testable. Do not add cross-package imports that create circular dependencies.

---

## Making Changes

### Branch naming

```
feat/short-description     # New feature
fix/short-description      # Bug fix
docs/short-description     # Documentation only
test/short-description     # Tests only
chore/short-description    # Dependencies, tooling
```

### Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(api): add schema profiler endpoint
fix(llm_adapter): handle timeout errors from Anthropic API
docs: update architecture diagram in README
test(query_engine): add DuckDB edge case for empty result sets
```

### Code style

**Python:** Formatted with [ruff](https://docs.astral.sh/ruff/). Run `make lint` before committing.

```bash
# Check
ruff check apps/api packages/

# Auto-fix
ruff check --fix apps/api packages/
ruff format apps/api packages/
```

**TypeScript:** Linted with ESLint and formatted with Prettier. Run `npm run lint` inside `apps/web/` before committing.

---

## Testing

All PRs must include tests for new behavior. Existing tests must not be broken.

### Backend tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run a specific test file
cd apps/api && pytest tests/test_ingest.py -v
```

Tests live in two places:
- `apps/api/tests/` — unit and integration tests for the API
- `tests/` — end-to-end integration tests that test the full stack

### Frontend tests

```bash
cd apps/web
npm run test        # Unit tests (Vitest)
npm run test:e2e    # Playwright smoke tests
```

### Test requirements for PRs

| Change type | Required tests |
|---|---|
| New API endpoint | At least one happy-path and one error-path test |
| New semantic model field | Schema validation test (valid and invalid) |
| New LLM adapter | Mock-based unit test + documented manual test steps |
| New connector | Integration test against a real or in-process database |
| Bug fix | A regression test that would have caught the bug |
| UI feature | Playwright smoke test covering the happy path |

---

## Submitting a Pull Request

1. Ensure your branch is up to date with upstream main:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```
2. Run the full test suite: `make test`
3. Run the linter: `make lint`
4. Push your branch and open a PR against `main`.
5. Fill out the PR template — include what changed, why, and how to test it.
6. A maintainer will review within a few days. Be responsive to review comments.

**PRs that will not be merged:**
- Code without tests for new behavior
- PRs that break existing tests
- Changes that bypass the semantic model validation layer
- Hardcoded API keys or credentials
- PRs that add dependencies without justification in the PR description

---

## Reporting Bugs

Use the [bug report issue template](.github/ISSUE_TEMPLATE/bug_report.yml).

Include:
- Steps to reproduce (exact commands or UI actions)
- Expected behavior
- Actual behavior
- Your environment (OS, Docker version, LLM provider)
- Relevant logs (`make logs` or `docker-compose logs api`)

---

## Proposing Features

Use the [feature request issue template](.github/ISSUE_TEMPLATE/feature_request.yml).

Before proposing, check:
- The [roadmap](docs/roadmap.md) — it may already be planned.
- Open issues — someone may have raised it already.

Good proposals explain the user problem, not just the solution.

---

## Adding a Connector

A connector extends MetricAnchor to query a new data source (PostgreSQL, Snowflake, etc.).

1. Create `packages/query_engine/connectors/your_connector.py`
2. Implement the `BaseConnector` interface (see `packages/query_engine/connectors/base.py`)
3. Register it in `packages/query_engine/connectors/__init__.py`
4. Add an integration test
5. Add documentation in `docs/connectors.md`
6. Open a PR with all four artifacts

See [docs/connectors.md](docs/connectors.md) for the full interface specification.

---

## Contributing a Semantic Model

Semantic model contributions are the lowest-friction way to contribute.

1. Create a directory under `examples/your_use_case/`
2. Add a `semantic_model.yml` following the format in `examples/retail_sales/`
3. Add a matching sample CSV (max 500 rows, no PII) to `sample_data/`
4. Validate: `metricanchor validate examples/your_use_case/semantic_model.yml`
5. Add a short `README.md` describing the use case and sample questions
6. Open a PR

The JSON schema for semantic models is at `packages/semantic_model/schema.json`.

---

## Questions?

Open a [GitHub Discussion](https://github.com/your-username/metricanchor/discussions) for anything that isn't a bug or feature request. This is the best place for questions about architecture, design decisions, or how to approach a contribution.
