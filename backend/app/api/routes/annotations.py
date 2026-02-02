from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.image import Image
from app.models.annotation import Annotation
from app.schemas.annotation import AnnotationCreate, AnnotationRead, AnnotationUpdate

router = APIRouter(
    prefix="/images/{image_id}/annotations",
    tags=["Annotations"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=AnnotationRead)
def create_annotation(
    image_id: str,
    data: AnnotationCreate,
    db: Session = Depends(get_db)
):
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    annotation = Annotation(
        image_id=image_id,
        label=data.label,
        x=data.x,
        y=data.y,
        width=data.width,
        height=data.height
    )

    db.add(annotation)
    db.commit()
    db.refresh(annotation)

    return annotation

@router.get("", response_model=list[AnnotationRead])
def get_annotations(
    image_id: str,
    db: Session = Depends(get_db)
):
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return db.query(Annotation).filter(
        Annotation.image_id == image_id
    ).all()


@router.patch("/{annotation_id}", response_model=AnnotationRead)
def update_annotation(
    image_id: str,
    annotation_id: str,
    data: AnnotationUpdate,
    db: Session = Depends(get_db)
):
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    annotation = db.get(Annotation, annotation_id)
    if not annotation or annotation.image_id != image_id:
        raise HTTPException(status_code=404, detail="Annotation not found")
    update_data = data.model_dump(exclude_unset=True) if hasattr(data, "model_dump") else data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(annotation, key, value)
    db.commit()
    db.refresh(annotation)
    return annotation


@router.delete("/{annotation_id}")
def delete_annotation(
    image_id: str,
    annotation_id: str,
    db: Session = Depends(get_db)
):
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    annotation = db.get(Annotation, annotation_id)
    if not annotation or annotation.image_id != image_id:
        raise HTTPException(status_code=404, detail="Annotation not found")
    db.delete(annotation)
    db.commit()
    return {"status": "deleted"}