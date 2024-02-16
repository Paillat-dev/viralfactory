import os
import gradio as gr

from src.engines import ENGINES, BaseEngine
from src.chore import GenerationContext


class GenerateUI:
    def __init__(self):
        self.css = """.generate_button {
                font-size: 5rem !important
            }
        """

    def get_switcher_func(self, engine_names: list[str]) -> list[gr.update]:
        def switch(selected: str):
            returnable = []
            for i, name in enumerate(engine_names):
                returnable.append(gr.update(visible=name == selected))

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
        return ([self.get_generate_interface()], ["Generate"])

    def get_generate_interface(self) -> gr.Blocks:
        with gr.Blocks() as interface:
            with gr.Row(equal_height=False) as row:
                inputs = []
                with gr.Blocks() as col1:
                    for engine_type, engines in ENGINES.items():
                        multiselect = engines["multiple"]
                        engines = engines["classes"]
                        with gr.Tab(engine_type) as engine_tab:
                            engine_names = [engine.name for engine in engines]
                            engine_dropdown = gr.Dropdown(
                                choices=engine_names,
                                value=engine_names[0],
                                multiselect=multiselect,
                                label="Engine provider:"
                            )
                            inputs.append(engine_dropdown)
                            engine_rows = []
                            for i, engine in enumerate(engines):
                                with gr.Row(
                                    equal_height=True, visible=(i == 0)
                                ) as engine_row:
                                    engine_rows.append(engine_row)
                                    options = engine.get_options()
                                    inputs.extend(options)
                            switcher = self.get_switcher_func(engine_names)
                            engine_dropdown.change(
                                switcher, inputs=engine_dropdown, outputs=engine_rows
                            )

                with gr.Blocks() as col2:
                    button = gr.Button(
                        "🚀",
                        scale=0.33,
                        size="lg",
                        variant="primary",
                        elem_classes="generate_button",
                    )
                    button.click(self.run_generate_interface, inputs=inputs)
        return interface

    def run_generate_interface(self, *args) -> None:
        options = self.repack_options(*args)
        arugments = {name.lower(): options[name] for name in ENGINES.keys()}
        ctx = GenerationContext(**arugments)
        ctx.process()  # Here we go ! 🚀

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
