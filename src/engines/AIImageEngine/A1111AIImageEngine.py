import os
from typing import Literal, TypedDict, List

import gradio as gr
import moviepy as mp
import moviepy.video.fx as vfx
import requests
import base64

from . import BaseAIImageEngine


class Spec(TypedDict):
    prompt: str
    start: float
    end: float
    style: Literal["vivid", "natural"]


class A1111AIImageEngine(BaseAIImageEngine):
    name = "A1111"
    description = "Stable Diffusion web UI"

    num_options = 0

    def __init__(self, options: dict):
        self.base_url = self.retrieve_setting(identifier="a1111_base_url")
        if not self.base_url:
            gr.Warning("Please set the base URL for the A1111 API.")
            return
        self.base_url = self.base_url["base_url"]

        super().__init__()

    def generate(self, prompt: str, start: float, end: float, i= "") -> mp.ImageClip:
        max_width = self.ctx.width / 3 * 2
        try:
            url = self.base_url + "/sdapi/v1/txt2img"
            payload = {
                "prompt": prompt,
                "width": 1024,
                "height": 1024,
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
            fname = f"temp{i}.png"
            with open(fname, "wb") as f:
                f.write(base64.b64decode(response.json()["images"][0]))
        except Exception as e:
            gr.Warning(f"Failed to get image: {e}")
            return (
                mp.ColorClip((self.ctx.width, self.ctx.height), color=(0, 0, 0))
                .with_duration(end - start)
                .with_start(start)
            )
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
        return []

    @classmethod
    def get_settings(cls):
        current_base_url: dict | list[dict] | None = cls.retrieve_setting(
            identifier="a1111_base_url"
        )
        current_base_url = current_base_url["base_url"] if current_base_url else ""
        base_url_input = gr.Textbox(
            label="Automatic 1111 Base URL",
            value=current_base_url,
        )
        save = gr.Button("Save")

        def save_base_url(base_url: str):
            cls.store_setting(identifier="a1111_base_url", data={"base_url": base_url})
            gr.Info("Base URL saved successfully.")
            return gr.update(value=base_url)

        save.click(save_base_url, inputs=[base_url_input])
