from abc import ABC, abstractmethod

from moviepy.editor import TextClip

from ..BaseEngine import BaseEngine


class BaseCaptioningEngine(BaseEngine):
    @abstractmethod
    def get_captions(self) -> None:
        ...
