from abc import abstractmethod

from src.engines.BaseEngine import BaseEngine


class BaseBackgroundEngine(BaseEngine):
    @abstractmethod
    def get_background(self) -> None: ...
