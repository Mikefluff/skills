# Music genre style library

A per-genre recipe library that produces paste-ready prompts for **Suno** (v5.5), **Udio** (v4), **Lyria 3 Pro**, **ElevenLabs Music**, and **Stable Audio 2.5**. Each file is a single source of truth for one genre — vibe, era, BPM, key tendency, sonic signature, and ready-to-paste prompts for every supported model.

## How skills consume this

Skills load by id:

```
load_style("hyperpop", "music")
load_style("drill-uk", "music")
```

The frontmatter (`id`, `mood`, `tags`, `bpm_range`, `energy`, `two_box`, `vocal_friendly`) drives auto-selection inside `music-prompt` and `reel-builder`. The Markdown body holds the paste-ready prompt blocks.

## What's in each file

- **Suno Style box** — natural language, ≤200 chars, NO brackets. Front-loaded with genre + era so Suno's 1000-char Style limit isn't wasted.
- **Suno meta-tag stacks** — one per section (Intro/Verse/Chorus/Bridge/Outro), tags pulled from the canonical 2026 taxonomy (`skills/music-prompt/references/meta-tags.md`).
- **Udio prompt** — natural language with bracketed inline cues, atomic tags, no `|` stacking.
- **Lyria 3 Pro** — field-driven (prompt / key / BPM / lyrics). Purely descriptive — Lyria refuses artist-mimicry.
- **ElevenLabs Music prompt** — single prompt + bracketed cues + timing markers.
- **Lyrics conventions, caption tone, best-for, avoid-for, suggested duration**.

## Override path

Drop a custom recipe at `~/.claude/style-library/music/<id>.md` to override the bundled version. Same frontmatter shape required.

## Rules baked in

- No living artists, no copyrighted song titles — every reference is era + scene (`80s glam metal`, `Y2K R&B`).
- No emojis.
- BPM ranges are realistic for each genre — recipes refuse impossible windows.
