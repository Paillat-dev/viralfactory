import os
import random
import shutil
import time

import gradio as gr
import moviepy.editor as mp
from moviepy.video.fx.crop import crop
from moviepy.video.fx.resize import resize

from . import BaseBackgroundEngine


class VideoBackgroundEngine(BaseBackgroundEngine):
    name = "SImple Background Engine"
    description = "A basic background engine to set the background of the video from a local file."
    num_options = 1

    def __init__(self, options: list[int]):
        assets = self.get_assets(type="bcg_video")
        self.background_video = assets[options[0]].path if len(assets) > 0 else ""
        super().__init__()

    @classmethod
    def get_options(cls) -> list:
        assets = cls.get_assets(type="bcg_video")
        choices = (
            [asset.data["name"] for asset in assets]
            if len(assets) > 0
            else ["No videos available"]
        )

        return [
            gr.Dropdown(
                choices=choices,
                label="Background Video",
                value=choices[0] if len(assets) > 0 else "No videos available",
                type="index",
            )
        ]

    def get_background(self) -> mp.VideoClip:
        background = mp.VideoFileClip(f"{self.background_video}", audio=False)
        background_max_start = background.duration - self.ctx.duration
        if background_max_start < 0:
            raise ValueError(
                "The background video is shorter than the video to be generated."
            )
        start = random.uniform(0, background_max_start)
        clip = background.subclip(start, start + self.ctx.duration)
        w, h = clip.size
        self.ctx.index_0.append(
            crop(
                clip,
                width=self.ctx.width,
                height=self.ctx.height,
                x_center=w / 2,
                y_center=h / 2,
            )
        )

    @classmethod
    def get_settings(cls) -> list:
        def add_file(fp: str, name: str, credits: str):
            if name == "":
                raise ValueError("Name cannot be empty.")
            new_fp = f"local/assets/videos/{time.time()}{os.path.splitext(fp)[1]}"
            shutil.move(fp, new_fp)
            cls.add_asset(
                path=new_fp,
                metadata={"name": name, "credits": credits},
                type="bcg_video",
            )
            gr.Info("Video added successfully.")

        with gr.Column() as add_asset_inputs:
            add_asset_name = gr.Textbox(label="Name of the video", value="")
            add_asset_credits = gr.Textbox(label="Credits", value="")
            add_asset_input = gr.File(
                file_count="single",
                file_types=["video"],
                type="filepath",
            )
        with gr.Column() as add_asset_button:
            add_asset_button = gr.Button(value="Add Video")
            add_asset_button.click(
                add_file,
                inputs=[add_asset_input, add_asset_name, add_asset_credits],
                outputs=[],
            )
