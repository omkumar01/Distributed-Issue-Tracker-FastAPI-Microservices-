"""Project routers module."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_projects():
    """List all projects."""
    return {"message": "List projects endpoint - Not implemented yet"}


@router.post("")
async def create_project():
    """Create a new project."""
    return {"message": "Create project endpoint - Not implemented yet"}


@router.get("/{project_id}")
async def get_project(project_id: str):
    """Get project by ID."""
    return {"message": f"Get project {project_id} - Not implemented yet"}


@router.put("/{project_id}")
async def update_project(project_id: str):
    """Update project."""
    return {"message": f"Update project {project_id} - Not implemented yet"}


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete project."""
    return {"message": f"Delete project {project_id} - Not implemented yet"}
