from abc import ABC, abstractmethod
from ..BaseEngine import BaseEngine

from moviepy.editor import VideoClip


class BaseBackgroundEngine(BaseEngine):
    @abstractmethod
    def get_background(self) -> None:
        ...
