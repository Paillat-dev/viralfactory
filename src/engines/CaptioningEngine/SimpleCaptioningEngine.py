import gradio as gr
from PIL import ImageFont
from moviepy.editor import TextClip

from . import BaseCaptioningEngine


class SimpleCaptioningEngine(BaseCaptioningEngine):
    name = "SimpleCaptioningEngine"
    description = "A basic captioning engine with nothing too fancy."
    num_options = 5

    def __init__(self, options: list[list | tuple | str | int | float | bool | None]):
        self.font = options[0]
        self.font_size = options[1]
        self.stroke_width = options[2]
        self.font_color = options[3]
        self.stroke_color = options[4]

        super().__init__()

    def build_caption_object(self, text: str, start: float, end: float) -> TextClip:
        return (
            TextClip(
                text,
                fontsize=self.font_size,
                color=self.font_color,
                font=self.font,
                stroke_color=self.stroke_color,
                stroke_width=self.stroke_width,
                method="caption",
                size=(self.ctx.width / 3 * 2, None),
            )
            .set_position(("center", 0.65), relative=True)
            .set_start(start)
            .set_duration(end - start)
        )

    def ends_with_punctuation(self, text: str) -> bool:
        punctuations = (".", "?", "!", ",", ":", ";")
        return text.strip().endswith(tuple(punctuations))

    def get_captions(self):
        # 3 words per 1000 px, we do the math
        max_words = int(self.ctx.width / 1000 * 3)

        clips = []
        words = (
            self.ctx.timed_script.copy()
        )  # List of dicts with "start", "end", and "text"
        current_line = ""
        current_start = words[0]["start"]
        current_end = words[0]["end"]
        for i, word in enumerate(words):
            # Use PIL to measure the text size
            line_with_new_word = (
                current_line + " " + word["text"] if current_line else word["text"]
            )
            pause = self.ends_with_punctuation(current_line.strip())

            if len(line_with_new_word.split(" ")) > max_words or pause:
                clips.append(
                    self.build_caption_object(
                        current_line.strip(), current_start, current_end
                    )
                )
                current_line = word["text"]  # Start a new line with the current word
                current_start = word["start"]
                current_end = word["end"]
            else:
                # If the line isn't too long, add the word to the current line
                current_line = line_with_new_word
                current_end = word["end"]
        # Don't forget to add the last line if it exists
        if current_line:
            clips.append(
                self.build_caption_object(
                    current_line.strip(), current_start, words[-1]["end"]
                )
            )

        self.ctx.index_7.extend(clips)

    @classmethod
    def get_options(cls) -> list:
        with gr.Column() as font_options:
            with gr.Group():
                font = gr.Dropdown(
                    label="Font",
                    choices=TextClip.list("font"),
                    value="Comic-Sans-MS",
                )
                font_size = gr.Number(
                    label="Font Size",
                    minimum=70,
                    maximum=200,
                    step=1,
                    value=110,
                )
                font_color = gr.ColorPicker(label="Font Color", value="#ffffff")
        with gr.Column() as font_stroke_options:
            with gr.Group():
                font_stroke_width = gr.Number(
                    label="Stroke Width",
                    minimum=0,
                    maximum=40,
                    step=1,
                    value=5,
                )
                font_stroke_color = gr.ColorPicker(
                    label="Stroke Color", value="#000000"
                )
        return [font, font_size, font_stroke_width, font_color, font_stroke_color]
