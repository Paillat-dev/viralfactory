import yaml
import os
from typing import TypedDict


class Prompt(TypedDict):
    system: str
    chat: str


def get_prompt(
    name, *, location: str = "src/chore/prompts", by_file_location: str = None
) -> tuple[str, str]:
    if by_file_location:
        path = os.path.join(
            os.path.dirname(os.path.abspath(by_file_location)),
            "prompts",
            f"{name}.yaml",
        )
    else:
        path = os.path.join(os.getcwd(), location, f"{name}.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file {path} does not exist.")
    with open(path, "r") as file:
        prompt: Prompt = yaml.safe_load(file)
    return prompt["system"], prompt["chat"]
