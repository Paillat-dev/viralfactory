import anthropic
import gradio as gr

from .BaseLLMEngine import BaseLLMEngine

# Assuming these are the models supported by Anthropics that you wish to include
ANTHROPIC_POSSIBLE_MODELS = [
    "claude-2.1",
    # Add more models as needed
]

class AnthropicsLLMEngine(BaseLLMEngine):
    num_options = 1
    name = "Anthropics"
    description = "Anthropics language model engine."

    def __init__(self, options: list) -> None:
        self.model = options[0]
        self.client = anthropic.Anthropic(api_key="YourAnthropicAPIKeyHere")  # Ensure API key is securely managed
        super().__init__()

    def generate(self, system_prompt: str, chat_prompt: str, max_tokens: int = 1024, temperature: float = 1.0, json_mode: bool = False, top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0) -> str | dict:
        # Note: Adjust the parameters as per Anthropics API capabilities
        message = self.client.messages.create(
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chat_prompt},
            ],
            model=self.model,
        )
        return message.content

    @classmethod
    def get_options(cls) -> list:
        return [
            gr.Dropdown(
                label="Model",
                choices=ANTHROPIC_POSSIBLE_MODELS,
                max_choices=1,
                value=ANTHROPIC_POSSIBLE_MODELS[0]
            )
        ]
