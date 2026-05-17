from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from src.db.database import get_db
from src.domain.user import User, UserCreate, UserUpdate, UserORM
from src.events.publish import publish_event
import uuid

router = APIRouter()

@router.post("/", response_model=User, status_code=201)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM).where(UserORM.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = UserORM(
        id=str(uuid.uuid4()), 
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    event_payload = {
        "event_type": "user.created",
        "user_id": db_user.id,
        "email": db_user.email
    }
    await publish_event("user.created", event_payload)

    return db_user

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM).where(UserORM.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM).where(UserORM.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.full_name is not None:
        db_user.full_name = user.full_name
    if user.avatar_url is not None:
        db_user.avatar_url = user.avatar_url

    await db.commit()
    await db.refresh(db_user)

    await publish_event("user.updated", {
        "event_type": "user.updated",
        "user_id": db_user.id
    })

    return db_user

@router.get("/", response_model=List[User])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM))
    return result.scalars().all()
