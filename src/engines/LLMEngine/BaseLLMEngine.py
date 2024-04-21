from abc import abstractmethod

from ..BaseEngine import BaseEngine


class BaseLLMEngine(BaseEngine):
    @abstractmethod
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
        pass
