import moviepy.editor as mp
import whisper_timestamped as wt

from typing import TypedDict
from torch.cuda import is_available
from abc import ABC, abstractmethod

from ..BaseEngine import BaseEngine


class Word(TypedDict):
    start: str
    end: str
    text: str


class BaseTTSEngine(BaseEngine):
    @abstractmethod
    def synthesize(self, text: str, path: str) -> str:
        pass

    def time_with_whisper(self, path: str) -> list[Word]:
        """
        Transcribes the audio file at the given path using a pre-trained model and returns a list of words.

        Args:
            path (str): The path to the audio file.

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
        model = wt.load_model("tiny", device=device)

        result = wt.transcribe(model=model, audio=audio)
        results = [word for chunk in result for word in chunk["words"]]
        for result in results:
            # Not needed for the current use case
            del result["confidence"]
        return results

    def force_duration(self, duration: float, path: str):
        """
        Forces the audio clip at the given path to have the specified duration.

        Args:
            duration (float): The desired duration in seconds.
            path (str): The path to the audio clip file.

        Returns:
            None
        """
        audio_clip = mp.AudioFileClip(path)

        if audio_clip.duration > duration:
            speed_factor = audio_clip.duration / duration

            new_audio = audio_clip.fx(
                mp.vfx.speedx, speed_factor, final_duration=duration
            )

            new_audio.write_audiofile(path, codec="libmp3lame")

        audio_clip.close()
