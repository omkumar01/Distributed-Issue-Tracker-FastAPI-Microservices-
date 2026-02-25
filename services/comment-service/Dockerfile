FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared modules
COPY shared/ /app/shared/

# Copy requirements
COPY services/comment-service/requirements.txt .

# Fix relative path in requirements.txt (pointing to shared reqs)
RUN sed -i 's|../../shared/requirements.txt|shared/requirements.txt|g' requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY services/comment-service/ .

# Set PYTHONPATH
ENV PYTHONPATH=/app:$PYTHONPATH

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
