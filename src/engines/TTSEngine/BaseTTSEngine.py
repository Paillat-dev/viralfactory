import moviepy.editor as mp
from abc import ABC, abstractmethod
# Assuming BaseEngine is defined elsewhere in your project
from ..BaseEngine import BaseEngine


class BaseTTSEngine(BaseEngine):

    @abstractmethod
    def synthesize(self, text: str, path: str) -> str:
        pass
    
    def force_duration(self, duration: float, path: str):
        audio_clip = mp.AudioFileClip(path)
        
        if audio_clip.duration > duration:
            speed_factor = audio_clip.duration / duration
            
            new_audio = audio_clip.fx(mp.vfx.speedx, speed_factor, final_duration=duration)
            
            new_audio.write_audiofile(path, codec='libmp3lame')
            
        audio_clip.close()