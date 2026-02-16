---
name: text-to-speech
description: |
  Generate speech audio from text using Qwen3-TTS on Apple Silicon via MLX. Creates podcast episodes, narrations, and audio files locally without cloud APIs.

  TRIGGERS: Use when:
  - User asks to generate audio, speech, or a podcast from text
  - User wants to convert text to spoken audio (TTS)
  - User asks to create a voiceover, narration, or audio file from written content
  - User asks to make a podcast episode from a script or topic
  - User mentions Qwen3-TTS, mlx-audio, or local text-to-speech
  - Companion skill to speech-to-text (STT)
---

# Text-to-Speech (Qwen3-TTS on MLX)

Generate high-quality speech audio from text locally on Apple Silicon using Qwen3-TTS via mlx-audio. No cloud APIs required. Supports single-clip narration and multi-segment podcast generation.

## Prerequisites

Ensure the environment is set up. The working directory can be any project folder — just create a venv with mlx-audio:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install mlx-audio
```

Also ensure ffmpeg is installed for MP3 conversion: `brew install ffmpeg`

A reference setup with a working podcast generator lives at `~/gitrepos/x-experiments/podcast-test/`.

## Workflow

### 1. Choose a Generation Mode

| Mode | Model | When to Use |
|------|-------|-------------|
| **CustomVoice** | `Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16` | Quick generation with built-in speakers + emotion control. **Default choice.** |
| **CustomVoice (HQ)** | `Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16` | Higher quality, same speakers, slower |
| **Voice Cloning** | `Qwen3-TTS-12Hz-0.6B-Base-bf16` or `1.7B` | Clone a voice from a 3+ second audio sample |
| **Voice Design** | `Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16` | Create any voice from a natural language description |

All model IDs are prefixed with `mlx-community/`.

### 2. Select a Speaker (CustomVoice mode)

| Speaker | Language | Notes |
|---------|----------|-------|
| `Ryan` | English | Male, neutral American |
| `Aiden` | English | Male, alternative |
| `Vivian` | Chinese | Female |
| `Serena` | Chinese | Female |
| `Uncle_Fu` | Chinese | Male |
| `Dylan` | Chinese (Beijing) | Male, dialectal |
| `Eric` | Chinese (Sichuan) | Male, dialectal |
| `Ono_Anna` | Japanese | Female |
| `Sohee` | Korean | Female |

### 3. Generate a Single Audio Clip

Write a Python script. The core pattern:

```python
#!/usr/bin/env python3
import subprocess
import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

# Load model (cached after first download)
model = load_model("mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16")

# Generate speech
results = list(model.generate_custom_voice(
    text="Your text here. Keep segments to 1-3 sentences for best quality.",
    speaker="Ryan",
    language="English",
    instruct="Warm, professional narration voice.",
))

# Save audio
audio = np.array(results[0].audio, dtype=np.float32)
sample_rate = results[0].sample_rate  # 24000 Hz
sf.write("output.wav", audio, sample_rate)

# Convert to MP3
subprocess.run(["ffmpeg", "-y", "-i", "output.wav",
                 "-codec:a", "libmp3lame", "-qscale:a", "2",
                 "output.mp3"], check=True, capture_output=True)
```

### 4. Generate a Podcast Episode

For podcast-style content, split the script into segments with different emotional directions and concatenate with pauses between them. Use the template script at `references/generate_podcast.py` or follow this pattern:

```python
#!/usr/bin/env python3
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

MODEL_ID = "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Define podcast segments — each with its own emotional direction
PODCAST_SEGMENTS = [
    {
        "text": "Welcome to the show! Today we have a great topic for you.",
        "speaker": "Ryan",
        "instruct": "Professional, warm, and enthusiastic podcast host voice.",
    },
    {
        "text": "Our main topic is about the latest developments in AI.",
        "speaker": "Ryan",
        "instruct": "Engaged and informative, building excitement.",
    },
    {
        "text": "Thanks for listening! See you next time.",
        "speaker": "Ryan",
        "instruct": "Warm and upbeat closing, friendly farewell.",
    },
]

def generate_podcast():
    print(f"Loading model: {MODEL_ID}")
    model = load_model(MODEL_ID)

    all_audio = []
    sample_rate = None

    for i, segment in enumerate(PODCAST_SEGMENTS):
        print(f"Generating segment {i + 1}/{len(PODCAST_SEGMENTS)}...")
        results = list(model.generate_custom_voice(
            text=segment["text"],
            speaker=segment["speaker"],
            language="English",
            instruct=segment["instruct"],
        ))

        if results:
            audio_np = np.array(results[0].audio, dtype=np.float32)
            if sample_rate is None:
                sample_rate = getattr(results[0], "sample_rate", 24000)
            all_audio.append(audio_np)
            # 0.5s pause between segments
            all_audio.append(np.zeros(int(sample_rate * 0.5), dtype=np.float32))

    full_audio = np.concatenate(all_audio)
    wav_path = OUTPUT_DIR / "podcast_episode.wav"
    sf.write(str(wav_path), full_audio, sample_rate)
    print(f"Saved WAV: {wav_path} ({len(full_audio) / sample_rate:.1f}s)")

    # Convert to MP3
    mp3_path = OUTPUT_DIR / "podcast_episode.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav_path),
         "-codec:a", "libmp3lame", "-qscale:a", "2", str(mp3_path)],
        check=True, capture_output=True,
    )
    print(f"Saved MP3: {mp3_path}")

if __name__ == "__main__":
    generate_podcast()
```

**Podcast generation tips:**
- Split content into 1-3 sentence segments for natural delivery
- Vary the `instruct` parameter between segments for dynamic prosody
- Use 0.3-0.8s pauses between segments (adjust silence duration)
- For multi-speaker podcasts, alternate `speaker` between `Ryan` and `Aiden`
- Consider the 1.7B model for final/published quality

### 5. Voice Cloning Pattern

```python
model = load_model("mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16")
results = list(model.generate(
    text="New text in cloned voice.",
    ref_audio="reference_3sec.wav",
    ref_text="Transcript of the reference audio.",
))
```

### 6. Voice Design Pattern

```python
model = load_model("mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16")
results = list(model.generate_voice_design(
    text="Content to speak.",
    language="English",
    instruct="A deep, authoritative male voice with a slight British accent.",
))
```

## Emotion/Style Instructions

The `instruct` parameter controls prosody, emotion, and delivery style. Examples:

| Instruction | Effect |
|-------------|--------|
| `"Professional, warm, and enthusiastic podcast host voice."` | Upbeat narration |
| `"Calm, measured, academic lecture tone."` | Formal presentation |
| `"Excited and energetic, building to a crescendo."` | Dynamic delivery |
| `"Soft, intimate whisper. ASMR-like."` | Quiet, close mic feel |
| `"News anchor delivery. Authoritative and clear."` | Broadcast style |
| `"Thoughtful and reflective, with deliberate pacing."` | Slow, contemplative |

## Output Formats

- **WAV**: 24kHz mono, 16-bit PCM (via soundfile)
- **MP3**: Variable bitrate via ffmpeg (`-qscale:a 2` ~ 190kbps)
- **Other**: Use ffmpeg to convert to any format (OGG, AAC, FLAC, etc.)

## Performance Notes

| Model | Speed (M4 Max) | Notes |
|-------|-----------------|-------|
| 0.6B CustomVoice | ~2-3x realtime | 6-9s for 12-21s audio |
| 1.7B CustomVoice | ~1-1.5x realtime | Higher quality |
| 0.6B Base (4bit) | ~3-4x realtime | Fastest, needs ref audio |

First model load downloads from HuggingFace (~1.2GB for 0.6B, ~3.4GB for 1.7B). Subsequent loads use cache at `~/.cache/huggingface/hub/`.

## Supported Languages

Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian.

## Troubleshooting

- **Requires macOS 15+** on Apple Silicon (M1/M2/M3/M4)
- **ffmpeg needed** for MP3: `brew install ffmpeg`
- **Slow first load**: Model downloads ~1.2GB. Set `HF_TOKEN` for faster HuggingFace access
- **Out of memory**: Use 0.6B or quantized models; close other apps
- **Audio quality**: Use 1.7B models; keep segments short (1-3 sentences); use punctuation for pacing

## Related Skills

- **speech-to-text**: Companion skill for transcription (STT) using mlx-audio
