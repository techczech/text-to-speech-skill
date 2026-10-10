#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["mlx-audio>=0.3", "soundfile", "numpy"]
#
# [tool.uv]
# prerelease = "allow"
# ///
"""Quick voice cloning test with Chatterbox Turbo and Qwen3-TTS.

Usage: uv run scripts/clone_test.py path/to/your_reference.wav [--ref-text "exact transcript"]

Only use reference audio of a voice you have permission to clone.
"""
import argparse
import time
from pathlib import Path

import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("ref_audio", help="path to reference audio (5-15 s, one speaker) you are authorised to clone")
parser.add_argument("--ref-text", default="", help="exact transcript of the reference audio (improves Qwen3-TTS quality)")
args = parser.parse_args()
REF_AUDIO = str(Path(args.ref_audio).expanduser())
if not Path(REF_AUDIO).is_file():
    parser.error(f"reference audio not found: {REF_AUDIO}")
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEXT = (
    "This is a voice cloning test. The model has captured the characteristics "
    "of the original speaker and is now generating entirely new speech. "
    "Local text to speech on Apple Silicon is truly remarkable."
)

# --- Chatterbox Turbo (no transcript needed) ---
print("=" * 60)
print("Chatterbox Turbo — voice cloning (no transcript)")
print("=" * 60)
t0 = time.time()
model = load_model("mlx-community/chatterbox-turbo-fp16")
print(f"Model loaded in {time.time() - t0:.1f}s")

t0 = time.time()
results = list(model.generate(text=TEXT, ref_audio=REF_AUDIO))
gen_time = time.time() - t0

if results:
    audio = np.array(results[0].audio, dtype=np.float32)
    sr = results[0].sample_rate
    dur = len(audio) / sr
    print(f"Generated {dur:.1f}s in {gen_time:.1f}s ({dur/gen_time:.1f}x RT)")
    out = OUTPUT_DIR / "clone_chatterbox_turbo.wav"
    sf.write(str(out), audio, sr)
    print(f"Saved: {out}")
else:
    print("ERROR: No audio generated")

# --- Qwen3-TTS Base (voice cloning with transcript) ---
print()
print("=" * 60)
print("Qwen3-TTS Base — voice cloning (with transcript)")
print("=" * 60)
t0 = time.time()
model2 = load_model("mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16")
print(f"Model loaded in {time.time() - t0:.1f}s")

# For best results, pass --ref-text with the exact transcript of the reference audio
t0 = time.time()
results2 = list(model2.generate(
    text=TEXT,
    ref_audio=REF_AUDIO,
    ref_text=args.ref_text,
))
gen_time2 = time.time() - t0

if results2:
    audio2 = np.array(results2[0].audio, dtype=np.float32)
    sr2 = results2[0].sample_rate
    dur2 = len(audio2) / sr2
    print(f"Generated {dur2:.1f}s in {gen_time2:.1f}s ({dur2/gen_time2:.1f}x RT)")
    out2 = OUTPUT_DIR / "clone_qwen3_base.wav"
    sf.write(str(out2), audio2, sr2)
    print(f"Saved: {out2}")
else:
    print("ERROR: No audio generated")

print()
print("Done! Compare the two outputs:")
print(f"  Chatterbox: {OUTPUT_DIR / 'clone_chatterbox_turbo.wav'}")
print(f"  Qwen3-TTS:  {OUTPUT_DIR / 'clone_qwen3_base.wav'}")
