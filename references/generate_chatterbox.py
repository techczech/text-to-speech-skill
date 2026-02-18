#!/usr/bin/env python3
"""
Chatterbox Turbo TTS demo using mlx-audio.
Demonstrates basic generation, voice cloning, and streaming on Apple Silicon.

Requires: pip install mlx-audio (v0.3+)
Model: mlx-community/chatterbox-turbo-fp16 (~3GB, downloads on first run)
"""

import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

# Configuration
MODEL_ID = "mlx-community/chatterbox-turbo-fp16"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_basic():
    """Basic text-to-speech generation."""
    print(f"Loading model: {MODEL_ID}")
    start = time.time()
    model = load_model(MODEL_ID)
    print(f"Model loaded in {time.time() - start:.1f}s")

    text = (
        "Chatterbox Turbo is a high-quality text to speech model from Resemble AI. "
        "It runs locally on Apple Silicon using the MLX framework, "
        "and can generate natural sounding speech in real time."
    )

    print(f"\nGenerating speech...")
    gen_start = time.time()
    results = list(model.generate(text=text))

    if not results:
        print("ERROR: No audio generated!")
        sys.exit(1)

    audio = np.array(results[0].audio, dtype=np.float32)
    sample_rate = results[0].sample_rate
    duration = len(audio) / sample_rate
    gen_time = time.time() - gen_start
    print(f"Generated {duration:.1f}s of audio in {gen_time:.1f}s ({duration/gen_time:.1f}x realtime)")

    # Save WAV
    wav_path = OUTPUT_DIR / "chatterbox_basic.wav"
    sf.write(str(wav_path), audio, sample_rate)
    print(f"Saved: {wav_path}")

    # Convert to MP3
    mp3_path = OUTPUT_DIR / "chatterbox_basic.mp3"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(wav_path),
             "-codec:a", "libmp3lame", "-qscale:a", "2", str(mp3_path)],
            check=True, capture_output=True,
        )
        print(f"Saved: {mp3_path}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")

    return model


def generate_with_voice_clone(model, ref_audio_path: str):
    """Voice cloning — just provide a reference audio file, no transcript needed."""
    ref_path = Path(ref_audio_path)
    if not ref_path.exists():
        print(f"Reference audio not found: {ref_path}")
        print("Skipping voice cloning demo. Provide a WAV file (5+ seconds) as argument.")
        return

    print(f"\nCloning voice from: {ref_path}")
    text = (
        "This text is being spoken in a cloned voice. "
        "Chatterbox Turbo can clone any voice from just a few seconds of reference audio, "
        "without needing a transcript of the reference."
    )

    gen_start = time.time()
    results = list(model.generate(
        text=text,
        ref_audio=str(ref_path),
    ))

    if not results:
        print("ERROR: No audio generated!")
        return

    audio = np.array(results[0].audio, dtype=np.float32)
    sample_rate = results[0].sample_rate
    duration = len(audio) / sample_rate
    print(f"Generated {duration:.1f}s in {time.time() - gen_start:.1f}s")

    wav_path = OUTPUT_DIR / "chatterbox_cloned.wav"
    sf.write(str(wav_path), audio, sample_rate)
    print(f"Saved: {wav_path}")


def generate_streaming(model):
    """Streaming generation — audio arrives in chunks."""
    print("\nStreaming generation...")
    text = (
        "This is a streaming generation demo. "
        "The audio is generated in chunks and can be played back in real time. "
        "This is useful for interactive applications where low latency matters."
    )

    all_chunks = []
    sample_rate = None

    for i, chunk in enumerate(model.generate(
        text=text,
        stream=True,
        streaming_interval=2.0,
    )):
        audio_np = np.array(chunk.audio, dtype=np.float32)
        if sample_rate is None:
            sample_rate = chunk.sample_rate
        all_chunks.append(audio_np)
        chunk_duration = len(audio_np) / sample_rate
        status = "final" if chunk.is_final_chunk else "streaming"
        print(f"  Chunk {i + 1}: {chunk_duration:.1f}s ({status})")

    if all_chunks:
        full_audio = np.concatenate(all_chunks)
        wav_path = OUTPUT_DIR / "chatterbox_streaming.wav"
        sf.write(str(wav_path), full_audio, sample_rate)
        print(f"Saved: {wav_path} ({len(full_audio) / sample_rate:.1f}s total)")


if __name__ == "__main__":
    model = generate_basic()
    generate_streaming(model)

    # Voice cloning: pass a reference audio file as argument
    if len(sys.argv) > 1:
        generate_with_voice_clone(model, sys.argv[1])
    else:
        print("\nTip: Pass a reference audio file to test voice cloning:")
        print(f"  python {sys.argv[0]} reference_voice.wav")

    print("\nDone!")
