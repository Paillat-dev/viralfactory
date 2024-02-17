import openai
import gradio as gr
import orjson

from abc import ABC, abstractmethod

from .BaseLLMEngine import BaseLLMEngine

OPENAI_POSSIBLE_MODELS = [  # Theese shall be the openai models supporting force_json
    "gpt-3.5-turbo-0125",
    "gpt-4-turbo-preview",
]


class OpenaiLLMEngine(BaseLLMEngine):
    num_options = 1
    name = "OpenAI"
    description = "OpenAI language model engine."

    def __init__(self, options: list) -> None:
        self.model = options[0]
        super().__init__()

    def generate(
        self,
        system_prompt: str,
        chat_prompt: str,
        max_tokens: int = 512,
        temperature: float = 1.0,
        json_mode: bool = False,
        top_p: float = 1,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
    ) -> str | dict:
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chat_prompt},
            ],
            max_tokens=int(max_tokens) if max_tokens else openai._types.NOT_GIVEN,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            response_format={"type": "json_object"}
            if json_mode
            else openai._types.NOT_GIVEN,
        )
        return (
            response.choices[0].message.content
            if not json_mode
            else orjson.loads(response.choices[0].message.content)
        )

    @classmethod
    def get_options(cls) -> list:
        return [
            gr.Dropdown(
                label="Model",
                choices=OPENAI_POSSIBLE_MODELS,
                max_choices=1,
                value=OPENAI_POSSIBLE_MODELS[0],
            )
        ]
