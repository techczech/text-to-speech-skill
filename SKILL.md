---
name: text-to-speech
description: "Generate speech audio locally."
---

# Text-to-Speech & Music Generation (Local Audio on Apple Silicon)

Generate high-quality speech and music locally on Apple Silicon. No cloud APIs required.

## Prerequisites

Scripts use `uv run` with inline dependencies (PEP 723) — no venv needed.
Ensure `uv` and `ffmpeg` are installed: `which uv && which ffmpeg`
If ffmpeg is missing: `brew install ffmpeg`
Models cache in `~/local-models` (via `HF_HUB_CACHE` in `.zshrc`).

**Pre-flight** — check cached models before generating (avoids multi-GB downloads):
```bash
ls ~/local-models/ | grep -iE "(Qwen3-TTS|chatterbox|Dia-|Kokoro|csm)"
```
Prefer a model already cached. Do NOT create local venvs or pip install into global Python.

## Quick Start

```bash
uv run --python 3.12 --with "mlx-audio>=0.3" --prerelease=allow \
  python -m mlx_audio.tts.generate \
    --model mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16 \
    --text "Hello! Local TTS on Apple Silicon." --play
```

First run downloads the model (~1.2GB). Subsequent runs load from cache in seconds.

## Generated Script Template

All scripts this skill generates MUST include this PEP 723 inline metadata header:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["mlx-audio>=0.3", "soundfile", "numpy"]
#
# [tool.uv]
# prerelease = "allow"
# ///
```

The `prerelease = "allow"` is required because mlx-audio 0.3+ depends on `transformers>=5.0.0rc3`.

**Rules for generated scripts:**
- Do NOT create local venvs or `pip install` into global Python
- Do NOT `import mlx.core as mx` unless explicitly needed for array operations
- Run all scripts with `uv run --python 3.12 script.py`
- Default model: `mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16` (Qwen3-TTS)
- Default speaker: `Ryan` (English, male, neutral American)
- For multi-segment audio (podcasts, paper narrations), add `mutagen` to dependencies and include MP3 chapter markers

### MP3 Chapter Markers

For narrations and podcasts with logical sections, add ID3v2 chapter markers so listeners can navigate in podcast apps. Add `"mutagen"` to the PEP 723 dependencies and a `"chapter"` field to segments that start a new chapter:

```python
SEGMENTS = [
    {"chapter": "Introduction", "text": "...", "instruct": "..."},
    {"text": "...", "instruct": "..."},  # continues same chapter
    {"chapter": "Methods", "text": "...", "instruct": "..."},  # new chapter
]
```

Track `cursor_ms` during generation (cumulative sample count / sample_rate * 1000) and write CHAP/CTOC frames after ffmpeg MP3 conversion. See `scripts/generate_podcast.py` for a complete working example.

## Engine Selection

| Engine | Model | Best For | Speed | Cloning | Languages | SR |
|--------|-------|----------|-------|---------|-----------|-----|
| **Qwen3-TTS** | `Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16` | **Default.** Podcasts, narration, emotion control, voice design | ~2-3x RT | Yes (Base) | 10 | 24kHz |
| **Chatterbox Turbo** | `chatterbox-turbo-fp16` | Easiest voice cloning, streaming | ~2x RT | Yes (ref_audio) | 14+ | 24kHz |
| **Dia** | `Dia-1.6B-fp16` | Multi-speaker dialogue, nonverbal sounds | ~1-2x RT | Yes | English | 44.1kHz |
| **Czech TTS** | `~/x-experiments/chatterbox/` | Czech speech with voice cloning (PyTorch, CPU) | ~0.1x RT | Yes | Czech | 24kHz |
| **ACE-Step 1.5** | `~/x-experiments/ace-step/` | Music generation from text + lyrics (MLX) | ~3x RT | N/A | 50+ | — |

All `mlx-community/` model IDs above are prefixed with `mlx-community/` when loading.

**When to use which:**
- **Qwen3-TTS** — Default choice. Best for podcasts, narration, paper reading, emotion control, multi-language, voice design
- **Chatterbox Turbo** — Voice cloning without transcript, streaming output, or when Qwen3-TTS isn't cached
- **Dia** — Two-speaker conversations with `[S1]`/`[S2]` tags and nonverbal sounds like `(laughs)`
- **Czech TTS** — Czech language speech synthesis with voice cloning
- **ACE-Step** — Songs and instrumental music from text descriptions and lyrics

## Qwen3-TTS

```python
model = load_model("mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16")
results = list(model.generate_custom_voice(
    text="Your text.", speaker="Ryan", language="English",
    instruct="Warm, professional narration voice.",
))
```

Built-in speakers: Ryan, Aiden (English), Vivian, Serena, Uncle_Fu, Dylan, Eric (Chinese), Ono_Anna (Japanese), Sohee (Korean).

Modes: CustomVoice (default), CustomVoice HQ (1.7B), Base (voice cloning), VoiceDesign (create voice from description).

See `references/qwen3-tts.md` for speakers, emotion control, voice design, and podcast patterns.
See `scripts/generate_podcast.py` for a complete podcast example with chapter markers.

## Chatterbox Turbo

```python
model = load_model("mlx-community/chatterbox-turbo-fp16")
results = list(model.generate(text="Your text.", ref_audio="ref.wav"))
```

Easiest voice cloning — just `ref_audio`, no transcript needed. Supports streaming with `stream=True`.

See `references/chatterbox.md` for streaming, emotion control (non-turbo), and cloning details.
See `scripts/generate_chatterbox.py` for a complete working example.

## Dia

```python
model = load_model("mlx-community/Dia-1.6B-fp16")
results = list(model.generate(
    text="[S1] Hello! [S2] Hi there! (laughs) Great to see you.",
    temperature=1.3, top_p=0.95,
))
```

Two speakers via `[S1]`/`[S2]` tags. Nonverbal sounds in parentheses. English only, 44.1 kHz output.

See `references/dia.md` for dialogue format, speaker tags, and voice cloning with Dia.
See `scripts/generate_dia.py` for a complete multi-speaker dialogue example.

## Voice Cloning

Three engines support voice cloning: Chatterbox Turbo (easiest, no transcript), Qwen3-TTS Base (best quality, needs transcript), Dia (cloned voice in dialogue). Qwen3-TTS VoiceDesign creates voices from text descriptions without audio.

See `references/voice-cloning.md` for cross-engine comparison and requirements.

## Paper Reading Modes

Two paper-specific TTS modes for academic papers: **paper-read** (verbatim audiobook style) and **paper-narrate** (guided narration with commentary). Both use Qwen3-TTS with chapter markers.

See `references/paper-reading.md` for the full workflow, segment types, and instruct values.

## Czech TTS

Czech speech via Chatterbox Multilingual + Czech T3 fine-tune (PyTorch, CPU only, ~1-2 min/sentence).

See `references/czech-tts.md` for setup and usage.

## ACE-Step Music Generation

Generate songs and instrumentals from text descriptions + lyrics via MLX (TOML config → `cli.py`).

See `references/ace-step.md` for setup, parameters, and caption/lyrics guides.

## More Models in mlx-audio

mlx-audio v0.3+ ships 16 TTS model backends. The three featured engines above cover most use cases. Other notable models: Spark (pitch/speed control), Sesame CSM-1B (conversational), Kokoro (fastest at 82M), OuteTTS (auto speaker profile), IndexTTS, Llama/Orpheus (LLM-based), Soprano (ultra-fast). All use the same `load_model()` → `generate()` → `GenerationResult` pattern.

## Output Formats

- **WAV**: 24kHz or 44.1kHz mono (via soundfile)
- **MP3**: Variable bitrate via ffmpeg (`-qscale:a 2` ~ 190kbps)
- **Other**: Use ffmpeg to convert to any format (OGG, AAC, FLAC, etc.)

## Troubleshooting

- **Requires macOS 15+** on Apple Silicon (M1/M2/M3/M4)
- **ffmpeg needed** for MP3: `brew install ffmpeg`
- **Chatterbox/Dia not found**: Ensure mlx-audio v0.3+ (use `uv run --with "mlx-audio>=0.3"`)
- **Anaconda conflicts**: Anaconda pins numpy <2 and old pandas/sklearn that conflict with mlx-audio. Use `uv run` instead of conda/pip
- **Slow first load**: Model downloads can be large (1-3GB). Set `HF_TOKEN` for faster HuggingFace access
- **Out of memory**: Use smaller models (Qwen3 0.6B, Kokoro 82M); close other apps
- **Audio quality**: Use larger models; keep segments short (1-3 sentences); use punctuation for pacing
- **Chatterbox exaggeration ignored**: Turbo ignores `exaggeration`/`cfg_weight`. Use non-turbo `chatterbox-fp16`
- **Dia only English**: Use Qwen3-TTS for other languages
- **Voice cloning sounds off**: Clean reference audio (5+ sec), single speaker, no background noise
- **Czech TTS**: See `references/czech-tts.md` for troubleshooting `language_id` and onnx errors
- **ACE-Step**: See `references/ace-step.md` for download stalls and `thinking=true` slowness

## Related Skills

- **speech-to-text**: Companion skill for transcription (STT) using mlx-audio
