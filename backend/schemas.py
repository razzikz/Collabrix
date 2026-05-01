from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

class UserBase(BaseModel):
    login: str
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    category: str
    roles: List[str] = Field(..., min_length=1)
    contacts: List[str] = Field(..., min_length=1)
    desc: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    login: str
    password: str

class UserUpdate(BaseModel):
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    category: Optional[str] = None
    roles: Optional[List[str]] = None
    contacts: Optional[List[str]] = None
    desc: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ProjectBase(BaseModel):
    title: str
    desc: str
    req_roles: List[str]
    creator_id: int
    creator_role: str
    status: Optional[str] = "Ищем участников"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    desc: Optional[str] = None
    req_roles: Optional[List[str]] = None
    status: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    members: List[dict] = []
    model_config = ConfigDict(from_attributes=True)

class NotificationResponse(BaseModel):
    id: int
    user_name: str
    user_desc: str
    user_roles: List[str]
    project_title: str