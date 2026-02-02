from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.image import Image
from app.services.prediction import fake_predict

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{image_id}")
def predict(
    image_id: str,
    db: Session = Depends(get_db)
):
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    predictions = fake_predict()

    return {
        "image_id": image_id,
        "predictions": predictions
    }