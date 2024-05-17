import os
import shutil
from typing import TypedDict

import gradio as gr
import moviepy as mp
import moviepy.video.fx as vfx

from google_images_search import GoogleImagesSearch
from .BaseStockImageEngine import BaseStockImageEngine


class Spec(TypedDict):
    query: str
    start: float
    end: float


class GoogleStockImageEngine(BaseStockImageEngine):
    name = "Google"
    description = "Search for images using the Google Images API."

    num_options = 0

    def __init__(self, options: dict):
        api_key = self.get_setting(type="google_api_key")["api_key"]
        project_cx = self.get_setting(type="google_project_cx")["project_cx"]
        self.google = GoogleImagesSearch(api_key, project_cx)
        super().__init__()

    def get(self, query: str, start: float, end: float, i="") -> mp.ImageClip:
        max_width = int(self.ctx.width / 3 * 2)
        _search_params = {
            "q": query,
            "num": 1,
        }
        os.makedirs(f"temp{i}", exist_ok=True)
        try:
            self.google.search(
                search_params=_search_params,
                path_to_dir=f"./temp{i}/",
                custom_image_name="temp",
            )
            # we find the file called temp. extension
            filename = [f for f in os.listdir(f"./temp{i}/") if f.startswith("temp.")][0]
            img = mp.ImageClip(f"./temp{i}/{filename}")
            # delete the temp folder
        except Exception as e:
            gr.Warning(f"Failed to get image: {e}")
            return (
                mp.ColorClip((self.ctx.width, self.ctx.height), color=(0, 0, 0))
                .with_duration(end - start)
                .with_start(start)
            )
        finally:
            shutil.rmtree(f"temp{i}")

        img = (
            img.with_duration(end - start)
            .with_start(start)
            .with_effects([vfx.Resize(width=max_width)])
            .with_position(("center", "center"))
        )
        return img

    @classmethod
    def get_options(cls):
        return []

    @classmethod
    def get_settings(cls):
        current_api_key = cls.get_setting(type="google_api_key")
        current_api_key = current_api_key["api_key"] if current_api_key else ""
        api_key_box = gr.Textbox(
            label="Google API Key",
            type="password",
            value=current_api_key,
        )
        current_project_cx = cls.get_setting(type="google_project_cx")
        current_project_cx = (
            current_project_cx["project_cx"] if current_project_cx else ""
        )
        project_cx_box = gr.Textbox(
            label="Google Project CX",
            type="password",
            value=current_project_cx,
        )
        submit_button = gr.Button("Save")

        def save_settings(api_key, project_cx):
            cls.store_setting(type="google_api_key", data={"api_key": api_key})
            cls.store_setting(type="google_project_cx", data={"project_cx": project_cx})
            gr.Info("Settings saved successfully")

        submit_button.click(save_settings, inputs=[api_key_box, project_cx_box])
