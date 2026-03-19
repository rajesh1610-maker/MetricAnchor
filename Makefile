.DEFAULT_GOAL := help
SHELL         := /bin/bash
API_DIR       := apps/api
WEB_DIR       := apps/web
PYTHON        := $(API_DIR)/.venv/bin/python3
PYTEST        := $(PYTHON) -m pytest
CLI           := $(PYTHON) -m cli.main

.PHONY: help up down logs build \
        test test-api test-coverage test-e2e test-eval \
        lint lint-fix typecheck validate \
        generate-data seed seed-reset \
        health status \
        cli-ingest cli-ask \
        clean clean-data

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Docker ────────────────────────────────────────────────────────────────────

up: ## Start all services (detached)
	docker compose up -d
	@echo ""
	@echo "  Web UI   → http://localhost:3000"
	@echo "  API      → http://localhost:8000"
	@echo "  API docs → http://localhost:8000/api/docs"
	@echo ""
	@echo "Run 'make logs' to follow service output."

down: ## Stop and remove containers
	docker compose down

build: ## Rebuild all Docker images
	docker compose build

logs: ## Tail logs from all services
	docker compose logs -f

logs-api: ## Tail API logs only
	docker compose logs -f api

logs-web: ## Tail web logs only
	docker compose logs -f web

# ── Health ────────────────────────────────────────────────────────────────────

health: ## Check API health endpoint (raw JSON)
	@curl -sf http://localhost:8000/api/health | python3 -m json.tool || \
		(echo "API is not responding. Run 'make up' first." && exit 1)

status: ## Check API status via CLI (coloured output)
	$(CLI) status

# ── Testing ───────────────────────────────────────────────────────────────────

test: ## Run unit + integration + eval tests (no API key or server needed)
	@echo "── Unit tests ─────────────────────────────────────────────────────"
	$(PYTEST) tests/unit/ -q --tb=short
	@echo ""
	@echo "── Integration tests ──────────────────────────────────────────────"
	$(PYTEST) tests/integration/ -q --tb=short
	@echo ""
	@echo "── Eval suite ─────────────────────────────────────────────────────"
	$(PYTEST) evals/test_evals.py -q --tb=short

test-api: ## Run API-level tests (no running server needed)
	cd $(API_DIR) && .venv/bin/python3 -m pytest tests/ -v --tb=short

test-coverage: ## Run API tests with HTML coverage report
	cd $(API_DIR) && .venv/bin/python3 -m pytest tests/ -v \
		--cov=. --cov-report=html --cov-report=term-missing
	@echo "Coverage report: $(API_DIR)/htmlcov/index.html"

test-e2e: ## Run Playwright end-to-end tests (requires make up)
	cd $(WEB_DIR) && npx playwright test --config=../tests/e2e/playwright.config.ts

typecheck: ## Run TypeScript type checks
	cd $(WEB_DIR) && npm run typecheck

test-eval: ## Run live question evaluations (requires make up && make seed)
	$(PYTEST) tests/test_demo_questions.py -v --tb=short

# ── Linting ───────────────────────────────────────────────────────────────────

lint: ## Run all linters (Python + TypeScript)
	@echo "Linting Python (api)..."
	cd $(API_DIR) && ruff check . && ruff format --check .
	@echo "Linting Python (packages, cli)..."
	ruff check packages/ cli/
	@echo "Linting TypeScript..."
	cd $(WEB_DIR) && npm run lint

lint-fix: ## Auto-fix lint issues where possible
	cd $(API_DIR) && ruff check --fix . && ruff format .
	ruff check --fix packages/ cli/ && ruff format packages/ cli/
	cd $(WEB_DIR) && npm run lint -- --fix

# ── Semantic Model ────────────────────────────────────────────────────────────

validate: ## Validate all semantic models in examples/
	@for f in examples/*/semantic_model.yml; do \
		echo "Validating $$f..."; \
		$(PYTHON) -m packages.semantic_model.validator $$f || exit 1; \
	done
	@echo "All semantic models valid."

# ── Sample Data ───────────────────────────────────────────────────────────────

generate-data: ## Regenerate sample CSVs from scratch (deterministic, seed=42)
	python3 sample_data/generate.py

seed: ## Upload sample CSVs + create semantic models (API must be running)
	@echo "Seeding demo datasets and semantic models..."
	@curl -sf http://localhost:8000/api/health > /dev/null || \
		(echo "API is not running. Run 'make up' first." && exit 1)
	python3 scripts/seed_demo.py

seed-reset: ## Re-seed from scratch, replacing existing semantic models
	python3 scripts/seed_demo.py --reset

# ── CLI shortcuts ─────────────────────────────────────────────────────────────

cli-datasets: ## List all uploaded datasets
	$(CLI) datasets

cli-status: ## Show API status via CLI
	$(CLI) status

# ── Cleanup ───────────────────────────────────────────────────────────────────

clean: ## Remove build artifacts, caches, and test outputs
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf $(WEB_DIR)/.next $(WEB_DIR)/out
	@echo "Cleaned."

clean-data: ## Remove uploaded data and the SQLite database (DESTRUCTIVE)
	@echo "WARNING: This will delete all uploaded datasets and question history."
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	docker compose down -v
	@echo "Data volume removed."
