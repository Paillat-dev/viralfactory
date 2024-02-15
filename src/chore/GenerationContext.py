import moviepy
import time
import os

from .. import engines
from ..utils.prompting import get_prompt

class GenerationContext:

    def __init__(self, powerfulllmengine: engines.LLMEngine.BaseLLMEngine, simplellmengine: engines.LLMEngine.BaseLLMEngine, scriptengine: engines.ScriptEngine.BaseScriptEngine, ttsengine: engines.TTSEngine.BaseTTSEngine) -> None:
        self.powerfulllmengine = powerfulllmengine
        self.powerfulllmengine.ctx = self
        
        self.simplellmengine = simplellmengine
        self.simplellmengine.ctx = self

        self.scriptengine = scriptengine
        self.scriptengine.ctx = self

        self.ttsengine = ttsengine
        self.ttsengine.ctx = self
    def setup_dir(self):
        self.dir = f"output/{time.time()}"
        os.makedirs(self.dir)

    def process(self):
        self.setup_dir()

        script = self.scriptengine.generate()

        timed_script = self.ttsengine.synthesize(script, self.dir)