import moviepy as mp

from abc import abstractmethod

from ..BaseEngine import BaseEngine


class BaseStockImageEngine(BaseEngine):
    """
    The base class for all Stock Image engines.
    """

    @abstractmethod
    def get(self, query: str, start: float, end: float, i = "") -> mp.ImageClip:
        """
        Get a stock image based on a query.

        Args:
            query (str): The query to search for.
            start (float): The starting time of the video clip.
            end (float): The ending time of the video clip.
            i (str): Unique identifier for the image, mandatory if running concurrently.

        Returns:
            str: The path to the saved image.
        """
        ...
