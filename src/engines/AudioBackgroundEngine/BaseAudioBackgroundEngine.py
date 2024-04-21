from abc import abstractmethod

from ..BaseEngine import BaseEngine


class BaseAudioBackgroundEngine(BaseEngine):
    @abstractmethod
    def get_background(self) -> None: ...
