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

    def upload(self):
        cookies = self.get_setting(type="cookies")["cookies"]
        if cookies is None:
            gr.Warning(
                "Skipping upload to TikTok because no cookies were provided. Please provide cookies in the settings."
            )
            return
        title: str = self.ctx.title
        description: str = self.ctx.description
        hashtags = self.hashtags.strip().split(" ")

        # extract any hashtags from the description / title and remove them from the description
        for word in title.split():
            if word.startswith("#"):
                hashtags.append(word)
                title = title.replace(word, "")
        for word in description.split():
            if word.startswith("#"):
                hashtags.append(word)
                description = description.replace(word, "")

        title = title.strip()
        description = description.strip()
        hashtags_str = " ".join(hashtags) + " " if hashtags else ""
        failed = upload_video(
            filename=self.ctx.get_file_path("final.mp4"),
            description=f"{title}\n{description} {hashtags_str}",
            cookies_str=cookies,
            browser="chrome",
            comment=True, stitch=False, duet=False
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
