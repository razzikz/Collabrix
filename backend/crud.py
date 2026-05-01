from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_login(db: Session, login: str):
    return db.query(models.User).filter(models.User.login == login).first()

def update_user(db: Session, user_id: int, update_data: dict):
    db_user = get_user(db, user_id)
    if db_user:
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def determine_status(req_roles: list) -> str:
    if not req_roles or len(req_roles) == 0:
        return "Набор команды завершен"
    return "Поиск участников"

def create_project(db: Session, project: schemas.ProjectCreate):
    user = get_user(db, project.creator_id)
    auto_status = determine_status(project.req_roles)

    db_project = models.Project(
        title=project.title,
        desc=project.desc,
        creator_id=project.creator_id,
        creator_role=project.creator_role,
        req_roles=project.req_roles,
        status=auto_status
    )

    db_project.members = [{
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "project_role": project.creator_role
    }]

    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: int, update_data: dict):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        if "req_roles" in update_data:
            update_data["status"] = determine_status(update_data["req_roles"])

        for key, value in update_data.items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

def remove_member(db: Session, project_id: int, user_id: int):
    project = db.query(models.Project).filter_by(id=project_id).first()
    if project and user_id != project.creator_id:
        project.members = [m for m in project.members if m['id'] != user_id]
        flag_modified(project, "members")
        db.commit()
        db.refresh(project)
    return project

def create_join_request(db: Session, project_id: int, user_id: int):
    project = db.query(models.Project).filter_by(id=project_id).first()
    if not project or project.status == "Набор команды завершен":
        return None

    existing = db.query(models.JoinRequest).filter_by(
        project_id=project_id, user_id=user_id, status="pending"
    ).first()
    if existing: return existing

    req = models.JoinRequest(project_id=project_id, user_id=user_id)
    db.add(req)
    db.commit()
    return req

def handle_join_request(db: Session, request_id: int, accept: bool, role: str = None):
    req = db.query(models.JoinRequest).filter_by(id=request_id).first()
    if not req: return None

    if accept and role:
        req.status = "accepted"
        project = db.query(models.Project).filter_by(id=req.project_id).first()
        user = get_user(db, req.user_id)

        new_members = list(project.members)
        if not any(m['id'] == user.id for m in new_members):
            new_members.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "project_role": role
            })
            project.members = new_members
            flag_modified(project, "members")
    else:
        req.status = "declined"

    db.commit()
    return req