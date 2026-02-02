from pydantic import BaseModel

try:
    from pydantic import ConfigDict
except ImportError:
    ConfigDict = None


class ImageRead(BaseModel):
    id: str
    filename: str
    url: str

    if ConfigDict is not None:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True