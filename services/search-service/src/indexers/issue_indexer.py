from src.indexers.es_client import sync_es_client
import logging

logger = logging.getLogger(__name__)

def index_issue_sync(issue_data: dict):
    try:
        sync_es_client.index(
            index="issues",
            id=issue_data.get("id", issue_data.get("issue_id", "unknown")),
            document={
                "id": issue_data.get("id"),
                "title": issue_data.get("title", ""),
                "description": issue_data.get("description", ""),
                "project_id": issue_data.get("project_id", "")
            }
        )
        logger.info(f"Indexed issue {issue_data.get('id')}")
    except Exception as e:
        logger.error(f"Error indexing issue: {e}")

def index_comment_sync(comment_data: dict):
    try:
        sync_es_client.index(
            index="comments",
            id=comment_data.get("id", "unknown"),
            document={
                "id": comment_data.get("id"),
                "issue_id": comment_data.get("issue_id", ""),
                "content": comment_data.get("content", ""),
            }
        )
        logger.info(f"Indexed comment {comment_data.get('id')}")
    except Exception as e:
        logger.error(f"Error indexing comment: {e}")
