import moviepy
import time
import os

from .. import engines
from ..utils.prompting import get_prompt


class GenerationContext:
    def __init__(
        self, powerfulllmengine, simplellmengine, scriptengine, ttsengine
    ) -> None:
        self.powerfulllmengine: engines.LLMEngine.BaseLLMEngine = powerfulllmengine
        self.powerfulllmengine.ctx = self

        self.simplellmengine: engines.LLMEngine.BaseLLMEngine = simplellmengine
        self.simplellmengine.ctx = self

        self.scriptengine: engines.ScriptEngine.BaseScriptEngine = scriptengine
        self.scriptengine.ctx = self

        self.ttsengine: engines.TTSEngine.BaseTTSEngine = ttsengine
        self.ttsengine.ctx = self

    def setup_dir(self):
        self.dir = f"output/{time.time()}"
        os.makedirs(self.dir)
    
    def get_file_path(self, name: str) -> str:
        return os.path.join(self.dir, name)

    def process(self):
        # IMPORTANT NOTE: All methods called here are expected to be defined as abstract methods in the base classes, if not there is an issue with the engine implementation.
        self.setup_dir()

        script = self.scriptengine.generate()

        timed_script = self.ttsengine.synthesize(script, self.get_file_path("tts.wav"))
