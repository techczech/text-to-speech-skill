#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["mlx-audio>=0.3", "soundfile", "numpy"]
#
# [tool.uv]
# prerelease = "allow"
# ///
"""
Voice Cloning Comparison: Chatterbox Turbo vs Qwen3-TTS Base.
Demonstrates voice cloning with both engines for side-by-side comparison.

Run with: uv run --python 3.12 scripts/voice_clone_demo.py reference_voice.wav
  or:     uv run --python 3.12 scripts/voice_clone_demo.py reference_voice.wav "Transcript of the reference audio."
"""

import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Text to generate in the cloned voice
CLONE_TEXT = (
    "This is a demonstration of voice cloning running entirely on device. "
    "The model captured the characteristics of the reference voice "
    "and is now generating new speech that sounds similar."
)


def clone_with_chatterbox(ref_audio: str):
    """Clone voice with Chatterbox Turbo — no transcript needed."""
    print("=" * 60)
    print("Chatterbox Turbo (no transcript needed)")
    print("=" * 60)

    model_id = "mlx-community/chatterbox-turbo-fp16"
    print(f"Loading {model_id}...")
    start = time.time()
    model = load_model(model_id)
    print(f"Loaded in {time.time() - start:.1f}s")

    print("Generating...")
    gen_start = time.time()
    results = list(model.generate(
        text=CLONE_TEXT,
        ref_audio=ref_audio,
    ))

    if not results:
        print("ERROR: No audio generated!")
        return

    audio = np.array(results[0].audio, dtype=np.float32)
    sample_rate = results[0].sample_rate
    duration = len(audio) / sample_rate
    gen_time = time.time() - gen_start
    print(f"Generated {duration:.1f}s in {gen_time:.1f}s ({duration/gen_time:.1f}x realtime)")

    out_path = OUTPUT_DIR / "clone_chatterbox.wav"
    sf.write(str(out_path), audio, sample_rate)
    print(f"Saved: {out_path}")
    print()


def clone_with_qwen3(ref_audio: str, ref_text: str = None):
    """Clone voice with Qwen3-TTS Base — best quality, needs transcript."""
    print("=" * 60)
    print("Qwen3-TTS Base (with transcript)")
    print("=" * 60)

    model_id = "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16"
    print(f"Loading {model_id}...")
    start = time.time()
    model = load_model(model_id)
    print(f"Loaded in {time.time() - start:.1f}s")

    if ref_text is None:
        print("WARNING: No ref_text provided. Qwen3-TTS works best with a transcript.")
        print("Provide it as the second argument: python voice_clone_demo.py audio.wav \"transcript\"")
        print("Attempting without transcript (quality may be lower)...")
        ref_text = ""

    print("Generating...")
    gen_start = time.time()
    results = list(model.generate(
        text=CLONE_TEXT,
        ref_audio=ref_audio,
        ref_text=ref_text,
    ))

    if not results:
        print("ERROR: No audio generated!")
        return

    audio = np.array(results[0].audio, dtype=np.float32)
    sample_rate = results[0].sample_rate
    duration = len(audio) / sample_rate
    gen_time = time.time() - gen_start
    print(f"Generated {duration:.1f}s in {gen_time:.1f}s ({duration/gen_time:.1f}x realtime)")

    out_path = OUTPUT_DIR / "clone_qwen3.wav"
    sf.write(str(out_path), audio, sample_rate)
    print(f"Saved: {out_path}")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python voice_clone_demo.py <ref_audio.wav> [ref_text]")
        print()
        print("  ref_audio.wav   Reference audio file (5+ seconds, clean speech)")
        print("  ref_text        Transcript of the reference audio (optional, improves Qwen3)")
        print()
        print("Outputs side-by-side cloned audio from both engines.")
        sys.exit(1)

    ref_audio = sys.argv[1]
    ref_text = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(ref_audio).exists():
        print(f"Error: File not found: {ref_audio}")
        sys.exit(1)

    print(f"Reference audio: {ref_audio}")
    if ref_text:
        print(f"Reference text:  {ref_text[:80]}{'...' if len(ref_text) > 80 else ''}")
    print()

    clone_with_chatterbox(ref_audio)
    clone_with_qwen3(ref_audio, ref_text)

    print("=" * 60)
    print("Comparison complete!")
    print(f"  Chatterbox: {OUTPUT_DIR / 'clone_chatterbox.wav'}")
    print(f"  Qwen3-TTS:  {OUTPUT_DIR / 'clone_qwen3.wav'}")
    print()
    print("Listen to both and compare voice similarity and naturalness.")


if __name__ == "__main__":
    main()
