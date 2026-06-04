import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.environ["DATABASE_URL"]

_echo_sql = os.getenv("APP_ENV", "production") == "development"

# SQLite nécessite check_same_thread=False pour FastAPI (multi-thread)
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args, echo=_echo_sql)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    return SessionLocal()


def init_db() -> None:
    """Crée toutes les tables depuis les DAOs SQLAlchemy.
    Utilisé avec SQLite (dev). En production PostgreSQL, utiliser db/script.sql.
    """
    Base.metadata.create_all(engine)
