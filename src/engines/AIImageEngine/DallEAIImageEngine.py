import os
from typing import Literal, TypedDict, List

import gradio as gr
import moviepy as mp
import moviepy.video.fx as vfx
import openai
from openai import OpenAI
import requests

from . import BaseAIImageEngine


class Spec(TypedDict):
    prompt: str
    start: float
    end: float
    style: Literal["vivid", "natural"]


class DallEAIImageEngine(BaseAIImageEngine):
    name = "DALL-E"
    description = "A powerful image generation model by OpenAI."

    num_options = 1

    def __init__(self, options: dict):
        self.aspect_ratio: Literal["portrait", "square", "landscape"] = options[0]
        api_key = self.retrieve_setting(identifier="openai_api_key")
        if not api_key:
            raise ValueError("OpenAI API key is not set.")
        self.client = OpenAI(api_key=api_key["api_key"])

        super().__init__()

    def generate(self, prompt: str, start: float, end: float, i="") -> mp.ImageClip:
        max_width = self.ctx.width / 3 * 2
        size: Literal["1024x1024", "1024x1792", "1792x1024"] = (
            "1024x1024"
            if self.aspect_ratio == "square"
            else "1024x1792" if self.aspect_ratio == "portrait" else "1792x1024"
        )
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                n=1,
                style="natural",
                response_format="url",
            )
        except openai.BadRequestError as e:
            if e.code == "content_policy_violation":
                gr.Warning("Image generation violated openai policies.")
                return (
                    mp.ColorClip((self.ctx.width, self.ctx.height), color=(0, 0, 0))
                    .with_duration(end - start)
                    .with_start(start)
                )

            else:
                raise
        img_bytes = requests.get(response.data[0].url)
        fname = f"temp{i}.png"
        with open(fname, "wb") as f:
            f.write(img_bytes.content)
        img = mp.ImageClip(fname)
        os.remove(fname)

        position = ("center", "center")
        img = (
            img.with_position(position)
            .with_duration(end - start)
            .with_start(start)
            .with_effects([vfx.Resize(width=max_width)])
        )
        return img

    @classmethod
    def get_options(cls):
        return [
            gr.Radio(
                ["portrait", "square", "landscape"],
                label="Aspect Ratio",
                value="square",
            )
        ]

    @classmethod
    def get_settings(cls):
        current_api_key: dict | list[dict] | None = cls.retrieve_setting(
            identifier="openai_api_key"
        )
        current_api_key = current_api_key["api_key"] if current_api_key else ""
        api_key_input = gr.Textbox(
            label="OpenAI API Key",
            type="password",
            value=current_api_key,
        )
        save = gr.Button("Save")

        def save_api_key(api_key: str):
            cls.store_setting(identifier="openai_api_key", data={"api_key": api_key})
            gr.Info("API key saved successfully.")
            return gr.update(value=api_key)

        save.click(save_api_key, inputs=[api_key_input])
