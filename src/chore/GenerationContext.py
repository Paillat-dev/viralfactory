import os
import time
from datetime import datetime

import moviepy.editor as mp

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
            powerfulllmengine,
            simplellmengine,
            scriptengine,
            ttsengine,
            captioningengine,
            assetsengine,
            settingsengine,
            backgroundengine,
            metadataengine,
            uploadengine,
            progress,
    ) -> None:
        self.progress = progress

        self.powerfulllmengine: engines.LLMEngine.BaseLLMEngine = powerfulllmengine[0]
        self.powerfulllmengine.ctx = self

        self.simplellmengine: engines.LLMEngine.BaseLLMEngine = simplellmengine[0]
        self.simplellmengine.ctx = self

        self.scriptengine: engines.ScriptEngine.BaseScriptEngine = scriptengine[0]
        self.scriptengine.ctx = self

        self.ttsengine: engines.TTSEngine.BaseTTSEngine = ttsengine[0]
        self.ttsengine.ctx = self

        self.captioningengine: engines.CaptioningEngine.BaseCaptioningEngine = (
            captioningengine[0]
        )
        self.captioningengine.ctx = self

        self.assetsengine: list[engines.AssetsEngine.BaseAssetsEngine] = assetsengine
        for eng in self.assetsengine:
            eng.ctx = self
        self.assetsengineselector = engines.AssetsEngine.AssetsEngineSelector()
        self.assetsengineselector.ctx = self

        self.settingsengine: engines.SettingsEngine.SettingsEngine = settingsengine[0]
        self.settingsengine.ctx = self

        self.backgroundengine: engines.BackgroundEngine.BaseBackgroundEngine = (
            backgroundengine[0]
        )
        self.backgroundengine.ctx = self

        self.metadataengine: engines.MetadataEngine.BaseMetadataEngine = metadataengine[
            0
        ]
        self.metadataengine.ctx = self

        self.uploadengine: list[engines.UploadEngine.BaseUploadEngine] = uploadengine
        for eng in self.uploadengine:
            eng.ctx = self

    def setup_dir(self):
        self.dir = f"output/{time.time()}"
        os.makedirs(self.dir)

    def get_file_path(self, name: str) -> str:
        return os.path.join(self.dir, name)

    def process(self):
        # ⚠️ IMPORTANT NOTE: All methods called here are expected to be defined as abstract methods in the base classes, if not there is an issue with the engine implementation.

        # Kinda like in css, we have a z-index of moviepy clips (any). Then the engines append some clips to this, and we render it all with index 0 below, and index 9 at the top.
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

        self.progress(0.1, "Loading settings...")
        self.setup_dir()
        self.settingsengine.load()

        self.progress(0.2, "Generating script...")
        self.scriptengine.generate()

        self.progress(0.3, "Generating synthtetizing voice...")
        self.ttsengine.synthesize(self.script, self.get_file_path("tts.wav"))
        self.duration: float  # for type hinting

        if not isinstance(self.backgroundengine, engines.NoneEngine):
            self.progress(0.4, "Generating background...")
            self.backgroundengine.get_background()

        self.assetsengine = [
            engine
            for engine in self.assetsengine
            if not isinstance(engine, engines.NoneEngine)
        ]
        if len(self.assetsengine) > 0:
            self.progress(0.5, "Generating assets...")
            self.assetsengineselector.get_assets()

        if not isinstance(self.captioningengine, engines.NoneEngine):
            self.progress(0.6, "Generating captions...")
            self.captioningengine.get_captions()
        else:
            self.captions = []

        # add any other processing steps here

        # we render to a file called final.mp4
        self.progress(0.7, "Rendering video...")
        clips = [
            *self.index_0,
            *self.index_1,
            *self.index_2,
            *self.index_3,
            *self.index_4,
            *self.index_5,
            *self.index_6,
            *self.index_7,
            *self.index_8,
            *self.index_9,
        ]
        clip = mp.CompositeVideoClip(clips, size=(self.width, self.height))
        clip.set_duration(self.duration)
        audio = mp.AudioFileClip(self.get_file_path("tts.wav"))
        clip: mp.CompositeVideoClip = clip.set_audio(audio)
        clip.write_videofile(self.get_file_path("final.mp4"), fps=60, threads=4)

        self.progress(0.8, "Generating metadata...")
        self.metadataengine.get_metadata()

        self.progress(0.9, "Uploading video...")
        for engine in self.uploadengine:
            engine.upload()

        self.progress(0.99, "Storing in database...")
        self.store_in_db()
        self.progress(1, "Done!")
