from . import TTSEngine
from .BaseEngine import BaseEngine
from . import ScriptEngine
from . import LLMEngine

ENGINES = {
    "LLMEngine": [LLMEngine.OpenaiLLMEngine],
    "TTSEngine": [TTSEngine.CoquiTTSEngine, TTSEngine.ElevenLabsTTSEngine],
    "ScriptEngine": [ScriptEngine.ShowerThoughtsScriptEngine, ScriptEngine.CustomScriptEngine],
}
