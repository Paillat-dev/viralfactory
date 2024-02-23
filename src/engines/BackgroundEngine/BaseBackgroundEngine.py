from abc import ABC, abstractmethod

from moviepy.editor import VideoClip

from ..BaseEngine import BaseEngine


class BaseBackgroundEngine(BaseEngine):
    @abstractmethod
    def get_background(self) -> None:
        ...
