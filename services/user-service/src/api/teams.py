from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from src.db.database import get_db
from src.domain.user import Team, TeamCreate, TeamORM
import uuid

router = APIRouter()

@router.post("/", response_model=Team, status_code=201)
async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_db)):
    db_team = TeamORM(id=str(uuid.uuid4()), name=team.name)
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    return db_team

@router.get("/", response_model=List[Team])
async def list_teams(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TeamORM))
    return result.scalars().all()
