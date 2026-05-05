import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.environ["DATABASE_URL"]

_echo_sql = os.getenv("APP_ENV", "production") == "development"
engine = create_engine(DATABASE_URL, echo=_echo_sql)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db_session() -> Session:
    return SessionLocal()
