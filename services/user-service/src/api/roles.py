from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from src.db.database import get_db
from src.domain.role import GlobalRole, GlobalRoleAssign, GlobalRoleORM
from src.domain.user import UserORM
import uuid

router = APIRouter()

@router.post("/", response_model=GlobalRole, status_code=201)
async def assign_role(assignment: GlobalRoleAssign, db: AsyncSession = Depends(get_db)):
    user_res = await db.execute(select(UserORM).where(UserORM.id == assignment.user_id))
    if not user_res.scalars().first():
        raise HTTPException(status_code=404, detail="User not found")

    db_role = GlobalRoleORM(
        id=str(uuid.uuid4()),
        user_id=assignment.user_id,
        role_name=assignment.role_name
    )
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role

@router.get("/{user_id}", response_model=List[GlobalRole])
async def get_user_roles(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GlobalRoleORM).where(GlobalRoleORM.user_id == user_id, GlobalRoleORM.is_active == True))
    return result.scalars().all()
