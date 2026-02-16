# Text-to-Speech Setup Guide

Complete instructions for setting up Qwen3-TTS on Apple Silicon via MLX from scratch on any machine.

## Overview

This setup uses:
- **Qwen3-TTS** (January 2026) — Alibaba's open-source TTS model supporting 10 languages, voice cloning, voice design, and emotion control
- **mlx-audio** — Apple MLX framework wrapper for TTS/STT optimized for Apple Silicon unified memory
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

model = load_model("mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16")

results = list(model.generate_custom_voice(
    text="Hello! This is a test of the Qwen 3 text to speech model running locally on Apple Silicon.",
    speaker="Ryan",
    language="English",
    instruct="Clear, friendly narration voice.",
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

First run downloads ~1.2GB model. Subsequent runs load from cache in seconds.

## Available Models

| Model ID | Method | Use Case | Download Size |
|----------|--------|----------|---------------|
| `mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16` | `generate_custom_voice()` | Built-in speakers + emotion | ~1.2GB |
| `mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16` | `generate_custom_voice()` | Higher quality + emotion | ~3.4GB |
| `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16` | `generate()` | Voice cloning | ~1.2GB |
| `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16` | `generate()` | HQ voice cloning | ~3.4GB |
| `mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16` | `generate_voice_design()` | Create any voice | ~3.4GB |
| `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit` | `generate()` | Smallest, fastest | ~0.4GB |
| `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-6bit` | `generate()` | Good quality/size | ~0.6GB |

## Architecture

```
Text Input → Qwen3-TTS (LLM) → Speech Tokens (12Hz) → DiT Decoder → 24kHz Audio
                                                                          ↓
                                                                    WAV → ffmpeg → MP3
```

1. **Qwen3-TTS** is an autoregressive language model that converts text + speaker/emotion instructions into discrete speech tokens at 12Hz
2. A **DiT (Diffusion Transformer) decoder** converts speech tokens into 24kHz audio waveforms
3. **MLX** runs everything on Apple Silicon's unified memory with Metal GPU acceleration
4. **ffmpeg** converts WAV to MP3/other formats

## Model Cache

Models are cached by HuggingFace Hub at:
```
~/.cache/huggingface/hub/models--mlx-community--Qwen3-TTS-12Hz-*/
```

To list cached models:
```bash
ls ~/.cache/huggingface/hub/ | grep Qwen3-TTS
```

To clear all Qwen3-TTS cache:
```bash
rm -rf ~/.cache/huggingface/hub/models--mlx-community--Qwen3-TTS-*
```

## CLI Usage (mlx-audio)

mlx-audio includes a command-line interface:

```bash
# Basic generation (creates WAV in current directory)
python -m mlx_audio.tts.generate \
    --model mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit \
    --text "Hello, this is a test."

# With immediate playback
python -m mlx_audio.tts.generate \
    --model mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit \
    --text "Hello!" --play

# Custom output directory
python -m mlx_audio.tts.generate \
    --model mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit \
    --text "Hello!" --output_path ./my_audio
```

## Performance Benchmarks (M4 Max, 128GB)

| Metric | 0.6B Model | 1.7B Model |
|--------|-----------|-----------|
| First load (download) | ~20 min | ~40 min |
| Cached load | ~5-10s | ~15-20s |
| Generation speed | ~2-3x realtime | ~1-1.5x realtime |
| Audio quality | Good | Better |
| Sample rate | 24kHz mono | 24kHz mono |

## Troubleshooting

### "No module named 'mlx'"
You're not on Apple Silicon or macOS < 15. MLX requires Apple Silicon + macOS 15+.

### Model download hangs or is very slow
```bash
# Set HuggingFace token
huggingface-cli login
# Or set environment variable
export HF_TOKEN=hf_your_token_here
```

### Out of memory
- Use the 0.6B model instead of 1.7B
- Use quantized variants (4bit/6bit)
- Close other applications to free unified memory
- Check with: `python3 -c "import mlx.core as mx; print(mx.metal.get_active_memory() / 1e9, 'GB')"`

### Audio sounds robotic or choppy
- Keep text segments to 1-3 sentences
- Use punctuation to control pacing
- Try different `instruct` values
- Switch to the 1.7B model for better quality

### ffmpeg errors
```bash
# Verify ffmpeg is installed
which ffmpeg
ffmpeg -version

# If not installed
brew install ffmpeg
```

## Links

- [Qwen3-TTS announcement](https://qwen.ai/blog?id=qwen3tts-0115)
- [Qwen3-TTS GitHub](https://github.com/QwenLM/Qwen3-TTS)
- [mlx-audio GitHub](https://github.com/Blaizzy/mlx-audio)
- [mlx-audio Qwen3 docs](https://github.com/Blaizzy/mlx-audio/blob/main/mlx_audio/tts/models/qwen3_tts/README.md)
- [MLX Community on HuggingFace](https://huggingface.co/mlx-community)
- [Apple MLX framework](https://github.com/ml-explore/mlx)
