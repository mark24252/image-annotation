from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import uuid


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String, nullable=False)

    images = relationship(
        "Image",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
