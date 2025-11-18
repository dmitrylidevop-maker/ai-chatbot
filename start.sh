#!/bin/bash

set -e

echo "========================================="
echo "AI Chat Bot - Starting Application"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found${NC}"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo "Please create .env with required configuration"
    exit 1
fi

echo -e "${GREEN}✓ Configuration file found${NC}"
echo ""

# Check PostgreSQL connection (load config and test connection)
echo "Checking PostgreSQL connection..."
if [ -f .env ]; then
    source .env
    
    # Try to connect to PostgreSQL
    if command -v psql &> /dev/null; then
        if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\q' &> /dev/null; then
            echo -e "${GREEN}✓ PostgreSQL connection successful${NC}"
        else
            echo -e "${YELLOW}⚠ Cannot connect to PostgreSQL at $DB_HOST:$DB_PORT${NC}"
            echo "Please check your database configuration in .env-tmp"
            echo ""
            read -p "Do you want to continue anyway? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    else
        echo -e "${YELLOW}⚠ psql client not found, skipping PostgreSQL check${NC}"
    fi
fi

echo ""

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}⚠ Ollama service is not running${NC}"
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
    echo -e "${GREEN}✓ Ollama service started${NC}"
else
    echo -e "${GREEN}✓ Ollama service is running${NC}"
fi

echo ""
echo "Starting FastAPI application..."
echo ""

# Start the application (stay in root directory)
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
