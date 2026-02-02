import os
import shutil
from uuid import uuid4
from fastapi import UploadFile


BASE_DIR = os.path.join("app", "static", "images")


def save_image(file: UploadFile, project_id: str) -> str:
    original_name = file.filename or ""
    ext = original_name.rsplit(".", 1)[-1] if "." in original_name else "bin"
    filename = f"{uuid4()}.{ext.lower()}"

    project_dir = os.path.join(BASE_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)

    file_path = os.path.join(project_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path