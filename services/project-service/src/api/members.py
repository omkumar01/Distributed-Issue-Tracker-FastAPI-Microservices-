from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from src.db.database import get_db
from src.domain.project import ProjectORM
from src.domain.membership import Membership, MembershipCreate, MembershipORM
from src.events.publish import publish_event
import uuid

router = APIRouter()

@router.post("/{project_id}/members", response_model=Membership, status_code=201)
async def add_member(project_id: str, membership: MembershipCreate, db: AsyncSession = Depends(get_db)):
    # Verify project exists
    result_proj = await db.execute(select(ProjectORM).where(ProjectORM.id == project_id))
    if not result_proj.scalars().first():
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if user already exists
    result_member = await db.execute(
        select(MembershipORM).where(MembershipORM.project_id == project_id, MembershipORM.user_id == membership.user_id)
    )
    if result_member.scalars().first():
        raise HTTPException(status_code=400, detail="User already in project")

    db_member = MembershipORM(
        id=str(uuid.uuid4()), 
        project_id=project_id, 
        user_id=membership.user_id, 
        role=membership.role.value
    )
    db.add(db_member)
    await db.commit()
    await db.refresh(db_member)

    event_payload = {
        "event_type": "project.member.added",
        "project_id": project_id,
        "user_id": membership.user_id,
        "role": membership.role.value
    }
    await publish_event("project.member.added", event_payload)

    return db_member

@router.get("/{project_id}/members", response_model=List[Membership])
async def list_members(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MembershipORM).where(MembershipORM.project_id == project_id))
    return result.scalars().all()
