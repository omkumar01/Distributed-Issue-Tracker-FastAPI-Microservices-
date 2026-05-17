from src.main import celery_app
from src.channels.email import send_email
from src.channels.in_app import send_in_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def process_comment_event(self, event_data: dict):
    """Process a comment event and send notifications (e.g. mentions)."""
    try:
        logger.info(f"Processing comment event: {event_data}")
        event_type = event_data.get("event_type")
        issue_id = event_data.get("issue_id")
        mentions = event_data.get("mentions", [])

        if event_type == "comment.created":
            for user_id in mentions:
                send_in_app(user_id, f"You were mentioned in issue {issue_id}")
                send_email("dummy@example.com", "You were mentioned!", f"Check issue {issue_id}")

        return {"status": "success", "event": event_type}
    except Exception as exc:
        logger.error(f"Error processing comment event: {exc}")
        self.retry(exc=exc, countdown=5)
