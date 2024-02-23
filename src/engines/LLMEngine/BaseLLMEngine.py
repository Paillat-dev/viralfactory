from abc import ABC, abstractmethod

import openai

from ..BaseEngine import BaseEngine


class BaseLLMEngine(BaseEngine):
    @abstractmethod
    def generate(
            self,
            system_prompt: str,
            chat_prompt: str,
            max_tokens: int,
            temperature: float,
            json_mode: bool,
            top_p: float,
            frequency_penalty: float,
            presence_penalty: float,
    ) -> str | dict:
        pass
