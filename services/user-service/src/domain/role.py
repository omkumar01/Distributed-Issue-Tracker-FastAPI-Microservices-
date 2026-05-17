import uuid
from sqlalchemy import Column, String, Boolean
from pydantic import BaseModel
from src.db.database import Base

class GlobalRoleORM(Base):
    __tablename__ = "global_roles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    role_name = Column(String, nullable=False)  # SUPERADMIN, MANAGER, etc.
    is_active = Column(Boolean, default=True)

class GlobalRole(BaseModel):
    id: str
    user_id: str
    role_name: str
    is_active: bool
    
    model_config = {"from_attributes": True}
    
class GlobalRoleAssign(BaseModel):
    user_id: str
    role_name: str
