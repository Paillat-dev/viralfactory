import os

import gradio as gr
import moviepy as mp

from . import BasePipeline
from ... import engines
from ...chore import GenerationContext
from ...utils.prompting import get_prompt, get_prompts


class ScriptedVideoPipeline(BasePipeline):
    name = "Scripted Long Form Pipeline"
    description = (
        "A pipeline that generates a long form video based on a script instruction."
    )
    num_options = 2

    def __init__(self, options: list) -> None:
        self.user_instructions = options[0]
        self.assets_instructions = options[1]
        super().__init__()

    def launch(self, ctx: GenerationContext) -> None:

        ctx.progress(0.1, "Loading settings...")
        ctx.setup_dir()
        if not isinstance(ctx.settingsengine, engines.NoneEngine):
            ctx.settingsengine.load()
        prompts = get_prompts("long_form", by_file_location=__file__)
        ctx.progress(0.2, "Generating chapters...")
        system = prompts["chapters"]["system"]
        chat = prompts["chapters"]["chat"]
        chat = chat.replace("{user_instructions}", str(self.user_instructions))
        chapters: list[dict[str, str]] = ctx.powerfulllmengine.generate(
            system_prompt=system,
            chat_prompt=chat,
            json_mode=True,
            temperature=1,
            max_tokens=4096,
        )["chapters"]
        ctx.script = ""

        for chapter in chapters:
            ctx.progress(0.2, f"Generating chapter: {chapter['title']}...")
            system = prompts["writer"]["system"]
            chat = prompts["writer"]["chat"]
            chat = (
                chat.replace("{user_instructions}", str(self.user_instructions))
                .replace("{chapter_title}", chapter["title"])
                .replace("{chapter_instructions}", chapter["explanation"])
            )
            ctx.script += ctx.powerfulllmengine.generate(
                system_prompt=system,
                chat_prompt=chat,
                temperature=1,
                max_tokens=4096,
                json_mode=True,
            )["chapter"]
            ctx.script += "\n"

        ctx.progress(0.3, "Synthesizing voice...")
        ctx.duration = ctx.ttsengine.synthesize(
            ctx.script, ctx.get_file_path("tts.wav")
        )
        ctx.audio.append(mp.AudioFileClip(ctx.get_file_path("tts.wav")))
        ctx.progress(0.4, "Transcribing audio...")
        ctx.timed_script = ctx.transcriptionengine.transcribe(
            ctx.get_file_path("tts.wav"), fast=False, words=True
        )

        ctx.progress(0.5, "Generating images...")
        system = prompts["imager"]["system"]
        chat = prompts["imager"]["chat"]
        chat = chat.replace("{user_instructions}", str(self.user_instructions))
        chat = chat.replace("{assets_instructions}", str(self.assets_instructions))
        chat = chat.replace("{video_transcript}", str(ctx.timed_script))
        assets: list[dict[str, str | float]] = ctx.powerfulllmengine.generate(
            system_prompt=system,
            chat_prompt=chat,
            temperature=1,
            max_tokens=4096,
            json_mode=True,
        )["assets"]
        for asset in assets:
            if asset["type"] == "stock":
                ctx.index_4.append(
                    ctx.stockimageengine.get(
                        asset["query"], asset["start"], asset["end"]
                    )
                )
            elif asset["type"] == "ai":
                ctx.index_5.append(
                    ctx.aiimageengine.generate(
                        asset["prompt"], asset["start"], asset["end"]
                    )
                )

        if not isinstance(ctx.audiobackgroundengine, engines.NoneEngine):
            ctx.progress(0.45, "Generating audio background...")
            ctx.audio.append(ctx.audiobackgroundengine.get_background())

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
        system = prompts["description"]["system"]
        chat = prompts["description"]["chat"]
        chat.replace("{script}", ctx.script)
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
        return [
            gr.Textbox(
                lines=4,
                max_lines=6,
                label="Video instructions",
            ),
            gr.Textbox(
                lines=4,
                max_lines=6,
                label="Assets only instructions",
            ),
        ]
