#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

export PYTHONPATH=$PYTHONPATH:.

cleanup() {
    if [ -n "$API_PID" ]; then
        echo -e "${BLUE} Shutting down background API (PID: $API_PID)...${NC}"
        kill $API_PID 2>/dev/null || taskkill //F //PID $API_PID //T 2>/dev/null || true
    fi
}

trap cleanup EXIT

# Define colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE} Starting Database Initialization${NC}"
echo -e "${BLUE}====================================================${NC}"

# Reset Database
echo -e "${GREEN}Resetting database and applying migrations${NC}"
make db-reset
make setup

# Seed Reference Tables
echo -e "${GREEN} Populating Soil Texture and Agroforestry Type enums${NC}"
uv run src/scripts/seed_references.py

# Create Test User
echo -e "${GREEN} Creating default test user${NC}"
uv run src/scripts/create_test_user.py

# Starting API server in background
uv run dotenv run fastapi dev src/main.py --port 8080 > api_log.txt 2>&1 &
API_PID=$!

# Waiting for API to be ready
echo "Waiting for API to respond on port 8080..."
for i in {1..15}; do
  if curl -s http://127.0.0.1:8080/ > /dev/null; then
    echo "API is up!"
    break
  fi
  if [ $i -eq 15 ]; then
    echo "Error: API failed to start. Check api_log.txt"
    exit 1
  fi
  sleep 1
done

# Ingest Species (The Many-to-Many data)
echo -e "${GREEN} Ingesting Species and building associations${NC}"
uv run src/scripts/import_species.py

# Ingest Farms
echo -e "${GREEN} Ingesting Farm records${NC}"
uv run src/scripts/import_farms.py

# Ingest Boundaries (Spatial Data)
echo -e "${GREEN} Ingesting Farm Boundaries${NC}"
uv run src/scripts/import_boundaries.py

echo -e "${BLUE}====================================================${NC}"
echo -e "${GREEN} SUCCESS: Database is fully populated${NC}"
echo -e "${BLUE}====================================================${NC}"