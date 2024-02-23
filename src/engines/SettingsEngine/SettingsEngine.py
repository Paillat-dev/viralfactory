import gradio as gr

from ..BaseEngine import BaseEngine


class SettingsEngine(BaseEngine):
    def __init__(self, options: list) -> None:
        self.width = options[0]
        self.height = options[1]
        super().__init__()

    name = "Settings Engine"
    description = "Engine for handling all the base settings for the content generation"
    num_options = 2

    def load(self):
        self.ctx.width = self.width
        self.ctx.height = self.height

    @classmethod
    def get_options(cls):
        # minimum is 720p, maximum is 4k, default is portrait hd
        width = gr.Number(value=1080, minimum=720, maximum=3840, label="Width", step=1)
        height = gr.Number(
            value=1920, minimum=720, maximum=3840, label="Height", step=1
        )

        return [width, height]
