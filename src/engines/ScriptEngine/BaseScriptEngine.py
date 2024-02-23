from abc import abstractmethod

from ..BaseEngine import BaseEngine


class BaseScriptEngine(BaseEngine):
    pass

    @abstractmethod
    def generate(self) -> None:
        pass

    def time_script(self):
        ...
