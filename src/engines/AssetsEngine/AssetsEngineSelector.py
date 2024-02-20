import json

from ...utils.prompting import get_prompt
from ...chore import GenerationContext


class AssetsEngineSelector:
    def __init__(self):
        self.ctx: GenerationContext

    def get_assets(self):
        system_prompt, chat_prompt = get_prompt("assets", by_file_location=__file__)
        engines_descriptors = ""

        for engine in self.ctx.assetsengine:
            engines_descriptors += (
                f"name: '{engine.name}'\n{json.dumps(engine.specification)}\n"
            )

        system_prompt = system_prompt.replace("{engines}", engines_descriptors)
        chat_prompt = chat_prompt.replace(
            "{caption}", json.dumps(self.ctx.timed_script)
        )

        assets = self.ctx.powerfulllmengine.generate(
            system_prompt=system_prompt,
            chat_prompt=chat_prompt,
            max_tokens=4096,
            json_mode=True,
        )["assets"]
        clips: list = []
        for engine in self.ctx.assetsengine:
            assets_opts = [asset for asset in assets if asset["engine"] == engine.name]
            assets_opts = [asset["args"] for asset in assets_opts]
            clips.extend(engine.get_assets(assets_opts))
        return clips
