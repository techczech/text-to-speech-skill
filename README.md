# text-to-speech

A Claude Code skill that turns text into speech, narration, podcasts, two-speaker dialogue or music **locally** on Apple Silicon, with no cloud API. It covers Qwen3-TTS (default, 10 languages, emotion control), Chatterbox Turbo (streaming, easy voice cloning), Dia (English dialogue), Czech speech via Chatterbox Multilingual, and ACE-Step 1.5 for songs. It is for anyone who wants private, offline audio generation driven from Claude Code.

## Requirements

- Apple Silicon Mac (M1 or later) on macOS 15 or later (the skill's own troubleshooting note).
- `uv` (`brew install uv`) and `ffmpeg` (`brew install ffmpeg`). Scripts declare their dependencies inline (PEP 723), so no venv is needed.
- Disk: roughly 1 to 3 GB per model (for example Breeze TTS 2 is ~3 GB); ACE-Step needs ~10 GB of checkpoints.
- RAM: the 0.6B Qwen3-TTS and Kokoro models run in modest memory; use smaller models if you run out.
- A Hugging Face token is optional (`HF_TOKEN`) and only speeds up downloads.
- Models download on first use into the standard Hugging Face cache (`$HF_HUB_CACHE`, else `$HF_HOME/hub`, else `~/.cache/huggingface/hub`). Set `HF_HOME` to use another volume.

## Install

```bash
git clone https://github.com/techczech/text-to-speech-skill ~/.claude/skills/text-to-speech
```

There is nothing else to install: the first run of a script fetches Python dependencies through `uv` and the model from Hugging Face. Try it:

```bash
uv run --python 3.12 --with "mlx-audio>=0.3" --prerelease=allow \
  python -m mlx_audio.tts.generate \
    --model mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16 \
    --text "Hello! Local TTS on Apple Silicon." --play
```

Or ask Claude: "read this paper aloud", "make a two-person podcast from this script". Engine choice, setup and recipes are in `SKILL.md` and `references/`.

## Voice cloning and consent

Several engines here can clone a voice from a short recording. Use that only responsibly:

- Clone only voices you have permission to use: your own, or a speaker who has clearly agreed.
- Do not impersonate real people, and do not use a cloned voice to deceive anyone.
- Label synthetic audio as synthetic when you share or publish it.
- Keep reference recordings private. `.gitignore` excludes `assets/` and audio files.
- `scripts/clone_test.py` takes the path to your own reference audio as a required argument: `uv run scripts/clone_test.py my_voice.wav --ref-text "exact transcript"`.

Details are in `references/voice-cloning.md`.

## Models and licences

Third-party models keep their own licences. Where this skill's notes do not state one, check the model card.

| Model | Source | Licence / terms |
|---|---|---|
| Qwen3-TTS 12Hz 0.6B/1.7B (CustomVoice, Base, VoiceDesign) | `mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16` and siblings | See the model card |
| Chatterbox / Chatterbox Turbo | `mlx-community/chatterbox-turbo-fp16`, `mlx-community/chatterbox-fp16` (from `resemble-ai/chatterbox`) | See the model card |
| Chatterbox Czech fine-tune | `Thomcles/Chatterbox-TTS-Czech` | See the model card |
| Dia 1.6B | `mlx-community/Dia-1.6B-fp16` | See the model card |
| Breeze TTS 2 (optional) | `mlx-community/Breeze-TTS-2-mlx-4bit` (from `BreezeBlue/Breeze-TTS-2`) | Research / non-commercial only for weights, derivatives and self-hosted outputs (per `SKILL.md`) |
| ACE-Step 1.5 | `ACE-Step/Ace-Step1.5` | See the model card |
| mlx-audio (runtime) | `Blaizzy/mlx-audio` | See the repository |

## Layout

- `SKILL.md`: entry point Claude reads.
- `references/`: per-engine guides, setup, voice cloning, paper reading.
- `scripts/`: working examples (podcast with chapter markers, Chatterbox, Dia, cloning tests).

## Licence

MIT. See `LICENSE`.
