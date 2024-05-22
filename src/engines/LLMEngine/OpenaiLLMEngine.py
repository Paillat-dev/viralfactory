import gradio as gr
import openai
import logging
from openai import OpenAI
import orjson

from .BaseLLMEngine import BaseLLMEngine

OPENAI_POSSIBLE_MODELS = [  # Theese shall be the openai models supporting force_json
    "gpt-3.5-turbo-0125",
    "gpt-4-turbo",
    "gpt-4o"
]


class OpenaiLLMEngine(BaseLLMEngine):
    num_options = 1
    name = "OpenAI"
    description = "OpenAI language model engine."

    def __init__(self, options: list) -> None:
        self.model = options[0]
        api_key = self.retrieve_setting(identifier="openai_api_key")
        if not api_key:
            raise ValueError("OpenAI API key is not set.")
        self.client = OpenAI(api_key=api_key["api_key"])
        super().__init__()

    def generate(
        self,
        system_prompt: str,
        chat_prompt: str = "",
        messages: list = [],
        max_tokens: int = 512,
        temperature: float = 1.0,
        json_mode: bool = False,
        top_p: float = 1,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
    ) -> str | dict:
        logging.info(
            f"Generating with OpenAI model {self.model} and system prompt: \n{system_prompt} and chat prompt: \n{chat_prompt[0:100]}..."
        )
        if chat_prompt:
            messages = [
                {"role": "user", "content": chat_prompt},
                *messages,
            ]
        for i, message in enumerate(messages):
            if type(message["content"]) is list:
                for i, content in enumerate(message["content"]):
                    if content["type"] == "image":
                        message["content"][i] = {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{content['source']['media_type']};base64,{content['source']['data']}",
                            },
                        }
                messages[i] = message

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                *messages,
            ],
            max_tokens=int(max_tokens) if max_tokens else openai.NOT_GIVEN,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            response_format=(
                {"type": "json_object"} if json_mode else openai.NOT_GIVEN
            ),
        )
        return (
            response.choices[0].message.content
            if not json_mode
            else orjson.loads(response.choices[0].message.content)
        )

    @classmethod
    def get_options(cls) -> list:
        return [
            gr.Dropdown(
                label="Model",
                choices=OPENAI_POSSIBLE_MODELS,
                value=OPENAI_POSSIBLE_MODELS[0],
            )
        ]

    @classmethod
    def get_settings(cls):
        current_api_key = cls.retrieve_setting(identifier="openai_api_key")
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

    @property
    def supports_vision(self) -> bool:
        return True if self.model in ["gpt-4-turbo-preview", "gpt-4-turbo", "gpt-4o"] else False
