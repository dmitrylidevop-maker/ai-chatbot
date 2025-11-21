#!/bin/bash

# Telegram Bot Startup Script
echo "========================================="
echo "AI Chat Bot - Starting Telegram Bot"
echo "========================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo ""
    echo "✓ Virtual environment activated"
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file from .env.example"
    exit 1
fi

echo "✓ Configuration file found"

# Check PostgreSQL connection
echo ""
echo "Checking PostgreSQL connection..."
source .env
if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\q' 2>/dev/null; then
    echo "✓ PostgreSQL connection successful"
else
    echo "❌ Error: Cannot connect to PostgreSQL database"
    echo "Please check your database configuration in .env"
    exit 1
fi

# Check if Ollama is running
echo ""
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama service is running"
else
    echo "❌ Error: Ollama service is not running"
    echo "Please start Ollama first: ollama serve"
    exit 1
fi

# Check if TELEGRAM_BOT_TOKEN is set
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "your_telegram_bot_token_here" ]; then
    echo ""
    echo "❌ Error: TELEGRAM_BOT_TOKEN is not configured!"
    echo "Please set your Telegram bot token in .env file"
    echo ""
    echo "To get a token:"
    echo "1. Open Telegram and search for @BotFather"
    echo "2. Send /newbot command"
    echo "3. Follow instructions to create your bot"
    echo "4. Copy the token and add it to .env file"
    exit 1
fi

echo ""
echo "Starting Telegram Bot..."
echo ""

# Run the Telegram bot
python3 telegram_bot.py
