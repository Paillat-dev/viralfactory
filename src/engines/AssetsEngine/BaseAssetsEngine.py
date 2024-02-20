from abc import ABC, abstractmethod
from ..BaseEngine import BaseEngine
from typing import TypedDict
from moviepy.editor import ImageClip, VideoFileClip


class BaseAssetsEngine(BaseEngine):
    """
    The base class for all assets engines.

    Attributes:
        specification (dict): A dictionary containing the specification of the engine, especially what an object returned by the llm should look like.
        spec_name (str): A comprehensive name for the specification for purely llm purposes.
        spec_description (str): A comprehensive description for the specification for purely llm purposes.
    """

    specification: dict
    spec_name: str
    spec_description: str

    @abstractmethod
    def get_assets(self, options: list) -> list:
        ...
