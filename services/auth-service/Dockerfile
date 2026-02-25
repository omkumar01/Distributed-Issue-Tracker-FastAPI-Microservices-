FROM python:3.11-slim

WORKDIR /app

# Copy shared modules first (needed for requirements)
COPY shared/ /app/shared/

# Copy auth-service requirements
COPY services/auth-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY services/auth-service/src ./src
COPY services/auth-service/tests ./tests
COPY services/auth-service/pytest.ini .

# Set PYTHONPATH to include shared modules
ENV PYTHONPATH=/app:$PYTHONPATH

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
