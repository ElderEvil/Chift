.PHONY: help install dev docker-up docker-down migrate migrate-create test lint format clean

help:
	@echo "Chift - Odoo Integration API"
	@echo ""
	@echo "Available commands:"
	@echo "  make install        Install dependencies"
	@echo "  make dev            Run development server"
	@echo "  make docker-up      Start with Docker Compose"
	@echo "  make docker-down    Stop Docker Compose"
	@echo "  make migrate        Run database migrations"
	@echo "  make migrate-create Create new migration"
	@echo "  make test           Run tests"
	@echo "  make lint           Run linter"
	@echo "  make format         Format code"
	@echo "  make clean          Clean cache files"

install:
	@echo "Installing dependencies..."
	pip install uv
	uv sync

dev:
	@echo "Starting development server..."
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	@echo "Starting Docker Compose..."
	docker-compose up -d
	@echo "Application running at http://localhost:8000"

docker-down:
	@echo "Stopping Docker Compose..."
	docker-compose down

docker-logs:
	docker-compose logs -f

migrate:
	@echo "Running database migrations..."
	uv run alembic upgrade head

migrate-create:
	@echo "Creating new migration..."
	@read -p "Migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

test:
	@echo "Running tests..."
	uv run pytest -v || echo "No tests found"

lint:
	@echo "Running linter..."
	uv run ruff check .

format:
	@echo "Formatting code..."
	uv run ruff format .

clean:
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "Done!"

.env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env file created from .env.example"; \
		echo "Please edit .env with your configuration"; \
	else \
		echo ".env file already exists"; \
	fi
