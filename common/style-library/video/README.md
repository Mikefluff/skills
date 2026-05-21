# Video director style library

Shared cinematographic style definitions consumed by the `reel-builder` skill. Each file distills the directorial grammar of a single filmmaker — lens habits, lighting ratios, motion conventions, editing cadence, palette discipline — into a model-agnostic prompt fragment that gets appended to every shot of a generated reel so 1-4 clips read as one continuous piece of authorship, not a stylistic shuffle.

This is a **directorial-grammar library**, not director-mimicry. We do not ask the model to "make a Fincher film". We extract the underlying cinematography conventions (cold low-key key/fill ratio, locked-off frames with subtle push-ins, deep-shadow corporate sterility) and pass those to the model. The director's name is a private bookmark for *us*; it never reaches the API.

## How skills consume this

The reel-builder loads a style via:

```
load_style(id, modality="video")
```

Resolution order:

1. User override — `~/.claude/style-library/video/<id>.md`
2. Bundled — `common/style-library/video/<id>.md`

The first match wins. Drop a file with the same `id` into the user override path to replace a bundled style without forking the skill.

## What gets passed to the model

Only the **shot anchor** paragraph (plus optional pulls from `cinematography anchor`, `lens & framing`, `lighting`, `motion language`, `action vocabulary`) is appended to the per-shot prompt sent to Veo 3.1 / Sora 2 / Kling 3.0 / Runway Gen-4. The `display`, `Inspired by`, and any director names live in metadata only — for human selection, never wire-format.

## File format

YAML frontmatter + Markdown body. Required frontmatter keys:

- `id` — kebab-case, matches filename
- `modality` — always `video`
- `display` — human-readable label
- `mood` — 2-4 lowercase tags
- `tags` — 5-8 cinematography tags
- `pacing` — `slow` / `medium` / `snap` / `kinetic`
- `dialogue_friendly` — boolean

Body sections (all required, in order): Inspired by, Cinematography anchor, Color palette, Lens & framing, Lighting, Motion language, Editing rhythm, Shot anchor, Action vocabulary, Sound design implications, Best for, Avoid for, Suggested duration, Suggested music style.

## Adding a custom style

1. Copy any bundled file into `~/.claude/style-library/video/`.
2. Rename the file and update the `id` field.
3. Rewrite the shot anchor — keep it concrete (focal length, lighting ratio, named color, real lens behaviour). Strip any director's name.
4. Re-run reel-builder with `--style <your-id>`.

## Index

See `_index.md` for the full list of bundled IDs sorted alphabetically with mood + pacing at-a-glance.
