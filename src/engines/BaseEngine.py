import gradio as gr
import moviepy.editor as mp

from abc import ABC, abstractmethod
from sqlalchemy.future import select

from ..chore import GenerationContext
from ..models import SessionLocal, File


class BaseEngine(ABC):
    num_options: int
    name: str
    description: str

    def __init__(self):
        self.ctx: GenerationContext  # This is for type hinting only
        pass

    @classmethod
    @abstractmethod
    def get_options():
        ...

    def get_video_duration(self, path: str) -> float:
        return mp.VideoFileClip(path).duration

    def get_audio_duration(self, path: str) -> float:
        return mp.AudioFileClip(path).duration

    @classmethod
    def get_assets(cls, *, type: str = None) -> list[File]:
        with SessionLocal() as db:
            if type:
                return (
                    db.execute(
                        select(File).filter(
                            File.type == type, File.provider == cls.name
                        )
                    )
                    .scalars()
                    .all()
                )
            else:
                return (
                    db.execute(select(File).filter(File.provider == cls.name))
                    .scalars()
                    .all()
                )
    
    @classmethod
    def add_asset(cls, *, path: str, metadata: dict, type: str = None):
        with SessionLocal() as db:
            db.add(File(path=path, data=metadata, type=type, provider=cls.name))
            db.commit()

    @classmethod
    def remove_asset(cls, *, path: str):
        with SessionLocal() as db:
            db.execute(select(File).filter(File.path == path)).delete()
            db.commit()

    @classmethod
    def get_settings(cls):
        ...
