import gradio as gr
import orjson
from google_auth_oauthlib.flow import InstalledAppFlow

from . import BaseUploadEngine
from ...utils import youtube_uploading


class YouTubeUploadEngine(BaseUploadEngine):
    name = "YouTube"
    description = "Upload videos to YouTube"

    num_options = 2

    def __init__(self, options: list, **kwargs):
        super().__init__(**kwargs)
        self.oauth_name = options[0]
        self.oauth = self.retrieve_setting(type="oauth_credentials")[self.oauth_name]
        self.credentials = self.retrieve_setting(type="youtube_client_secrets")[
            self.oauth["client_secret"]
        ]

        self.hashtags = options[1]

    @classmethod
    def __oauth(cls, credentials):
        flow = InstalledAppFlow.from_client_config(
            credentials, scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )
        user_credentials = flow.run_local_server(
            success_message="Heyy, yippie, you're authenticated ! You can close this window now !",
            authorization_prompt_message="Please authorize this app to upload videos on your YouTube account !",
        )

        result = user_credentials.to_json()
        if isinstance(result, str):
            result = orjson.loads(result)
        return result

    def upload(self, title: str, description: str, path: str):
        options = {
            "file": path,
            "title": title + " | " + self.hashtags,
            "description": description,
            "privacyStatus": "private",
            "category": 28,
        }
        try:
            youtube_uploading.upload(self.oauth["credentials"], options)
        except Exception as e:
            # this means we need to re-authenticate likely
            # use self.__oauth to re-authenticate
            new_oauth = self.__oauth(self.credentials)
            # also update the credentials in the settings
            current_oauths = self.retrieve_setting(type="oauth_credentials") or {}
            current_oauths[self.oauth_name] = {
                "client_secret": self.oauth["client_secret"],
                "credentials": new_oauth,
            }
            self.store_setting(
                type="oauth_credentials",
                data=current_oauths,
            )
            self.oauth = current_oauths[self.oauth_name]
            youtube_uploading.upload(self.oauth["credentials"], options)

    @classmethod
    def get_options(cls):
        choices = cls.retrieve_setting(type="oauth_credentials") or {}
        choices = list(choices.keys())
        return [
            gr.Dropdown(
                choices=choices,
                label="Choose Channel",
                value=choices[0] if choices else "No channels available !",
            ),
            gr.Textbox(label="Hashtags", value="#shorts", max_lines=1),
        ]

    @classmethod
    def get_settings(cls):
        with gr.Row():
            with gr.Column() as ytb_secret:
                clien_secret_name = gr.Textbox(label="Name", max_lines=1)
                client_secret_file = gr.File(
                    label="Client Secret File", file_types=["json"], type="binary"
                )
                submit_button = gr.Button("Save")

                def save(binary, clien_secret_name):
                    current_client_secrets = (
                        cls.retrieve_setting(type="youtube_client_secrets") or {}
                    )
                    client_secret_json = orjson.loads(binary)
                    current_client_secrets[clien_secret_name] = client_secret_json
                    cls.store_setting(
                        type="youtube_client_secrets",
                        data=current_client_secrets,
                    )
                    gr.Info(f"{clien_secret_name} saved successfully !")

                submit_button.click(
                    save, inputs=[client_secret_file, clien_secret_name]
                )

            with gr.Column() as ytb_oauth:
                possible_client_secrets = (
                    cls.retrieve_setting(type="youtube_client_secrets") or {}
                )
                possible_client_secrets = list(possible_client_secrets.keys())
                choosen_client_secret = gr.Dropdown(
                    label="Login secret", choices=possible_client_secrets
                )
                name = gr.Textbox(label="Name", max_lines=1)
                login_button = gr.Button("Login", variant="primary")

                def login(choosen_client_secret, name):
                    choosen_secret_data = cls.retrieve_setting(
                        type="youtube_client_secrets"
                    )[choosen_client_secret]
                    new_oauth_entry = cls.__oauth(choosen_secret_data)
                    current_oauths = (
                        cls.retrieve_setting(type="oauth_credentials") or {}
                    )
                    current_oauths[name] = {
                        "client_secret": choosen_client_secret,
                        "credentials": new_oauth_entry,
                    }
                    cls.store_setting(
                        type="oauth_credentials",
                        data=current_oauths,
                    )
                    gr.Info(f"{name} saved successfully !")

                login_button.click(login, inputs=[choosen_client_secret, name])
