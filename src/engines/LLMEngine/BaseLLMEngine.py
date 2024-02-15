from abc import ABC, abstractmethod
from ..BaseEngine import BaseEngine

import openai


class BaseLLMEngine(BaseEngine):
    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        chat_prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        frequency_penalty: float,
        presence_penalty: float,
    ) -> str | dict:
        pass
