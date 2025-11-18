#!/bin/bash

set -e

echo "========================================="
echo "AI Chat Bot - Setup Script"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Ollama is installed
echo "Checking if Ollama is installed..."
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is already installed${NC}"
    OLLAMA_VERSION=$(ollama --version)
    echo "  Version: $OLLAMA_VERSION"
else
    echo -e "${YELLOW}⚠ Ollama is not installed${NC}"
    echo "Installing Ollama..."
    
    # Install Ollama
    curl -fsSL https://ollama.com/install.sh | sh
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Ollama installed successfully${NC}"
    else
        echo -e "${RED}✗ Failed to install Ollama${NC}"
        exit 1
    fi
fi

echo ""
echo "Checking if Ollama service is running..."

# Start Ollama service if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 5
    echo -e "${GREEN}✓ Ollama service started (PID: $OLLAMA_PID)${NC}"
else
    echo -e "${GREEN}✓ Ollama service is already running${NC}"
fi

echo ""
echo "Checking for required model..."

# Load model name from .env
if [ -f .env ]; then
    source .env
    MODEL_NAME=${OLLAMA_MODEL:-llama3:8b}
else
    MODEL_NAME="llama3:8b"
    echo -e "${YELLOW}⚠ .env not found, using default model: $MODEL_NAME${NC}"
fi

echo "Required model: $MODEL_NAME"

# Check if model exists
if ollama list | grep -q "$MODEL_NAME"; then
    echo -e "${GREEN}✓ Model $MODEL_NAME is already available${NC}"
else
    echo -e "${YELLOW}⚠ Model $MODEL_NAME not found${NC}"
    echo "Pulling model $MODEL_NAME (this may take a while)..."
    ollama pull $MODEL_NAME
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Model $MODEL_NAME pulled successfully${NC}"
    else
        echo -e "${RED}✗ Failed to pull model $MODEL_NAME${NC}"
        exit 1
    fi
fi

echo ""
echo "Checking Python environment..."

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python is installed: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3.12 or higher"
    exit 1
fi

echo ""
echo "Setting up Python virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

echo ""
echo "Checking database configuration..."

if [ ! -f .env ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo "Please create .env file with database configuration"
    exit 1
fi

echo -e "${GREEN}✓ Configuration file found${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Configure your database settings in .env"
echo "2. Make sure PostgreSQL is running"
echo "3. Run ./start.sh to start the application"
echo ""
