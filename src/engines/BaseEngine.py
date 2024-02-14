from abc import ABC, abstractmethod
import gradio as gr


class BaseEngine(ABC):
    num_options: int
    name: str
    description: str

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def get_options():
        ...
