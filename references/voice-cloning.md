# Voice Cloning Guide

Cross-engine voice cloning comparison and best practices.

## Voice Cloning and Consent

- Clone only voices you have permission to use: your own, or a speaker who has clearly agreed. Recordings you merely have access to (broadcasts, podcasts, calls, family archives) are not permission.
- Do not impersonate real people, and do not use a cloned voice to deceive anyone (fake endorsements, fraud, fake calls or messages, misleading audio of a real person).
- Label synthetic audio as synthetic wherever it is shared or published, for example in the title, description or a spoken disclosure.
- Keep reference recordings private and out of version control; this skill's `.gitignore` excludes `assets/` and common audio files.
- If a user asks for a clone of someone else's voice and no consent is evident, ask before proceeding; if consent is absent, decline and suggest Qwen3-TTS VoiceDesign (a synthetic voice from a text description) instead.

## Which Engine to Use

| Scenario | Engine | What You Need |
|----------|--------|---------------|
| **Easiest cloning** (no transcript) | Chatterbox Turbo | ref_audio only (5+ sec) |
| **Highest fidelity** cloning | Qwen3-TTS Base | ref_audio (3+ sec) + ref_text |
| **Cloned voice in dialogue** | Dia | ref_audio + ref_text |
| **Create voice without audio** | Qwen3-TTS VoiceDesign | Text description only |

## Reference Audio Requirements

| Requirement | Qwen3-TTS | Chatterbox | Dia |
|-------------|-----------|------------|-----|
| Minimum length | 3 seconds | 5 seconds | A few seconds |
| Ideal length | 5-15 seconds | 5-15 seconds | 5-15 seconds |
| Transcript needed | Yes (`ref_text`) | No | Optional (`ref_text`) |
| Format | WAV preferred | WAV, MP3, etc. | WAV preferred |
| Quality | Clean, single speaker | Clean, single speaker | Clean, single speaker |

## Auto-Transcription

When `ref_text` is not provided but required, the mlx-audio CLI auto-transcribes using Whisper. In the Python API, provide `ref_text` explicitly for best results.

## Tips for Reference Audio

- Use a clean recording with minimal background noise
- Single speaker, no music
- Consistent volume throughout
- The better the reference, the better the clone

## Quick API Examples

**Chatterbox Turbo** (easiest — no transcript):
```python
model = load_model("mlx-community/chatterbox-turbo-fp16")
results = list(model.generate(text="New text.", ref_audio="ref.wav"))
```

**Qwen3-TTS Base** (best quality):
```python
model = load_model("mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16")
results = list(model.generate(text="New text.", ref_audio="ref.wav",
                               ref_text="Exact transcript of reference."))
```

**Qwen3-TTS VoiceDesign** (no audio needed):
```python
model = load_model("mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16")
results = list(model.generate_voice_design(
    text="Content to speak.", language="English",
    instruct="A warm female voice, mid-30s, slight Irish accent.",
))
```

See `scripts/voice_clone_demo.py` for a side-by-side comparison script and `scripts/clone_test.py` for a quick cloning test.

For engine-specific details: `references/qwen3-tts.md`, `references/chatterbox.md`, `references/dia.md`.
