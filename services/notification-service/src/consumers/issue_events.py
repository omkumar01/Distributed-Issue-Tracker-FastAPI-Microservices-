from src.main import celery_app
from src.channels.email import send_email
from src.channels.in_app import send_in_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def process_issue_event(self, event_data: dict):
    """Process an issue event and send notifications."""
    try:
        logger.info(f"Processing issue event: {event_data}")
        event_type = event_data.get("event_type")
        issue_id = event_data.get("issue_id")
        user_id = event_data.get("user_id")

        if event_type == "issue.created":
            subject = f"New issue created: {issue_id}"
            body = f"Issue {issue_id} was just created."
            send_email("dummy@example.com", subject, body)
            send_in_app(user_id, f"You created issue {issue_id}")

        return {"status": "success", "event": event_type}
    except Exception as exc:
        logger.error(f"Error processing issue event: {exc}")
        self.retry(exc=exc, countdown=5)
