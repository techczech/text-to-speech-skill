# Dia Reference

Dia from Nari Labs generates multi-speaker dialogue in a single pass using `[S1]` and `[S2]` speaker tags. Best for creating conversations with nonverbal sounds.

## Multi-Speaker Dialogue

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

## Dialogue Format

- Two speakers only: `[S1]` and `[S2]`
- Each line is a turn — split on newlines
- Nonverbal sounds in parentheses: `(laughs)`, `(sighs)`, `(clears throat)`
- English only
- Output is 44100 Hz (higher than other engines)

## Voice Cloning with Dia

Clone a voice into dialogue (applies to `[S1]`):

```python
results = list(model.generate(
    text="[S1] This is the cloned voice speaking.",
    ref_audio="reference_voice.wav",
    ref_text="Transcript of the reference audio.",
))
```

## Performance

| Metric | Value |
|--------|-------|
| Speed (M4 Max) | ~1-2x realtime |
| Download | ~3.2GB |
| Sample rate | 44.1 kHz |
| Languages | English only |
| Max speakers | 2 per generation |

See `scripts/generate_dia.py` for the complete working example.
