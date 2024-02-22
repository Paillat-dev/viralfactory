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

    def get_switcher_func(self, engine_names: list[str]) -> list[gr.update]:
        def switch(selected: str | list[str]):
            if isinstance(selected, str):
                selected = [selected]
            returnable = []
            for i, name in enumerate(engine_names):
                returnable.append(gr.update(visible=name in selected))

            return returnable

        return switch

    def launch_ui(self):
        ui = gr.TabbedInterface(
            *self.get_interfaces(), "Viral Factory", gr.themes.Soft(), css=self.css
        )
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
                    with gr.Row() as preset_row:
                        presets = self.get_presets()
                        preset_dropdown = gr.Dropdown(
                            choices=list(presets.keys()),
                            label="Presets",
                            allow_custom_value=True,
                            value=None
                        )
                        preset_button = gr.Button("Load")
                        def load_preset(preset_name, *inputs) -> list[gr.update]:
                            with open("local/presets.json", "r") as f:
                                presets = orjson.loads(f.read())
                            returnable = []
                            if preset_name in presets.keys():
                            # If the preset exists
                                preset = presets[preset_name]
                                for engine_type, engines in ENGINES.items():
                                    engines = engines["classes"]
                                    values = [[]]
                                    for engine in engines:
                                        if engine.name in preset.get(engine_type, {}).keys():
                                            values[0].append(engine.name)
                                            values.extend(gr.update(value=value) for value in preset[engine_type][engine.name])
                                        else:
                                            values.extend(gr.update() for _ in range(engine.num_options))
                                    returnable.extend(values)
                            else:
                                poppable_inputs = list(inputs)
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
                                    presets[preset_name] = new_preset
                                    f.write(orjson.dumps(presets))
                            return returnable
                    preset_button.click(load_preset, inputs=[preset_dropdown, *inputs], outputs=inputs)
                    output_gallery = gr.Markdown("aaa", render=False)
                    button.click(
                        self.run_generate_interface,
                        inputs=inputs,
                        outputs=output_gallery,
                    )
            output_gallery.render()
        return interface

    def run_generate_interface(self, progress=gr.Progress(), *args) -> gr.update:
        progress(0, desc="Loading engines... 🚀")
        options = self.repack_options(*args)
        arugments = {name.lower(): options[name] for name in ENGINES.keys()}
        ctx = GenerationContext(**arugments, progress=progress)
        ctx.process()  # Here we go ! 🚀
        return gr.update(value=ctx.get_file_path("final.mp4"))

    def repack_options(self, *args) -> dict[BaseEngine]:
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
                    args = args[engine.num_options :]
                else:
                    # we don't care about this, it's not the selected engine, we throw it away
                    args = args[engine.num_options :]
        return options


if __name__ == "__main__":
    ui_generator = GenerateUI()
    ui_generator.launch_ui()
