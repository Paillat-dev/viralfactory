from typing import TypedDict
from .BaseEngine import BaseEngine
from .NoneEngine import NoneEngine
from . import TTSEngine
from . import ScriptEngine
from . import LLMEngine
from . import CaptioningEngine
from . import AssetsEngine
from . import SettingsEngine
from . import BackgroundEngine
from . import MetadataEngine
from . import UploadEngine


class EngineDict(TypedDict):
    classes: list[BaseEngine]
    multiple: bool


ENGINES: dict[str, EngineDict] = {
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
