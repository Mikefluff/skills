# Style library — moved (v2.15.0)

The monolithic style-library file has been split into an extensible per-file library under [`styles/`](styles/).

## New location

- **Catalog** → [`styles/_index.md`](styles/_index.md) — lists all available styles
- **Schema** → [`styles/_schema.md`](styles/_schema.md) — required fields when adding a new style
- **Auto-pick matrix** → [`styles/_auto-pick.md`](styles/_auto-pick.md) — topic-signal → style resolution
- **Each style** → [`styles/<slug>.md`](styles/) — one file per style with structured frontmatter

## Why moved

- Extensible — drop a new `<slug>.md` file in `styles/` and it becomes available to every visual skill (carousel-builder / cover-maker / quote-card-maker / meme-card-maker / banner-maker / logo-maker) without code changes.
- No more hardcoded style lists in `system-prompt.md`. The shared SYSTEM_PROMPT references the directory by pattern, not a fixed enumeration.
- Per-style metadata stays atomic — adding `BIOTECH` doesn't require editing a 600-line file.

## How visual skills load styles at runtime

See [`styles/_index.md` → "Resolution order"](styles/_index.md#resolution-order-in-skills).

Short version:

1. `--style <slug>` → load `styles/<slug>.md` (error if not found).
2. `--style custom "<desc>"` → skip library; pass `<desc>` verbatim as `Visual style`.
3. `--style auto` (default) → consult `styles/_auto-pick.md` matrix → resolve slug → load.
4. Library style + `--style-mod "<override>"` → load library entry + append modifier.
