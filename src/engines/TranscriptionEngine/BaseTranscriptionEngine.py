from abc import abstractmethod
from typing import TypedDict

from ..BaseEngine import BaseEngine


class Word(TypedDict):
    start: str
    end: str
    text: str


class BaseTranscriptionEngine(BaseEngine):

    @abstractmethod
    def transcribe(
        self,
        path: str,
        fast: bool = False,
        words: bool = False,
        avoid_hallucinations: bool = False,
    ) -> list[Word]:
        """
        Transcribes the audio file at the given path using a pre-trained model and returns a list of words.

        Args:
            path (str): The path to the audio file.
            fast (bool): Whether to use a fast transcription model.
            words (bool): Whether to return the words as a list of Word objects.

        Returns:
            list[Word]: A list of Word objects representing the transcribed words.
            Example:
            ```json
            [
                {
                    "start": "0.00",
                    "end": "0.50",
                    "text": "Hello"
                },
                {
                    "start": "0.50",
                    "end": "1.00",
                    "text": "world"
                }
            ]
            ```
        """
        ...
