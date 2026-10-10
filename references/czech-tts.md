# Czech TTS with Chatterbox Multilingual

Czech speech synthesis using the PyTorch-based Chatterbox Multilingual model with a Czech T3 fine-tune from `Thomcles/Chatterbox-TTS-Czech`. This is **not** an mlx-audio model — it runs via PyTorch on CPU.

## When to Use

When the user needs Czech language speech synthesis with voice cloning.

## Setup

Clone `resemble-ai/chatterbox` anywhere you like; below, `<chatterbox-dir>` means that checkout.

```bash
cd <chatterbox-dir>
uv sync  # installs PyTorch + dependencies
# Czech weights download automatically on first use via HF cache
huggingface-cli download Thomcles/Chatterbox-TTS-Czech
```

**Patches applied to `src/chatterbox/mtl_tts.py`:**
- Added `"cs": "Czech"` to `SUPPORTED_LANGUAGES` dict
- Changed `map_location` to `"cpu"` for Apple Silicon

## Generation with Voice Cloning

```python
import sys, os
from pathlib import Path
from safetensors.torch import load_file as load_safetensors

sys.path.insert(0, "<chatterbox-dir>/src")  # path to your chatterbox checkout
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")

# Swap T3 weights for Czech fine-tune
from huggingface_hub import snapshot_download
czech_dir = snapshot_download("Thomcles/Chatterbox-TTS-Czech")  # uses your HF cache
czech_t3_path = Path(czech_dir) / "t3_cs.safetensors"
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

## Notes

- Runs on **CPU only** (PyTorch, not MLX) — generation takes ~1-2 minutes per sentence
- Voice cloning via `audio_prompt_path` — use a clean 5-15 second reference clip
- The Czech fine-tune modifies only the T3 (text-to-token) component; S3Gen vocoder is shared
- Quality is reasonable but not as polished as the English Chatterbox models

## Troubleshooting

- **`language_id` error**: Ensure `mtl_tts.py` has `"cs": "Czech"` in `SUPPORTED_LANGUAGES` dict
- **onnx/ml_dtypes error**: Run `.venv/bin/pip install "onnx<1.17"` to downgrade onnx. Use `.venv/bin/python` directly instead of `uv run` (which re-syncs and restores the broken version)
