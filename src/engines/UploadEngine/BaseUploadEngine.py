from abc import abstractmethod

from .. import BaseEngine


class BaseUploadEngine(BaseEngine):
    def __init__(self, **kwargs) -> None:
        ...

    @abstractmethod
    def upload(self):
        ...
