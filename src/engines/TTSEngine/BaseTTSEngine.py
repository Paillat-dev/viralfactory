from abc import abstractmethod
from typing import TypedDict

import moviepy as mp
import whisper_timestamped as wt
from torch.cuda import is_available

from ..BaseEngine import BaseEngine


class Word(TypedDict):
    start: str
    end: str
    text: str


class BaseTTSEngine(BaseEngine):
    @abstractmethod
    def synthesize(self, text: str, path: str) -> float:
        pass

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
