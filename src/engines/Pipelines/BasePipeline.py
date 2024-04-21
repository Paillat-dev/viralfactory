from ...chore import GenerationContext
from abc import ABC, abstractmethod
from ..BaseEngine import BaseEngine


class BasePipeline(BaseEngine):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def launch(self, ctx: GenerationContext) -> None:
        pass
