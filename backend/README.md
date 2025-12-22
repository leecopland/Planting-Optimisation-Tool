# Not complete, just jotting notes

Activate virtual environment

```bash
source .venv/bin/activate
```

## Makefile commands

run `make [target]` in `/backend` to execute.

| Target | Purpose | Shell Commands Executed |
| :--- | :--- | :--- |
| **`help`** | Shows all available `make` commands | Iterates over all targets and outputs to the terminal |
| **`setup`** | Initializes the database container from scratch (`db-teardown`, `db-start`, `db-migrate`, ), starts the service, and applies all pending Alembic migrations. | 1. `docker compose down` (via `db-stop`)<br> 2. `docker compose up -d db` (via `db-start`)<br> 3. `sleep 5` <br> 4. **`uv run dotenv run alembic upgrade head` (via `db-apply`)** |
| **`populate-dev-db`** | Wipes the DB, migrates, and ingests all CSV data. | Runs `setup_import_db.sh` | 
| **`db-stop`** | Stops the PostgreSQL container. | `docker compose down` |
| **`db-start`** | Ensures a clean state (`db-teardown`) then starts the PostgreSQL container service in detached mode. | 1. `docker compose down -v` (via `db-teardown`) 2. `docker compose up -d db` 3. `sleep 5` |
| **`revision`** | **GENERATES** a new Alembic migration script based on changes detected in your Python models. **Requires `M="message"`**. After running, you must **review the script** before running `make db-apply`. | `uv run dotenv run alembic revision --autogenerate -m "message"` |
| **`db-apply`** | Applies any pending Alembic migration scripts to upgrade the database schema to the latest version. This is the final step after creating and reviewing a script. | `uv run dotenv run alembic upgrade head` |
| **`test`** | Executes the full test suite using Pytest on the contents of the `tests/` directory. | `uv run dotenv run pytest tests/` |
| **`db-stop`** | Stops the running PostgreSQL container without removing the data volumes, preserving current data. | `docker compose stop` |
| **`schema`** | Generates a markdown formatted schema diagram and writes it to **`SCHEMA.md`**. | `uv run dotenv run python -m src.generate_schema > SCHEMA.md` |
| **`erd`** | Generates an Entity-Relationship Diagram of the database and outputs to **`ERD.svg`**. | `uv run dotenv run python -m src.generate_erd` |
| **`psql`** | Starts an interactive psql DB session | `docker exec -it pot_postgres_db psql -U postgres -d POT_db` |
| **`kill-api`** | Kills the API server running on port 8080 <br> Because `populate_dev_db` starts the api in the background for ease-of-use. | For Linux/MacOS: <br> `lsof -t -i:8080 \| xargs kill -9 2>/dev/null \|\| true` <br> For Windows: <br> `taskkill //F //FI "PID ge 1" //FI "EXENAME eq python.exe" //FI "WINDOWTITLE eq fastapi*" /T 2>/dev/null \|\| true` |