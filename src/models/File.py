from sqlalchemy import String, Column, JSON, Integer
from sqlalchemy.ext.mutable import MutableDict

from . import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider: str = Column(String, nullable=False)
    type: str = Column(String, nullable=True)
    path: str = Column(String, nullable=False)
    data: dict = Column(MutableDict.as_mutable(JSON), nullable=False, default={})  # type: ignore
