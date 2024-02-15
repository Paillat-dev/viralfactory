from .BaseEngine import BaseEngine
from . import TTSEngine
from . import ScriptEngine
from . import LLMEngine

ENGINES = {
    "SimpleLLMEngine": [LLMEngine.OpenaiLLMEngine, LLMEngine.AnthropicLLMEngine],
    "PowerfulLLMEngine": [LLMEngine.OpenaiLLMEngine, LLMEngine.AnthropicLLMEngine],
    "TTSEngine": [TTSEngine.CoquiTTSEngine, TTSEngine.ElevenLabsTTSEngine],
    "ScriptEngine": [
        ScriptEngine.ShowerThoughtsScriptEngine,
        ScriptEngine.CustomScriptEngine,
    ],
}
