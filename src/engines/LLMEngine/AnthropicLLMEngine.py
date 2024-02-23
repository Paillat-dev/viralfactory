import anthropic
import gradio as gr
import orjson

from .BaseLLMEngine import BaseLLMEngine

ANTHROPIC_POSSIBLE_MODELS = [
    "claude-2.1",
]


class AnthropicLLMEngine(BaseLLMEngine):
    num_options = 1
    name = "Anthropic"
    description = "Anthropic language model engine."

    def __init__(self, options: list) -> None:
        self.model = options[0]
        self.client = anthropic.Anthropic(
            api_key="YourAnthropicAPIKeyHere"
        )  # Ensure API key is securely managed
        super().__init__()

    def generate(
            self,
            system_prompt: str,
            chat_prompt: str,
            max_tokens: int = 1024,
            temperature: float = 1.0,
            json_mode: bool = False,
            top_p: float = 1,
            frequency_penalty: float = 0,
            presence_penalty: float = 0,
    ) -> str | dict:
        prompt = f"""{anthropic.HUMAN_PROMPT} {system_prompt} {anthropic.HUMAN_PROMPT} {chat_prompt} {anthropic.AI_PROMPT}"""
        if json_mode:
            # anthropic does not officially support JSON mode, but we can bias the output towards a JSON-like format
            prompt += " {"
        # noinspection PyArgumentList
        response: anthropic.types.Completion = self.client.completions.create(
            max_tokens_to_sample=max_tokens,
            prompt=prompt,
            model=self.model,
            top_p=top_p,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
        )

        content = response.completion
        if json_mode:
            # we add back the opening curly brace wich is not included in the response since it is in the prompt
            content = "{" + content
            # we remove everything after the last closing curly brace
            content = content[: content.rfind("}") + 1]
            return orjson.loads(content)
        else:
            return content

    @classmethod
    def get_options(cls) -> list:
        return [
            gr.Dropdown(
                label="Model",
                choices=ANTHROPIC_POSSIBLE_MODELS,
                max_choices=1,
                value=ANTHROPIC_POSSIBLE_MODELS[0],
            )
        ]
