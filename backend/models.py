from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)
    last_name = Column(String)
    first_name = Column(String)
    middle_name = Column(String, nullable=True)
    category = Column(String)
    roles = Column(JSON)
    contacts = Column(JSON)
    desc = Column(String)
    status = Column(String)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    desc = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator_role = Column(String)
    req_roles = Column(JSON)
    status = Column(String, default="Ищем участников")
    members = Column(JSON, default=[])

class JoinRequest(Base):
    __tablename__ = "join_requests"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")