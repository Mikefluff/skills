# Style templates — schema + conventions

The shape of a valid style file, enforced by `skills-styles validate`.

The bundled templates live at:

- `common/style-library/carousel/_template.md`
- `common/style-library/video/_template.md`
- `common/style-library/music/_template.md`

`add` copies the bundled template, replacing `<ID>` and `<MODALITY>` placeholders. Below is the schema per modality.

---

## Common to all modalities

### Frontmatter (YAML-ish)

Parsed via regex (no PyYAML dep). Must look like:

```yaml
---
id: <kebab-case-id>
modality: carousel|video|music
display: "Human-readable name"
mood: [<tag1>, <tag2>]
tags: [<tag1>, <tag2>, <tag3>]
# modality-specific fields below
---
```

Required:

- `id` (string) — matches `^[a-z][a-z0-9-]{1,40}$` AND equals the filename stem
- `modality` (string) — exactly `carousel`, `video`, or `music`
- `display` (string) — human-readable name shown in `list` output
- `mood` (list of strings) — 2-4 emotional/cultural tags
- `tags` (list of strings) — 5-8 stylistic / cinematography / musical tags

### Body conventions

- Single H1 at the top: `# <Display name>`
- Required fields marked by `**Field name**:` markers
- Anchor text (the field that gets injected into prompts) goes in a blockquote: `> ...`
- Short fields can be inline; longer fields can span multiple lines
- NO emoji anywhere
- NO copyrighted living-artist names in prompt-facing fields
- NO real-brand mimicry in anchor text

---

## Carousel (visual style for image carousels)

### Required frontmatter

In addition to the common fields:

- `text_friendly: true|false` — true if the style works well with text-in-image models (Ideogram / gpt-image-2)
- `photoreal: true|false` — true if photographic; false if illustrated / 3D / abstract

### Required body fields

| Field | What |
|---|---|
| `**Vibe**:` | One sentence emotional / cultural anchor |
| `**Palette**:` | 3-5 specific color names (concrete, not "warm tones") |
| `**Typography**:` | Serif/sans/display + named reference fonts |
| `**Medium**:` | Photograph / flat vector / 3D render / watercolor / etc + concrete descriptors |
| `**Composition**:` | Framing rules — symmetry / negative space / rule-of-thirds / etc |
| `**Style anchor (carousel)**:` | 80-150 word model-agnostic prompt fragment — THE key field |
| `**Style anchor (text-in-image mode)**:` | 60-100 word variant for text-in-image models, with typography spec |
| `**Best for**:` | 2-4 use cases |
| `**Avoid for**:` | 2-3 mismatches |
| `**Suggested models**:` | Comma list ranked by fit |
| `**Caption tone**:` | One-line guidance for paired post copy |

### Validation specifics

- Style anchor (carousel) must be ≥40 chars
- `text_friendly` + `photoreal` must be `true` or `false` (literal booleans)
- Mood + tags must be lowercase strings

### Conventions reviewers enforce

- Anchor is model-agnostic (no "Midjourney aspect 4:5" or "v6 stylize 250")
- No copyrighted living artist names in anchor text
- No real-brand mimicry — use era + cultural movement instead
- Color names are specific (not "vibrant" or "modern colors")
- Typography names real font categories + reference fonts

---

## Video (directorial style for reel shots)

### Required frontmatter

- `pacing` (string) — one of `slow`, `medium`, `snap`, `kinetic`
- `dialogue_friendly: true|false` — true if the style supports on-camera dialogue

### Required body fields

| Field | What |
|---|---|
| `**Inspired by**:` | Single director's body of work — name films explicitly (user-facing only, never enters prompts) |
| `**Cinematography anchor**:` | 100-150 word visual-language paragraph — lens / depth / lighting / color / motion |
| `**Color palette**:` | 3-5 concrete colors that recur |
| `**Lens & framing**:` | Focal length, DoF, common framings |
| `**Lighting**:` | Key/fill ratio, motivated practicals, shadows |
| `**Motion language**:` | Camera motion conventions |
| `**Editing rhythm**:` | Cuts per minute, cut style |
| `**Shot anchor (per-shot prompt fragment)**:` | 80-150 word fragment APPENDED to every shot's prompt — THE key field |
| `**Action vocabulary**:` | 8-12 SPECIFIC camera + character moves (bullet list) |
| `**Sound design implications**:` | 2-3 lines on audio expectations |
| `**Best for**:` | 2-3 use cases |
| `**Avoid for**:` | 2-3 anti-fits |
| `**Suggested duration**:` | "3-shot × 6s" / "1-shot × 10s" / etc |
| `**Suggested music style**:` | One music-library id for pairing |

### Validation specifics

- Shot anchor must be ≥40 chars
- `pacing` must be one of: slow / medium / snap / kinetic
- `dialogue_friendly` must be literal true/false

### Conventions reviewers enforce

- The director's name appears in `display:` and `Inspired by:` ONLY
- The director's name MUST NOT appear in `Cinematography anchor` / `Shot anchor` / Action vocabulary — those go to the model and most providers refuse director mimicry
- Action vocabulary has 8-12 items (the upper-end is preferred)
- Cinematography vocabulary is real (anamorphic, focal length, key/fill ratio, motivated practicals, motivated practicals, named lens flares) — not "cinematic" or "stunning"
- Shot anchor works with all relevant providers (Veo 3.1 / Sora 2 / Kling 3.0 / Runway Gen-4) — no provider-specific syntax

---

## Music (genre preset for AI music gen)

### Required frontmatter

- `bpm_range` (string) — format `NN-NN` (e.g. `"100-110"`)
- `energy` (string) — one of `calm`, `warm`, `driving`, `aggressive`
- `two_box: true|false` — true if works with Suno/Udio two-box (Style + Lyrics)
- `vocal_friendly: true|false` — true if vocal-friendly; false if instrumental-only

### Required body fields

| Field | What |
|---|---|
| `**Vibe**:` | One sentence emotional/cultural anchor |
| `**Era & lineage**:` | When/where the style emerged, hallmark eras |
| `**Tempo**:` | BPM range + key tendency |
| `**Core sonic signature**:` | 5-7 bullets — specific instruments + production tricks |
| `**Suno Style box (paste-ready, ≤200 chars)**:` | Natural language, NO brackets, ≤200 chars — THE key field |
| `**Suno meta-tag stacks (by section)**:` | `[Intro \| ...]` `[Verse \| ...]` `[Chorus \| ...]` etc — from canonical taxonomy |
| `**Udio prompt**:` | Udio-style natural language + atomic bracketed tags (no `\|` stacking) |
| `**Lyria 3 Pro field-driven**:` | Field-style block — `prompt:` + `key:` + `BPM:` + `lyrics:` |
| `**ElevenLabs Music prompt**:` | Single-prompt natural language with bracketed cues + timing markers |
| `**Lyrics conventions for this genre**:` | Section structure, ad-libs, language tendencies |
| `**Caption tone (for paired carousel post or reel CTA)**:` | One-line guidance |
| `**Best for**:` | 2-3 use cases |
| `**Avoid for**:` | 2-3 mismatches |
| `**Suggested duration**:` | "30-60s reel chunk" / "full track 2:30-3:30" / etc |

### Validation specifics

- Suno Style box must be ≥40 chars (paste-ready and useful)
- `bpm_range` matches `^\d{2,3}-\d{2,3}$` — both integers, both 2-3 digits
- `energy` must be one of: calm / warm / driving / aggressive
- `two_box` + `vocal_friendly` must be literal true/false

### Conventions reviewers enforce

- Suno Style box: NO brackets (brackets go in Lyrics box only)
- Meta-tags from the canonical taxonomy at:
  - `music-prompt/references/meta-tags.md` (8 categories)
  - `music-prompt/references/vocal-tags.md`
  - `music-prompt/references/instrumental-tags.md`
  - `music-prompt/references/mix-production-tags.md`
- Max 4-8 tags per stack
- One tag per category per stack
- Order in stacks: structure → era → mood → instrument → mix/FX → vocal direction
- NEVER name living artists or copyrighted songs (Suno / Udio / Lyria refuse)
- Lyria 3 Pro: prompt must be purely descriptive (refuses artist mimicry)
- Stable Audio is weak on vocals — don't promise singing
- BPM range realistic for the genre (not "120-200")

---

## Adding a new modality (advanced)

To add a fourth modality (e.g. `audio` for SFX presets):

1. Add `audio` to `REQUIRED_FRONTMATTER` + `REQUIRED_BODY_FIELDS` in `common/runners/styles.py`
2. Create `common/style-library/audio/_template.md`
3. Update CLI: add `audio` to `_VALID_MODALITIES` in `common/runners/cli/styles.py`
4. Update this file with the schema

The loader (`Style.anchor()` / `.section()` / `find_by_tags()`) is modality-agnostic — it works with any frontmatter + body shape that follows the conventions above. The validator is the only place that needs per-modality knowledge.
