import os
import time
from datetime import datetime

from .. import engines
from ..models import Video, SessionLocal


class GenerationContext:
    def store_in_db(self):
        with SessionLocal() as db:
            db.add(
                Video(
                    title=self.title,
                    description=self.description,
                    script=self.script,
                    timed_script=self.timed_script,
                    timestamp=datetime.now(),
                    path=self.dir,
                )
            )
            db.commit()

    def __init__(
        self,
        pipeline,
        settingsengine,
        simplellmengine,
        powerfulllmengine,
        ttsengine,
        transcriptionengine,
        captioningengine,
        aiimageengine,
        stockimageengine,
        backgroundengine,
        audiobackgroundengine,
        uploadengine,
        progress,
    ) -> None:
        self.captions = []
        self.dir = None
        self.script = None
        self.description = None
        self.title = None
        self.credits = None
        self.duration = None
        self.progress = progress

        self.pipeline: engines.Pipelines.BasePipeline = pipeline[0]
        self.pipeline.ctx = self

        self.simplellmengine: engines.LLMEngine.BaseLLMEngine = simplellmengine[0]
        self.simplellmengine.ctx = self

        self.powerfulllmengine: engines.LLMEngine.BaseLLMEngine = powerfulllmengine[0]
        self.powerfulllmengine.ctx = self

        self.ttsengine: engines.TTSEngine.BaseTTSEngine = ttsengine[0]
        self.ttsengine.ctx = self

        self.transcriptionengine: (
            engines.TranscriptionEngine.BaseTranscriptionEngine
        ) = transcriptionengine[0]

        self.captioningengine: engines.CaptioningEngine.BaseCaptioningEngine = (
            captioningengine[0]
        )
        self.captioningengine.ctx = self

        self.aiimageengine: engines.AIImageEngine.BaseAIImageEngine = aiimageengine[0]
        self.aiimageengine.ctx = self

        self.stockimageengine: engines.StockImageEngine.BaseStockImageEngine = (
            stockimageengine[0]
        )
        self.stockimageengine.ctx = self

        self.settingsengine: engines.SettingsEngine.SettingsEngine = settingsengine[0]
        self.settingsengine.ctx = self

        self.backgroundengine: engines.BackgroundEngine.BaseBackgroundEngine = (
            backgroundengine[0]
        )
        self.backgroundengine.ctx = self

        self.uploadengine: list[engines.UploadEngine.BaseUploadEngine] = uploadengine
        for eng in self.uploadengine:
            eng.ctx = self

        self.audiobackgroundengine: (
            engines.AudioBackgroundEngine.BaseAudioBackgroundEngine
        ) = audiobackgroundengine[0]
        self.audiobackgroundengine.ctx = self

        # Kinda like in css, we have a z-index of moviepy clips (any). Then the engines append some clips to this,
        # and we render it all with index 0 below, and index 9 at the top.
        self.index_0 = []
        self.index_1 = []
        self.index_2 = []
        self.index_3 = []
        self.index_4 = []
        self.index_5 = []
        self.index_6 = []
        self.index_7 = []
        self.index_8 = []
        self.index_9 = []

        self.audio = []

        self.credits = "Generated by AI"

    def setup_dir(self):
        self.dir = f"output/{time.time()}"
        os.makedirs(self.dir)

    def get_file_path(self, name: str) -> str:
        return os.path.join(self.dir, name)

    def process(self):
        self.pipeline.launch(self)
