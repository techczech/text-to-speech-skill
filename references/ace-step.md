# ACE-Step 1.5 Music Generation

ACE-Step 1.5 generates music (vocals + instruments) from text descriptions and lyrics. Runs natively on Apple Silicon via MLX with the turbo DiT model. This is a **separate project** from mlx-audio.

## When to Use

When the user wants to generate songs, instrumental music, or audio from text descriptions and lyrics.

## Setup

The project lives at `~/gitrepos/x-experiments/ace-step/`.

```bash
cd ~/gitrepos/x-experiments/ace-step
uv sync  # installs dependencies
# Models download on first run to checkpoints/ (~10GB total)
```

## Quick Start — TOML Config

Create a `song.toml` file and run:

```toml
caption = "acoustic folk guitar, warm male vocal, gentle fingerpicking, folk ballad, 100 BPM"
lyrics = """[Verse]
Walking down the old dirt road
Carrying my heavy load

[Chorus]
Home is where the heart will be
Calling out to you and me
"""
duration = 30
instrumental = false
vocal_language = "en"
task_type = "text2music"
inference_steps = 8
seed = 42
audio_format = "mp3"
save_dir = "output"
```

```bash
cd ~/gitrepos/x-experiments/ace-step
HF_HUB_CACHE=~/local-models uv run python cli.py -c song.toml
```

Output appears in `output/` as `{uuid}.mp3`.

## Key Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `caption` | Free text | Style description: genre, instruments, mood, BPM |
| `lyrics` | Text with section tags | Song lyrics (`[Instrumental]` for no vocals) |
| `duration` | 10-600 | Length in seconds |
| `instrumental` | true/false | Force instrumental (no vocals) |
| `vocal_language` | `en`, `zh`, `ja`, `ko`, `cs`, `de`, `fr`, `es`, etc. | 50+ language codes |
| `task_type` | `text2music`, `cover`, `repaint` | Generation mode |
| `inference_steps` | 8 (turbo) | Diffusion steps |
| `thinking` | true/false | Enable LLM chain-of-thought for lyrics enhancement |
| `seed` | integer or -1 | Random seed (-1 for random) |
| `audio_format` | `mp3`, `flac`, `wav`, `opus`, `aac` | Output format |
| `batch_size` | 1+ | Number of variations to generate |

## Caption Style Guide

The caption describes the musical style. Include genre, instruments, mood, tempo:

```
"acoustic folk guitar, warm male vocal, gentle fingerpicking, folk ballad, 100 BPM"
"electronic dance music, synth leads, heavy bass, energetic, 128 BPM"
"jazz piano trio, upright bass, brushed drums, smooth, 90 BPM"
"orchestral film score, strings, brass, epic cinematic, 80 BPM"
"lo-fi hip hop beat, vinyl crackle, mellow keys, chill, 85 BPM"
```

## Lyrics Format

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

## Performance

On M4 Max: **~11 seconds** for a 30-second song (8 inference steps, turbo model). DiT diffusion runs at ~7-8 it/s. Roughly **3x real-time** generation speed.

Models stored in `~/gitrepos/x-experiments/ace-step/checkpoints/` (~10GB total):
- `acestep-v15-turbo/` — DiT diffusion model (4.8GB)
- `acestep-5Hz-lm-1.7B/` — LM for chain-of-thought (3.7GB, used when `thinking=true`)
- `Qwen3-Embedding-0.6B/` — Text encoder (1.1GB)
- `vae/` — Audio VAE decoder (322MB)

## Troubleshooting

- **Model download stalls**: Use `curl -C - -L` to download individual model files to `checkpoints/` (see SETUP.md)
- **`thinking=true` slow**: Thinking mode loads the 3.7GB LM. Use `thinking=false` for faster generation
