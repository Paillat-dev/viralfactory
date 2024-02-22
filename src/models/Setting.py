from . import Base
from typing import Optional
from sqlalchemy import String, Column, JSON, Integer
from sqlalchemy.ext.mutable import MutableDict


class Setting(Base):
    __tablename__ = "Settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider: str = Column(String, nullable=False)
    type: str = Column(String, nullable=True)
    data: dict = Column(MutableDict.as_mutable(JSON), nullable=False, default={})
