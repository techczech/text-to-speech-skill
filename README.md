# text-to-speech

## Scope

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

## Trigger

- Skill trigger: Generate speech audio locally.
- Procedure: see `SKILL.md`.
