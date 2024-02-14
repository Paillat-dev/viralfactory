import openai
import gradio as gr

from abc import ABC, abstractmethod

from .BaseLLMEngine import BaseLLMEngine

OPENAI_POSSIBLE_MODELS = [
    "gpt-3.5-turbo-0125",
    "gpt-4-turbo-preview",
]

class OpenaiLLMEngine(BaseLLMEngine):
    num_options = 1
    name = "OpenAI"
    description = "OpenAI language model engine."

    def generate(self, system_prompt: str, chat_prompt: str, max_tokens: int = 512, temperature: float = 1.0, json_mode: bool= False, top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0) -> str:
        ... # TODO: Implement this method

    def get_options(self) -> list:
        return [
            gr.Dropdown(
                label="Model",
                choices=OPENAI_POSSIBLE_MODELS,
                max_choices=1,
                value=OPENAI_POSSIBLE_MODELS[0]
            )
        ]