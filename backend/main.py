import torch
import numpy as np
import crud, database, models, schemas, auth
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()

tokenizer = AutoTokenizer.from_pretrained("cointegrated/rubert-tiny2")
model = AutoModel.from_pretrained("cointegrated/rubert-tiny2")

def get_embedding(text: str):
    if not text: text = "пусто"
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].numpy()

@app.get("/recommendations/{project_id}")
def get_recommendations(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    p_text = f"{project.title} {project.desc} {' '.join(project.req_roles)}"
    p_vector = get_embedding(p_text)

    all_users = db.query(models.User).all()
    member_ids = [m['id'] for m in project.members]

    scored_users = []
    for user in all_users:
        if user.id in member_ids or user.id == project.creator_id:
            continue

        u_text = f"{' '.join(user.roles)} {user.desc or ''}"
        u_vector = get_embedding(u_text)

        similarity = cosine_similarity(p_vector, u_vector)[0][0]
        scored_users.append((user, float(similarity)))

    scored_users.sort(key=lambda x: x[1], reverse=True)
    return [u[0] for u in scored_users]

@app.post("/register/", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if crud.get_user_by_login(db, user.login):
        raise HTTPException(status_code=400, detail="Login already exists")
    user_data = user.model_dump()
    user_data["password"] = auth.get_password_hash(user.password)
    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login/")
def login(user_data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_login(db, user_data.login)
    if not user or not auth.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    return crud.get_user(db, user_id)

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, data: schemas.UserUpdate, db: Session = Depends(database.get_db)):
    return crud.update_user(db, user_id, data.model_dump(exclude_unset=True))

@app.get("/projects/", response_model=List[schemas.ProjectResponse])
def read_projects(db: Session = Depends(database.get_db)):
    return db.query(models.Project).all()

@app.post("/projects/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db)):
    return crud.create_project(db, project)

@app.put("/projects/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, data: schemas.ProjectUpdate, db: Session = Depends(database.get_db)):
    return crud.update_project(db, project_id, data.model_dump(exclude_unset=True))

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(database.get_db)):
    crud.delete_project(db, project_id)
    return {"status": "ok"}

@app.post("/projects/{project_id}/apply")
def apply_to_project(project_id: int, user_id: int, db: Session = Depends(database.get_db)):
    return crud.create_join_request(db, project_id, user_id)

@app.get("/users/{user_id}/notifications")
def get_notifications(user_id: int, db: Session = Depends(database.get_db)):
    reqs = db.query(models.JoinRequest).join(models.Project).filter(
        models.Project.creator_id == user_id,
        models.JoinRequest.status == "pending"
    ).all()

    output = []
    for r in reqs:
        applicant = db.query(models.User).get(r.user_id)
        proj = db.query(models.Project).get(r.project_id)
        if applicant:
            output.append({
                "id": r.id,
                "user_name": f"{applicant.last_name} {applicant.first_name}",
                "user_desc": applicant.desc,
                "user_roles": applicant.roles,
                "project_title": proj.title
            })
    return output

@app.post("/requests/{request_id}/handle")
def handle_request(request_id: int, accept: bool, role: str = None, db: Session = Depends(database.get_db)):
    return crud.handle_join_request(db, request_id, accept, role)

@app.delete("/projects/{project_id}/members/{user_id}")
def kick_member(project_id: int, user_id: int, db: Session = Depends(database.get_db)):
    return crud.remove_member(db, project_id, user_id)