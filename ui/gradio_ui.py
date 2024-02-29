import os

import gradio as gr
import orjson

from src.engines import ENGINES, BaseEngine
from src.chore import GenerationContext


class GenerateUI:
    def __init__(self):
        self.css = """.generate_button {
                font-size: 5rem !important
            }
        """

    def get_presets(self):
        with open("local/presets.json", "r") as f:
            return orjson.loads(f.read())

    def get_switcher_func(self, engine_names: list[str]) -> callable:
        def switch(selected: str | list[str]) -> list[gr.update]:
            if isinstance(selected, str):
                selected = [selected]
            returnable = []
            for i, name in enumerate(engine_names):
                returnable.append(gr.update(visible=name in selected))

            return returnable

        return switch

    def get_load_preset_func(self):
        def load_preset(preset_name, *selected_inputs) -> list[gr.update]:
            with open("local/presets.json", "r") as f:
                current_presets = orjson.loads(f.read())
            returnable = []
            if preset_name in current_presets.keys():
                # If the preset exists
                preset = current_presets[preset_name]
                for engine_type, engines in ENGINES.items():
                    engines_classes = engines["classes"]
                    values = [[]]
                    for engine in engines_classes:
                        if engine.name in preset.get(engine_type, {}).keys():
                            values[0].append(engine.name)
                            values.extend(
                                gr.update(value=value) for value in preset[engine_type][engine.name])
                        else:
                            values.extend(gr.update() for _ in range(engine.num_options))
                    if not engines["multiple"]:
                        if len(values[0]) > 0:
                            values[0] = values[0][0]
                        else:
                            values[0] = None
                    else:
                        ...
                    returnable.extend(values)
            else:
                raise gr.Error(f"Preset {preset_name} does not exist.")
            gr.Info(f"Preset {preset_name} loaded successfully.")
            return [gr.Dropdown(choices=list(current_presets.keys()), value=preset_name), *returnable]
        return load_preset

    def get_save_preset_func(self):
        def save_preset(preset_name, *selected_inputs) -> list[gr.update]:
            with open("local/presets.json", "rb") as f:
                current_presets = orjson.loads(f.read())
            returnable = []
            poppable_inputs = list(selected_inputs)
            new_preset = {}
            for engine_type, engines in ENGINES.items():
                engines = engines["classes"]
                new_preset[engine_type] = {}
                engine_names = poppable_inputs.pop(0)
                if isinstance(engine_names, str):
                    engine_names = [engine_names]
                returnable.append(gr.update())
                for engine in engines:
                    if engine.name in engine_names:
                        new_preset[engine_type][engine.name] = poppable_inputs[:engine.num_options]
                        poppable_inputs = poppable_inputs[engine.num_options:]
                    else:
                        poppable_inputs = poppable_inputs[engine.num_options:]
                    returnable.extend(gr.update() for _ in range(engine.num_options))
            with open("local/presets.json", "wb") as f:
                current_presets[preset_name] = new_preset
                f.write(orjson.dumps(current_presets))
            gr.Info(f"Preset {preset_name} saved successfully.")
            return [gr.Dropdown(choices=list(current_presets.keys()), value=preset_name), *returnable]
        return save_preset

    def get_delete_preset_func(self):
        def delete_preset(preset_name) -> list[gr.update]:
            with open("local/presets.json", "r") as f:
                current_presets = orjson.loads(f.read())
            if not current_presets.get(preset_name):
                raise ValueError("You cannot delete a non-existing preset.")
            current_presets.pop(preset_name)
            with open("local/presets.json", "wb") as f:
                f.write(orjson.dumps(current_presets))
            return gr.Dropdown(choices=list(current_presets.keys()), value=None)
        return delete_preset
    def get_ui(self):
        ui = gr.TabbedInterface(
            *self.get_interfaces(), title="Viral Factory", theme=gr.themes.Soft(), css=self.css
        )
        return ui

    def launch_ui(self):
        ui = self.get_ui()
        ui.launch()

    def get_interfaces(self) -> tuple[list[gr.Blocks], list[str]]:
        """
        Returns a tuple containing a list of gr.Blocks interfaces and a list of interface names.

        Returns:
            tuple[list[gr.Blocks], list[str]]: A tuple containing a list of gr.Blocks interfaces and a list of interface names.
        """
        return (
            [self.get_generate_interface(), self.get_settings_interface()],
            ["Generate", "Settings"],
        )

    def get_settings_interface(self) -> gr.Blocks:
        with gr.Blocks() as interface:
            reload_ui = gr.Button("Reload UI", variant="primary")

            def reload():
                gr.Warning("Please restart the server to apply changes.")

            reload_ui.click(reload)
            for engine_type, engines in ENGINES.items():
                engines = engines["classes"]
                with gr.Tab(engine_type) as engine_tab:
                    for engine in engines:
                        gr.Markdown(f"## {engine.name}")
                        engine.get_settings()
        return interface

    def get_generate_interface(self) -> gr.Blocks:
        with gr.Blocks() as interface:
            with gr.Row(equal_height=False) as row:
                inputs = []
                with gr.Column(scale=2) as col1:
                    for engine_type, engines in ENGINES.items():
                        multiselect = engines["multiple"]
                        show_dropdown = engines.get("show_dropdown", True)
                        engines = engines["classes"]
                        with gr.Tab(engine_type) as engine_tab:
                            engine_names = [engine.name for engine in engines]
                            engine_dropdown = gr.Dropdown(
                                choices=engine_names,
                                value=engine_names[0],
                                multiselect=multiselect,
                                label="Engine provider:"
                                if not multiselect
                                else "Engine providers:",
                                visible=show_dropdown,
                            )
                            inputs.append(engine_dropdown)
                            engine_rows = []
                            for i, engine in enumerate(engines):
                                with gr.Column(visible=(i == 0)) as engine_row:
                                    gr.Markdown(value=f"## {engine.name}")
                                    engine_rows.append(engine_row)
                                    options = engine.get_options()
                                    inputs.extend(options)
                            switcher = self.get_switcher_func(engine_names)
                            engine_dropdown.change(
                                switcher, inputs=engine_dropdown, outputs=engine_rows
                            )

                with gr.Column() as col2:
                    button = gr.Button(
                        "🚀",
                        size="lg",
                        variant="primary",
                        elem_classes="generate_button",
                    )
                    gr.Markdown(value="## Presets")
                    presets = self.get_presets()
                    preset_dropdown = gr.Dropdown(
                        choices=list(presets.keys()),
                        show_label=False,
                        label="",
                        allow_custom_value=True,
                        value="",
                    )
                    load_preset_button = gr.Button("📂", size="sm", variant="primary")
                    save_preset_button = gr.Button("💾", size="sm", variant="secondary")
                    delete_preset_button = gr.Button("🗑️", size="sm", variant="stop")

                    load_preset = self.get_load_preset_func()
                    save_preset = self.get_save_preset_func()
                    delete_preset = self.get_delete_preset_func()
                    load_preset_button.click(load_preset, inputs=[preset_dropdown, *inputs],
                                        outputs=[preset_dropdown, *inputs])
                    save_preset_button.click(save_preset, inputs=[preset_dropdown, *inputs],
                                        outputs=[preset_dropdown, *inputs])
                    delete_preset_button.click(delete_preset, inputs=preset_dropdown,
                                        outputs=preset_dropdown)
                    output_title = gr.Markdown(visible=True, render=False)
                    output_description = gr.Markdown(visible=True, render=False)
                    output_video = gr.Video(visible=True, render=False)
                    output_path = gr.State(value=None)
                    button.click(
                        self.run_generate_interface,
                        inputs=inputs,
                        outputs=[output_video, output_title, output_description, output_path],
                    )
            with gr.Row():
                with gr.Column():
                    output_title.render()
                    output_description.render()
                with gr.Column():
                    output_video.render()

        return interface

    def run_generate_interface(self, progress=gr.Progress(track_tqdm=True), *args) -> list[gr.update]:
        progress(0, desc="Loading engines... 🚀")
        options = self.repack_options(*args)
        arguments = {name.lower(): options[name] for name in ENGINES.keys()}
        ctx = GenerationContext(**arguments, progress=progress)
        ctx.process()  # Here we go ! 🚀
        return [gr.update(value=ctx.get_file_path("final.mp4"), visible=True), gr.update(value=ctx.title, visible=True), gr.update(value=ctx.description, visible=True), gr.update(value=ctx.dir)]

    def repack_options(self, *args) -> dict[str, list[BaseEngine]]:
        """
        Repacks the options provided as arguments into a dictionary based on the selected engine.

        Args:
            *args: Variable number of arguments representing the options for each engine.

        Returns:
            dict: A dictionary containing the repacked options, where the keys are the engine types and the values are the corresponding engine options.
        """
        options = {}
        args = list(args)
        for engine_type, engines in ENGINES.items():
            engines = engines["classes"]
            selected_engines = args.pop(0)
            if isinstance(selected_engines, str):
                selected_engines = [selected_engines]
            options[engine_type] = []
            # for every selected engine
            for engine in engines:
                # if it correspods to the selected engine
                if engine.name in selected_engines:
                    # we add it to the options
                    options[engine_type].append(
                        engine(options=args[: engine.num_options])
                    )
                    args = args[engine.num_options:]
                else:
                    # we don't care about this, it's not the selected engine, we throw it away
                    args = args[engine.num_options:]
        return options


def launch():
    ui_generator = GenerateUI()
    ui_generator.launch_ui()
