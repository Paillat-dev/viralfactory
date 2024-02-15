import moviepy

from .. import engines
class GenerationContext:

    def __init__(self, llmengine: engines.LLMEngine.BaseLLMEngine, scriptengine: engines.ScriptEngine.BaseScriptEngine, ttsengine: engines.TTSEngine.BaseTTSEngine) -> None:
        self.llmengine = llmengine
        self.llmengine.ctx = self

        self.scriptengine = scriptengine
        self.scriptengine.ctx = self

        self.ttsengine = ttsengine
        self.ttsengine.ctx = self
    
    def process(self):
        timed_script = self.scriptengine.generate()