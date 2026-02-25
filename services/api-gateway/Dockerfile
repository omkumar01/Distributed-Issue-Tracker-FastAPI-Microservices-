# Multi-stage build for API Gateway
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared modules first (needed for imports)
COPY shared/ /app/shared/

# Copy requirements for API Gateway
COPY services/api-gateway/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH to include app directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Copy API Gateway application code
COPY services/api-gateway/ ./

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=150s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
