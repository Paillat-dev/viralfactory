from datetime import datetime

from sqlalchemy import String, Column, JSON, Integer, DateTime
from sqlalchemy.ext.mutable import MutableList

from . import Base


class Video(Base):
    __tablename__ = "Videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title: str = Column(String, nullable=False)
    description: str = Column(String, nullable=False)
    script: str = Column(String, nullable=False)
    timed_script: dict = Column(MutableList.as_mutable(JSON), nullable=False)  # type: ignore
    timestamp: datetime = Column(DateTime, nullable=False, default=datetime.now())
    path: str = Column(String, nullable=False)
