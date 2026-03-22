# converts videos into mp3 files (skip videos without audio)

import os
import subprocess

VIDEO_DIR = "videos"
AUDIO_DIR = "audios"

os.makedirs(AUDIO_DIR, exist_ok=True)


def has_audio(video_path):
    """Check if video has an audio stream"""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=index",
        "-of", "csv=p=0",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return bool(result.stdout.strip())


for root, _, files in os.walk(VIDEO_DIR):

    for file in files:

        if not file.lower().endswith((".mp4", ".mkv", ".avi")):
            continue

        if "_" not in file:
            continue

        full_path = os.path.join(root, file)

        tutorial_number, file_name = file.split("_", 1)
        base_name = os.path.splitext(file_name)[0]

        output_mp3 = os.path.join(
            AUDIO_DIR,
            f"{tutorial_number}_{base_name}.mp3"
        )

        # Skip if audio already exists
        if os.path.exists(output_mp3):
            print("Skipping (audio exists):", file)
            continue

        # Skip if video has no audio track
        if not has_audio(full_path):
            print("Skipping (no audio track):", file)
            continue

        print("Converting:", full_path)

        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i", full_path,
                "-vn",
                "-ac", "1",
                "-ar", "16000",
                "-ab", "192k",
                output_mp3
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Safety check
        if not os.path.exists(output_mp3):
            print("⚠ FFmpeg failed:", file)
