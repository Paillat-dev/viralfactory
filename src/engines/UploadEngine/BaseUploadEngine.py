from abc import abstractmethod

from ..BaseEngine import BaseEngine


class BaseUploadEngine(BaseEngine):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        ...

    @abstractmethod
    def upload(self):
        ...
