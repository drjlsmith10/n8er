# Project Automata: Docker Image
# Version: 2.0.0-alpha

FROM python:3.11.9-slim

LABEL maintainer="Project Automata Team"
LABEL version="2.0.0-alpha"
LABEL description="Autonomous n8n workflow builder with AI-powered generation"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install application in development mode
RUN pip install --no-cache-dir -e .

# Create necessary directories
RUN mkdir -p knowledge_base workflows logs && \
    chmod 755 knowledge_base workflows logs

# Run configuration validation
RUN python config.py || echo "Configuration check skipped (no .env)"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from skills.knowledge_base import KnowledgeBase; kb = KnowledgeBase()" || exit 1

# Set environment
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Expose ports (for future web API)
EXPOSE 8000

# Default command - run web research
CMD ["python", "scripts/run_web_research.py"]
