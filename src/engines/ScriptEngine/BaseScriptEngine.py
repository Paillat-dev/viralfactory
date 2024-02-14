from abc import ABC, abstractmethod
from ..BaseEngine import BaseEngine


class BaseScriptEngine(BaseEngine):
    pass

    @abstractmethod
    def generate(self) -> str:
        pass
