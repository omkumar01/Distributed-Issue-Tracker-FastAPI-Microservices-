from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.database import get_db
from src.domain.membership import MembershipORM

router = APIRouter()

@router.get("/{project_id}/permissions/{user_id}")
async def get_user_permissions(project_id: str, user_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve effective permissions for a user in a project."""
    result = await db.execute(
        select(MembershipORM).where(MembershipORM.project_id == project_id, MembershipORM.user_id == user_id)
    )
    membership = result.scalars().first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="User has no role in this project")
        
    return {"project_id": project_id, "user_id": user_id, "role": membership.role}
