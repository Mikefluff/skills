---
id: <ID>
modality: music
display: "<Human-readable genre name>"
mood: [<mood-tag-1>, <mood-tag-2>]
tags: [<musical-tag-1>, <musical-tag-2>, <musical-tag-3>]
bpm_range: "90-120"
energy: warm
two_box: true
vocal_friendly: true
---

# <Human-readable genre name>

**Vibe**: <one sentence — emotional/cultural anchor>.

**Era & lineage**: <when/where this style emerged, 1-2 hallmark eras or scenes>.

**Tempo**: <BPM range>. **Key tendency**: <e.g. "minor, often Em/Am" or "major, often C/G/D">.

**Core sonic signature**:

- <specific instrument or production trick #1>
- <specific instrument or production trick #2>
- <specific instrument or production trick #3>
- <specific instrument or production trick #4>
- <specific vocal style if relevant>

**Suno Style box (paste-ready, ≤200 chars)**:

```
<natural language genre+mood+instrument+era — NO brackets — ≤200 chars>
```

**Suno meta-tag stacks (by section)**:

```
[Intro | <2-3 tags>]
[Verse | <3-5 tags>]
[Chorus | <3-5 tags>]
[Bridge | <2-4 tags>]
[Outro | <2-3 tags>]
```

**Udio prompt**:

```
<udio-style natural language + bracketed inline tags like [breakdown] [build-up]; atomic tags, no `|` stacking>
```

**Lyria 3 Pro field-driven**:

```
prompt: <natural language genre+mood+instruments+era>
key: <e.g. C minor>
BPM: <number>
lyrics: <optional — see below>
```

**ElevenLabs Music prompt**:

```
<single-prompt natural language with [bracketed cues] + timing markers + exclude-styles hint>
```

**Lyrics conventions for this genre**:

- <e.g. "verse-chorus-verse-bridge-chorus, ~16 lines verse, ~4 lines chorus repeated">
- <e.g. "ad-libs in parens on own line">
- <language tendencies — EN-dominant, mix-friendly, etc>

**Caption tone (for paired carousel post or reel CTA)**:
<one-line guidance>

**Best for**: <2-3 use cases — e.g. "energetic product reels, gym brand content, sports highlights">.

**Avoid for**: <2-3 mismatches>.

**Suggested duration**: <e.g. "30-60s reel chunk", "full track 2:30-3:30">.

<!--
Conventions enforced by `skills-styles validate`:

- bpm_range must be 'NN-NN' string, both integers.
- energy must be one of: calm, warm, driving, aggressive.
- two_box + vocal_friendly must be true/false.
- Suno Style box: NO brackets — that's lyrics-box territory.
- Meta-tags should be from the canonical taxonomy in
  skills/music-prompt/references/{meta-tags,vocal-tags,instrumental-tags,mix-production-tags}.md.
- Max 4-8 tags per stack.
- NEVER name living artists or copyrighted songs (Suno/Udio/Lyria refuse).
- NO emoji.

Run `skills-styles validate music <ID>` after editing.
-->
