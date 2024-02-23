from abc import abstractmethod

from ..BaseEngine import BaseEngine


class BaseCaptioningEngine(BaseEngine):
    @abstractmethod
    def get_captions(self) -> None:
        ...
