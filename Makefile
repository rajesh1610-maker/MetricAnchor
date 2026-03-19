.DEFAULT_GOAL := help
SHELL         := /bin/bash
API_DIR       := apps/api
WEB_DIR       := apps/web

.PHONY: help up down logs build test test-coverage lint lint-fix validate seed health clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── Docker ────────────────────────────────────────────────────────────────────

up: ## Start all services (detached)
	docker compose up -d
	@echo ""
	@echo "  Web UI  → http://localhost:3000"
	@echo "  API     → http://localhost:8000"
	@echo "  API docs→ http://localhost:8000/api/docs"
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

health: ## Check API health endpoint
	@curl -sf http://localhost:8000/api/health | python3 -m json.tool || \
		(echo "API is not responding. Run 'make up' first." && exit 1)

# ── Testing ───────────────────────────────────────────────────────────────────

test: ## Run the full test suite
	@echo "Running backend tests..."
	cd $(API_DIR) && python -m pytest tests/ -v --tb=short
	@echo ""
	@echo "Running integration tests..."
	python -m pytest tests/ -v --tb=short

test-coverage: ## Run tests with coverage report
	cd $(API_DIR) && python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
	@echo "Coverage report: $(API_DIR)/htmlcov/index.html"

test-e2e: ## Run Playwright end-to-end tests
	cd $(WEB_DIR) && npx playwright test

# ── Linting ───────────────────────────────────────────────────────────────────

lint: ## Run all linters (Python + TypeScript)
	@echo "Linting Python..."
	cd $(API_DIR) && ruff check . && ruff format --check .
	@echo "Linting packages..."
	ruff check packages/
	@echo "Linting TypeScript..."
	cd $(WEB_DIR) && npm run lint

lint-fix: ## Auto-fix lint issues where possible
	cd $(API_DIR) && ruff check --fix . && ruff format .
	ruff check --fix packages/ && ruff format packages/
	cd $(WEB_DIR) && npm run lint -- --fix

# ── Semantic Model ────────────────────────────────────────────────────────────

validate: ## Validate all semantic models in examples/
	@for f in examples/*/semantic_model.yml; do \
		echo "Validating $$f..."; \
		python -m packages.semantic_model.validator $$f || exit 1; \
	done
	@echo "All semantic models valid."

# ── Sample Data ───────────────────────────────────────────────────────────────

seed: ## Upload sample datasets to a running API
	@echo "Seeding sample datasets..."
	@curl -sf http://localhost:8000/api/health > /dev/null || \
		(echo "API is not running. Run 'make up' first." && exit 1)
	curl -s -X POST http://localhost:8000/api/datasets \
		-F "file=@sample_data/retail_sales.csv" | python3 -m json.tool
	curl -s -X POST http://localhost:8000/api/datasets \
		-F "file=@sample_data/support_tickets.csv" | python3 -m json.tool
	curl -s -X POST http://localhost:8000/api/datasets \
		-F "file=@sample_data/saas_funnel.csv" | python3 -m json.tool
	@echo "Done. Open http://localhost:3000 to explore."

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
