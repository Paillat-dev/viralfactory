import gradio as gr
from abc import ABC, abstractmethod

from ..chore import GenerationContext


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
