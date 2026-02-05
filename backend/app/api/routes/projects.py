from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.project import Project
from app.models.image import Image
from app.schemas.project import ProjectCreate, ProjectRead
import os
import shutil

router = APIRouter(prefix="/projects", tags=["Projects"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=ProjectRead)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db)
):
    project = Project(name=data.name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("", response_model=list[ProjectRead])
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    images = db.query(Image).filter(Image.project_id == project_id).all()
    for image in images:
        if os.path.exists(image.file_path):
            try:
                os.remove(image.file_path)
            except Exception:
                pass

    project_dir = os.path.join("app", "static", "images", project_id)
    if os.path.isdir(project_dir):
        try:
            shutil.rmtree(project_dir)
        except Exception:
            pass

    db.delete(project)
    db.commit()

    return {"status": "deleted"}