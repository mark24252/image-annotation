from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import uuid


class Image(Base):
    __tablename__ = "images"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )

    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)

    project_id: Mapped[str] = mapped_column(
        String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    project = relationship("Project", back_populates="images")
    annotations = relationship(
        "Annotation",
        back_populates="image",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
