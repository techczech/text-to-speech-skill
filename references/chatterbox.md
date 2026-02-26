# Chatterbox Turbo Reference

Chatterbox Turbo from Resemble AI offers high-quality speech with easy voice cloning (no transcript needed) and streaming support. Best choice when you need voice cloning without a transcript or real-time streaming output.

## Basic Generation

```python
from mlx_audio.tts.utils import load_model
import numpy as np, soundfile as sf

model = load_model("mlx-community/chatterbox-turbo-fp16")
results = list(model.generate(text="Your text here."))
audio = np.array(results[0].audio, dtype=np.float32)
sf.write("output.wav", audio, results[0].sample_rate)
```

CLI:
```bash
python -m mlx_audio.tts.generate \
    --model mlx-community/chatterbox-turbo-fp16 \
    --text "Hello, this is Chatterbox Turbo."
```

## Voice Cloning (No Transcript Needed)

Chatterbox clones a voice from just a reference audio file:

```python
results = list(model.generate(
    text="New text in the cloned voice.",
    ref_audio="reference_voice.wav",  # 5+ seconds recommended
))
```

CLI: add `--ref_audio reference_voice.wav`

## Streaming Mode

Generate audio in chunks for real-time playback:

```python
for chunk in model.generate(
    text="This text will stream out in chunks.",
    stream=True,
    streaming_interval=2.0,  # seconds between chunks
):
    # chunk.audio — audio data
    # chunk.is_streaming_chunk — True for intermediate chunks
    # chunk.is_final_chunk — True for the last chunk
    process_audio(chunk.audio, chunk.sample_rate)
```

## Emotion Control (Non-Turbo Variant)

The Turbo variant ignores `exaggeration`. Use the non-turbo model for emotion control:

```python
model = load_model("mlx-community/chatterbox-fp16")
results = list(model.generate(
    text="This is very exciting news!",
    ref_audio="reference_voice.wav",
    exaggeration=0.7,  # 0.0 = flat, 1.0 = very expressive
    cfg_weight=0.5,    # classifier-free guidance strength
))
```

## Performance

| Model | Speed (M4 Max) | Download |
|-------|-----------------|----------|
| Turbo (fp16) | ~2x realtime | ~3.0GB |
| Non-turbo (fp16) | ~1.5x realtime | ~2.6GB |
| Sample rate | 24 kHz | |
| Languages | 14+ | |

See `scripts/generate_chatterbox.py` for the complete working example.
