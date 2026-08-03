# Style resolution

How `--style auto / <library-id> / --style-ref <image>` is resolved into the per-slide style anchor text + optional reference image.

---

## Resolution decision tree

```
if --style-ref <image-path>:
    use IMAGE-REF mode (multi-ref capable model required)
    if --style <id> also passed:
        text anchor = library style's anchor + "match reference image style"
    else:
        text anchor = "match reference image style"

elif --style <library-id>:
    style = load_style(<library-id>, "carousel")
    if --text-mode embedded:
        text anchor = style.anchor("Style anchor (text-in-image mode)")
    else:
        text anchor = style.anchor("Style anchor (carousel)")
    if --style-mod "<override>":
        text anchor = text anchor + " " + override

elif --style auto:
    candidates = library.find_by_tags(<tags derived from topic+tone>, "carousel")
    pick top 3, log alternatives, use top 1
    same anchor extraction as above
```

---

## `--style auto` algorithm

Auto-pick uses the topic + a few heuristics to narrow library candidates.

### Step 1 — Derive tags from the topic

Examples:
- "AI productivity tools for solo founders" → tags: [tech, professional, modern, b2b, editorial]
- "Slow-living trends 2026" → tags: [lifestyle, calm, refined, kinfolk-adjacent]
- "Synthwave music history" → tags: [retro, futuristic, 80s, neon]
- "How to write a cold email" → tags: [professional, educational, clean, b2b]

### Step 2 — Match against library tags + moods

Use `find_by_tags()`. Returns ordered list by tag-overlap count.

### Step 3 — Apply platform bias

- LinkedIn → prefer styles tagged `clean`, `editorial`, `b2b`, `professional`, `intellectual` (kinfolk-minimal, swiss-grid-poster, photo-editorial-bw, gradient-mesh-modern, flat-vector-illustration)
- Instagram → prefer styles with `lifestyle`, `playful`, `bold`, `modern` (paper-cutout-craft, gradient-mesh-modern, polaroid-faded, watercolor-soft, kinfolk-minimal)
- TikTok → prefer `bold`, `playful`, `viral`, `meme-friendly` (memphis-90s, sticker-mascot, y2k-chrome, neon-cyberpunk, holographic-iridescent)

### Step 4 — Apply text-mode constraint

If `--text-mode embedded`, drop candidates with `text_friendly: false`. (Holographic-iridescent / paper-cutout / watercolor often score poorly here — they're great as overlay targets, weak at embedding crisp typography.)

### Step 5 — Apply variants constraint

If `--variants 1` (default): pick top 1. If `--variants > 1`: pick top N candidates (gives the user style variants too, not just slide variants).

### Step 6 — Log alternatives

Print to stderr:
```
Style: kinfolk-minimal (auto). Alternatives: photo-editorial-bw, swiss-grid-poster.
Override with --style <id>.
```

---

## Image-ref mode

When `--style-ref <image-path>` is passed:

### Requirement check

The chosen model MUST support image-ref input. As of 2026:
- Nano Banana Pro: yes (best identity preservation)
- Flux Kontext: yes (text-edit on existing image)
- Flux 2 Pro: yes (multi-ref + style transfer)
- Seedream 5.0: yes
- Ideogram 3: yes (style-ref mode)
- gpt-image-2: yes (up to 16 refs)
- Nano Banana Pro: limited (single ref)
- Nano Banana 2 / 4 Fast: no — falls back to text-only

If user passed `--style-ref` AND `--model <model-without-ref>`: warn + auto-switch to a ref-capable model, OR exit if the chosen model can't be substituted.

### How the ref propagates per slide

The same reference image is attached to ALL N slides' generation calls. The provider blends it into each slide's content prompt. Result: stylistic + sometimes character consistency across slides.

### Caveats

- Identity / face preservation is BEST in Nano Banana Pro. If the ref is a person, prefer this model.
- Color palette transfer is BEST in Flux 2 Pro / Seedream.
- Typography transfer (matching a font from a logo image) is BEST in gpt-image-2 / Ideogram 3.
- If the ref is photographic and the desired output is illustrated: this often fights — the ref pulls toward photo. Use `--style-mod "stylized illustrated interpretation, not photographic"` to nudge.

---

## `--style-mod` override snippet

Appended to the chosen style anchor as a final sentence. Use for:

- Color tweaks: `"but with warmer color temperature, more amber tones"`
- Mood shifts: `"but more intimate and personal, less commercial"`
- Composition adjustments: `"with more negative space and looser framing"`
- Removing an element: `"without the geometric shapes — just typography and palette"`

Avoid:
- Adding a different medium ("but make it watercolor when chosen style is 3D") — pick a different `--style <id>` instead.
- Contradicting the style's core ("Memphis 90s but minimal and quiet") — these fight and produce muddled output.

---

## Multi-ref vs. single-ref provider matrix

| Provider | Max refs | Best at | Notes |
|---|---|---|---|
| gpt-image-2 | 16 | Text-in-image, mixed-source assembly | Slower, more $ per slide |
| Nano Banana Pro | 5-8 | Identity, face/character preserve | Best for "make 8 slides featuring this person" |
| Flux 2 Pro | 4 | Style + palette transfer | Best general-purpose ref-capable model |
| Flux Kontext | 1 | Text-prompted edit of one image | Good for "carousel from one photo + variations" |
| Seedream 5.0 | 4 | Photographic style transfer | Strong at brand-asset matching |
| Ideogram 3 | 1 (style-ref) | Embedded text + brand colors | Best for text-heavy carousels with brand consistency |
| Nano Banana Pro | 1 | Limited ref support | Mostly for text-to-image; ref is secondary |

---

## What gets saved to `style-used.md`

Every carousel run snapshots the resolved style to `./generated/carousel/<slug>/style-used.md`:

```markdown
# Style used: <library-id-or-custom>

**Resolution mode**: auto | explicit | ref | combined
**Library file**: <path-to-source.md>
**Style anchor**:
> <full anchor text used in prompts>

**Modifier**: <--style-mod text, if any>
**Reference image**: <path, if --style-ref was used>
**Alternatives considered (if auto)**: <list>
```

This makes runs reproducible — to redo a carousel with the SAME style next time, the user references this file.
