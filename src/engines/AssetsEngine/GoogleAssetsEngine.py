import os
import shutil
from typing import TypedDict

import gradio as gr
import moviepy.editor as mp
from google_images_search import GoogleImagesSearch
from moviepy.video.fx.resize import resize

from . import BaseAssetsEngine


class Spec(TypedDict):
    query: str
    start: float
    end: float


class GoogleAssetsEngine(BaseAssetsEngine):
    name = "Google"
    description = "Search for images using the Google Images API."
    spec_name = "google"
    spec_description = (
        "Use the Google Images API to search for images based on a query."
    )
    specification = {
        "query": "A short and concise query to search for images. Do not include any details, just a simple query. [str]",
        "start": "The starting time of the video clip. [float]",
        "end": "The ending time of the video clip. [float]",
    }

    num_options = 0

    def __init__(self, options: dict):
        api_key = self.get_setting(type="google_api_key")["api_key"]
        project_cx = self.get_setting(type="google_project_cx")["project_cx"]
        self.google = GoogleImagesSearch(api_key, project_cx)
        super().__init__()

    def generate(self, options: list[Spec]) -> list[mp.ImageClip]:
        max_width = self.ctx.width / 3 * 2
        clips = []
        for option in options:
            query = option["query"]
            start = option["start"]
            end = option["end"]
            _search_params = {
                "q": query,
                "num": 1,
            }
            os.makedirs("temp", exist_ok=True)
            try:
                self.google.search(
                    search_params=_search_params,
                    path_to_dir="./temp/",
                    custom_image_name="temp",
                )
                # we find the file called temp. extension
                filename = [f for f in os.listdir("./temp/") if f.startswith("temp.")][0]
                img = mp.ImageClip(f"./temp/{filename}")
                # delete the temp folder
            finally:
                shutil.rmtree("temp")

            img: mp.ImageClip = img.set_duration(end - start)
            img: mp.ImageClip = img.set_start(start)
            img: mp.ImageClip = resize(img, width=max_width)
            img: mp.ImageClip = img.set_position(("center", "top"))
            clips.append(img)
        return clips

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
