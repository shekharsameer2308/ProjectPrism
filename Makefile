# ==============================================================================
# Omnichannel Marketing ROI & Attribution Engine - Master Makefile
# ==============================================================================
.DEFAULT_GOAL := help
SHELL := /bin/bash

PYTHON := $(shell which python3.12 2>/dev/null || which python3.11 2>/dev/null || which python3 2>/dev/null)
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

.PHONY: help setup generate ingest-gcs ingest-bq run test lint format dbt-deps dbt-build dbt-docs airflow-up airflow-down clean

help: ## Show this help menu
	@echo "=========================================================================="
	@echo "Omnichannel Marketing ROI & Attribution Engine - CLI Commands"
	@echo "=========================================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

setup: ## Set up local environment, directories, and virtualenv
	@echo "--> Setting up directories..."
	@mkdir -p data/raw data/processed credentials airflow/logs dbt_project/target
	@if [ ! -f .env ]; then \
		echo "--> Creating .env from .env.example..."; \
		cp .env.example .env; \
	fi
	@if [ ! -d "$(VENV)" ]; then \
		echo "--> Creating virtual environment with $(PYTHON)..."; \
		$(PYTHON) -m venv $(VENV); \
	fi
	@echo "--> Installing dependencies in $(VENV)..."
	@$(VENV_PIP) install --upgrade pip
	@$(VENV_PIP) install -r requirements.txt
	@echo "==> Setup completed successfully."

generate: ## Generate synthetic omnichannel marketing and sales data (Seed=42)
	@echo "--> Generating synthetic datasets into data/raw/..."
	@if [ -f "$(VENV_PYTHON)" ]; then \
		$(VENV_PYTHON) data_gen/generate.py; \
	else \
		python3 data_gen/generate.py; \
	fi

ingest-gcs: ## Ingest partitioned raw data to Google Cloud Storage
	@echo "--> Uploading date-partitioned files to GCS..."
	@if [ -f "$(VENV_PYTHON)" ]; then \
		$(VENV_PYTHON) ingestion/load_to_gcs.py; \
	else \
		python3 ingestion/load_to_gcs.py; \
	fi

ingest-bq: ## Load raw tables from GCS into BigQuery raw dataset
	@echo "--> Loading raw dataset into BigQuery..."
	@if [ -f "$(VENV_PYTHON)" ]; then \
		$(VENV_PYTHON) ingestion/load_to_bq.py; \
	else \
		python3 ingestion/load_to_bq.py; \
	fi

dbt-deps: ## Install dbt package dependencies (dbt_utils, dbt_expectations)
	@echo "--> Installing dbt packages..."
	@cd dbt_project && dbt deps

dbt-build: ## Execute dbt run and dbt test across all layers
	@echo "--> Running dbt build (staging, intermediate, marts)..."
	@cd dbt_project && dbt build

dbt-docs: ## Generate and serve dbt documentation and lineage graph
	@echo "--> Generating dbt documentation..."
	@cd dbt_project && dbt docs generate && dbt docs serve

run: generate ## Execute end-to-end pipeline: generate, ingest to GCS & BQ, and run dbt
	@echo "--> Running end-to-end pipeline..."
	@$(MAKE) ingest-gcs
	@$(MAKE) ingest-bq
	@$(MAKE) dbt-build
	@echo "==> End-to-end pipeline execution complete."

test: ## Run unit tests, data verification tests, and dbt tests
	@echo "--> Running pytest suites..."
	@if [ -f "$(VENV_PYTHON)" ]; then \
		$(VENV)/bin/pytest -v data_gen/tests; \
	else \
		pytest -v data_gen/tests; \
	fi

lint: ## Run code linter checks (Ruff & SQLFluff)
	@echo "--> Linting Python files..."
	@ruff check data_gen/ ingestion/ airflow/
	@echo "--> Linting dbt SQL models..."
	@cd dbt_project && sqlfluff lint models/

format: ## Format code automatically
	@ruff format data_gen/ ingestion/ airflow/

airflow-up: ## Start Airflow locally with Docker Compose
	@echo "--> Initializing and launching Airflow services..."
	@mkdir -p airflow/logs
	@docker compose up -d
	@echo "==> Airflow running at http://localhost:8080 (airflow / airflow)"

airflow-down: ## Stop Airflow Docker Compose services
	@echo "--> Stopping Airflow services..."
	@docker compose down

clean: ## Clean generated data, virtualenv, and build artifacts
	@echo "--> Cleaning up temporary files and caches..."
	@rm -rf data/raw/* data/processed/* dbt_project/target .pytest_cache .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "==> Clean complete."
