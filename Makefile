.PHONY: help dev up down build test lint format migrate

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start development environment
	docker-compose -f docker-compose.dev.yml up -d

up: ## Start production environment
	docker-compose up -d --build

down: ## Stop all containers
	docker-compose down

build: ## Build all containers
	docker-compose build

test: ## Run backend tests
	cd backend && python -m pytest tests/ -v --cov=app

lint: ## Run linters
	cd backend && ruff check app/ && mypy app/

format: ## Format code
	cd backend && black app/ tests/ && ruff check --fix app/

migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MSG="description")
	cd backend && alembic revision --autogenerate -m "$(MSG)"

shell: ## Open Python shell
	cd backend && python -c "import IPython; IPython.start_ipython()" 2>/dev/null || python

logs: ## Show container logs
	docker-compose logs -f

clean: ## Clean up containers, volumes, and caches
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
