"""Notification routers module."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/{notification_id}")
async def get_notification(notification_id: str):
    """Get notification by ID."""
    return {"message": f"Get notification {notification_id} - Not implemented yet"}


@router.post("")
async def send_notification():
    """Send a notification."""
    return {"message": "Send notification endpoint - Not implemented yet"}


@router.put("/{notification_id}")
async def update_notification(notification_id: str):
    """Update notification."""
    return {"message": f"Update notification {notification_id} - Not implemented yet"}
