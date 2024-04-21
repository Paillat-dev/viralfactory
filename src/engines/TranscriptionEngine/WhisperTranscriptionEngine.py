from abc import abstractmethod
from typing import TypedDict

import whisper_timestamped as wt
from torch.cuda import is_available

from . import BaseTranscriptionEngine


class Word(TypedDict):
    start: str
    end: str
    text: str


class WhisperTranscriptionEngine(BaseTranscriptionEngine):
    name = "Whisper Transcription Engine"
    description = (
        "A transcription engine that uses the whisper model to transcribe audio files."
    )
    num_options = 0

    def __init__(self, options: list) -> None:
        super().__init__()

    def transcribe(
        self,
        path: str,
        fast: bool = False,
        words=False,
        avoid_hallucinations: bool = False,
    ) -> list[Word] | dict[str, dict[str, str]]:
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
        device = "cuda" if is_available() else "cpu"
        audio = wt.load_audio(path)
        model = wt.load_model("large-v3" if not fast else "base", device=device)
        result = wt.transcribe(model=model, audio=audio, vad=avoid_hallucinations)
        if words:
            results = [word for chunk in result["segments"] for word in chunk["words"]]
            for result in results:
                del result["confidence"]

            return results
        return result

    @classmethod
    def get_options(cls):
        return []
