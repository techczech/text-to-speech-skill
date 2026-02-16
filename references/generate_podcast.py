#!/usr/bin/env python3
"""
Podcast TTS Generator using Qwen3-TTS via mlx-audio.
Generates a short podcast segment using Qwen3-TTS CustomVoice model on Apple Silicon.
"""

import subprocess
import sys
import time
from pathlib import Path

import mlx.core as mx
import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

# Configuration
MODEL_ID = "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Podcast script - a short tech podcast intro
PODCAST_SEGMENTS = [
    {
        "text": (
            "Welcome to The Silicon Pulse, your weekly deep dive into the world of "
            "artificial intelligence and machine learning. I'm your host, Ryan, and today "
            "we have a fascinating episode lined up for you."
        ),
        "speaker": "Ryan",
        "instruct": "Professional, warm, and enthusiastic podcast host voice. Clear enunciation with a friendly tone.",
    },
    {
        "text": (
            "Today we're talking about something truly exciting: running large language models "
            "right on your laptop. No cloud, no API calls, just pure local inference. "
            "Apple Silicon has completely changed the game here."
        ),
        "speaker": "Ryan",
        "instruct": "Engaged and informative, building excitement about the topic.",
    },
    {
        "text": (
            "Think about it. Just two years ago, running a seven billion parameter model "
            "locally would have been unthinkable for most developers. Now, with frameworks "
            "like MLX, optimized specifically for Apple's unified memory architecture, "
            "you can run these models at incredible speeds on a MacBook."
        ),
        "speaker": "Ryan",
        "instruct": "Thoughtful and explanatory, emphasizing the significance of the technological progress.",
    },
    {
        "text": (
            "And it's not just text models. We're now seeing text to speech, speech recognition, "
            "image generation, all running locally with remarkable quality. "
            "The democratization of AI is happening right before our eyes."
        ),
        "speaker": "Ryan",
        "instruct": "Excited and forward-looking, conveying wonder at the possibilities.",
    },
    {
        "text": (
            "That's all for today's episode of The Silicon Pulse. If you enjoyed this, "
            "make sure to subscribe and leave a review. Until next time, keep experimenting, "
            "keep building, and keep pushing the boundaries of what's possible. See you next week!"
        ),
        "speaker": "Ryan",
        "instruct": "Warm and upbeat closing, friendly farewell tone.",
    },
]


def generate_podcast():
    print(f"Loading model: {MODEL_ID}")
    start = time.time()
    model = load_model(MODEL_ID)
    print(f"Model loaded in {time.time() - start:.1f}s")

    all_audio = []
    sample_rate = None

    for i, segment in enumerate(PODCAST_SEGMENTS):
        print(f"\nGenerating segment {i + 1}/{len(PODCAST_SEGMENTS)}...")
        print(f"  Text: {segment['text'][:80]}...")

        seg_start = time.time()
        results = list(
            model.generate_custom_voice(
                text=segment["text"],
                speaker=segment["speaker"],
                language="English",
                instruct=segment["instruct"],
            )
        )

        if results:
            audio_array = results[0].audio
            # Convert mlx array to numpy
            audio_np = np.array(audio_array, dtype=np.float32)

            # Get sample rate from model (Qwen3-TTS uses 24000 Hz)
            if sample_rate is None:
                sample_rate = getattr(results[0], "sample_rate", 24000)
                print(f"  Sample rate: {sample_rate} Hz")

            all_audio.append(audio_np)

            # Add a short pause between segments (0.5 seconds of silence)
            pause = np.zeros(int(sample_rate * 0.5), dtype=np.float32)
            all_audio.append(pause)

            print(f"  Generated in {time.time() - seg_start:.1f}s ({len(audio_np) / sample_rate:.1f}s of audio)")
        else:
            print(f"  WARNING: No audio generated for segment {i + 1}")

    if not all_audio:
        print("ERROR: No audio was generated!")
        sys.exit(1)

    # Concatenate all audio
    full_audio = np.concatenate(all_audio)
    print(f"\nTotal audio length: {len(full_audio) / sample_rate:.1f}s")

    # Save as WAV
    wav_path = OUTPUT_DIR / "podcast_episode.wav"
    sf.write(str(wav_path), full_audio, sample_rate)
    print(f"Saved WAV: {wav_path}")

    # Convert to MP3 using ffmpeg
    mp3_path = OUTPUT_DIR / "podcast_episode.mp3"
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(wav_path),
                "-codec:a", "libmp3lame",
                "-qscale:a", "2",
                str(mp3_path),
            ],
            check=True,
            capture_output=True,
        )
        print(f"Saved MP3: {mp3_path}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        print("WAV file is still available.")

    print("\nDone! Your podcast is ready.")
    return mp3_path


if __name__ == "__main__":
    generate_podcast()
