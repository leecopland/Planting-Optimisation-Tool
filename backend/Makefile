SERVICE_NAME = db
CONTAINER_NAME = pot_postgres_db
ALEMBIC_CMD = uv run dotenv run alembic
PYTHON_PATH_ROOT = .
PYTEST_RUNNER = uv run dotenv run
PYTEST_CMD = $(PYTEST_RUNNER) pytest
UV_RUNNER = uv run dotenv run
FASTAPI_TARGET = src/main.py
FASTAPI_CMD = fastapi dev $(FASTAPI_TARGET) --port 8080 --reload

.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# The primary command for a developer to set up the project from scratch.
setup: db-teardown db-start db-migrate ## Initializes or updates the database
	@echo "--- Setup/Update Complete ---"

.PHONY: db-teardown
db-teardown: ## Stops and removes containers but PRESERVES data volumes
	@echo "--- Stopping PostgreSQL Container (Preserving Data) ---"
	docker compose down


.PHONY: db-start
db-start: ## Starts the container if it's not running
	@echo "--- Starting PostgreSQL Container ---"
	docker compose up -d $(SERVICE_NAME)
	@echo "Waiting for DB to be ready..."
	sleep 5

.PHONY: db-migrate 
db-migrate: ## Applies the schema migration
	@echo "--- Applying Schema Migration ---"
	$(ALEMBIC_CMD) upgrade head

.PHONY: db-reset
db-reset: ## Stops and WIPES everything (Use with caution)
	@echo "--- WARNING: Wiping Database and Volumes ---"
	docker compose down -v
	$(MAKE) db-start

.PHONY: revision 
revision: ## Generate a new DB alembic autogenerate revision
	@echo "--- Generating New Migration Script ---"
	@if [ -z "$M" ]; then \
		echo "Error: Migration message not provided. Use: make revision M=\"Your message\""; \
		exit 1; \
	fi
	# Step 1: Create the script (with autogenerate)
	$(ALEMBIC_CMD) revision --autogenerate -m "$M"
	@echo ""
	@echo "--- SCRIPT CREATED. NEXT ACTION REQUIRED: REVIEW/EDIT ---"
	@echo "1. Script created in alembic/versions/. Open and inspect the upgrade() function."
	@echo "2. If you renamed a column or dropped data, manually correct the script (e.g., use op.alter_column)."
	@echo ""
	@echo "3. TO APPLY THE CHANGE, RUN: make db-migrate"

.PHONY: rename-column 
rename-column: ## Rename a column
	@echo "--- STARTING MANUAL RENAME PROCEDURE ---"
	@echo "1. Ensure the column name is changed ONLY in your SQLAlchemy model."
	@echo "2. Generating a BLANK revision script now (DO NOT USE --autogenerate)..."
	# Generate a manual, blank script (no --autogenerate flag)
	$(ALEMBIC_CMD) revision -m "MANUAL_RENAME_REQUIRED"
	@echo ""
	@echo "--- SCRIPT CREATED. NEXT ACTION REQUIRED: EDIT MANUALLY ---"
	@echo "3. Find the script in alembic/versions/ and manually ADD the op.alter_column command."
	@echo "   Example: op.alter_column('table', 'old', new_column_name='new', ...)"
	@echo ""
	@echo "4. TO APPLY THE RENAME, RUN: make db-migrate"


.PHONY: test 
test: ## Run all tests with environment loaded
	@echo "--- Running Pytest ---"
	$(PYTEST_CMD) tests/


.PHONY: db-stop 
db-stop: ## Stop the database without removing data volumes
	@echo "--- Stopping PostgreSQL Container ---"
	docker compose stop


.PHONY: schema 
schema: ## Outputs current DB schema to SCHEMA.md from models
	@echo "--- Generating SCHEMA.md from Models ---"
	$(UV_RUNNER) python -m src.generate_schema > SCHEMA.md
	@echo "--- SCHEMA.md created ---"


.PHONY: erd 
erd: ## Outputs ER-Diagram to ERD.svg
	@echo "--- Generating ER-Diagram from Database ---"
	$(UV_RUNNER) python -m src.generate_erd
	@echo "--- ER-Diagram created ---"


.PHONY: run-api 
run-api: ## Start the FastAPI server on port 8080
	@echo "--- Starting FastAPI Server on http://0.0.0.0:8080 ---"
	$(UV_RUNNER) $(FASTAPI_CMD)


.PHONY: psql 
psql: ## Start an interactive psql shell session
	docker exec -it pot_postgres_db psql -U postgres -d POT_db

.PHONY: populate-dev-db
populate-dev-db: ## Wipe DB, apply migrations, and run all ingestion scripts (Seeders, Farms, Boundaries, Species)
	@echo "Preparing data ingestion environment..."
	@chmod +x src/scripts/setup_import_db.sh
	@echo "Running database data import script..."
	@./src/scripts/setup_import_db.sh

.PHONY: kill-api
kill-api: ## Kill the API server running on port 8080
	@echo "Stopping API server on port 8080..."
	@# For Mac/Linux:
	@lsof -t -i:8080 | xargs kill -9 2>/dev/null || true
	@# For Windows (Git Bash):
	@taskkill //F //FI "PID ge 1" //FI "EXENAME eq python.exe" //FI "WINDOWTITLE eq fastapi*" /T 2>/dev/null || true
	@# Generic fallback for Windows port targeting:
	@for /f "tokens=5" %a in ('netstat -aon ^| findstr :8080') do taskkill /f /pid %a 2>/dev/null || true