import anthropic
import gradio as gr
import fix_busted_json
import orjson

from .BaseLLMEngine import BaseLLMEngine

ANTHROPIC_POSSIBLE_MODELS = [
    "claude-2.1",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
]


class AnthropicLLMEngine(BaseLLMEngine):
    num_options = 1
    name = "Anthropic"
    description = "Anthropic language model engine."

    def __init__(self, options: list) -> None:
        self.model = options[0]
        api_key = self.retrieve_setting(identifier="anthropic_api_key")["api_key"]
        self.client = anthropic.Anthropic(api_key=api_key)
        super().__init__()

    def generate(
        self,
        system_prompt: str,
        chat_prompt: str = "",
        messages: list = [],
        max_tokens: int = 1024,
        temperature: float = 1.0,
        json_mode: bool = False,
        top_p: float = 1,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
    ) -> str | dict:
        tries = 0
        while tries < 2:
            if chat_prompt:
                messages = [
                    {"role": "user", "content": chat_prompt},
                    *messages,
                ]
            if json_mode:
                # anthropic does not officially support JSON mode, but we can bias the output towards a JSON-like format
                messages.append({"role": "assistant", "content": "{"})
            response: anthropic.types.Message = self.client.messages.create(
                max_tokens=max_tokens,
                messages=messages,
                model=self.model,
                top_p=top_p,
                temperature=temperature if temperature <= 1.0 else 1.0,
                system=system_prompt,
            )

            content = response.content[0].text
            if json_mode:
                content = "{" + content
                # we remove everything after the last closing curly brace
                content = content[: content.rfind("}") + 1]
                content = content.replace("\n", "")
                try:
                    returnable = fix_busted_json.repair_json(content)
                    returnable = orjson.loads(returnable)
                    return returnable
                except fix_busted_json.JsonFixError as e:
                    tries += 1
            else:
                return content

    @classmethod
    def get_options(cls) -> list:
        return [
            gr.Dropdown(
                label="Model",
                choices=ANTHROPIC_POSSIBLE_MODELS,
                value=ANTHROPIC_POSSIBLE_MODELS[0],
            )
        ]

    @classmethod
    def get_settings(cls):
        current_api_key = cls.retrieve_setting(identifier="anthropic_api_key")
        current_api_key = current_api_key["api_key"] if current_api_key else ""
        api_key_input = gr.Textbox(
            label="Anthropic API Key",
            type="password",
            value=current_api_key,
        )
        save = gr.Button("Save")

        def save_api_key(api_key: str):
            cls.store_setting(identifier="anthropic_api_key", data={"api_key": api_key})
            gr.Info("API key saved successfully.")
            return gr.update(value=api_key)

        save.click(save_api_key, inputs=[api_key_input])

    @property
    def supports_vision(self) -> bool:
        return (
            True
            if self.model in ["claude-3-opus-20240229", "claude-3-sonnet-20240229"]
            else False
        )
