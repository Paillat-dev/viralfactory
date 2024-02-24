from . import AssetsEngine
from . import BackgroundEngine
from . import CaptioningEngine
from . import LLMEngine
from . import MetadataEngine
from . import ScriptEngine
from . import SettingsEngine
from . import TTSEngine
from . import UploadEngine
from .BaseEngine import BaseEngine
from .NoneEngine import NoneEngine

ENGINES: dict[str, dict[str, bool | list[BaseEngine]]] = {
    "SettingsEngine": {
        "classes": [SettingsEngine.SettingsEngine],
        "multiple": False,
        "show_dropdown": False,
    },
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
            ScriptEngine.ScientificFactsScriptEngine,
        ],
        "multiple": False,
    },
    "TTSEngine": {
        "classes": [TTSEngine.CoquiTTSEngine],
        "multiple": False,
    },
    "CaptioningEngine": {
        "classes": [CaptioningEngine.SimpleCaptioningEngine, NoneEngine],
        "multiple": False,
    },
    "AssetsEngine": {
        "classes": [
            AssetsEngine.DallEAssetsEngine,
            AssetsEngine.GoogleAssetsEngine,
            NoneEngine,
        ],
        "multiple": True,
    },
    "BackgroundEngine": {
        "classes": [BackgroundEngine.VideoBackgroundEngine, NoneEngine],
        "multiple": False,
    },
    "MetadataEngine": {
        "classes": [MetadataEngine.ShortsMetadataEngine],
        "multiple": False,
    },
    "UploadEngine": {
        "classes": [UploadEngine.TikTokUploadEngine, UploadEngine.YouTubeUploadEngine, NoneEngine],
        "multiple": True,
    },
}
