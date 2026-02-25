"""Search routers module."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def search():
    """Search for issues."""
    return {"message": "Search endpoint - Not implemented yet"}


@router.get("/filters")
async def get_filters():
    """Get available filters."""
    return {"message": "Get filters endpoint - Not implemented yet"}


@router.get("/suggestions")
async def get_suggestions():
    """Get search suggestions."""
    return {"message": "Get suggestions endpoint - Not implemented yet"}
