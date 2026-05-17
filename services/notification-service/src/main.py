"""Notification Service - Main application."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
from celery import Celery
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app for health checks
app = FastAPI(
    title="Notification Service",
    description="Async user notifications via Celery and RabbitMQ",
    version="1.0.0"
)

# Celery App Configuration
RABBITMQ_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672/")
REDIS_URL = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "notification_service",
    broker=RABBITMQ_URL,
    backend=REDIS_URL,
    include=[
        "src.consumers.issue_events",
        "src.consumers.comment_events"
    ]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "notification-service"
    }


@app.get("/")
async def root():
    return {"message": "Notification Service API", "version": "1.0.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
