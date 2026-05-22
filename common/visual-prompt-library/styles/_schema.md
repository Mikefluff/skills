# Style entry schema — visual-prompt-library/styles/

Each style is ONE `<slug>.md` file in this directory. The library is extensible: drop a new file in, list it in `_index.md`, optionally add it to `_auto-pick.md` if it should be auto-picked, and every visual-prompt skill in the collection will pick it up automatically via the shared chain.

## Required frontmatter

```yaml
---
id: <SCREAMING-KEBAB-CASE>      # e.g. CYBER-NOIR, ART-DECO, NORDIC-MINIMAL
slug: <kebab-case>              # the file basename, e.g. cyber-noir, art-deco
name: <Display name>            # e.g. "CYBER-NOIR / DIGITAL"
when_to_use: <one-sentence>     # the situational fit — topics / tones / audiences
background: <one-line>          # dominant background palette + texture + treatment
accents: <one-line>             # accent / glow / highlight colors
elements: <one-line>            # comma-separated motif vocabulary (8–14 items)
mood: <one-line>                # emotional / atmospheric direction
accent_text_color: <one-line>   # color(s) used for ==accent== words + key numbers
typography: <one-line>          # genre-level font descriptors (NOT named fonts)
composition_signature: <one-line>  # layout patterns this style is known for
---
```

## Optional body (after the frontmatter)

- Extended notes on the style's history, when NOT to use, edge cases
- Real-world examples (magazines, brands, films — for orientation only, NEVER inject brand names into actual image prompts)
- Variation hints (e.g. "darker = night-time mood; lighter = morning")

## Field rules

- **`typography`**: image models don't have font libraries; they approximate by genre. Use descriptors like `heavy stencil display`, `condensed grotesque sans`, `italic copperplate script`, `monospace terminal`, `classical Caslon-style serif`, `humanist serif with organic curves`. NEVER name a specific font file (Helvetica Neue 75 Bold won't work — it just approximates). Mix at least 2 descriptors so the LLM has hierarchy variety.

- **`composition_signature`**: list 3–6 layout patterns the style is famous for, so when N>1 the LLM can pick a DIFFERENT signature per slide. Use historical references (e.g. "art deco — symmetric mirrored framing, sunburst medallion, ornamental corner stamps") not abstract terms like "clean layout".

- **`elements`**: 8–14 concrete motifs. The LLM picks 1–3 per slide and varies across the deck — so the more options, the more variety. Avoid duplication with `composition_signature` (motifs vs layouts are different).

- **`accent_text_color`**: 1–3 colors used specifically for `==marked==` accent phrases and key numbers (NOT the dominant text color, which usually contrasts the background). E.g. CYBER-NOIR background = black; main text white; accent = matrix green + signal red.

- **`mood`**: 3–5 short emotional words (e.g. "calming, hopeful, scientific yet warm"). Drives lighting + composition energy in the prompt.

## How to add a new style

1. Create `<slug>.md` in this directory with the frontmatter above + optional body.
2. Add a one-line entry to `_index.md` under the appropriate category.
3. Optional: add a row to `_auto-pick.md` if the style should match certain topic signals.
4. No other code changes needed — the shared SYSTEM_PROMPT loads styles by slug at runtime.

## How styles are loaded at request time

The carousel-builder / cover-maker / etc. skill, when running:

1. Resolves the requested style slug (explicit `--style <name>`, `--style auto` → consult `_auto-pick.md`, or `--style custom "<desc>"` → skip the library).
2. Reads the chosen `<slug>.md` file's frontmatter.
3. Injects the resolved fields verbatim into the LLM user message under `Style entry:` (see `system-prompt.md` for the `buildUserMessage` shape).
4. The LLM step (shared SYSTEM_PROMPT) then pulls from those fields when drafting each per-image prompt.

The SYSTEM_PROMPT itself does NOT hardcode style names. Anything you add to `styles/` becomes available automatically.
