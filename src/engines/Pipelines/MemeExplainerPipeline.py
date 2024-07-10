import base64
import os
import shutil

import gradio as gr
import moviepy as mp
import requests

from . import BasePipeline
from ... import engines
from ...chore import GenerationContext
from ...utils.prompting import get_prompts

BASE_URL = "https://meme-api.com/gimme/"


class MemeExplainerPipeline(BasePipeline):
    name = "Meme Explainer"
    description = (
        "A pipeline that generates a long form video based on a script instruction."
    )
    num_options = 4

    def __init__(self, options: list) -> None:
        self.url = BASE_URL + options[0]
        self.sub = options[0]
        self.meme_path = options[1]
        self.character = options[2]
        self.duration = options[3]
        super().__init__()

    def launch(self, ctx: GenerationContext) -> None:
        if not ctx.powerfulllmengine.supports_vision:
            raise ValueError("Selected Powerful LLM engine does not support vision.")
        ctx.progress(0.1, "Loading settings...")
        ctx.setup_dir()
        ctx.width = 1080
        ctx.height = 1920

        system = get_prompts("MemeExplainer", by_file_location=__file__)["explainer"][
            "system"
        ]
        ctx.progress(0.2, "Getting meme...")
        if self.meme_path:
            # copy the meme to the directory
            ext = self.meme_path.split(".")[-1]
            with open(self.meme_path, "rb") as f:
                meme_b64 = base64.b64encode(f.read()).decode("utf-8")
            shutil.copy(self.meme_path, ctx.get_file_path("meme." + ext))
        else:
            with requests.get(self.url) as response:
                response.raise_for_status()
                meme = response.json()
                ctx.title = meme["title"]
                ctx.credits = f"Source: r/{self.sub}"
                url = meme["url"]
                ext = url.split(".")[-1]
                with requests.get(url) as response:
                    response.raise_for_status()
                    with open(ctx.get_file_path("meme." + ext), "wb") as f:
                        f.write(response.content)
            with open(ctx.get_file_path("meme." + ext), "rb") as f:
                meme_b64 = base64.b64encode(f.read()).decode("utf-8")
        meme_clip = mp.ImageClip(ctx.get_file_path("meme." + ext))
        meme_clip: mp.ImageClip = meme_clip.resized(width=ctx.width)
        meme_clip: mp.ImageClip = meme_clip.with_duration(self.duration)
        meme_clip: mp.ImageClip = meme_clip.with_position(("center", "center"))
        ctx.duration = 6
        ctx.index_8.append(meme_clip)

        meme_msg: dict = {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": f"image/{ext}",
                        "data": meme_b64,
                    },
                }
            ],
        }

        ctx.progress(0.3, "Generating explanation...")
        explanation = ctx.powerfulllmengine.generate(
            system_prompt=system.replace("{character}", self.character),
            messages=[meme_msg],
            max_tokens=1024,
            temperature=1.2,
        )
        if not isinstance(ctx.audiobackgroundengine, engines.NoneEngine):
            ctx.progress(0.6, "Generating audio background...")
            ctx.audio.append(ctx.audiobackgroundengine.get_background())

        if not isinstance(ctx.backgroundengine, engines.NoneEngine):
            ctx.progress(0.65, "Generating background...")
            ctx.index_0.append(ctx.backgroundengine.get_background())

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
            ctx.get_file_path("final.mp4"), fps=60, threads=16, codec="hevc_nvenc"
        )

        ctx.description = explanation + "\n" + ctx.credits

        ctx.progress(0.9, "Uploading video...")
        for engine in ctx.uploadengine:
            try:
                engine.upload(
                    ctx.title, ctx.description, ctx.get_file_path("final.mp4")
                )
            except Exception as e:
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
                lines=1,
                max_lines=1,
                label="Reddit sub",
                info="Reddit sub where to take the meme from",
                value="ExplainTheJoke",
            ),
            gr.Image(
                label="Meme",
                #                info="Upload a meme to explain instead of scraping one from Reddit",
                type="filepath",
                sources=["upload", "clipboard"],
            ),
            gr.Textbox(
                lines=1,
                max_lines=4,
                label="Character",
                info="Describe the behaviour and tone of the AI when explaining the meme",
                value="You should behave like an English Aristocrat from the 19th century. You should stay serious, "
                "but keep your vocabulary simple and clear so that everyone can understand it without a degree "
                "in English literature lol.",
            ),
            gr.Number(
                label="Duration",
                info="Duration of the video in seconds",
                value=6,
                minimum=1,
                maximum=60,
                step=1,
            ),
        ]
