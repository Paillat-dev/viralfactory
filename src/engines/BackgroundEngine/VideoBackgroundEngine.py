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
    name = "Video Background Engine"
    description = "A basic background engine to set the background of the video from a local file."
    num_options = 1

    def __init__(self, options: list[str]):
        assets = self.get_assets(type="bcg_video")
        self.background_video = [asset for asset in assets if asset.data["name"] == options[0]][0]
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
                type="value",
            )
        ]

    def get_background(self):
        background = mp.VideoFileClip(f"{self.background_video.path}", audio=False)
        background_max_start = background.duration - self.ctx.duration
        if background_max_start < 0:
            raise ValueError(
                "The background video is shorter than the video to be generated."
            )
        start = random.uniform(0, background_max_start)
        clip = background.subclip(start, start + self.ctx.duration)
        self.ctx.credits += f"\n{self.background_video.data['credits']}"
        clip = resize(clip, width=self.ctx.width, height=self.ctx.height)
        w, h = clip.size
        if w > h:
            clip = crop(clip, width=self.ctx.width, height=self.ctx.height, x_center=w / 2, y_center=h / 2)
        else:
            clip = crop(clip, width=self.ctx.width, height=self.ctx.height, x_center=w / 2, y_center=h / 2)
        self.ctx.index_0.append(clip)

    @classmethod
    def get_settings(cls):
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
