"""Database engine/session setup (SQLAlchemy)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # Needed for SQLite when used across threads (MQTT callback thread, etc.)
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Called on startup."""
    from app import models  # noqa: F401  (ensure models are registered)
    Base.metadata.create_all(bind=engine)
