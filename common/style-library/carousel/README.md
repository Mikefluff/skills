# Carousel style library

Shared visual style definitions consumed by the `carousel-builder` skill. Each file locks one aesthetic — palette, medium, typography, composition, and a model-agnostic prompt fragment that gets appended to every slide of a generated carousel so the 8 frames read as a single piece, not a stylistic shuffle.

## How skills consume this

The carousel-builder loads a style via:

```
load_style(id, modality="carousel")
```

Resolution order:

1. User override — `~/.claude/style-library/carousel/<id>.md`
2. Bundled — `common/style-library/carousel/<id>.md`

The first match wins. Drop a file with the same `id` into the user override path to replace a bundled style without forking the skill.

## File format

Every style file is Markdown with YAML frontmatter. Required frontmatter keys:

- `id` — kebab-case, matches the filename
- `modality` — always `carousel` here
- `display` — human-readable name
- `mood` — 2–4 lowercase tags
- `tags` — 5–8 lowercase stylistic tags
- `text_friendly` — boolean, true if the style holds up with text rendered inside the image
- `photoreal` — boolean, true for photographic styles

The body must include two prompt anchors — one for image-only generation and one tuned for text-in-image models (Ideogram, gpt-image-2, Imagen 4). The carousel-builder picks the right anchor based on which provider it routes to.

## Adding a custom style

1. Copy any bundled file into `~/.claude/style-library/carousel/`.
2. Rename the file and update the `id` frontmatter field.
3. Rewrite the anchors. Keep them concrete — named fonts, named colors, named eras.
4. Re-run carousel-builder with `--style <your-id>`.

## Index

See `_index.md` for the full list of bundled IDs and their best-fit use cases.
