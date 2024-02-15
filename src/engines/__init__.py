from .BaseEngine import BaseEngine
from . import TTSEngine
from . import ScriptEngine
from . import LLMEngine

ENGINES = {
    "LLMEngine": [LLMEngine.OpenaiLLMEngine],
    "TTSEngine": [TTSEngine.CoquiTTSEngine, TTSEngine.ElevenLabsTTSEngine],
    "ScriptEngine": [ScriptEngine.ShowerThoughtsScriptEngine, ScriptEngine.CustomScriptEngine],
}
