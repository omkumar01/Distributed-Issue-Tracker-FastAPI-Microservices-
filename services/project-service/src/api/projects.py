from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from src.db.database import get_db
from src.domain.project import Project, ProjectCreate, ProjectUpdate, ProjectORM
from src.events.publish import publish_event
import uuid

router = APIRouter()

@router.post("/", response_model=Project, status_code=201)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    db_project = ProjectORM(id=str(uuid.uuid4()), name=project.name, description=project.description)
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)

    event_payload = {
        "event_type": "project.created",
        "project_id": db_project.id,
        "name": db_project.name
    }
    await publish_event("project.created", event_payload)

    return db_project

@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectORM).where(ProjectORM.id == project_id))
    db_project = result.scalars().first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.get("/", response_model=List[Project])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectORM))
    return result.scalars().all()
