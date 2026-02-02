from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import DATABASE_URL


def _get_engine():
    if DATABASE_URL.startswith("sqlite"):
        return create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
        )

    return create_engine(DATABASE_URL)


engine = _get_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass