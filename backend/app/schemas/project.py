from pydantic import BaseModel

try:
    from pydantic import ConfigDict
except ImportError:
    ConfigDict = None


class ProjectCreate(BaseModel):
    name: str


class ProjectRead(BaseModel):
    id: str
    name: str

    if ConfigDict is not None:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True
