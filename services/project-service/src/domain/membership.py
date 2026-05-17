import uuid
from sqlalchemy import Column, String, DateTime, func
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from src.db.database import Base

class RoleEnum(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

# --- Database Model ---

class MembershipORM(Base):
    __tablename__ = "memberships"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False, default=RoleEnum.MEMBER.value)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

# --- Pydantic Schemas ---

class MembershipBase(BaseModel):
    user_id: str
    role: RoleEnum = RoleEnum.MEMBER

class MembershipCreate(MembershipBase):
    pass

class Membership(MembershipBase):
    id: str
    project_id: str
    joined_at: datetime

    model_config = {"from_attributes": True}
