import gradio as gr
import TTS
import os
import torch

from .BaseTTSEngine import BaseTTSEngine


class CoquiTTSEngine(BaseTTSEngine):
    voices = [
        "Claribel Dervla",
        "Daisy Studious",
        "Gracie Wise",
        "Tammie Ema",
        "Alison Dietlinde",
        "Ana Florence",
        "Annmarie Nele",
        "Asya Anara",
        "Brenda Stern",
        "Gitta Nikolina",
        "Henriette Usha",
        "Sofia Hellen",
        "Tammy Grit",
        "Tanja Adelina",
        "Vjollca Johnnie",
        "Andrew Chipper",
        "Badr Odhiambo",
        "Dionisio Schuyler",
        "Royston Min",
        "Viktor Eka",
        "Abrahan Mack",
        "Adde Michal",
        "Baldur Sanjin",
        "Craig Gutsy",
        "Damien Black",
        "Gilberto Mathias",
        "Ilkin Urbano",
        "Kazuhiko Atallah",
        "Ludvig Milivoj",
        "Suad Qasim",
        "Torcull Diarmuid",
        "Viktor Menelaos",
        "Zacharie Aimilios",
        "Nova Hogarth",
        "Maja Ruoho",
        "Uta Obando",
        "Lidiya Szekeres",
        "Chandra MacFarland",
        "Szofi Granger",
        "Camilla Holmström",
        "Lilya Stainthorpe",
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
    ]
    name = "Coqui TTS"
    description = "Coqui TTS engine."
    languages = [
        "en",  # English
        "es",  # Spanish
        "fr",  # French
        "de",  # German
        "it",  # Italian
        "pt",  # Portuguese
        "pl",  # Polish
        "tr",  # Turkish
        "ru",  # Russian
        "nl",  # Dutch
        "cs",  # Czech
        "ar",  # Arabic
        "zh-cn",  # Chinese (Simplified)
        "ja",  # Japanese
        "hu",  # Hungarian
        "ko",  # Korean
        "hi",  # Hindi
    ]
    options = [
        {
            "type": "dropdown",
            "label": "Voice",
            "choices": voices,
            "max": 1,
        },
        {
            "type": "dropdown",
            "label": "Language",
            "choices": languages,
            "max": 1,
        },
    ]

    def __init__(self, options: list):
        super().__init__()

        self.voice = options[0][0]
        self.language = options[1][0]

        os.environ["COQUI_TOS_AGREED"] = "1"
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts.to(device)

    def synthesize(self, text: str, path: str) -> str:
        self.tts.tts_to_file(text=text, file_path=path, lang=self.language, speaker=self.voice)
        return path