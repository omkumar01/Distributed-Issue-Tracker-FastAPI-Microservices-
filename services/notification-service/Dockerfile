FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

COPY shared/ /app/shared/
COPY services/notification-service/requirements.txt /app/requirements.txt

RUN sed -i 's/\.\.\/\.\.\///g' /app/requirements.txt || true
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/notification-service/ /app/

ENV PYTHONPATH=/app

EXPOSE 8000
CMD sh -c "celery -A src.main.celery_app worker -l info & uvicorn src.main:app --host 0.0.0.0 --port 8000"
