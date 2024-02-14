import os
import gradio as gr
from src.engines import ENGINES


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
            *self.get_interfaces(),
            "Viral Automator",
            "NoCrypt/miku",
            css=self.css
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
            with gr.Row() as row:
                inputs = []
                with gr.Blocks() as col1:
                    for engine_type, engines in ENGINES.items():
                        with gr.Tab(engine_type) as engine_tab:
                            engine_names = [engine.name for engine in engines]
                            engine_dropdown = gr.Dropdown(
                                choices=engine_names, value=engine_names[0]
                            )
                            inputs.append(engine_dropdown)
                            engine_rows = []
                            for i, engine in enumerate(engines):
                                with gr.Row(visible=(i == 0)) as engine_row:
                                    engine_rows.append(engine_row)
                                    options = engine.get_options()
                                    inputs.extend(options)
                            switcher = self.get_switcher_func(engine_names)
                            engine_dropdown.change(
                                switcher, inputs=engine_dropdown, outputs=engine_rows
                            )

                with gr.Blocks() as col2:
                    button = gr.Button("🚀", size="lg", variant="primary", elem_classes="generate_button")
                    button.click(self.repack_options, inputs=inputs)
        return interface

    def repack_options(self, *args):
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
            engine_name = args.pop(0)
            for engine in engines:
                if engine.name == engine_name:
                    options[engine_type] = engine(options=args[: engine.num_options])
                    args = args[engine.num_options :]
                else:
                    # we don't care about this, it's not the selected engine, we throw it away
                    args = args[engine.num_options :]
        print(options)


if __name__ == "__main__":
    ui_generator = GenerateUI()
    ui_generator.launch_ui()
