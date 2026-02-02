from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import uuid


class Annotation(Base):
    __tablename__ = "annotations"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )

    label: Mapped[str] = mapped_column(String, nullable=False)

    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)

    image_id: Mapped[str] = mapped_column(
        String, ForeignKey("images.id", ondelete="CASCADE"), nullable=False
    )

    image = relationship("Image", back_populates="annotations")
