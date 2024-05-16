import os

import gradio as gr
import moviepy as mp

from . import BasePipeline
from ... import engines
from ...chore import GenerationContext
from ...utils.prompting import get_prompt, get_prompts


class ScriptedVideoPipeline(BasePipeline):
    name = "Scripted Long Form Pipeline"
    description = (
        "A pipeline that generates a long form video based on a script instruction."
    )
    num_options = 5

    def __init__(self, options: list) -> None:
        self.user_instructions = options[0]
        self.assets_instructions = options[1]
        # ratio = options[2] we don't need this
        self.width = options[3]
        self.height = options[4]
        super().__init__()

    def launch(self, ctx: GenerationContext) -> None:

        ctx.progress(0.1, "Loading settings...")
        ctx.setup_dir()
        ctx.width = self.width
        ctx.height = self.height

        prompts = get_prompts("long_form", by_file_location=__file__)
        ctx.progress(0.2, "Generating chapters...")
        system = prompts["chapters"]["system"]
        chat = prompts["chapters"]["chat"]
        chat = chat.replace("{user_instructions}", str(self.user_instructions))
        chapters: list[dict[str, str]] = ctx.powerfulllmengine.generate(
            system_prompt=system,
            chat_prompt=chat,
            json_mode=True,
            temperature=1,
            max_tokens=4096,
        )["chapters"]
        ctx.script = ""

        text_audio = []

        ctx.duration = 0

        for i, chapter in enumerate(chapters):
            ctx.progress(0.2, f"Generating chapter: {chapter['title']}...")
            system = prompts["writer"]["system"]
            chat = prompts["writer"]["chat"]
            chat = (
                chat.replace("{user_instructions}", str(self.user_instructions))
                .replace("{chapter_title}", chapter["title"])
                .replace("{chapter_instructions}", chapter["explanation"])
            )
            script = ctx.powerfulllmengine.generate(
                system_prompt=system,
                chat_prompt=chat,
                temperature=1,
                max_tokens=4096,
                json_mode=True,
            )["chapter"]
            ctx.script += script
            ctx.script += "\n"

            ctx.progress(0.3, "Synthesizing voice...")
            duration = ctx.ttsengine.synthesize(
                script, ctx.get_file_path(f"tts_{i}.wav")
            )
            audioclip = mp.AudioFileClip(ctx.get_file_path(f"tts_{i}.wav"))
            audioclip = audioclip.with_start(ctx.duration)
            text_audio.append(audioclip)
            ctx.progress(0.2, f"Transcribing chapter: {chapter['title']}...")
            timed_script = ctx.transcriptionengine.transcribe(
                ctx.get_file_path(f"tts_{i}.wav"), fast=False, words=True
            )

            sentence_split_script = []
            current_sentence = None

            for word in timed_script.copy():
                if current_sentence is None:
                    # Initialize the first sentence
                    current_sentence = {
                        "text": word["text"],
                        "end": word["end"],
                        "start": word["start"],
                    }
                elif word["text"].endswith((".", "!", "?")):
                    # Add the word to the current sentence and finalize it
                    current_sentence["text"] += f" {word['text']}"
                    current_sentence["end"] = word["end"]
                    sentence_split_script.append(current_sentence)
                    current_sentence = None  # Prepare to start a new sentence
                else:
                    # Continue adding words to the current sentence
                    current_sentence["text"] += f" {word['text']}"
                    current_sentence["end"] = word["end"]

            # If the last sentence didn't end with a punctuation mark
            if current_sentence is not None:
                sentence_split_script.append(current_sentence)

            ctx.progress(0.2, f"Generating video for chapter: {chapter['title']}...")
            system = prompts["imager"]["system"]
            chat = prompts["imager"]["chat"]
            chat = chat.replace("{user_instructions}", str(self.user_instructions))
            chat = chat.replace("{assets_instructions}", str(self.assets_instructions))
            chat = chat.replace("{video_transcript}", str(sentence_split_script))
            assets: list[dict[str, str | float]] = ctx.powerfulllmengine.generate(
                system_prompt=system,
                chat_prompt=chat,
                temperature=1,
                max_tokens=4096,
                json_mode=True,
            )["assets"]
            for i, asset in enumerate(assets):
                if asset["type"] == "stock":
                    ctx.progress(0.5, f"Getting stock image {i + 1}...")
                    ctx.index_4.append(
                        ctx.stockimageengine.get(
                            asset["query"],
                            asset["start"] + ctx.duration,
                            asset["end"] + ctx.duration,
                        )
                    )
                elif asset["type"] == "ai":
                    ctx.progress(0.5, f"Generating AI image {i + 1}...")
                    ctx.index_5.append(
                        ctx.aiimageengine.generate(
                            asset["prompt"],
                            asset["start"] + ctx.duration,
                            asset["end"] + ctx.duration,
                        )
                    )

            ctx.duration += duration + 0.5
        ctx.audio.extend(text_audio)
        if not isinstance(ctx.audiobackgroundengine, engines.NoneEngine):
            ctx.progress(0.6, "Generating audio background...")
            ctx.audio.append(ctx.audiobackgroundengine.get_background())

        if not isinstance(ctx.backgroundengine, engines.NoneEngine):
            ctx.progress(0.65, "Generating background...")
            ctx.index_0.append(ctx.backgroundengine.get_background())

        ctx.progress(0.7, "Rendering video...")
        clips = [
            *ctx.index_0,
            *ctx.index_1,
            *ctx.index_2,
            *ctx.index_3,
            *ctx.index_4,
            *ctx.index_5,
            *ctx.index_6,
            *ctx.index_7,
            *ctx.index_8,
            *ctx.index_9,
        ]
        audio = mp.CompositeAudioClip(ctx.audio)
        clip = (
            mp.CompositeVideoClip(clips, size=(ctx.width, ctx.height))
            .with_duration(ctx.duration)
            .with_audio(audio)
        )
        clip.write_videofile(
            ctx.get_file_path("final.mp4"), fps=60, threads=4, codec="h264_nvenc"
        )
        system = prompts["description"]["system"]
        chat = prompts["description"]["chat"]
        chat.replace("{script}", ctx.script)
        metadata = ctx.powerfulllmengine.generate(
            system_prompt=system, chat_prompt=chat, json_mode=True, temperature=1
        )
        ctx.title = metadata["title"]
        ctx.description = metadata["description"]

        ctx.description = ctx.description + "\n" + ctx.credits
        ctx.progress(0.9, "Uploading video...")
        for engine in ctx.uploadengine:
            try:
                engine.upload(
                    ctx.title, ctx.description, ctx.get_file_path("final.mp4")
                )
            except Exception as e:
                print(e)
                gr.Warning(f"{engine.name} failed to upload the video.")

        ctx.progress(0.99, "Storing in database...")
        ctx.store_in_db()
        ctx.progress(1, "Done!")

        command = "start" if os.name == "nt" else "open"
        os.system(f"{command} {os.path.abspath(ctx.dir)}")

    @classmethod
    def get_options(cls):
        def change_resolution(chosen_ratio: str) -> list[gr.update]:
            match chosen_ratio:
                case "1920x1080":
                    return [
                        gr.update(value=1920, visible=False),
                        gr.update(value=1080, visible=False),
                    ]
                case "1080x1920":
                    return [
                        gr.update(value=1080, visible=False),
                        gr.update(value=1920, visible=False),
                    ]
                case "1280x720":
                    return [
                        gr.update(value=1280, visible=False),
                        gr.update(value=720, visible=False),
                    ]
                case "720x1280":
                    return [
                        gr.update(value=720, visible=False),
                        gr.update(value=1280, visible=False),
                    ]
                case "custom":
                    return [gr.update(visible=True), gr.update(visible=True)]

        with gr.Row():
            ratio = gr.Dropdown(
                choices=["1920x1080", "1080x1920", "1280x720", "720x1280", "custom"],
                label="Resolution",
            )
            width = gr.Number(
                value=1080, minimum=720, maximum=3840, label="Width", step=1
            )
            height = gr.Number(
                value=1920, minimum=720, maximum=3840, label="Height", step=1
            )
            ratio.change(change_resolution, inputs=[ratio], outputs=[width, height])

        return [
            gr.Textbox(
                lines=4,
                max_lines=6,
                label="Video instructions",
                info="Explain what the video should be about, how many chapters, and any specific instructions.",
            ),
            gr.Textbox(
                lines=4,
                max_lines=6,
                label="Assets only instructions",
                info="Explain how the assets should be used in the video. When, how many, and of what type (stock images, AI or both)",
            ),
            ratio,
            width,
            height,
        ]
