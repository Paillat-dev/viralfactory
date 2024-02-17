import moviepy.editor as mp
import time
import os
import gradio as gr

from .. import engines
from ..utils.prompting import get_prompt


class GenerationContext:
    def __init__(
        self,
        powerfulllmengine,
        simplellmengine,
        scriptengine,
        ttsengine,
        captioningengine,
        assetsengine,
    ) -> None:
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

    def setup_dir(self):
        self.dir = f"output/{time.time()}"
        os.makedirs(self.dir)

    def get_file_path(self, name: str) -> str:
        return os.path.join(self.dir, name)

    def process(self):
        # ⚠️ IMPORTANT NOTE: All methods called here are expected to be defined as abstract methods in the base classes, if not there is an issue with the engine implementation.

        progress = gr.Progress()
        self.width, self.height = (
            1080,
            1920,
        )  # TODO: Add support for custom resolution, for now it's tiktok's resolution
        self.setup_dir()

        self.script = self.scriptengine.generate()

        self.timed_script = self.ttsengine.synthesize(
            self.script, self.get_file_path("tts.wav")
        )

        self.assetsengine = [
            engine for engine in self.assetsengine if not isinstance(engine, engines.NoneEngine)
        ]
        if len(self.assetsengine) > 0:
            self.assets = self.assetsengineselector.get_assets()
        else:
            self.assets = []


        if not isinstance(self.captioningengine, engines.NoneEngine):
            self.captions = self.captioningengine.get_captions()
        else:
            self.captions = []

        # add any other processing steps here

        # we render to a file called final.mp4
        # using moviepy CompositeVideoClip
        clips = [*self.assets, *self.captions]
        clip = mp.CompositeVideoClip(clips, size=(self.width, self.height))
        audio = mp.AudioFileClip(self.get_file_path("tts.wav"))
        clip = clip.set_audio(audio)
        clip.write_videofile(self.get_file_path("final.mp4"), fps=60)
        