import importlib
import json
import os
import gradio as gr
from src import engines

class GenerateUI:
    def __init__(self):
        self.engines = self.get_engines()

    def get_engines(self):
        engines_d = {}
        with open(os.path.join(os.getcwd(), "src", "engines", "engines.json"), "r") as f:
            engine_types = json.load(f)
        for engine_type, engine_list in engine_types.items():
            engines_d[engine_type] = {}
            for engine_name in engine_list:
                module = importlib.import_module(f"src.engines.{engine_type}.{engine_name}")
                engine_class = getattr(module, engine_name)
                engines_d[engine_type][engine_name] = engine_class
        return engines_d

    def launch_ui(self):
        with gr.Blocks() as main_block:
            for engine_type, engines in self.engines.items():
                switch_dropdown = gr.Dropdown(list(engines.keys()), label=engine_type)
                engine_blocks = []

                for engine_name, engine_class in engines.items():
                    with gr.Blocks(elem_id=f"{engine_type}_{engine_name}_block", visible=False) as engine_block:
                        options = engine_class().get_options()
                        for option in options:
                            engine_block.add(option)
                        engine_blocks.append(engine_block)

                def switch_engine(engine_name, engine_blocks=engine_blocks, switch_dropdown=switch_dropdown):
                    for block in engine_blocks:
                        block.visible = block.elem_id.startswith(f"{engine_type}_{engine_name}")

                switch_dropdown.change(switch_engine, inputs=[switch_dropdown], outputs=engine_blocks)

                # Initially show the first engine's options
                if engines:
                    first_engine_name = list(engines.keys())[0]
                    switch_engine(first_engine_name)

        main_block.launch()

if __name__ == "__main__":
    ui_generator = GenerateUI()
    ui_generator.launch_ui()
