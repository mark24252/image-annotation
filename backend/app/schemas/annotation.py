from pydantic import BaseModel, Field

try:
    from pydantic import ConfigDict
except ImportError:
    ConfigDict = None


class AnnotationCreate(BaseModel):
    label: str
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(ge=0, le=1)
    height: float = Field(ge=0, le=1)


class AnnotationUpdate(BaseModel):
    label: str | None = None
    x: float | None = Field(default=None, ge=0, le=1)
    y: float | None = Field(default=None, ge=0, le=1)
    width: float | None = Field(default=None, ge=0, le=1)
    height: float | None = Field(default=None, ge=0, le=1)


class AnnotationRead(AnnotationCreate):
    id: str

    if ConfigDict is not None:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True