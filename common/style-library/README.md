# common/style-library — shared style presets

A library of named visual + sonic styles consumed by `carousel-builder`, `reel-builder`, and the `music-prompt` skill. Each style is a markdown file with YAML frontmatter + structured anchor blocks the skills load on demand.

## Layout

```
common/style-library/
  README.md                    # this file
  carousel/
    _index.md                  # one-row-per-style table
    README.md                  # carousel-specific notes
    <style-id>.md              # 24 visual styles
  video/
    _index.md
    README.md                  # video-specific notes
    <style-id>.md              # 12 directorial styles
  music/
    _index.md
    README.md                  # music-specific notes
    <style-id>.md              # 12 genre presets
```

50 bundled styles (24 + 12 + 12) + 2 indices + 4 READMEs.

## How skills use the library

```python
from common.runners.styles import load_style, list_styles, find_by_tags

style = load_style("kinfolk-minimal", "carousel")
anchor = style.anchor("Style anchor (carousel)")          # prose block
text_anchor = style.anchor("Style anchor (text-in-image mode)")
moods = style.mood                                          # list
tags = style.tags                                           # list
```

`load_style()` resolves in this priority order:

1. `~/.claude/style-library/<modality>/<id>.md` — user override
2. `<repo>/common/style-library/<modality>/<id>.md` — bundled (this directory)

User overrides win by exact id match. To override `kinfolk-minimal`, copy the bundled file to `~/.claude/style-library/carousel/kinfolk-minimal.md` and edit.

## Style file format

```markdown
---
id: <kebab-case-id>             # must match filename stem
modality: carousel|video|music   # one of three modalities
display: "Human-readable name"
mood: [tag1, tag2, ...]
tags: [tag1, tag2, ...]
# modality-specific fields (text_friendly / photoreal / pacing / dialogue_friendly / bpm_range / energy / two_box / vocal_friendly):
---

# Display name

**Vibe**: <one sentence>

[Field-specific sections per modality — see each subdir's README for the exact schema]

**Style anchor (carousel)**:
> <prose paragraph injected into prompts>

**Best for**: ...
**Avoid for**: ...
**Suggested models**: ...
```

## Adding a custom style

1. Pick the modality (carousel / video / music) and a kebab-case id.
2. Create the file at `~/.claude/style-library/<modality>/<id>.md` (or commit to a fork of the repo).
3. Follow the exact frontmatter + body schema (copy a bundled file as a starting template).
4. The skill will auto-discover the next time it runs.

## Style ids must be unique per modality

`kinfolk-minimal` in `carousel/` doesn't conflict with `kinfolk-minimal` in `video/` — modality is part of the lookup key. But within one modality, ids MUST be unique. If you fork the repo and add a custom carousel style, give it a distinct id.

## What gets snapshotted to output

When a skill uses a style, it writes a `style-used.md` to the output directory recording:
- Style id resolved
- Source file path
- Anchor text used
- Any --style-mod modifier applied
- Alternatives considered (if --style auto picked)

This makes runs reproducible — to redo with the SAME style, point the skill at the same id.

## See also

- `common/runners/styles.py` — the loader implementation
- `skills/carousel-builder/references/style-resolution.md` — auto-pick algorithm
- `skills/reel-builder/references/style-resolution.md` — directorial style application
- `skills/music-prompt/references/meta-tags.md` — canonical meta-tag taxonomy used in music style files
