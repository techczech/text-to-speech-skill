# Qwen3-TTS Reference

Qwen3-TTS from Alibaba offers the richest TTS feature set: built-in speakers with emotion control, voice cloning, and voice design from text descriptions. Default engine for podcasts, narration, and paper reading.

## Mode Selection

| Mode | Model | When to Use |
|------|-------|-------------|
| **CustomVoice** | `Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16` | Quick generation with built-in speakers + emotion control. **Default choice.** |
| **CustomVoice (HQ)** | `Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16` | Higher quality, same speakers, slower |
| **Voice Cloning** | `Qwen3-TTS-12Hz-0.6B-Base-bf16` or `1.7B` | Clone a voice from a 3+ second audio sample |
| **Voice Design** | `Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16` | Create any voice from a natural language description |

## Built-in Speakers (CustomVoice mode)

| Speaker | Language | Notes |
|---------|----------|-------|
| `Ryan` | English | Male, neutral American — **default** |
| `Aiden` | English | Male, alternative |
| `Vivian` | Chinese | Female |
| `Serena` | Chinese | Female |
| `Uncle_Fu` | Chinese | Male |
| `Dylan` | Chinese (Beijing) | Male, dialectal |
| `Eric` | Chinese (Sichuan) | Male, dialectal |
| `Ono_Anna` | Japanese | Female |
| `Sohee` | Korean | Female |

## Single Audio Clip

```python
from mlx_audio.tts.utils import load_model
import numpy as np, soundfile as sf

model = load_model("mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16")
results = list(model.generate_custom_voice(
    text="Your text here. Keep segments to 1-3 sentences for best quality.",
    speaker="Ryan", language="English",
    instruct="Warm, professional narration voice.",
))
audio = np.array(results[0].audio, dtype=np.float32)
sf.write("output.wav", audio, results[0].sample_rate)
```

## Podcast Segments with Chapter Markers

For podcast-style content, split the script into segments with different emotional directions and concatenate with pauses. Add `"chapter"` fields to mark navigable sections in the MP3:

```python
PODCAST_SEGMENTS = [
    {"chapter": "Introduction",
     "text": "Welcome to the show!",
     "speaker": "Ryan", "instruct": "Warm, enthusiastic podcast host."},
    {"text": "Continuing the intro...",
     "speaker": "Ryan", "instruct": "Engaged and informative."},
    {"chapter": "Main Topic",
     "text": "Our main topic today...",
     "speaker": "Ryan", "instruct": "Thoughtful and explanatory."},
]
```

Track `cursor_ms` during generation and write CHAP/CTOC ID3 frames after ffmpeg MP3 conversion. See `scripts/generate_podcast.py` for the complete working example with chapter markers.

**Tips:** Keep segments to 1-3 sentences. Vary `instruct` for dynamic prosody. Use 0.3-0.8s pauses. For multi-speaker podcasts, alternate between `Ryan` and `Aiden`.

## Emotion/Style Instructions

The `instruct` parameter controls prosody, emotion, and delivery style:

| Instruction | Effect |
|-------------|--------|
| `"Professional, warm, and enthusiastic podcast host voice."` | Upbeat narration |
| `"Calm, measured, academic lecture tone."` | Formal presentation |
| `"Excited and energetic, building to a crescendo."` | Dynamic delivery |
| `"Soft, intimate whisper. ASMR-like."` | Quiet, close mic feel |
| `"News anchor delivery. Authoritative and clear."` | Broadcast style |

## Voice Design (No Audio Needed)

Create any voice from a natural language description — no reference audio required:

```python
model = load_model("mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16")
results = list(model.generate_voice_design(
    text="Content to speak.",
    language="English",
    instruct="A deep, authoritative male voice with a slight British accent.",
))
```

## Languages

Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian (10 total).

## Performance

| Model | Speed (M4 Max) | Download |
|-------|-----------------|----------|
| 0.6B CustomVoice | ~2-3x realtime | ~1.2GB |
| 1.7B CustomVoice | ~1-1.5x realtime | ~3.4GB |
| 0.6B Base (4bit) | ~3-4x realtime | ~0.4GB |
| Sample rate | 24 kHz | |
