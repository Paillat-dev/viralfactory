import os

import gradio as gr
import moviepy as mp

from . import BasePipeline
from ... import engines
from ...chore import GenerationContext
from ...utils.prompting import get_prompt, get_prompts


class ScriptedShortPipeline(BasePipeline):
    name = "Scripted Short Pipeline"
    description = "A pipeline that generates a short video based on a script."
    num_options = 2

    def __init__(self, options: list) -> None:
        self.script_prompt = self.get_prompts()[options[0]]
        self.n_sentences = options[1]
        super().__init__()

    @classmethod
    def get_prompts(cls):
        return get_prompts("scripts", by_file_location=__file__)

    def launch(self, ctx: GenerationContext) -> None:

        ctx.progress(0.1, "Loading settings...")
        ctx.setup_dir()
        if not isinstance(ctx.settingsengine, engines.NoneEngine):
            ctx.settingsengine.load()

        ctx.progress(0.2, "Generating script...")
        system, chat = self.script_prompt["system"], self.script_prompt["chat"]
        system, chat = system.replace(
            "{n_sentences}", str(self.n_sentences)
        ), chat.replace("{n_sentences}", str(self.n_sentences))
        ctx.script = ctx.powerfulllmengine.generate(
            system_prompt=system,
            chat_prompt=chat,
            json_mode=False,
            temperature=1.3,
            max_tokens=20 * self.n_sentences,
        )

        ctx.progress(0.3, "Synthesizing voice...")
        ctx.duration = ctx.ttsengine.synthesize(
            ctx.script, ctx.get_file_path("tts.wav")
        )
        ctx.audio.append(mp.AudioFileClip(ctx.get_file_path("tts.wav")))
        ctx.timed_script = ctx.transcriptionengine.transcribe(
            ctx.get_file_path("tts.wav"), fast=False, words=True
        )

        if not isinstance(ctx.backgroundengine, engines.NoneEngine):
            ctx.progress(0.4, "Generating background...")
            ctx.index_0.append(ctx.backgroundengine.get_background())

        if not isinstance(ctx.audiobackgroundengine, engines.NoneEngine):
            ctx.progress(0.45, "Generating audio background...")
            ctx.audio.append(ctx.audiobackgroundengine.get_background())

        ctx.assetsengine = [
            engine
            for engine in ctx.assetsengine
            if not isinstance(engine, engines.NoneEngine)
        ]
        if len(ctx.assetsengine) > 0:
            ctx.progress(0.5, "Generating assets...")
            ctx.index_3.extend(ctx.assetsengineselector.get_assets())

        if not isinstance(ctx.captioningengine, engines.NoneEngine):
            ctx.progress(0.6, "Generating captions...")
            ctx.index_7.extend(
                ctx.captioningengine.get_captions(words=ctx.timed_script)
            )

        # we render to a file called final.mp4
        ctx.progress(0.7, "Rendering video...")
        clips = [
            *ctx.index_0,
            *ctx.index_1,
            *ctx.index_2,
            *ctx.index_3,
            *ctx.index_4,
            *ctx.index_5,
            *ctx.index_6,
            *ctx.index_7,
            *ctx.index_8,
            *ctx.index_9,
        ]
        audio = mp.CompositeAudioClip(ctx.audio)
        clip = (
            mp.CompositeVideoClip(clips, size=(ctx.width, ctx.height))
            .with_duration(ctx.duration)
            .with_audio(audio)
        )
        clip.write_videofile(
            ctx.get_file_path("final.mp4"), fps=60, threads=4, codec="h264_nvenc"
        )

        system, chat = get_prompt("description", by_file_location=__file__)
        metadata = ctx.powerfulllmengine.generate(
            system_prompt=system, chat_prompt=chat, json_mode=True, temperature=1
        )
        ctx.title = metadata["title"]
        ctx.description = metadata["description"]

        ctx.description = ctx.description + "\n" + ctx.credits
        ctx.progress(0.9, "Uploading video...")
        for engine in ctx.uploadengine:
            try:
                engine.upload(
                    ctx.title, ctx.description, ctx.get_file_path("final.mp4")
                )
            except Exception as e:
                print(e)
                gr.Warning(f"{engine.name} failed to upload the video.")

        ctx.progress(0.99, "Storing in database...")
        ctx.store_in_db()
        ctx.progress(1, "Done!")

        command = "start" if os.name == "nt" else "open"
        os.system(f"{command} {os.path.abspath(ctx.dir)}")

    @classmethod
    def get_options(cls):
        prompts = list(cls.get_prompts().keys())
        return [
            gr.Radio(
                prompts,
                label="Script",
                value=prompts[0],
            ),
            gr.Number(
                minimum=1,
                maximum=25,
                label="Number of sentences",
                value=5,
                step=1,
            ),
        ]
