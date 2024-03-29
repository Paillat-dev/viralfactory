import gradio as gr

from .BaseScriptEngine import BaseScriptEngine


class CustomScriptEngine(BaseScriptEngine):
    name = "Custom Script Engine"
    description = "Generate a script with a custom provided prompt"
    num_options = 1

    def __init__(self, options: list[list | tuple | str | int | float | bool | None]):
        self.script = options[0]
        super().__init__()

    def generate(self, *args, **kwargs):
        self.ctx.script = self.script.strip()

    @classmethod
    def get_options(cls) -> list:
        return [
            gr.Textbox(
                label="Script",
                placeholder="Enter your script here",
                value="",
            )
        ]
