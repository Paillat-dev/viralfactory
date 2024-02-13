from .BaseTTSEngine import AbstractTTSEngine
import gradio as gr

class ElevenLabsTTSEngine(AbstractTTSEngine):
    options = [gr.Radio(["Neutral", "Happy", "Sad"], label="emotion")]
    name = "ElevenLabs"
    description = "ElevenLabs TTS engine."

    def __init__(self):
        super().__init__()

    def synthesize(self, text: str, path: str) -> str:
        pass