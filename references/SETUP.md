# Text-to-Speech Setup Guide

Complete instructions for setting up multi-engine TTS on Apple Silicon via MLX from scratch on any machine.

## Overview

This setup uses:
- **mlx-audio** (v0.3+) — Apple MLX framework wrapper for TTS/STT with 16 TTS model backends
- **Qwen3-TTS** (January 2026) — Alibaba's open-source TTS with emotion control, voice cloning, voice design, 10 languages. **Default engine.**
- **Chatterbox Turbo** (Resemble AI) — High-quality TTS with easy voice cloning (no transcript needed) and streaming
- **Dia** (Nari Labs, 1.6B) — Multi-speaker dialogue generation with `[S1]`/`[S2]` speaker tags
- **MLX Community models** — Pre-converted model weights on HuggingFace optimized for MLX

## System Requirements

| Requirement | Details |
|------------|---------|
| **Hardware** | Apple Silicon Mac (M1/M2/M3/M4) |
| **macOS** | 15.0+ (required for MLX Metal backend) |
| **Python** | 3.10+ (3.11 or 3.12 recommended) |
| **uv** | Recommended for running scripts (no venv needed) |
| **RAM** | 8GB minimum, 16GB+ recommended for 1.7B models |
| **Disk** | Model cache ~1-3GB per model |
| **ffmpeg** | Required for MP3/OGG/AAC conversion |

**Not supported:** Intel Macs, Linux, Windows (MLX is Apple Silicon only)

## Step-by-Step Setup (uv run — Recommended)

`uv run` with PEP 723 inline dependencies is the primary method. No venv creation needed.

### 1. Install uv and ffmpeg

```bash
# Install uv (if not present)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install ffmpeg (if not present)
brew install ffmpeg
```

Verify: `which uv && which ffmpeg`

### 2. Check Cached Models

Before generating, check what's already cached (avoids multi-GB downloads):

```bash
ls "${HF_HUB_CACHE:-${HF_HOME:-$HOME/.cache/huggingface}/hub}" | grep -iE "(Qwen3-TTS|chatterbox|Dia-|Kokoro|csm)"
```

Prefer a model that's already cached. The default is `Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16`.

### 3. (Optional) Set HuggingFace Token for Faster Downloads

```bash
uv run --with huggingface_hub huggingface-cli login
```

### 4. Test with One Command

```bash
uv run --python 3.12 --with "mlx-audio>=0.3" --prerelease=allow \
  python -m mlx_audio.tts.generate \
    --model mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16 \
    --text "Hello! Local TTS on Apple Silicon." --play
```

First run downloads the model (~1.2GB). Subsequent runs load from cache in seconds.

### 5. Run a PEP 723 Script

All reference scripts include inline dependency metadata and can be run directly:

```bash
uv run --python 3.12 scripts/generate_podcast.py
```

No `pip install`, no `venv`, no activation step.

## Available Models

### Featured Engines

| Model ID | Engine | Method | Use Case | Download Size |
|----------|--------|--------|----------|---------------|
| `mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16` | Qwen3-TTS | `generate_custom_voice()` | **Default.** Built-in speakers + emotion | ~1.2GB |
| `mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16` | Qwen3-TTS | `generate_custom_voice()` | Higher quality + emotion | ~3.4GB |
| `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16` | Qwen3-TTS | `generate()` | Voice cloning | ~1.2GB |
| `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16` | Qwen3-TTS | `generate()` | HQ voice cloning | ~3.4GB |
| `mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16` | Qwen3-TTS | `generate_voice_design()` | Create any voice from description | ~3.4GB |
| `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit` | Qwen3-TTS | `generate()` | Smallest, fastest | ~0.4GB |
| `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-6bit` | Qwen3-TTS | `generate()` | Good quality/size | ~0.6GB |
| `mlx-community/chatterbox-turbo-fp16` | Chatterbox Turbo | `generate()` | Easy voice cloning, streaming | ~3.0GB |
| `mlx-community/chatterbox-fp16` | Chatterbox | `generate()` | Voice cloning + emotion control | ~2.6GB |
| `mlx-community/Dia-1.6B-fp16` | Dia | `generate()` | Multi-speaker dialogue | ~3.2GB |

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
$HF_HUB_CACHE  (if set)
$HF_HOME/hub  (if HF_HOME is set)
~/.cache/huggingface/hub/  (default)
```

To list cached TTS models:
```bash
ls "${HF_HUB_CACHE:-${HF_HOME:-$HOME/.cache/huggingface}/hub}" | grep -E "(Qwen3-TTS|chatterbox|Dia)"
```

## CLI Usage (mlx-audio)

mlx-audio includes a command-line interface that works with all engines. Use `uv run` to invoke without a venv:

```bash
# Qwen3-TTS — default, with playback
uv run --python 3.12 --with "mlx-audio>=0.3" --prerelease=allow \
  python -m mlx_audio.tts.generate \
    --model mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16 \
    --text "Hello, this is a test." --play

# Chatterbox Turbo — voice cloning
uv run --python 3.12 --with "mlx-audio>=0.3" --prerelease=allow \
  python -m mlx_audio.tts.generate \
    --model mlx-community/chatterbox-turbo-fp16 \
    --text "Hello in cloned voice." \
    --ref_audio voice_sample.wav

# Dia — multi-speaker dialogue
uv run --python 3.12 --with "mlx-audio>=0.3" --prerelease=allow \
  python -m mlx_audio.tts.generate \
    --model mlx-community/Dia-1.6B-fp16 \
    --text "[S1] Hello! [S2] Hi there!"
```

## Performance Benchmarks (M4 Max, 128GB)

| Engine | Cached Load | Generation Speed | Sample Rate |
|--------|-------------|-----------------|-------------|
| Qwen3-TTS 0.6B | ~5-10s | ~2-3x realtime | 24kHz |
| Qwen3-TTS 1.7B | ~15-20s | ~1-1.5x realtime | 24kHz |
| Chatterbox Turbo | ~5-10s | ~2x realtime | 24kHz |
| Dia 1.6B | ~10-15s | ~1-2x realtime | 44.1kHz |

## Czech TTS & ACE-Step Setup

For Czech TTS setup, see `references/czech-tts.md`.
For ACE-Step music generation setup, see `references/ace-step.md`.

## Troubleshooting

### "No module named 'mlx'"
You're not on Apple Silicon or macOS < 15. MLX requires Apple Silicon + macOS 15+.

### Chatterbox/Dia model not found
Ensure mlx-audio v0.3+. With `uv run`, specify `--with "mlx-audio>=0.3"`. In a venv: `pip install -U mlx-audio`.

### Anaconda Conflicts
Anaconda environments pin `numpy <2` and old `pandas`/`sklearn` that conflict with mlx-audio. Use `uv run` instead of conda/pip.

### Model download hangs or is very slow
```bash
huggingface-cli login
# Or: export HF_TOKEN=<your-hugging-face-token>
```

### Out of memory
Use smaller models (Qwen3 0.6B, Kokoro 82M), quantized variants (4bit/6bit), or close other applications.

### Audio sounds robotic or choppy
Keep text segments to 1-3 sentences. Use punctuation for pacing. Try larger models for better quality.

### Voice cloning sounds off
Use clean reference audio (5+ seconds, single speaker, no background noise). For Qwen3-TTS, provide accurate `ref_text`.

### ffmpeg errors
```bash
which ffmpeg && ffmpeg -version
# If not installed: brew install ffmpeg
```

## Alternative: Project venv

If you prefer a traditional virtual environment:

```bash
mkdir -p ~/my-tts-project && cd ~/my-tts-project
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install mlx-audio
```

**Note**: The venv approach is not recommended for skill-generated scripts. Use `uv run` for scripts generated by this skill.

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
