"""
Event Publisher module for Comment Service.
"""

import logging
import pika
from datetime import datetime
from uuid import UUID
from functools import lru_cache

from src.core.config import settings
from shared.events.schemas import BaseEvent

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes domain events to RabbitMQ."""

    def __init__(self):
        self._connection = None
        self._channel = None

    def _connect(self):
        """Establish connection to RabbitMQ."""
        if not self._connection or self._connection.is_closed:
            try:
                params = pika.URLParameters(settings.RABBITMQ_URL)
                self._connection = pika.BlockingConnection(params)
                self._channel = self._connection.channel()
                self._channel.exchange_declare(
                    exchange='issue_events', 
                    exchange_type='topic', 
                    durable=True
                )
                logger.info("Connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise

    def publish(self, event: BaseEvent):
        """Publish an event."""
        try:
            self._connect()
            
            routing_key = event.event_type
            body = event.model_dump_json()
            
            self._channel.basic_publish(
                exchange='issue_events',
                routing_key=routing_key,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json',
                    timestamp=int(datetime.utcnow().timestamp())
                )
            )
            logger.info(f"Published event: {event.event_type} - {event.event_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {e}")
            pass # Suppress for now to avoid breaking API if RabbitMQ is down

    def close(self):
        """Close connection."""
        if self._connection and not self._connection.is_closed:
            self._connection.close()


@lru_cache()
def get_publisher() -> EventPublisher:
    """Get singleton publisher."""
    return EventPublisher()
