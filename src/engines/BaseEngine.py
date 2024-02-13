from abc import ABC, abstractmethod
import gradio as gr

class BaseEngine(ABC):
    options: list
    name: str
    description: str

    def __init__(self):
        pass