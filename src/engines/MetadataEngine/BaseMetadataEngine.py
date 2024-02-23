from abc import abstractmethod

from .. import BaseEngine


class BaseMetadataEngine(BaseEngine):
    def __init__(self, **kwargs) -> None:
        ...

    @abstractmethod
    def get_metadata(self) -> None:
        ...
