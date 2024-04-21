import moviepy as mp
from abc import abstractmethod

from ..BaseEngine import BaseEngine


class BaseCaptioningEngine(BaseEngine):
    @abstractmethod
    def get_captions(self, words: list[dict[str, str]] = None) -> list[mp.TextClip]: ...
