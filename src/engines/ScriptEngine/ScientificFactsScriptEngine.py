import os

import gradio as gr

from .BaseScriptEngine import BaseScriptEngine
from ...utils.prompting import get_prompt


class ScientificFactsScriptEngine(BaseScriptEngine):
    name = "Scientific facts"
    description = "Generate a scientific facts script."
    num_options = 1

    def __init__(self, options: list[list | tuple | str | int | float | bool | None]):
        self.n_sentences = options[0]
        super().__init__()

    def generate(self):
        sys_prompt, chat_prompt = get_prompt(
            "scientific_facts",
            location=os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "prompts"
            ),
        )
        sys_prompt = sys_prompt.format(n_sentences=self.n_sentences)
        chat_prompt = chat_prompt.format(n_sentences=self.n_sentences)
        self.ctx.script = self.ctx.powerfulllmengine.generate(
            system_prompt=sys_prompt,
            chat_prompt=chat_prompt,
            max_tokens=20 * self.n_sentences,
            temperature=1.3,
            json_mode=False,
        ).strip()

    @classmethod
    def get_options(cls) -> list:
        return [gr.Number(label="Number of sentences", value=5, minimum=1)]
