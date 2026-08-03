# Aspect presets

Pixel dimensions for the supported aspects + platform fit + composition hints.

---

## Aspect catalog

| Aspect ID | Dimensions | Ratio | Native platform | Print equivalent |
|---|---|---|---|---|
| `portrait` | 1080×1350 | 4:5 | Instagram feed (modern), LinkedIn carousel slide | — |
| `square` | 1080×1080 | 1:1 | Instagram feed (classic), LinkedIn single image | 4×4" social card |
| `story` | 1080×1920 | 9:16 | Instagram Story, TikTok cover, YouTube Shorts cover | — |
| `landscape` | 1920×1080 | 16:9 | LinkedIn document, Twitter card, OG image, event-page hero | 8×4.5" landscape |
| `a4` | 1240×1754 | 1:√2 (close) | Print A4 portrait at 150 DPI (preview) | A4 (export to PDF for true print) |
| `tabloid` | 1224×1584 | Tabloid portrait | Print 11×17" tabloid at ~150 DPI | Tabloid |
| `square-large` | 2160×2160 | 1:1 | High-res square (Twitter card, OG image) | 8×8" social card |

Default `--aspects`: `portrait,square,story`. This covers the three most-shared social formats and runs ~3 × $0.05-0.10 = ~$0.30 on default model.

Pass `--aspects landscape` if you need a LinkedIn / Twitter card or an event page hero.
Pass `--aspects a4` if you're going to print.
Pass `--aspects portrait,square,story,landscape,a4` for the full set — ~5 × cost.

---

## Platform fit

### Instagram

- **Feed post**: `portrait` (1080×1350) is current best practice — takes 3× more feed real estate than 1:1.
- **Story / Reels cover**: `story` (1080×1920).
- **Multi-aspect run**: `--aspects portrait,square,story` covers feed + story + a square for cross-platform reuse.

### LinkedIn

- **Single image post**: `square` (1080×1080) or `landscape` (1920×1080).
- **Document / carousel**: `square` (1080×1080) is the document-format standard.
- **Multi-aspect run**: `--aspects square,landscape`.

### TikTok

- **Pre-roll graphic / event cover**: `story` (1080×1920).
- **Multi-aspect run**: `--aspects story`.

### Twitter / X

- **Card / shared image**: `landscape` (1920×1080) for in-feed; `square` (1080×1080) for inline.

### Threads / Bluesky / Mastodon

- **Feed image**: `portrait` (1080×1350) or `square` (1080×1080) work fine.

### Email newsletter banner

- The skill doesn't have a dedicated 600px wide banner aspect. Use `landscape` (1920×1080) and downsample to 600px wide in your editor.

### Print (A4 / tabloid)

- Use `a4` aspect for A4 portrait preview at 150 DPI. For true 300 DPI print:
  1. Generate at `a4` (1240×1754)
  2. Open in Affinity / Photoshop / GIMP
  3. Scale to 2480×3508 (300 DPI) — likely needs upscaling pass
  4. Convert to CMYK
  5. Export as PDF

This is intentional friction — the skill is for digital flyers. For print-first projects, a dedicated DTP tool is better.

---

## Composition implications per aspect

Different aspects need different headline/details placement.

### `portrait` (1080×1350)

- Headline zone: top 25% (~340px)
- Visual zone: middle 50% (~675px)
- Details zone: bottom 25% (~340px)
- Generous vertical space — works well for editorial / minimal styles

### `square` (1080×1080)

- Headline zone: top 25% (~270px)
- Visual zone: middle 50% (~540px)
- Details zone: bottom 25% (~270px)
- Tightest fit — bold typography essential, photo crops more aggressively

### `story` (1080×1920)

- Headline zone: top 20-25% but offset below the safe-zone top mask (Instagram UI bars cover top 220px) — effectively top 12-25%
- Visual zone: middle 50-55%
- Details zone: bottom 20-25% but offset above safe-zone bottom mask (~250px)
- Vertical-heavy framing — full-body or environmental photos work better than headshots

### `landscape` (1920×1080)

- Headline zone: left 40% OR top 25% (the skill assumes top by default; pass `--composition side-headline` to override)
- Visual zone: right 60% if side-headline; else middle 50%
- Details zone: bottom-right OR bottom 25%
- More options for layout — see composition-zones.md

### `a4` (1240×1754)

- Headline zone: top 20% (~350px) — more room for branding/logo above
- Visual zone: middle 55% (~960px) — the dominant photo / illustration area
- Details zone: bottom 25% (~440px) — date / location / CTA + sometimes a sponsor strip
- Print-format conventions apply: more whitespace, less visual weight at the edges (assume 1cm margin)

---

## Custom aspect

If you need a non-standard aspect (e.g. 728×90 banner ad), the skill currently doesn't have a preset. Two workarounds:

1. **Pass `--aspects landscape` and crop manually** in an image editor.
2. **Use `image-prompt --execute --size <WxH>`** directly for a single-image custom-aspect generation.

Adding a new aspect to the skill: edit `common/runners/cli/flyer.py` and add the preset to the `ASPECT_PRESETS` dict. PR welcome.

---

## File naming

Per-aspect output files:

```
<aspect-id>.png           # if --variants 1 (default)
<aspect-id>-v1.png        # if --variants > 1, first variant
<aspect-id>-v2.png        # second variant
...
```

Examples:

- `./generated/flyer/workshop-slow-software/portrait.png`
- `./generated/flyer/workshop-slow-software/story-v1.png`
- `./generated/flyer/workshop-slow-software/story-v2.png`

The aspect ID matches the `--aspects` value, so easy to script:

```bash
ls ./generated/flyer/<slug>/*.png
```
