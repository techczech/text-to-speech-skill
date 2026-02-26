#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["mlx-audio>=0.3", "soundfile", "numpy"]
#
# [tool.uv]
# prerelease = "allow"
# ///
"""
Dia Multi-Speaker Dialogue TTS demo using mlx-audio.
Generates a two-speaker conversation with nonverbal sounds on Apple Silicon.

Run with: uv run --python 3.12 scripts/generate_dia.py
Model: mlx-community/Dia-1.6B-fp16 (~3.2GB, downloads on first run)
"""

import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

# Configuration
MODEL_ID = "mlx-community/Dia-1.6B-fp16"
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Two-speaker dialogue with nonverbal sounds
DIALOGUE = """[S1] Good morning! How are you doing today?
[S2] I'm doing great, thanks for asking! Did you see the news about local AI models?
[S1] Yes! (laughs) It's incredible what you can run on a laptop now.
[S2] I know, right? Text to speech, image generation, even music creation. All running locally.
[S1] The quality is surprisingly good too. I've been using it for podcast production.
[S2] (sighs) I wish I had started sooner. What engine do you recommend for dialogue?
[S1] Well, you're listening to it right now! Dia handles two speakers in a single pass.
[S2] That's amazing. And the nonverbal sounds really add to the natural feel."""


def generate_dialogue():
    print(f"Loading model: {MODEL_ID}")
    start = time.time()
    model = load_model(MODEL_ID)
    print(f"Model loaded in {time.time() - start:.1f}s")

    print("\nGenerating multi-speaker dialogue...")
    gen_start = time.time()
    results = list(model.generate(
        text=DIALOGUE,
        temperature=1.3,
        top_p=0.95,
    ))

    if not results:
        print("ERROR: No audio generated!")
        sys.exit(1)

    audio = np.array(results[0].audio, dtype=np.float32)
    sample_rate = results[0].sample_rate  # 44100 Hz for Dia
    duration = len(audio) / sample_rate
    gen_time = time.time() - gen_start
    print(f"Generated {duration:.1f}s of audio in {gen_time:.1f}s ({duration/gen_time:.1f}x realtime)")
    print(f"Sample rate: {sample_rate} Hz")

    # Save WAV
    wav_path = OUTPUT_DIR / "dia_dialogue.wav"
    sf.write(str(wav_path), audio, sample_rate)
    print(f"Saved WAV: {wav_path}")

    # Convert to MP3
    mp3_path = OUTPUT_DIR / "dia_dialogue.mp3"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(wav_path),
             "-codec:a", "libmp3lame", "-qscale:a", "2", str(mp3_path)],
            check=True, capture_output=True,
        )
        print(f"Saved MP3: {mp3_path}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        print("WAV file is still available.")

    print("\nDone! Your dialogue is ready.")
    return wav_path


if __name__ == "__main__":
    generate_dialogue()
