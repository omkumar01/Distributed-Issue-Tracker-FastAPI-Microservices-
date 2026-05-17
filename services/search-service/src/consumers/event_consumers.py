import os
import json
import pika
import time
import threading
import logging
from src.indexers.issue_indexer import index_issue_sync, index_comment_sync

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

def start_consuming():
    while True:
        try:
            parameters = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            channel.exchange_declare(exchange='issue_tracker_events', exchange_type='topic', durable=True)
            
            result = channel.queue_declare('', exclusive=True)
            queue_name = result.method.queue
            
            # Consume everything
            channel.queue_bind(exchange='issue_tracker_events', queue=queue_name, routing_key='#')
            
            def callback(ch, method, properties, body):
                event = json.loads(body)
                event_type = method.routing_key
                logger.info(f"Search Service received event: {event_type}")
                
                if getattr(event_type, "startswith", lambda x: False)("issue."):
                    index_issue_sync(event)
                elif getattr(event_type, "startswith", lambda x: False)("comment."):
                    index_comment_sync(event)
                
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            logger.info("Search Service started consuming events")
            channel.start_consuming()
            
        except Exception as e:
            logger.error(f"RabbitMQ connection lost/failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def start_consumer_thread():
    thread = threading.Thread(target=start_consuming, daemon=True)
    thread.start()
