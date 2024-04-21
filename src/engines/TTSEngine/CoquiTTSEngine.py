import os

import gradio as gr
import torch
from TTS.api import TTS

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
    num_options = 5

    def __init__(self, options: list):
        super().__init__()

        self.voice = options[0]
        self.language = options[1]
        self.to_force_duration = options[2]
        self.duration = options[3]

        os.environ["COQUI_TOS_AGREED"] = str(options[4])
        try:
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        except:
            raise Exception(
                "An error occured when loading thr TTS model. Make sure that you have agreed to the TOS in the TTSEngine tab."
            )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts.to(device)

    def synthesize(self, text: str, path: str):
        """
        Synthesizes the given text into speech and saves it to the specified file path.

        Args:
            text (str): The text to synthesize into speech.
            path (str): The file path to save the synthesized speech.

        Returns:
            float: The time taken to synthesize the speech with whispering effect.
        """
        self.tts.tts_to_file(
            text=text, file_path=path, language=self.language, speaker=self.voice
        )
        if self.to_force_duration:
            self.force_duration(float(self.duration), path)

        return self.get_audio_duration(path)

    @classmethod
    def get_options(cls) -> list:
        options = [
            gr.Dropdown(
                label="Voice",
                choices=cls.voices,
                max_choices=1,
                value="Damien Black",
            ),
            gr.Dropdown(
                label="Language",
                choices=cls.languages,
                max_choices=1,
                value=cls.languages[0],
            ),
        ]

        duration_checkbox = gr.Checkbox(
            label="Force duration",
            info="Force the duration of the generated audio to be at most the specified value",
            value=False,
            show_label=True,
        )
        duration = gr.Number(
            label="Duration [s]", value=57, step=1, minimum=10, visible=False
        )
        duration_switch = lambda x: gr.update(visible=x)
        duration_checkbox.change(
            duration_switch, inputs=[duration_checkbox], outputs=[duration]
        )

        options.append(duration_checkbox)
        options.append(duration)

        options.append(
            gr.Checkbox(
                label="I agree to the Coqui public mode license",
                info="You must agree to the Coqui TTS terms of service to use this engine: https://coqui.ai/cpml",
                value=False,
                show_label=True,
            )
        )
        return options
