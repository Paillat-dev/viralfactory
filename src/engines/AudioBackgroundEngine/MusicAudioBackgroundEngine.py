import os
import random
import shutil
import time

import gradio as gr
import moviepy as mp
import moviepy.audio.fx as afx

from . import BaseAudioBackgroundEngine


class MusicAudioBackgroundEngine(BaseAudioBackgroundEngine):
    name = "Music Audio Background Engine"
    description = "A basic background engine to set the background audio to a music track."
    num_options = 1

    def __init__(self, options: list[str]):
        assets = self.get_assets(type="bcg_music")
        self.background_audio = [asset for asset in assets if asset.data["name"] == options[0]][0]
        super().__init__()

    @classmethod
    def get_options(cls) -> list:
        assets = cls.get_assets(type="bcg_music")
        choices = (
            [asset.data["name"] for asset in assets]
            if len(assets) > 0
            else ["No audios available"]
        )

        return [
            gr.Dropdown(
                choices=choices,
                label="Background Music",
                value=choices[0] if len(assets) > 0 else "No audios available",
                type="value",
            )
        ]

    def get_background(self):
        background = mp.AudioFileClip(f"{self.background_audio.path}")
        self.ctx.credits += f"\n{self.background_audio.data['credits']}"
        # we add fade in and fade out to the audio
        background = background.with_effects([afx.AudioFadeIn(1), afx.AudioFadeOut(1)])
        # loop the audio to match the duration of the video
        audio_clips = []
        while sum([clip.duration for clip in audio_clips]) < self.ctx.duration:
            audio_clips.append(background)
        # now we cut the audio to match the duration of the video exactly
        audio = mp.concatenate_audioclips(audio_clips)
        audio = audio.with_subclip(0, self.ctx.duration)
        # finally we add a new fade OUT only to the audio
        audio = audio.with_effects([afx.AudioFadeOut(1)])
        # change volume to 0.5
        audio: mp.AudioFileClip = audio.with_multiply_volume(0.5)
        self.ctx.audio.append(audio)

    @classmethod
    def get_settings(cls):
        def add_file(fp: str, name: str, credits: str):
            if name == "":
                raise ValueError("Name cannot be empty.")
            new_fp = f"local/assets/audios/{time.time()}{os.path.splitext(fp)[1]}"
            shutil.move(fp, new_fp)
            cls.add_asset(
                path=new_fp,
                metadata={"name": name, "credits": credits},
                type="bcg_music",
            )
            gr.Info("Video added successfully.")

        with gr.Column() as add_asset_inputs:
            add_asset_name = gr.Textbox(label="Name of the audio", value="")
            add_asset_credits = gr.Textbox(label="Credits", value="")
            add_asset_input = gr.File(
                file_count="single",
                file_types=["audio"],
                type="filepath",
            )
        with gr.Column() as add_asset_button:
            add_asset_button = gr.Button(value="Add Audio")
            add_asset_button.click(
                add_file,
                inputs=[add_asset_input, add_asset_name, add_asset_credits],
                outputs=[],
            )
