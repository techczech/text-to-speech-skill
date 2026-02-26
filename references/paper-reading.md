# Paper Reading Modes

When a user provides a paper (markdown, PDF, or Zotero key) and asks for TTS, use one of two paper-specific modes. These integrate with the `academic-paper-review` skill's paper-analysis structure.

**Default model**: `mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16` with `Ryan` speaker. Use 1.7B only if user requests higher quality.

## Workflow

### Step 1 — Investigate the Paper

Read the paper content. Check what's available:
- Fulltext markdown in `paper-analysis/{slug}/` (via `*-fulltext.md`) or `articles/`
- Highlights, reviews, extracts, notes in `paper-analysis/{slug}/`
- PDF (note extraction is needed first)
- Source metadata (`00-source.md`) with title, authors, abstract, DOI

### Step 2 — Ask User Preference

Determine via `AskUserQuestion` or conversation:
- **Mode**: "paper-read" (straight reading) or "paper-narrate" (guided with commentary)?
- **Focus**: Full paper / Abstract + highlights / Methods & results / Conclusions first
- **Depth**: Brief (~5 min) / Standard (~15 min) / Comprehensive (~30+ min)
- **Tables/figures**: Include descriptions? Skip?

### Step 3 — Generate Script

Create a PEP 723 Python script with segments following the chosen mode. Group segments into logical chapters using the `"chapter"` field — these become navigable chapter markers in the MP3.

### Step 4 — Run

```bash
uv run --python 3.12 paper_audio.py
```

The output MP3 will contain ID3v2 chapter markers for navigation in podcast apps.

---

## Paper-Read Mode

Straight read-through of the paper text — verbatim content with minimal framing.

**When to use**: User wants to listen to the paper as written, like an audiobook.

**Script structure**:
1. Investigate the paper first: read source markdown/fulltext
2. Generate segments that read chosen content verbatim
3. Add minimal framing: title + authors at start, "End of paper" at close
4. Use measured, academic narration style

```python
SEGMENTS = [
    {"chapter": "Title & Authors",
     "text": "Paper title. By authors. Published in journal, year.",
     "instruct": "Professional announcement"},
    {"chapter": "Abstract",
     "text": "[Abstract text verbatim]",
     "instruct": "Clear academic reading, measured pace"},
    {"chapter": "Introduction",
     "text": "[Section text verbatim]",
     "instruct": "Academic reading voice"},
    # One segment per ~2-3 paragraphs (under 500 words per segment)
]
```

**Tips**:
- Split on paragraph boundaries, not mid-sentence
- Keep segments under 500 words for best audio quality
- Use consistent `instruct` values for uniform delivery
- If fulltext lacks section headers, infer breaks from topic shifts

---

## Paper-Narrate Mode

Guided narration with commentary, context, and reader orientation — like a knowledgeable colleague walking you through a paper.

**When to use**: User wants to understand the paper, not just hear it read aloud.

**Script structure**:
1. Investigate thoroughly: read fulltext, highlights, reviews, summary-card, notes
2. Generate a narrated script interleaving orientation, context, verbatim, and commentary segments
3. Use varied `instruct` values for different segment types

```python
SEGMENTS = [
    {"chapter": "Overview",
     "text": "This is a narrated guide to 'Paper Title'...",
     "instruct": "Professional, warm narrator introducing a research paper"},
    {"text": "The abstract introduces several key terms...",
     "instruct": "Thoughtful academic guide, defining terms clearly"},
    {"chapter": "Abstract",
     "text": "[Full abstract text]",
     "instruct": "Clear academic reading, measured pace"},
    {"text": "Notice the gap between X and Y. This is the central finding...",
     "instruct": "Engaged, highlighting a surprising finding"},
    {"chapter": "Methods",
     "text": "The methods section describes a study with N participants...",
     "instruct": "Methodical, explanatory tone"},
    {"text": "Table 1 shows the distribution...",
     "instruct": "Clear, descriptive data presentation"},
    {"chapter": "Key Takeaways",
     "text": "The key takeaway: while LLMs achieve high accuracy...",
     "instruct": "Thoughtful, summarizing with conviction"},
]
```

### Instruct Values by Segment Type

| Segment Type | `instruct` Example |
|---|---|
| Orientation | "Professional, warm narrator introducing a research paper" |
| Context | "Thoughtful, analytical academic guide" |
| Verbatim | "Clear academic reading, measured pace" |
| Commentary | "Engaged, insightful scholarly commentary" |
| Section preview | "Methodical, explanatory tone" |
| Table/figure | "Clear, descriptive data presentation" |
| Synthesis | "Thoughtful, summarizing with conviction" |

**Tips**:
- Read all available reviews and highlights to inform commentary
- Interleave verbatim and commentary — don't just paraphrase the whole paper
- For "brief" depth: abstract + key findings + conclusion
- For "comprehensive" depth: cover every section with orientation and commentary
- Describe tables/figures verbally since the listener can't see them
