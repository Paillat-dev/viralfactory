from abc import abstractmethod
from typing import TypedDict

from .. import BaseEngine


class MetadataEngineSettings(TypedDict):
    title: str
    description: str


class BaseMetadataEngine(BaseEngine):
    def __init__(self, **kwargs) -> None:
        ...

    @abstractmethod
    def get_metadata(self, input: str) -> MetadataEngineSettings:
        ...
