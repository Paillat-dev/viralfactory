from .BaseScriptEngine import BaseScriptEngine
import gradio as gr


class CustomScriptEngine(BaseScriptEngine):
    name = "Custom Script Engine"
    description = "Generate a script with a custom provided prompt"
    num_options = 1

    def __init__(self, options: list[list | tuple | str | int | float | bool | None]):
        self.script = options[0]
        super().__init__()

    def generate(self, *args, **kwargs) -> str:
        return self.script

    @classmethod
    def get_options(cls) -> list:
        return [
            gr.Textbox(
                label="Prompt",
                placeholder="Enter your prompt here",
                value="",
            )
        ]
