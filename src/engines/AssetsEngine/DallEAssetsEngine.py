import gradio as gr
import openai
import moviepy.editor as mp
import io
import base64
import time
import requests
import os

from moviepy.video.fx.resize import resize
from typing import Literal, TypedDict

from . import BaseAssetsEngine


class Spec(TypedDict):
    prompt: str
    start: float
    end: float
    style: Literal["vivid", "natural"]


class DallEAssetsEngine(BaseAssetsEngine):
    name = "DALL-E"
    description = "A powerful image generation model by OpenAI."
    spec_name = "dalle"
    spec_description = (
        "Use the dall-e 3 model to generate images from a detailed prompt."
    )
    specification = {
        "prompt": "A detailed prompt to generate the image from. Describe every subtle detail of the image you want to generate. [str]",
        "start": "The starting time of the video clip. [float]",
        "end": "The ending time of the video clip. [float]",
        "style": "The style of the generated images. Must be one of vivid or natural. Vivid causes the model to lean towards generating hyper-real and dramatic images. Natural causes the model to produce more natural, less hyper-real looking images. [str]",
    }

    num_options = 1

    def __init__(self, options: dict):
        self.aspect_ratio: Literal["portrait", "square", "landscape"] = options[0]

        super().__init__()

    def get_assets(self, options: list[Spec]) -> list[mp.ImageClip]:
        max_width = self.ctx.width / 3 * 2
        clips = []
        for option in options:
            prompt = option["prompt"]
            start = option["start"]
            end = option["end"]
            style = option["style"]
            size = (
                "1024x1024"
                if self.aspect_ratio == "square"
                else "1024x1792"
                if self.aspect_ratio == "portrait"
                else "1792x1024"
            )
            try:
                response = openai.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size=size,
                    n=1,
                    style=style,
                    response_format="url",
                )
            except openai.BadRequestError as e:
                if e.code == "content_policy_violation":
                    # we skip this prompt
                    continue
                else:
                    raise
            img = requests.get(response.data[0].url)
            with open("temp.png", "wb") as f:
                f.write(img.content)
            img = mp.ImageClip("temp.png")
            os.remove("temp.png")

            img: mp.ImageClip = img.set_duration(end - start)
            img: mp.ImageClip = img.set_start(start)
            img: mp.ImageClip = resize(img, width=max_width)
            if self.aspect_ratio == "portrait":
                img: mp.ImageClip = img.set_position(("center", "top"))
            elif self.aspect_ratio == "landscape":
                img: mp.ImageClip = img.set_position(("center", "top"))
            elif self.aspect_ratio == "square":
                img: mp.ImageClip = img.set_position(("center", "top"))
            clips.append(img)
        return clips

    @classmethod
    def get_options(cls):
        return [
            gr.Radio(
                ["portrait", "square", "landscape"],
                label="Aspect Ratio",
                value="square",
            )
        ]
