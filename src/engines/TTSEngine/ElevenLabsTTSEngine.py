from .BaseTTSEngine import BaseTTSEngine
import gradio as gr


class ElevenLabsTTSEngine(BaseTTSEngine):
    name = "ElevenLabs"
    description = "ElevenLabs TTS engine."
    num_options = 0

    def __init__(self, options: list[list | tuple | str | int | float | bool | None]):
        # self.voice = options[0][0]
        super().__init__()

    def synthesize(self, text: str, path: str) -> str:
        pass

    @classmethod
    def get_options(cls) -> list:
        return []
