from abc import ABC, abstractmethod
from ..BaseEngine import BaseEngine

from moviepy.editor import TextClip


class BaseCaptioningEngine(BaseEngine):
    @abstractmethod
    def get_captions(self) -> None:
        ...
