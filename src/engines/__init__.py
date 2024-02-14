from . import TTSEngine
from .BaseEngine import BaseEngine
from . import ScriptEngine

ENGINES = {
    "TTSEngine": [TTSEngine.CoquiTTSEngine, TTSEngine.ElevenLabsTTSEngine],
    "ScriptEngine": [ScriptEngine.ShowerThoughtsScriptEngine],
}
