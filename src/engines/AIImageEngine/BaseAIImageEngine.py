import moviepy as mp

from abc import abstractmethod

from ..BaseEngine import BaseEngine


class BaseAIImageEngine(BaseEngine):
    """
    The base class for all assets engines.
    """

    @abstractmethod
    def generate(self, prompt: str, start: float, end: float, i = "") -> mp.ImageClip:
        """
        Ge
        """
        ...
