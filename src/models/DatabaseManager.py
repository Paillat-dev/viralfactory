import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from . import Base

engine = create_engine(f"sqlite:///local/database/db.db")

SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)
    pass
