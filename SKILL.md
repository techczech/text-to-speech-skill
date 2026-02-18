---
name: text-to-speech
description: |
  Generate speech audio from text locally on Apple Silicon via MLX. Supports multiple TTS engines: Qwen3-TTS (emotion control, voice cloning, 10 languages), Chatterbox Turbo (streaming, easy voice cloning), and Dia (multi-speaker dialogue). Also supports Czech TTS via Chatterbox Multilingual and music generation via ACE-Step 1.5. Creates podcast episodes, narrations, songs, and audio files without cloud APIs.

  TRIGGERS: Use when:
  - User asks to generate audio, speech, or a podcast from text
  - User wants to convert text to spoken audio (TTS)
  - User asks to create a voiceover, narration, or audio file from written content
  - User asks to make a podcast episode from a script or topic
  - User wants to clone a voice or create a custom voice
  - User wants multi-speaker dialogue audio (use Dia)
  - User wants streaming TTS generation (use Chatterbox Turbo)
  - User wants Czech TTS or speech in Czech (use Chatterbox Multilingual)
  - User wants to generate music, a song, or instrumental audio (use ACE-Step)
  - User mentions Qwen3-TTS, Chatterbox, Dia, ACE-Step, mlx-audio, or local text-to-speech
  - Companion skill to speech-to-text (STT)
---

# Text-to-Speech & Music Generation (Local Audio on Apple Silicon)

Generate high-quality speech and music locally on Apple Silicon. TTS engines via mlx-audio: Qwen3-TTS (emotion control, voice design), Chatterbox Turbo (easy voice cloning, streaming), Dia (multi-speaker dialogue). Czech TTS via Chatterbox Multilingual fine-tune. Music generation via ACE-Step 1.5. No cloud APIs required.

## Prerequisites

Ensure the environment is set up. The working directory can be any project folder — just create a venv with mlx-audio:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install mlx-audio
```

**Requires mlx-audio 0.3+** for Chatterbox Turbo and Dia support. Upgrade with `pip install -U mlx-audio`.

Also ensure ffmpeg is installed for MP3 conversion: `brew install ffmpeg`

Models are stored in `~/local-models` (set via `HF_HUB_CACHE` in `.zshrc`, symlinked from `~/.cache/huggingface/hub`). This is shared with the speech-to-text skill and all other HuggingFace-based tools.

A reference setup with a working podcast generator lives at `~/gitrepos/x-experiments/podcast-test/`.

## Quick Start

Generate speech with Chatterbox Turbo — one command, no configuration:

```bash
python -m mlx_audio.tts.generate \
    --model mlx-community/chatterbox-turbo-fp16 \
    --text "Hello! This is a quick test of local text to speech on Apple Silicon." \
    --play
```

Or in Python:

```python
from mlx_audio.tts.utils import load_model
import numpy as np, soundfile as sf

model = load_model("mlx-community/chatterbox-turbo-fp16")
results = list(model.generate(text="Hello! Local TTS on Apple Silicon."))
audio = np.array(results[0].audio, dtype=np.float32)
sf.write("output.wav", audio, results[0].sample_rate)
```

First run downloads the model (~3GB). Subsequent runs load from cache in seconds.

## Workflow

### 1. Choose a TTS Engine

| Engine | Model / Location | Best For | Voice Cloning | Languages |
|--------|-----------------|----------|:---:|-----------|
| **Qwen3-TTS** | `mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16` | Emotion control, built-in speakers, podcasts. **Default.** | Yes (with Base model) | 10 |
| **Chatterbox Turbo** | `mlx-community/chatterbox-turbo-fp16` | Easiest voice cloning, streaming, production quality | Yes (ref_audio only) | 14+ |
| **Dia** | `mlx-community/Dia-1.6B-fp16` | Multi-speaker dialogue, nonverbal sounds | Yes | English |
| **Czech TTS** | `~/gitrepos/x-experiments/chatterbox/` | Czech speech with voice cloning (PyTorch, CPU) | Yes | Czech |
| **ACE-Step 1.5** | `~/gitrepos/x-experiments/ace-step/` | Music generation from text + lyrics (MLX) | N/A | 50+ |

**When to use which:**
- **Qwen3-TTS** — Best for podcasts, narration with emotion control, multi-language content, or voice design from text description
- **Chatterbox Turbo** — Best for voice cloning (no transcript needed), streaming output, or quick high-quality generation
- **Dia** — Best for two-speaker conversations, dialogue with `[S1]`/`[S2]` speaker tags, and nonverbal sounds like `(laughs)`
- **Czech TTS** — For Czech language speech synthesis with voice cloning (Chatterbox Multilingual + Czech T3 fine-tune)
- **ACE-Step** — For generating songs and instrumental music from text descriptions and lyrics

### 2. Generation with Qwen3-TTS

Qwen3-TTS offers the richest feature set: built-in speakers with emotion control, voice cloning, and voice design from text descriptions.

#### Choose a Qwen3-TTS Mode

| Mode | Model | When to Use |
|------|-------|-------------|
| **CustomVoice** | `Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16` | Quick generation with built-in speakers + emotion control. **Default choice.** |
| **CustomVoice (HQ)** | `Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16` | Higher quality, same speakers, slower |
| **Voice Cloning** | `Qwen3-TTS-12Hz-0.6B-Base-bf16` or `1.7B` | Clone a voice from a 3+ second audio sample |
| **Voice Design** | `Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16` | Create any voice from a natural language description |

#### Built-in Speakers (CustomVoice mode)

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

#### Single Audio Clip

```python
#!/usr/bin/env python3
import subprocess
import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

model = load_model("mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16")

results = list(model.generate_custom_voice(
    text="Your text here. Keep segments to 1-3 sentences for best quality.",
    speaker="Ryan",
    language="English",
    instruct="Warm, professional narration voice.",
))

audio = np.array(results[0].audio, dtype=np.float32)
sample_rate = results[0].sample_rate  # 24000 Hz
sf.write("output.wav", audio, sample_rate)

subprocess.run(["ffmpeg", "-y", "-i", "output.wav",
                 "-codec:a", "libmp3lame", "-qscale:a", "2",
                 "output.mp3"], check=True, capture_output=True)
```

#### Podcast Episode

For podcast-style content, split the script into segments with different emotional directions and concatenate with pauses. Use the template script at `references/generate_podcast.py` or follow this pattern:

```python
PODCAST_SEGMENTS = [
    {
        "text": "Welcome to the show! Today we have a great topic.",
        "speaker": "Ryan",
        "instruct": "Professional, warm, enthusiastic podcast host voice.",
    },
    {
        "text": "Our main topic is about the latest developments in AI.",
        "speaker": "Ryan",
        "instruct": "Engaged and informative, building excitement.",
    },
]

model = load_model("mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16")
all_audio = []
for segment in PODCAST_SEGMENTS:
    results = list(model.generate_custom_voice(
        text=segment["text"], speaker=segment["speaker"],
        language="English", instruct=segment["instruct"],
    ))
    audio_np = np.array(results[0].audio, dtype=np.float32)
    sample_rate = results[0].sample_rate
    all_audio.append(audio_np)
    all_audio.append(np.zeros(int(sample_rate * 0.5), dtype=np.float32))  # pause

full_audio = np.concatenate(all_audio)
sf.write("podcast.wav", full_audio, sample_rate)
```

**Podcast tips:** Keep segments to 1-3 sentences. Vary `instruct` for dynamic prosody. Use 0.3-0.8s pauses. For multi-speaker podcasts, alternate `speaker` between `Ryan` and `Aiden`. Use the 1.7B model for published quality.

#### Emotion/Style Instructions

The `instruct` parameter controls prosody, emotion, and delivery style:

| Instruction | Effect |
|-------------|--------|
| `"Professional, warm, and enthusiastic podcast host voice."` | Upbeat narration |
| `"Calm, measured, academic lecture tone."` | Formal presentation |
| `"Excited and energetic, building to a crescendo."` | Dynamic delivery |
| `"Soft, intimate whisper. ASMR-like."` | Quiet, close mic feel |
| `"News anchor delivery. Authoritative and clear."` | Broadcast style |

#### Voice Design (No Audio Needed)

Create any voice from a natural language description — no reference audio required:

```python
model = load_model("mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16")
results = list(model.generate_voice_design(
    text="Content to speak.",
    language="English",
    instruct="A deep, authoritative male voice with a slight British accent.",
))
```

### 3. Generation with Chatterbox Turbo

Chatterbox Turbo from Resemble AI offers high-quality speech with easy voice cloning (no transcript needed) and streaming support.

#### Basic Generation

```python
from mlx_audio.tts.utils import load_model
import numpy as np, soundfile as sf

model = load_model("mlx-community/chatterbox-turbo-fp16")
results = list(model.generate(text="Your text here. Chatterbox produces natural speech."))
audio = np.array(results[0].audio, dtype=np.float32)
sf.write("output.wav", audio, results[0].sample_rate)
```

CLI:
```bash
python -m mlx_audio.tts.generate \
    --model mlx-community/chatterbox-turbo-fp16 \
    --text "Hello, this is Chatterbox Turbo."
```

#### Voice Cloning (Easiest Method)

Chatterbox clones a voice from just a reference audio file — no transcript required:

```python
model = load_model("mlx-community/chatterbox-turbo-fp16")
results = list(model.generate(
    text="New text in the cloned voice.",
    ref_audio="reference_voice.wav",  # 5+ seconds recommended
))
audio = np.array(results[0].audio, dtype=np.float32)
sf.write("cloned_output.wav", audio, results[0].sample_rate)
```

CLI:
```bash
python -m mlx_audio.tts.generate \
    --model mlx-community/chatterbox-turbo-fp16 \
    --text "Text in cloned voice." \
    --ref_audio reference_voice.wav
```

#### Streaming Mode

Generate audio in chunks for real-time playback:

```python
model = load_model("mlx-community/chatterbox-turbo-fp16")
for chunk in model.generate(
    text="This text will stream out in chunks as it generates.",
    stream=True,
    streaming_interval=2.0,  # seconds between chunks
):
    # chunk.audio contains the audio data
    # chunk.is_streaming_chunk is True for intermediate chunks
    # chunk.is_final_chunk is True for the last chunk
    process_audio(chunk.audio, chunk.sample_rate)
```

#### Chatterbox (Non-Turbo) for Emotion Control

The non-turbo variant supports emotion `exaggeration` control (Turbo ignores this parameter):

```python
model = load_model("mlx-community/chatterbox-fp16")
results = list(model.generate(
    text="This is very exciting news!",
    ref_audio="reference_voice.wav",
    exaggeration=0.7,  # 0.0 = flat, 1.0 = very expressive
    cfg_weight=0.5,    # classifier-free guidance strength
))
```

### 4. Generation with Dia

Dia from Nari Labs generates multi-speaker dialogue in a single pass using `[S1]` and `[S2]` speaker tags. Unique for creating conversations and includes nonverbal sounds.

#### Multi-Speaker Dialogue

```python
from mlx_audio.tts.utils import load_model
import numpy as np, soundfile as sf

model = load_model("mlx-community/Dia-1.6B-fp16")

dialogue = """[S1] Good morning! How are you today?
[S2] I'm doing great, thanks for asking. Did you see the news?
[S1] Yes! It's incredible. (laughs) I couldn't believe it.
[S2] I know, right? Let me tell you what I think about it."""

results = list(model.generate(text=dialogue, temperature=1.3, top_p=0.95))
audio = np.array(results[0].audio, dtype=np.float32)
sf.write("dialogue.wav", audio, results[0].sample_rate)  # 44100 Hz
```

CLI:
```bash
python -m mlx_audio.tts.generate \
    --model mlx-community/Dia-1.6B-fp16 \
    --text "[S1] Hello there! [S2] Hi! How can I help you today?"
```

**Dia notes:**
- Two speakers only: `[S1]` and `[S2]`
- Nonverbal sounds in parentheses: `(laughs)`, `(sighs)`, `(clears throat)`
- Output is 44100 Hz (higher than other engines)
- English only
- Split long dialogues on newlines (each line is a turn)

#### Voice Cloning with Dia

Clone a voice into dialogue:

```python
model = load_model("mlx-community/Dia-1.6B-fp16")
results = list(model.generate(
    text="[S1] This is the cloned voice speaking.",
    ref_audio="reference_voice.wav",
    ref_text="Transcript of the reference audio.",
))
```

### 5. Voice Cloning Guide

#### Which Engine to Use

| Scenario | Engine | What You Need |
|----------|--------|---------------|
| **Easiest cloning** (no transcript) | Chatterbox Turbo | ref_audio only (5+ sec) |
| **Highest fidelity** cloning | Qwen3-TTS Base | ref_audio (3+ sec) + ref_text |
| **Cloned voice in dialogue** | Dia | ref_audio + ref_text |
| **Create voice without audio** | Qwen3-TTS VoiceDesign | Text description only |

#### Reference Audio Requirements

| Requirement | Qwen3-TTS | Chatterbox | Dia |
|-------------|-----------|------------|-----|
| Minimum length | 3 seconds | 5 seconds | A few seconds |
| Ideal length | 5-15 seconds | 5-15 seconds | 5-15 seconds |
| Transcript needed | Yes (`ref_text`) | No | Optional (`ref_text`) |
| Format | WAV preferred | WAV, MP3, etc. | WAV preferred |
| Quality | Clean, single speaker | Clean, single speaker | Clean, single speaker |

**Tips for reference audio:** Use a clean recording with minimal background noise. A single speaker, no music. Consistent volume. The better the reference, the better the clone.

#### Auto-Transcription

When `ref_text` is not provided but required, the mlx-audio CLI auto-transcribes the reference audio using Whisper. This happens automatically — you don't need to transcribe manually. In Python API, provide `ref_text` explicitly for best results.

#### Cloning with Qwen3-TTS (Best Quality)

```python
model = load_model("mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16")
results = list(model.generate(
    text="New text in the cloned voice.",
    ref_audio="reference_3sec.wav",
    ref_text="Exact transcript of the reference audio.",
))
audio = np.array(results[0].audio, dtype=np.float32)
sf.write("cloned.wav", audio, results[0].sample_rate)
```

Use the 1.7B Base model for higher fidelity: `Qwen3-TTS-12Hz-1.7B-Base-bf16`.

#### Cloning with Chatterbox Turbo (Easiest)

```python
model = load_model("mlx-community/chatterbox-turbo-fp16")
results = list(model.generate(
    text="New text in the cloned voice.",
    ref_audio="reference_5sec.wav",  # no transcript needed
))
```

#### Voice Design Alternative (No Audio Needed)

Qwen3-TTS VoiceDesign creates a voice from a natural language description:

```python
model = load_model("mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16")
results = list(model.generate_voice_design(
    text="Content to speak.",
    language="English",
    instruct="A warm female voice, mid-30s, slight Irish accent, conversational tone.",
))
```

### 6. Czech TTS with Chatterbox Multilingual

Czech speech synthesis uses the PyTorch-based Chatterbox Multilingual model with a Czech T3 fine-tune from `Thomcles/Chatterbox-TTS-Czech`. This is **not** an mlx-audio model — it runs via PyTorch on CPU.

**Setup:** The project lives at `~/gitrepos/x-experiments/chatterbox/` (cloned from `resemble-ai/chatterbox`). The `mtl_tts.py` file has been patched to add Czech (`"cs"`) to `SUPPORTED_LANGUAGES` and to fix `map_location="cpu"` for Apple Silicon.

**Prerequisites:**
```bash
cd ~/gitrepos/x-experiments/chatterbox
uv sync  # installs PyTorch + dependencies
# Czech weights download automatically on first use via HF cache
huggingface-cli download Thomcles/Chatterbox-TTS-Czech
```

**Generation with voice cloning:**

```python
import sys, os
from pathlib import Path
from safetensors.torch import load_file as load_safetensors

os.environ["HF_HUB_CACHE"] = os.path.expanduser("~/local-models")
sys.path.insert(0, str(Path(__file__).parent / "src"))
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")

# Swap T3 weights for Czech fine-tune
czech_dir = os.path.expanduser("~/local-models/models--Thomcles--Chatterbox-TTS-Czech/snapshots/")
czech_t3_path = next(Path(czech_dir).iterdir()) / "t3_cs.safetensors"
t3_state = load_safetensors(str(czech_t3_path))
model.t3.load_state_dict(t3_state)
model.t3.to("cpu").eval()

wav = model.generate(
    text="Dobrý den, toto je ukázka syntézy řeči v češtině.",
    language_id="cs",
    audio_prompt_path="reference_voice.wav",  # voice to clone
    exaggeration=0.5,
    cfg_weight=0.5,
    temperature=0.8,
)

import torchaudio, subprocess
torchaudio.save("output.wav", wav, model.sr)
subprocess.run(["ffmpeg", "-y", "-i", "output.wav", "-b:a", "192k", "output.mp3"])
```

**Czech TTS notes:**
- Runs on **CPU only** (PyTorch, not MLX) — generation takes ~1-2 minutes for a sentence
- Voice cloning via `audio_prompt_path` — use a clean 5-15 second reference clip
- The Czech fine-tune modifies only the T3 (text-to-token) component; S3Gen vocoder is shared
- Reference script: `~/gitrepos/x-experiments/chatterbox/test_czech.py`
- Quality is reasonable but not as polished as the English Chatterbox models

### 7. Music Generation with ACE-Step 1.5

ACE-Step 1.5 generates music (vocals + instruments) from text descriptions and lyrics. It runs natively on Apple Silicon via MLX with the turbo DiT model. This is a **separate project** from mlx-audio.

**Setup:** The project lives at `~/gitrepos/x-experiments/ace-step/`.

**Prerequisites:**
```bash
cd ~/gitrepos/x-experiments/ace-step
uv sync  # installs dependencies
# Models download on first run to checkpoints/ (~10GB total)
```

#### Quick Start — TOML Config

Create a `song.toml` file:

```toml
caption = "acoustic folk guitar, warm male vocal, gentle fingerpicking, folk ballad, 100 BPM"
lyrics = """[Verse]
Walking down the old dirt road
Carrying my heavy load
Stars are shining up above
Guiding me to those I love

[Chorus]
Home is where the heart will be
Calling out to you and me
"""
duration = 30
instrumental = false
vocal_language = "en"
task_type = "text2music"
inference_steps = 8
batch_size = 1
seed = 42
thinking = false
audio_format = "mp3"
save_dir = "output"
```

Generate:
```bash
cd ~/gitrepos/x-experiments/ace-step
HF_HUB_CACHE=~/local-models uv run python cli.py -c song.toml
```

Output appears in `output/` as `{uuid}.mp3`.

#### Key Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `caption` | Free text | Style description: genre, instruments, mood, BPM |
| `lyrics` | Text with `[Verse]`/`[Chorus]` tags | Song lyrics (use `[Instrumental]` for no vocals) |
| `duration` | 10-600 | Length in seconds |
| `instrumental` | true/false | Force instrumental (no vocals) |
| `vocal_language` | `en`, `zh`, `ja`, `ko`, `cs`, `de`, `fr`, `es`, etc. | 50+ language codes |
| `task_type` | `text2music`, `cover`, `repaint` | Generation mode |
| `inference_steps` | 8 (turbo) | Diffusion steps |
| `thinking` | true/false | Enable LLM chain-of-thought for metadata/lyrics enhancement |
| `seed` | integer or -1 | Random seed (-1 for random) |
| `audio_format` | `mp3`, `flac`, `wav`, `opus`, `aac` | Output format |
| `batch_size` | 1+ | Number of variations to generate |

#### Caption Style Guide

The caption describes the musical style. Include genre, instruments, mood, tempo:

```
"acoustic folk guitar, warm male vocal, gentle fingerpicking, folk ballad, 100 BPM"
"electronic dance music, synth leads, heavy bass, energetic, 128 BPM"
"jazz piano trio, upright bass, brushed drums, smooth, 90 BPM"
"orchestral film score, strings, brass, epic cinematic, 80 BPM"
"lo-fi hip hop beat, vinyl crackle, mellow keys, chill, 85 BPM"
```

#### Lyrics Format

Use section tags: `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]`, `[Instrumental]`.

```
[Verse]
First verse lyrics here
Each line is a phrase

[Chorus]
Catchy chorus lyrics
Repeated section

[Bridge]
Contrasting section

[Outro]
Ending lyrics here
```

For instrumental tracks, set `instrumental = true` or use `lyrics = "[Instrumental]"`.

#### Performance

On M4 Max: **~11 seconds** for a 30-second song (8 inference steps, turbo model). DiT diffusion runs at ~7-8 it/s on MLX. This is roughly **3x real-time** generation speed.

Models stored in `~/gitrepos/x-experiments/ace-step/checkpoints/` (~10GB total):
- `acestep-v15-turbo/` — DiT diffusion model (4.8GB)
- `acestep-5Hz-lm-1.7B/` — LM for chain-of-thought (3.7GB, used when `thinking=true`)
- `Qwen3-Embedding-0.6B/` — Text encoder (1.1GB)
- `vae/` — Audio VAE decoder (322MB)

### 8. More Models in mlx-audio

mlx-audio v0.3+ ships 16 TTS model backends. The three featured engines above cover most use cases. Here is a reference table of all available models:

| Model | Voice Cloning | Key Feature | Approx Size |
|-------|:---:|-------------|-------------|
| **Qwen3-TTS** | Yes | Emotion control, voice design, 10 languages | 0.6B / 1.7B |
| **Chatterbox Turbo** | Yes | Streaming, easy cloning | ~350M |
| **Chatterbox** | Yes | Emotion exaggeration control | ~300M |
| **Dia** | Yes | Multi-speaker dialogue `[S1]`/`[S2]` | ~1.6B |
| **Spark** | Yes | Gender/pitch/speed control | ~0.5B |
| **Sesame (CSM-1B)** | Yes | Conversational speech | ~1B |
| **Kokoro** | No (54+ presets) | Fastest generation (82M) | 82M |
| **OuteTTS** | Yes | Auto speaker profile via Whisper | ~500M |
| **IndexTTS** | Yes | Always uses reference voice | Variable |
| **Pocket TTS** | Yes | Compact model | Variable |
| **Llama (Orpheus)** | Yes | LLM-based TTS | Variable |
| **VoxCPM** | Yes | Accent/rhythm capture | Variable |
| **Soprano** | No | Ultra-fast base generation | ~80M |
| **Bark** | No (presets) | Older model | ~350M |
| **F5-TTS** | Yes | Flow matching TTS | Variable |
| **VibeVoice** | Check | Streaming variant | Variable |

All models use the same `load_model()` → `generate()` → `GenerationResult` pattern. Model type is auto-detected from the HuggingFace repo config.

## Model Comparison

| Feature | Qwen3-TTS 0.6B | Chatterbox Turbo | Dia 1.6B |
|---------|----------------|------------------|----------|
| **Download size** | ~1.2 GB | ~3.0 GB | ~3.2 GB |
| **Sample rate** | 24 kHz | 24 kHz | 44.1 kHz |
| **Speed (M4 Max)** | ~2-3x realtime | ~2x realtime | ~1-2x realtime |
| **Speakers** | 9 built-in | Clone any voice | 2 speakers per generation |
| **Voice cloning** | Yes (Base model) | Yes (easiest) | Yes |
| **Streaming** | No | Yes | No |
| **Emotion control** | Yes (`instruct`) | No (Turbo) / Yes (non-Turbo) | No |
| **Languages** | 10 | 14+ | English only |
| **Voice design** | Yes (VoiceDesign model) | No | No |

## Output Formats

- **WAV**: 24kHz or 44.1kHz mono (via soundfile)
- **MP3**: Variable bitrate via ffmpeg (`-qscale:a 2` ~ 190kbps)
- **Other**: Use ffmpeg to convert to any format (OGG, AAC, FLAC, etc.)

## Performance Notes

| Model | Speed (M4 Max) | Notes |
|-------|-----------------|-------|
| Qwen3-TTS 0.6B CustomVoice | ~2-3x realtime | 6-9s for 12-21s audio |
| Qwen3-TTS 1.7B CustomVoice | ~1-1.5x realtime | Higher quality |
| Qwen3-TTS 0.6B Base (4bit) | ~3-4x realtime | Fastest, needs ref audio |
| Chatterbox Turbo | ~2x realtime | Supports streaming |
| Chatterbox Multilingual (Czech) | ~0.1-0.2x realtime | CPU-only PyTorch, ~1-2 min per sentence |
| Dia 1.6B | ~1-2x realtime | Higher sample rate (44.1kHz) |
| ACE-Step 1.5 (music) | ~3x realtime | 11s for 30s song (MLX turbo) |

First model load downloads from HuggingFace. Subsequent loads use cache at `~/local-models`.

## Supported Languages

| Engine | Languages |
|--------|-----------|
| Qwen3-TTS | Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian |
| Chatterbox Turbo | English + 13 other languages |
| Chatterbox Multilingual (Czech) | Czech (via T3 fine-tune) + base multilingual languages |
| Dia | English only |
| ACE-Step (vocals) | 50+ languages (en, zh, ja, ko, cs, de, fr, es, and many more) |

## Troubleshooting

- **Requires macOS 15+** on Apple Silicon (M1/M2/M3/M4)
- **ffmpeg needed** for MP3: `brew install ffmpeg`
- **Chatterbox/Dia not found**: Upgrade mlx-audio: `pip install -U mlx-audio` (requires v0.3+)
- **Slow first load**: Model downloads can be large (1-3GB). Set `HF_TOKEN` for faster HuggingFace access
- **Out of memory**: Use smaller models (Qwen3 0.6B, Kokoro 82M); close other apps
- **Audio quality**: Use larger models; keep segments short (1-3 sentences); use punctuation for pacing
- **Chatterbox exaggeration ignored**: The Turbo variant ignores `exaggeration` and `cfg_weight`. Use the non-turbo `chatterbox-fp16` for emotion control
- **Dia only English**: Dia currently supports English only. Use Qwen3-TTS for other languages
- **Voice cloning sounds off**: Use clean reference audio (5+ sec), single speaker, no background noise
- **Czech TTS slow**: Chatterbox Multilingual runs on CPU (PyTorch, not MLX). Expect ~1-2 min per sentence
- **Czech `language_id` error**: Ensure `mtl_tts.py` has `"cs": "Czech"` in `SUPPORTED_LANGUAGES` dict
- **Czech onnx/ml_dtypes error**: Run `.venv/bin/pip install "onnx<1.17"` to downgrade onnx to a version compatible with the lockfile's ml_dtypes. Use `.venv/bin/python` directly instead of `uv run` (which re-syncs and restores the broken version)
- **ACE-Step model download stalls**: Use `curl -C - -L` to download individual model files to `checkpoints/` (see SETUP.md)
- **ACE-Step `thinking=true` slow**: Thinking mode loads the 3.7GB LM. Use `thinking=false` for faster generation without LLM reasoning

## Related Skills

- **speech-to-text**: Companion skill for transcription (STT) using mlx-audio
