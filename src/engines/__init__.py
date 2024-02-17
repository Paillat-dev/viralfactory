from typing import TypedDict
from .BaseEngine import BaseEngine
from .NoneEngine import NoneEngine
from . import TTSEngine
from . import ScriptEngine
from . import LLMEngine
from . import CaptioningEngine


class EngineDict(TypedDict):
    classes: list[BaseEngine]
    multiple: bool


ENGINES: dict[str, EngineDict] = {
    "SimpleLLMEngine": {
        "classes": [LLMEngine.OpenaiLLMEngine, LLMEngine.AnthropicLLMEngine],
        "multiple": False,
    },
    "PowerfulLLMEngine": {
        "classes": [LLMEngine.OpenaiLLMEngine, LLMEngine.AnthropicLLMEngine],
        "multiple": False,
    },
    "ScriptEngine": {
        "classes": [
            ScriptEngine.ShowerThoughtsScriptEngine,
            ScriptEngine.CustomScriptEngine,
        ],
        "multiple": False,
    },
    "TTSEngine": {
        "classes": [TTSEngine.CoquiTTSEngine, TTSEngine.ElevenLabsTTSEngine],
        "multiple": False,
    },
    "CaptioningEngine": {
        "classes": [CaptioningEngine.SimpleCaptioningEngine, NoneEngine],
        "multiple": False,
    },
}
