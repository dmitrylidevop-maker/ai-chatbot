FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY init_db.py .
COPY .env .env

# Expose port
EXPOSE 8000

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting Ollama service..."\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
sleep 5\n\
\n\
echo "Pulling Ollama model..."\n\
ollama pull ${OLLAMA_MODEL:-llama3:8b}\n\
\n\
echo "Initializing database..."\n\
python3 init_db.py || echo "Database already initialized"\n\
\n\
echo "Starting FastAPI application..."\n\
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
