# Text-to-Speech Setup Guide

Complete instructions for setting up multi-engine TTS on Apple Silicon via MLX from scratch on any machine.

## Overview

This setup uses:
- **mlx-audio** (v0.3+) — Apple MLX framework wrapper for TTS/STT with 16 TTS model backends
- **Qwen3-TTS** (January 2026) — Alibaba's open-source TTS with emotion control, voice cloning, voice design, 10 languages
- **Chatterbox Turbo** (Resemble AI) — High-quality TTS with easy voice cloning (no transcript needed) and streaming
- **Dia** (Nari Labs, 1.6B) — Multi-speaker dialogue generation with `[S1]`/`[S2]` speaker tags
- **MLX Community models** — Pre-converted model weights on HuggingFace optimized for MLX

## System Requirements

| Requirement | Details |
|------------|---------|
| **Hardware** | Apple Silicon Mac (M1/M2/M3/M4) |
| **macOS** | 15.0+ (required for MLX Metal backend) |
| **Python** | 3.10+ (3.11 or 3.12 recommended) |
| **RAM** | 8GB minimum, 16GB+ recommended for 1.7B models |
| **Disk** | ~2GB for venv + model cache (per model) |
| **ffmpeg** | Required for MP3/OGG/AAC conversion |

**Not supported:** Intel Macs, Linux, Windows (MLX is Apple Silicon only)

## Step-by-Step Setup

### 1. Install ffmpeg (if not present)

```bash
brew install ffmpeg
```

Verify: `ffmpeg -version`

### 2. Create Project Directory

```bash
mkdir -p ~/my-tts-project
cd ~/my-tts-project
```

### 3. Create Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### 4. Install mlx-audio

```bash
pip install mlx-audio
```

**Important:** Chatterbox Turbo and Dia require mlx-audio v0.3+. If you have an older version:
```bash
pip install -U mlx-audio
```

This installs:
- `mlx` (Apple MLX framework)
- `mlx-metal` (Metal GPU backend)
- `mlx-lm` (language model support)
- `transformers`, `huggingface_hub` (model loading)
- `soundfile`, `librosa` (audio I/O)
- `numpy`, `scipy` (numerical computing)

### 5. (Optional) Set HuggingFace Token for Faster Downloads

```bash
pip install huggingface_hub
huggingface-cli login
```

### 6. Test the Installation

```bash
python3 -c "
import mlx.core as mx
from mlx_audio.tts.utils import load_model
print('MLX device:', mx.default_device())
print('mlx-audio loaded successfully')
"
```

Expected output:
```
MLX device: gpu
mlx-audio loaded successfully
```

### 7. First Generation (Downloads Model)

Create a test script `test_tts.py`:

```python
#!/usr/bin/env python3
import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

# Chatterbox Turbo — fastest first experience
model = load_model("mlx-community/chatterbox-turbo-fp16")

results = list(model.generate(
    text="Hello! This is a test of local text to speech running on Apple Silicon.",
))

audio = np.array(results[0].audio, dtype=np.float32)
sample_rate = results[0].sample_rate
sf.write("test_output.wav", audio, sample_rate)
print(f"Generated {len(audio) / sample_rate:.1f}s of audio at {sample_rate}Hz")
print("Saved to test_output.wav")
```

Run it:
```bash
python3 test_tts.py
```

First run downloads the model (~3GB). Subsequent runs load from cache in seconds.

## Available Models

### Featured Engines

| Model ID | Engine | Method | Use Case | Download Size |
|----------|--------|--------|----------|---------------|
| `mlx-community/chatterbox-turbo-fp16` | Chatterbox Turbo | `generate()` | Easy voice cloning, streaming | ~3.0GB |
| `mlx-community/chatterbox-fp16` | Chatterbox | `generate()` | Voice cloning + emotion control | ~2.6GB |
| `mlx-community/Dia-1.6B-fp16` | Dia | `generate()` | Multi-speaker dialogue | ~3.2GB |
| `mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16` | Qwen3-TTS | `generate_custom_voice()` | Built-in speakers + emotion | ~1.2GB |
| `mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16` | Qwen3-TTS | `generate_custom_voice()` | Higher quality + emotion | ~3.4GB |
| `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16` | Qwen3-TTS | `generate()` | Voice cloning | ~1.2GB |
| `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16` | Qwen3-TTS | `generate()` | HQ voice cloning | ~3.4GB |
| `mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16` | Qwen3-TTS | `generate_voice_design()` | Create any voice from description | ~3.4GB |
| `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit` | Qwen3-TTS | `generate()` | Smallest, fastest | ~0.4GB |
| `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-6bit` | Qwen3-TTS | `generate()` | Good quality/size | ~0.6GB |

### Other Models in mlx-audio

These models are also available via `load_model()` but are not featured in the main skill documentation:

| Model | Key Feature | Approx Size |
|-------|-------------|-------------|
| Spark | Gender/pitch/speed control, voice cloning | ~0.5B |
| Sesame (CSM-1B) | Conversational speech | ~1B |
| Kokoro | Fastest generation, 54+ preset voices | 82M |
| OuteTTS | Auto speaker profile via Whisper | ~500M |
| IndexTTS | Always uses reference voice | Variable |
| Llama (Orpheus) | LLM-based TTS | Variable |
| Soprano | Ultra-fast base generation | ~80M |
| Bark | Older model, preset voices | ~350M |

Search `mlx-community` on HuggingFace for the latest model IDs.

## Architecture

### Qwen3-TTS
```
Text Input → Qwen3-TTS (LLM) → Speech Tokens (12Hz) → DiT Decoder → 24kHz Audio
```

### Chatterbox Turbo
```
Text Input → T3 (Token Generator) → S3Gen (Vocoder) → 24kHz Audio
              ↑ VoiceEncoder (speaker embedding from ref_audio)
```

### Dia
```
Text with [S1]/[S2] tags → Dia (Autoregressive + CFG) → 44.1kHz Audio
```

All pipelines output WAV → ffmpeg → MP3/other formats.

## Model Cache

Models are cached by HuggingFace Hub at:
```
~/local-models/  (if HF_HUB_CACHE is set)
~/.cache/huggingface/hub/  (default)
```

To list cached TTS models:
```bash
ls ~/local-models/ | grep -E "(Qwen3-TTS|chatterbox|Dia)"
```

To clear all TTS model cache:
```bash
rm -rf ~/local-models/models--mlx-community--Qwen3-TTS-*
rm -rf ~/local-models/models--mlx-community--chatterbox-*
rm -rf ~/local-models/models--mlx-community--Dia-*
```

## CLI Usage (mlx-audio)

mlx-audio includes a command-line interface that works with all engines:

```bash
# Chatterbox Turbo — basic generation
python -m mlx_audio.tts.generate \
    --model mlx-community/chatterbox-turbo-fp16 \
    --text "Hello, this is a test."

# Chatterbox Turbo — voice cloning
python -m mlx_audio.tts.generate \
    --model mlx-community/chatterbox-turbo-fp16 \
    --text "Hello in cloned voice." \
    --ref_audio voice_sample.wav

# Dia — multi-speaker dialogue
python -m mlx_audio.tts.generate \
    --model mlx-community/Dia-1.6B-fp16 \
    --text "[S1] Hello! [S2] Hi there!"

# Qwen3-TTS — with playback
python -m mlx_audio.tts.generate \
    --model mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit \
    --text "Hello!" --play

# Custom output directory
python -m mlx_audio.tts.generate \
    --model mlx-community/chatterbox-turbo-fp16 \
    --text "Hello!" --output_path ./my_audio
```

## Performance Benchmarks (M4 Max, 128GB)

| Engine | First Load (download) | Cached Load | Generation Speed | Sample Rate |
|--------|----------------------|-------------|-----------------|-------------|
| Qwen3-TTS 0.6B | ~20 min | ~5-10s | ~2-3x realtime | 24kHz |
| Qwen3-TTS 1.7B | ~40 min | ~15-20s | ~1-1.5x realtime | 24kHz |
| Chatterbox Turbo | ~30 min | ~5-10s | ~2x realtime | 24kHz |
| Dia 1.6B | ~30 min | ~10-15s | ~1-2x realtime | 44.1kHz |

## Troubleshooting

### "No module named 'mlx'"
You're not on Apple Silicon or macOS < 15. MLX requires Apple Silicon + macOS 15+.

### Chatterbox/Dia model not found
Upgrade mlx-audio to v0.3+:
```bash
pip install -U mlx-audio
```

### Model download hangs or is very slow
```bash
# Set HuggingFace token
huggingface-cli login
# Or set environment variable
export HF_TOKEN=hf_your_token_here
```

### Out of memory
- Use smaller models (Qwen3 0.6B, Kokoro 82M)
- Use quantized variants (4bit/6bit) for Qwen3-TTS
- Close other applications to free unified memory
- Check with: `python3 -c "import mlx.core as mx; print(mx.metal.get_active_memory() / 1e9, 'GB')"`

### Audio sounds robotic or choppy
- Keep text segments to 1-3 sentences
- Use punctuation to control pacing
- Try different engines (Chatterbox Turbo often has most natural default voice)
- Switch to larger models for better quality

### Voice cloning sounds off
- Use clean reference audio (5+ seconds, single speaker)
- No background noise or music
- For Qwen3-TTS, provide accurate `ref_text` transcript
- Try both engines and compare results

### ffmpeg errors
```bash
# Verify ffmpeg is installed
which ffmpeg
ffmpeg -version

# If not installed
brew install ffmpeg
```

## Czech TTS Setup (Chatterbox Multilingual)

Czech speech uses a PyTorch-based Chatterbox Multilingual model (not mlx-audio).

```bash
cd ~/gitrepos/x-experiments/chatterbox
uv sync

# Download Czech T3 fine-tune weights
HF_HUB_CACHE=~/local-models huggingface-cli download Thomcles/Chatterbox-TTS-Czech
```

**Patches applied to `src/chatterbox/mtl_tts.py`:**
- Added `"cs": "Czech"` to `SUPPORTED_LANGUAGES` dict (line ~24)
- Changed `map_location` to `"cpu"` on lines 166 and 179 (for Apple Silicon)

Czech T3 weights location: `~/local-models/models--Thomcles--Chatterbox-TTS-Czech/snapshots/*/t3_cs.safetensors`

Test script: `test_czech.py` and `test_czech_deda.py` in the project root.

## ACE-Step 1.5 Setup (Music Generation)

ACE-Step generates music from text descriptions and lyrics using MLX on Apple Silicon.

```bash
cd ~/gitrepos/x-experiments/ace-step
uv sync
```

**Models** are stored in `checkpoints/` (~10GB total). They download automatically on first run, but can stall. Manual download via curl:

```bash
cd ~/gitrepos/x-experiments/ace-step/checkpoints

# VAE decoder (322MB)
curl -L -o vae/diffusion_pytorch_model.safetensors \
  "https://huggingface.co/ACE-Step/Ace-Step1.5/resolve/main/vae/diffusion_pytorch_model.safetensors"

# Text encoder (1.1GB)
curl -L -o Qwen3-Embedding-0.6B/model.safetensors \
  "https://huggingface.co/ACE-Step/Ace-Step1.5/resolve/main/Qwen3-Embedding-0.6B/model.safetensors"

# LM for chain-of-thought (3.7GB) — only needed if thinking=true
curl -C - -L -o acestep-5Hz-lm-1.7B/model.safetensors \
  "https://huggingface.co/ACE-Step/Ace-Step1.5/resolve/main/acestep-5Hz-lm-1.7B/model.safetensors"

# Turbo DiT model (4.8GB)
curl -C - -L -o acestep-v15-turbo/model.safetensors \
  "https://huggingface.co/ACE-Step/Ace-Step1.5/resolve/main/acestep-v15-turbo/model.safetensors"
```

Config files (JSON, tokenizer, etc.) download automatically via `huggingface_hub` on first run.

**Usage:** Create a TOML config and run `uv run python cli.py -c song.toml`. See SKILL.md section 7 for full parameter reference.

HuggingFace repo: `ACE-Step/Ace-Step1.5`

## Links

- [Qwen3-TTS announcement](https://qwen.ai/blog?id=qwen3tts-0115)
- [Qwen3-TTS GitHub](https://github.com/QwenLM/Qwen3-TTS)
- [Chatterbox GitHub](https://github.com/resemble-ai/chatterbox)
- [Chatterbox-TTS-Czech](https://huggingface.co/Thomcles/Chatterbox-TTS-Czech)
- [Dia GitHub](https://github.com/nari-labs/dia)
- [ACE-Step GitHub](https://github.com/ace-step/ACE-Step)
- [ACE-Step 1.5 HuggingFace](https://huggingface.co/ACE-Step/Ace-Step1.5)
- [mlx-audio GitHub](https://github.com/Blaizzy/mlx-audio)
- [MLX Community on HuggingFace](https://huggingface.co/mlx-community)
- [Apple MLX framework](https://github.com/ml-explore/mlx)
