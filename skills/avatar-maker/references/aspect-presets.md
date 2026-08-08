# Aspect presets — avatar-maker

Pixel dimensions + framing conventions + platform fit per aspect.

---

## Aspect catalog

| Aspect ID | Dimensions | Ratio | Native platform | Framing |
|---|---|---|---|---|
| `square` | 1080×1080 | 1:1 | LinkedIn / Twitter / IG / GitHub profile | medium close-up — head + shoulders |
| `square-tight` | 1080×1080 | 1:1 | Small thumbnail (chat avatars, comment avatars) | tight headshot — face fills 60-70% of frame |
| `cover` | 1080×1350 | 4:5 | LinkedIn cover banner (4:1 area at top), IG feed portrait | 3/4 — head + shoulders + some environment |
| `story` | 1080×1920 | 9:16 | IG Story / TikTok cover background | full-body or environmental |
| `wide` | 1920×1080 | 16:9 | Twitter/X header, YouTube channel banner top | wide framing — face left or center with negative space |

Default `--aspects`: `square` (1 aspect × 3 variants = 3 images total). Most users need just 1:1.

For someone setting up new social accounts cross-platform: `--aspects square,cover` gives the profile pic + a cover-banner-area photo in matching style.

For full cross-platform pack: `--aspects square,square-tight,cover,wide`.

---

## Per-aspect framing prompts

The skill encodes per-aspect framing in the prompt. Different aspects produce different output even with the same source photo.

### `square` (1080×1080)

> Framing: medium close-up — head + shoulders fill the upper 60-70% of frame. Subject centered or slightly off-center. Some background context visible.

### `square-tight` (1080×1080)

> Framing: tight headshot — face fills 60-70% of frame, top of head near frame edge, shoulders cropped at the bottom. Minimal background. Identity emphasis.

### `cover` (1080×1350)

> Framing: 3/4 framing — head + shoulders + some upper body. Subject offset to one side (default: subject centered with negative space at top for headline-area). Environment / palette visible around subject.

### `story` (1080×1920)

> Framing: full-body or 3/4 environmental — subject's full upper body or full body visible. Vertical composition with subject mid-frame. Background takes more visual weight in this aspect.

### `wide` (1920×1080)

> Framing: wide horizontal — subject occupies left third or center, with negative space for header text / branding (handled outside this skill). Looking forward or slightly off-camera.

---

## Platform fit notes

### LinkedIn

- **Profile picture**: `square` (1080×1080). LinkedIn crops this to a circle for display, but stores the source 1:1. Keep eye line in the upper 40% so the circle doesn't cut off head.
- **Cover banner background**: `wide` (1920×1080) — but note LinkedIn cover is 1584×396 (4:1). The `wide` aspect doesn't match exactly. For pure cover-banner use, generate at `wide` and crop the bottom 60% in your editor.
- **Multi-aspect run**: `--aspects square,wide` gives both.

### Twitter / X

- **Profile picture**: `square` (1080×1080) — Twitter crops to circle.
- **Header banner**: 1500×500 (3:1). Closest preset: `wide` (1920×1080, 16:9) — crop the bottom 40%.

### Instagram

- **Profile picture**: `square` (1080×1080) — IG crops to circle.
- **Feed posts featuring avatar-as-content**: `cover` (4:5) or `square-tight`.
- **Story background**: `story` (9:16).

### GitHub / Slack / Discord / Notion / Linear

- **Profile picture**: `square` (1080×1080) — all crop to circle.
- **Username-area thumbnail**: `square-tight` works for tiny thumb where face needs to be clearly visible.

### YouTube channel

- **Channel icon**: `square` (1080×1080) — YT crops to circle.
- **Channel banner**: 2560×1440. Closest preset: `wide` (1920×1080); the YT banner has a complex safe-zone (different on desktop / mobile / TV) — generate `wide` and resize in your editor.

---

## When variants make sense

Default `--variants 3` is the sweet spot.

- `--variants 1`: fast preview, single take. Often you'll re-roll because the first take has a quirk.
- `--variants 3` (default): three takes per aspect, pick the best one. Catches most quirks.
- `--variants 5`: when identity-preserve is shaky (style transfer fighting identity) — more takes give more chances at a "yes that's me" shot.
- `--variants 10+`: probably over-spending. Iterate on prompt / style instead.

<!-- prices: batch=6 -->

If `--aspects square,cover --variants 3`: total is 6 images, $0.80 at nano-banana-pro.

---

## File naming

Per-variant output files:

```
<aspect-id>-v<N>.png         # if --variants > 1
<aspect-id>.png              # if --variants == 1 (no suffix)
```

Examples:

- `./generated/avatar/alex-headshot/square-v1.png`
- `./generated/avatar/alex-headshot/square-v2.png`
- `./generated/avatar/alex-headshot/square-v3.png`
- `./generated/avatar/alex-headshot/cover-v1.png`
- `./generated/avatar/alex-headshot/cover-v2.png`
- `./generated/avatar/alex-headshot/cover-v3.png`

---

## Custom slug

By default, slug derived from `--photo` filename:

- `./alex-headshot.jpg` → `alex-headshot`
- `./IMG_1234.HEIC` → `img-1234`

Override:

```bash
avatar-maker --photo ./me.jpg --slug "alex-2026-headshot"
```

Output dir becomes `./generated/avatar/alex-2026-headshot/`.

---

## What gets saved to `style-used.md`

```markdown
# Avatar set: <slug>

## Source

**Photo**: <path-or-url>
**Slug**: <slug>

## Style

**Library file**: <path>
**Style anchor (carousel)**:
> <full anchor text>

**Modifier**: <--style-mod text, if any>

## Provider

- Model: <slug>
- Identity preserve mode: <native | image-ref>
```

Reproducibility: same photo + style + model = same character look across future runs.
