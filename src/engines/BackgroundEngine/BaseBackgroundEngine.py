from abc import abstractmethod

from ..BaseEngine import BaseEngine


class BaseBackgroundEngine(BaseEngine):
    @abstractmethod
    def get_background(self) -> None:
        ...
