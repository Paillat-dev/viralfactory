from abc import abstractmethod

from ..BaseEngine import BaseEngine


class BaseMetadataEngine(BaseEngine):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        ...

    @abstractmethod
    def get_metadata(self) -> None:
        ...
