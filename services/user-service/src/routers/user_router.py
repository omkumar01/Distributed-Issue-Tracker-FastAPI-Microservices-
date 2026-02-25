"""User routers module."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/{user_id}")
async def get_user(user_id: str):
    """Get user by ID."""
    return {"message": f"Get user {user_id} - Not implemented yet"}


@router.post("")
async def create_user():
    """Create a new user."""
    return {"message": "Create user endpoint - Not implemented yet"}


@router.put("/{user_id}")
async def update_user(user_id: str):
    """Update user."""
    return {"message": f"Update user {user_id} - Not implemented yet"}


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete user."""
    return {"message": f"Delete user {user_id} - Not implemented yet"}
