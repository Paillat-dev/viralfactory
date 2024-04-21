from . import Pipelines
from . import AIImageEngine
from . import StockImageEngine
from . import BackgroundEngine
from . import CaptioningEngine
from . import LLMEngine
from . import SettingsEngine
from . import TTSEngine
from . import UploadEngine
from . import AudioBackgroundEngine
from . import TranscriptionEngine
from .BaseEngine import BaseEngine
from .NoneEngine import NoneEngine

ENGINES: dict[str, dict[str, bool | list[BaseEngine]]] = {
    "Pipeline": {
        "classes": [Pipelines.ScriptedVideoPipeline],
        "multiple": False,
    },
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
    "TTSEngine": {
        "classes": [TTSEngine.CoquiTTSEngine],
        "multiple": False,
    },
    "TranscriptionEngine": {
        "classes": [TranscriptionEngine.WhisperTranscriptionEngine],
        "multiple": False,
    },
    "CaptioningEngine": {
        "classes": [CaptioningEngine.SimpleCaptioningEngine, NoneEngine],
        "multiple": False,
    },
    "AIImageEngine": {
        "classes": [
            AIImageEngine.DallEAIImageEngine,
            AIImageEngine.A1111AIImageEngine,
        ],
        "multiple": False,
    },
    "StockImageEngine": {
        "classes": [StockImageEngine.GoogleStockImageEngine],
        "multiple": False,
    },
    "BackgroundEngine": {
        "classes": [NoneEngine, BackgroundEngine.VideoBackgroundEngine],
        "multiple": False,
    },
    "AudioBackgroundEngine": {
        "classes": [NoneEngine, AudioBackgroundEngine.MusicAudioBackgroundEngine],
        "multiple": False,
    },
    "UploadEngine": {
        "classes": [
            UploadEngine.TikTokUploadEngine,
            UploadEngine.YouTubeUploadEngine,
            NoneEngine,
        ],
        "multiple": True,
    },
}
