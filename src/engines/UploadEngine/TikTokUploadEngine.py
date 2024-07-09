import gradio as gr
from tiktok_uploader.upload import upload_video

from .BaseUploadEngine import BaseUploadEngine


class TikTokUploadEngine(BaseUploadEngine):
    name = "TikTokUpload"
    description = "Upload to TikTok"

    num_options = 1

    def __init__(self, options) -> None:
        self.hashtags = options[0]
        super().__init__()

    def upload(
        self, title: str, description: str, path: str, hashtags_end: bool = True
    ):
        cookies = self.get_setting(type="cookies")["cookies"]
        if cookies is None:
            gr.Warning(
                "Skipping upload to TikTok because no cookies were provided. Please provide cookies in the settings."
            )
            return
        hashtags = self.hashtags.strip().split(" ")

        title = title.strip()
        description = description.strip()
        # we get all the hastags from title and description and add them to the list of hashtags, while removing them from the title and description
        for word in title.split():
            if word.startswith("#"):
                hashtags.append(word)
                title = title.replace(word, "")
        for word in description.split():
            if word.startswith("#"):
                hashtags.append(word)
                description = description.replace(word, "")

        hashtags_str = " ".join(hashtags) + " " if hashtags else ""
        final_description = (
            f"{title} {description} {hashtags_str}"
            if hashtags_end
            else f"{title} {hashtags_str} {description}"
        )
        final_description = final_description.strip()
        failed = upload_video(
            filename=path,
            description=final_description,
            cookies_str=cookies,
            browser="chrome",
            comment=True,
            stitch=False,
            duet=False,
        )
        for _ in failed:
            gr.Error(f"Failed to upload to TikTok")

    @classmethod
    def get_options(cls):
        hashtags = gr.Textbox(label="hashtags", type="text", value="#fyp #foryou")
        return [hashtags]

    @classmethod
    def get_settings(cls):
        current_settings = cls.get_setting(type="cookies") or {"cookies": ""}
        gr.Markdown(
            "Input your TikTok session cookies. You can get them as shown [here](https://github.com/wkaisertexas/tiktok-uploader?tab=readme-ov-file#authentication)."
        )
        cookies_input = gr.Textbox(
            lines=20,
            max_lines=50,
            label="cookies",
            type="text",
            value=current_settings["cookies"],
        )
        cookies_save_btn = gr.Button("Save")

        def save(cookies: str):
            cls.store_setting(type="cookies", data={"cookies": cookies})
            gr.Info("Cookies saved successfully")

        cookies_save_btn.click(save, inputs=[cookies_input])
