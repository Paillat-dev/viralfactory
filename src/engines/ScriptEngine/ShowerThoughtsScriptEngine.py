from .BaseScriptEngine import BaseScriptEngine
import gradio as gr


class ShowerThoughtsScriptEngine(BaseScriptEngine):
    name = "Shower Thoughts"
    description = "Generate a Shower Thoughts script"
    num_options = 0

    def __init__(self, options: list[list | tuple | str | int | float | bool | None]):
        super().__init__()

    def generate(self, text: str, path: str) -> str:
        pass

    @classmethod
    def get_options(cls) -> list:
        return []
