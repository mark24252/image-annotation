import os

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.project import Project
from app.models.image import Image
from app.schemas.image import ImageRead
from app.services.storage import save_image

router = APIRouter(tags=["Images"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/projects/{project_id}/images", response_model=list[ImageRead])
def upload_images(
    project_id: str,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    images = []

    for file in files:
        path = save_image(file, project_id)
        stored_filename = os.path.basename(path)

        image = Image(
            filename=file.filename,
            file_path=path,
            project_id=project_id
        )

        db.add(image)
        db.commit()
        db.refresh(image)

        images.append(
            ImageRead(
                id=image.id,
                filename=image.filename,
                url=f"/static/images/{project_id}/{stored_filename}"
            )
        )

    return images

@router.get("/projects/{project_id}/images", response_model=list[ImageRead])
def get_images(
    project_id: str,
    db: Session = Depends(get_db)
):
    images = db.query(Image).filter(Image.project_id == project_id).all()

    return [
        ImageRead(
            id=img.id,
            filename=img.filename,
            url=f"/static/images/{img.project_id}/{os.path.basename(img.file_path)}"
        )
        for img in images
    ]

@router.get("/images/{image_id}", response_model=ImageRead)
def get_image(
    image_id: str,
    db: Session = Depends(get_db)
):
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return ImageRead(
        id=image.id,
        filename=image.filename,
        url=f"/static/images/{image.project_id}/{os.path.basename(image.file_path)}",
    )

@router.delete("/images/{image_id}")
def delete_image(
    image_id: str,
    db: Session = Depends(get_db)
):
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    if os.path.exists(image.file_path):
        os.remove(image.file_path)

    db.delete(image)
    db.commit()

    return {"status": "deleted"}