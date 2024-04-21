import json
import os

import cv2
import gradio as gr
import moviepy as mp
import yt_dlp
import numpy as np

from . import BasePipeline
from ... import engines
from ...chore import GenerationContext
from ...utils.prompting import get_prompts


def track_and_center_face(
    input_video_path, output_video_path, output_resolution, progress=lambda x, y: None
):
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    temp_output_video_path = output_video_path.replace(".mp4", "_temp.mp4")

    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise IOError(f"Could not open video {input_video_path}")

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    output_fps = min(fps, 30)  # Limit to 30 FPS if necessary
    total_frames_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if fps > 30:
        frame_interval = int(np.round(fps / 30))
    else:
        frame_interval = 1
    positions: dict[int, tuple[int, int]] = {}
    frame_count = 0
    previous_center = None
    while True:
        progress(frame_count, total_frames_count)
        ret, frame = cap.read()
        if not ret:
            break

        # Adjusting frame rate to 30 FPS if necessary
        if (fps > 30) and (frame_count % frame_interval != 0):
            frame_count += 1
            continue
        frame_count += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        H, W = frame.shape[:2]

        if len(faces) > 0:
            x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])  # largest face
            center_x, center_y = (x + w // 2, y + h // 2)

            positions[frame_count] = (center_x, center_y)
            previous_center = (center_x, center_y)

            # Crop and center based on the face
            """
            startX = max(center_x - output_resolution[0] // 2, 0)
            startY = max(center_y - output_resolution[1] // 2, 0)
            startX = min(startX, W - output_resolution[0])
            startY = min(startY, H - output_resolution[1])

            output_frame = frame[
                startY : startY + output_resolution[1],
                startX : startX + output_resolution[0],
            ]
            output_frame = cv2.resize(output_frame, output_resolution)
            """
        else:
            if previous_center:
                positions[frame_count] = previous_center
                previous_center = positions[frame_count]
            else:
                positions[frame_count] = (0, 0)

    del previous_center
    cap.release()
    cv2.destroyAllWindows()
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_output_video_path, fourcc, output_fps, output_resolution)
    cap = cv2.VideoCapture(input_video_path)
    frame_count = 0
    movement_threshold = 2 * output_resolution[0] / 3
    while True:
        # if the image moved more than movement_threshold in 2d space, and the next two images did as well, then move to that image, else use the previous center
        ret, frame = cap.read()
        if not ret:
            break
        if positions.get(frame_count):
            if (
                positions.get(frame_count - 1)  # The previous frame exists
                and np.linalg.norm(  # The previous face is far enough from the current face
                    np.array(positions.get(frame_count))
                    - np.array(positions.get(frame_count - 1))
                )
                > movement_threshold
                and positions.get(frame_count + 1)  # The next frame exists
                and np.linalg.norm(  # The previous face is far enough from the current face
                    np.array(positions.get(frame_count - 1))
                    - np.array(positions.get(frame_count + 1))
                )
                > movement_threshold
            ):
                # the big movement is consistent between two frames, so we do move the camera (in this case, don't do anything)
                pass
            else:
                # did not move enough, so we use the previous center to allow for more consistent tracking
                positions[frame_count] = positions.get(
                    frame_count - 1, positions[frame_count]
                )
        else:
            positions[frame_count] = positions.get(
                frame_count + 1, positions.get(frame_count - 1)
            )
        if positions.get(frame_count):
            center_x, center_y = positions[frame_count]
            startX = max(center_x - output_resolution[0] // 2, 0)
            startY = max(center_y - output_resolution[1] // 2, 0)
            startX = min(startX, W - output_resolution[0])
            startY = min(startY, H - output_resolution[1])
            output_frame = frame[
                startY : startY + output_resolution[1],
                startX : startX + output_resolution[0],
            ]
            output_frame = cv2.resize(output_frame, output_resolution)
            out.write(output_frame)
        else:
            # we CROP!!! fo size output_resolution in the middle of the frame
            startX = (W - output_resolution[0]) // 2
            startY = (H - output_resolution[1]) // 2
            output_frame = frame[
                startY : startY + output_resolution[1],
                startX : startX + output_resolution[0],
            ]
            output_frame = cv2.resize(output_frame, output_resolution)
            out.write(output_frame)
        frame_count += 1
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # Process audio and finalize the video
    original_clip = mp.VideoFileClip(input_video_path)
    processed_video = mp.VideoFileClip(temp_output_video_path)
    processed_video = processed_video.with_audio(original_clip.audio)
    processed_video.write_videofile(output_video_path, codec="libx264")


class BestofShortPipeline(BasePipeline):
    name = "Bestof Short Pipeline"
    description = (
        "Creates a short video based on a best-of compilation of a given video."
    )
    num_options = 2

    def __init__(self, options: list) -> None:
        self.n_shorts = options[0]
        self.url = options[1]
        super().__init__()

    def launch(self, ctx: GenerationContext) -> None:

        ctx.progress(0.1, "Loading settings...")
        ctx.setup_dir()
        if not isinstance(ctx.settingsengine, engines.NoneEngine):
            ctx.settingsengine.load()
        prompts = get_prompts("bestof", by_file_location=__file__)

        ctx.progress(0.2, "Downloading video...")
        video_id = self.url.split("v=")[1]
        video_id = video_id.split("&")[0]
        self.url = f"https://www.youtube.com/watch?v={video_id}"
        input_video_path = f"local/assets/youtube/{video_id}.mp4"
        if not os.path.exists(input_video_path):
            os.makedirs("local/assets/youtube", exist_ok=True)
            ydl_opts = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "outtmpl": input_video_path,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
                info = ydl.extract_info(self.url, download=False)
                title = info["title"]
                heatmap = info["heatmap"]
                channel = info["channel"]
        else:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(self.url, download=False)
                title = info["title"]
                heatmap = info["heatmap"]
                channel = info["channel"]
        ctx.progress(0.3, "Transcribing video...")
        input_transcript_path = f"local/assets/youtube/{video_id}_transcript.json"
        if not os.path.exists(input_transcript_path):
            result = ctx.transcriptionengine.transcribe(
                input_video_path, fast=True, words=False, avoid_hallucinations=True
            )
            with open(input_transcript_path, "w") as f:
                json.dump(result, f)
        else:
            with open(input_transcript_path, "r") as f:
                result = json.load(f)
        timed_script = [
            {
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
            }
            for segment in result["segments"]
        ]
        ctx.progress(0.4, "Finding viral sections...")
        sections = [
            {
                "start": x["start_time"] - 30,
                "end": x["end_time"] + 30,
                "value": x["value"],
            }
            for x in heatmap
            if x["value"] > 0.35 and x["start_time"] > 30
        ]
        if len(sections) > self.n_shorts:
            sections = sections[: self.n_shorts]
        elif len(sections) < self.n_shorts:
            gr.Warning(
                "The number of viral sections found is less than the number of shorts requested. Less shorts will be generated."
            )

        for i, section in enumerate(sections):
            if i == 0:
                continue
            allocated_progress = 0.5 / len(sections)
            get_progress = lambda x, t: 0.5 + allocated_progress * (x / t)

            ctx.progress(
                get_progress(1, 8), f"Preprocessing {i+1} of {len(sections)}..."
            )
            rough_start_time = section["start"]
            rough_end_time = section["end"]
            audio = mp.AudioFileClip(input_video_path)
            rough_audio = audio.with_subclip(rough_start_time, rough_end_time)
            filename = ctx.get_file_path(
                f"audio_{rough_start_time}_{rough_end_time}.mp3"
            )
            rough_audio.write_audiofile(filename)

            ctx.progress(
                get_progress(2, 9), f"Transcribing {i+1} of {len(sections)}..."
            )
            rough_transcript = ctx.transcriptionengine.transcribe(
                filename, fast=False, words=True
            )

            ctx.progress(
                get_progress(3, 9), f"Generating edit {i+1} of {len(sections)}..."
            )
            full_edit = ctx.powerfulllmengine.generate(
                system_prompt=prompts["Full edit"]["system"],
                chat_prompt=prompts["Full edit"]["chat"].replace(
                    "{transcript}", json.dumps(rough_transcript)
                ),
                temperature=1,
                json_mode=True,
            )
            video = mp.VideoFileClip(input_video_path)
            full_edit_start = rough_start_time + full_edit["start"]
            full_edit_end = rough_start_time + full_edit["end"]
            clip: mp.VideoClip = video.with_subclip(full_edit_start, full_edit_end)
            w, h = clip.size
            resolution: float = w / h
            canvas_resolution: float = ctx.width / ctx.height
            if resolution > canvas_resolution:
                clip = clip.resized(height=ctx.height)
            else:
                clip = clip.resized(width=ctx.width)
            video_filename = ctx.get_file_path(
                f"intermediary_video_{full_edit_start}_{full_edit_end}.mp4"
            )
            clip.write_videofile(video_filename, codec="h264_nvenc")

            ctx.progress(
                get_progress(4, 9),
                f"Tracking and centering face {i+1} of {len(sections)}...",
            )

            def track_progress(step, total):
                # sub_allocated_progress is the allocated progress divided by 9
                sub_allocated_progress = allocated_progress / 9
                current_progress = sub_allocated_progress * step / total
                ctx.progress(
                    get_progress(4, 9) + current_progress,
                    f"Tracking and centering face {i+1} of {len(sections)}, frame {step} of {total}...",
                )

            tracked_video_filename = ctx.get_file_path(
                f"tracked_video_{full_edit_start}_{full_edit_end}.mp4"
            )
            track_and_center_face(
                video_filename,
                tracked_video_filename,
                (ctx.width, ctx.height),
                track_progress,
            )

            ctx.progress(
                get_progress(5, 9), f"Transcribing {i+1} of {len(sections)}..."
            )
            final_transcript = ctx.transcriptionengine.transcribe(
                tracked_video_filename, fast=False, words=True
            )

            ctx.progress(
                get_progress(6, 9), f"Generating captions {i+1} of {len(sections)}..."
            )
            captions = ctx.captioningengine.get_captions(final_transcript)
            video = mp.VideoFileClip(tracked_video_filename)
            final = mp.CompositeVideoClip(
                [video, *captions], size=(ctx.width, ctx.height)
            )
            final_filename = ctx.get_file_path(
                f"final_video_{full_edit_start}_{full_edit_end}.mp4"
            )

            ctx.progress(
                get_progress(7, 9), f"Final rendering {i+1} of {len(sections)}..."
            )
            final.write_videofile(final_filename, codec="h264_nvenc")

            ctx.progress(
                get_progress(8, 9),
                f"Generating description {i+1} of {len(sections)}...",
            )
            description = ctx.powerfulllmengine.generate(
                system_prompt=prompts["Description"]["system"],
                chat_prompt=prompts["Description"]["chat"]
                .replace("{transcript}", json.dumps(final_transcript))
                .replace("{title}", title)
                .replace("{channel}", channel),
                temperature=1,
                json_mode=True,
            )
            ctx.credits += f"\nOriginal video by {channel} on Youtube."
            title = description["title"]
            description = description["description"]

            ctx.progress(get_progress(9, 9), f"Uploading {i+1} of {len(sections)}...")
            description = description + "\n" + ctx.credits
            for engine in ctx.uploadengine:
                try:
                    engine.upload(
                        title=title,
                        description=description,
                        path=final_filename,
                    )
                except Exception as e:
                    print(e)
                    gr.Warning(f"{engine.name} failed to upload the video.")

        # ctx.progress(0.99, "Storing in database...")
        # ctx.store_in_db()
        ctx.progress(1, "Done!")

        command = "start" if os.name == "nt" else "open"
        os.system(f"{command} {os.path.abspath(ctx.dir)}")

    @classmethod
    def get_options(cls):
        return [
            gr.Number(
                minimum=1,
                maximum=10,
                label="Number of shorts",
                value=1,
                step=1,
            ),
            gr.Textbox(
                label="Youtube URL",
                placeholder="Enter the URL of the video you want to use",
                value="",
                max_lines=1,
            ),
        ]
