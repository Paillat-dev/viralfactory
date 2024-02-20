from . import BaseMetadataEngine

from ...utils.prompting import get_prompt

class ShortsMetadataEngine(BaseMetadataEngine):
    def __init__(self, **kwargs) -> None:
        ...

    def get_metadata(self):
        sytsem_prompt, chat_prompt = get_prompt("ShortsMetadata", by_file_location=__file__)
        chat_prompt = chat_prompt.replace("{script}", self.ctx.script)

        return self.ctx.simplellmengine.generate(chat_prompt=chat_prompt, system_prompt=sytsem_prompt, json_mode=True)

    def get_options(self):
        return []