from .BaseTTSEngine import BaseTTSEngine
import gradio as gr

class ElevenLabsTTSEngine(BaseTTSEngine):
    options = [
        {
            "type": "dropdown",
            "label": "Voice",
            "choices": [
                "Zofija Kendrick",
                "Narelle Moon",
                "Barbora MacLean",
                "Alexandra Hisakawa",
                "Alma María",
                "Rosemary Okafor",
                "Ige Behringer",
                "Filip Traverse",
                "Damjan Chapman",
                "Wulf Carlevaro",
                "Aaron Dreschner",
                "Kumar Dahl",
                "Eugenio Mataracı",
                "Ferran Simen",
                "Xavier Hayasaka",
                "Luis Moray",
                "Marcos Rudaski",
            ],
        }
    ]
    name = "ElevenLabs"
    description = "ElevenLabs TTS engine."

    def __init__(self, options: list[list | tuple | str | int | float | bool | None]):
        self.voice = options[0][0]
        super().__init__()

    def synthesize(self, text: str, path: str) -> str:
        pass