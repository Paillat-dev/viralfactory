from abc import ABC, abstractmethod
from ..BaseEngine import BaseEngine


class BaseTTSEngine(BaseEngine):
    pass

    @abstractmethod
    def synthesize(self, text: str, path: str) -> str:
        pass