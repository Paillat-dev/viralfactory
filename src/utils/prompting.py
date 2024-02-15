import yaml
import os
from typing import TypedDict


class Prompt(TypedDict):
    system: str
    chat: str


def get_prompt(name, *, location="src/chore/prompts") -> tuple[str, str]:
    path = os.path.join(os.getcwd(), location, f"{name}.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file {path} does not exist.")
    with open(path, "r") as file:
        prompt: Prompt = yaml.safe_load(file)
    return prompt["system"], prompt["chat"]