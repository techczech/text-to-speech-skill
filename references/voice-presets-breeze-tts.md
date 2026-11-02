---
title: Breeze TTS 2 narration voice presets
verified: 2026-09-11
scope: research-non-commercial
---

# Breeze narration voice presets

Use with [the Swift setup](setup-breeze-tts.md). Pass the **entire description** as `--voice`; names below are labels, not built-in IDs. These are text-designed synthetic voices, not clones of real people.

## The Quiet Observer

Warm, intimate documentary direction; 22.00-second audition.

```text
An adult woman speaking English with a natural British accent. Warm low-mid register, intimate documentary narration, unhurried and thoughtful. Clear consonants, subtle curiosity, gentle changes of emphasis. Calm but engaged; natural spoken delivery, not whispering or theatrical.
```

## The Wry Storyteller

Conversational storytelling direction; 19.36-second audition.

```text
A mature man speaking English with a light Irish accent. Warm resonant mid-low voice with a slightly textured timbre. Conversational storytelling with dry humour, lively melodic phrasing and a faint smile. Begin matter-of-factly, then let genuine wonder enter the final sentence. Clear, natural delivery.
```

## The Night Archivist

Restrained science-fiction suspense direction; 21.60-second audition.

```text
An adult woman speaking English with a clear neutral American accent. Low resonant voice, measured and precise science-fiction narration. Cool composure with an undercurrent of unease. Deliberate pauses, restrained intensity, and a softer, more human final sentence. Fully voiced, not a whisper.
```

## Shared audition text

```text
At three in the morning, the museum's oldest clock began to run backwards. Nobody noticed at first. Then the rain rose from the pavement, a dropped glass assembled itself on the bar, and somewhere beneath the city, a woman heard her father's voice on a telephone that had not been connected for thirty years.
```

Settings: pinned 4-bit model/Swift runtime from setup reference; `--max_tokens 640 --benchmark`; default sampling; no reference audio. Each clip passed finite/non-silent mono 24 kHz checks; local Parakeet transcripts matched the words, with punctuation variation.

Accent, timbre and emotional fidelity were not independently rated. The durations identify those auditions, not fixed generation lengths. A reused description does not guarantee identical speaker identity across runs.

For iteration: keep the text constant, change one voice trait, preserve each prompt and clip, then ask which reading suits the narration. For longer work, verify chunk-to-chunk voice consistency. If stable identity needs reference conditioning, obtain permission for the reference voice and use its exact transcript; do not assume prompt reuse supplies voice cloning.
