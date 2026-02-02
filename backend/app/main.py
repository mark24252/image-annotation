from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.routes.projects import router as project_router
from fastapi.staticfiles import StaticFiles
from app.api.routes.images import router as image_router
from app.api.routes.annotations import router as annotation_router
from app.api.routes.predict import router as predict_router
import os

app = FastAPI(title="Image Annotation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    os.makedirs("app/static", exist_ok=True)
    os.makedirs("app/static/images", exist_ok=True)

app.include_router(project_router)

app.mount("/static", StaticFiles(directory="app/static", check_dir=False), name="static")

app.include_router(image_router)

app.include_router(annotation_router)

app.include_router(predict_router)