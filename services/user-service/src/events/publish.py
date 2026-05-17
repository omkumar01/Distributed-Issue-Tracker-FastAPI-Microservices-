import os
import json
import logging
import pika
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def _publish_sync(event_type: str, payload: dict):
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange='issue_tracker_events', exchange_type='topic', durable=True)
        message = json.dumps(payload).encode('utf-8')
        channel.basic_publish(
            exchange='issue_tracker_events',
            routing_key=event_type,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        logger.info(f"Published event {event_type}")
    except Exception as e:
        logger.error(f"Failed to publish event {event_type}: {e}")

async def publish_event(event_type: str, payload: dict):
    """Publish an event to RabbitMQ using a background thread."""
    await run_in_threadpool(_publish_sync, event_type, payload)
