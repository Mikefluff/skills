# Composition zones — how text + photo land on the flyer

Per-aspect templates. The skill assembles the per-aspect prompt by combining the style anchor + zone template + event details.

---

## Three-zone model

Every flyer is structured as three zones:

1. **Headline zone** — title + optional subtitle
2. **Visual zone** — photo (if provided) or style-anchor-driven visual
3. **Details zone** — date / time / location / CTA

The proportions and exact placement depend on the aspect.

---

## Per-aspect zone templates

### Portrait (1080×1350, 4:5)

```
┌──────────────────────────────┐
│                              │
│      [Headline zone]         │  ← Top 25% (~340px)
│      Bold large title        │
│      [optional subtitle]     │
│                              │
├──────────────────────────────┤
│                              │
│                              │
│      [Visual zone]           │  ← Middle 50% (~675px)
│   photo subject, integrated  │
│   with style-anchor backdrop │
│                              │
│                              │
├──────────────────────────────┤
│      [Details zone]          │  ← Bottom 25% (~340px)
│   Date · Time                │
│   Location                   │
│   CTA                        │
└──────────────────────────────┘
```

Composition prompt fragment:

> Portrait flyer composition, 4:5 aspect ratio. Top quarter: bold headline typography reading "<TITLE>" in large display weight, with optional subtitle "<SUBTITLE>" below in lighter weight. Middle half: <photo description OR style-anchor visual>. Bottom quarter: smaller typography stack with date "<DATE>", location "<LOCATION>", and CTA "<CTA>" arranged left-aligned or center, consistent with the chosen style.

### Square (1080×1080, 1:1)

```
┌──────────────────────────────┐
│   [Headline zone]            │  ← Top 25% (~270px)
│   Bold title                 │
├──────────────────────────────┤
│                              │
│                              │
│   [Visual zone]              │  ← Middle 50% (~540px)
│   photo + style backdrop     │
│                              │
│                              │
├──────────────────────────────┤
│   [Details zone]             │  ← Bottom 25% (~270px)
│   Date · Location · CTA      │
│   (often single line)        │
└──────────────────────────────┘
```

Composition prompt fragment:

> Square flyer composition, 1:1 aspect ratio. Top quarter: bold headline "<TITLE>" centered. Middle half: <visual>. Bottom quarter: details line "<DATE> · <LOCATION> · <CTA>" arranged horizontally to fit the square format.

### Story (1080×1920, 9:16)

```
┌──────────────┐
│ ╳╳╳╳╳╳╳╳╳╳╳╳ │  ← Safe-zone top mask (Instagram UI), ~220px
│              │
│ [Headline]   │  ← Below safe zone, ~12-25% (200-470px)
│ Bold title   │
│              │
├──────────────┤
│              │
│              │
│              │
│ [Visual]     │  ← Middle ~50% (470-1430px)
│  photo / bg  │
│              │
│              │
│              │
├──────────────┤
│ [Details]    │  ← Above safe-zone bottom (~1430-1670px)
│ Date         │
│ Location     │
│ CTA          │
│              │
│ ╳╳╳╳╳╳╳╳╳╳╳╳ │  ← Safe-zone bottom mask (CTA buttons), ~250px
└──────────────┘
```

Composition prompt fragment:

> Vertical Story flyer composition, 9:16 aspect ratio. Reserve top 12% (220px) and bottom 13% (250px) as safe zones (kept clear of important content — these areas are masked by Instagram/TikTok UI overlays). Headline "<TITLE>" lands in the upper-third below the safe zone. Visual fills the middle half. Details "<DATE> · <LOCATION> · <CTA>" land in the lower-third above the safe zone, stacked vertically.

### Landscape (1920×1080, 16:9)

Two layout modes:

**Top-headline (default)**:
```
┌──────────────────────────────────────────┐
│ [Headline zone]                          │
│ Bold title  [optional subtitle]          │  ← Top 25% (~270px)
├──────────────────────────────────────────┤
│                                          │
│        [Visual zone]                     │
│   photo subject + style backdrop         │  ← Middle 50% (~540px)
│                                          │
├──────────────────────────────────────────┤
│ [Details zone]                           │
│ Date · Location · CTA (single line)      │  ← Bottom 25% (~270px)
└──────────────────────────────────────────┘
```

**Side-headline (`--composition side-headline`)**:
```
┌────────────────────┬─────────────────────┐
│                    │                     │
│  [Headline]        │                     │
│  Title             │                     │
│  Subtitle          │                     │
│                    │  [Visual zone]      │
│                    │                     │
├────────────────────┤                     │
│                    │                     │
│  [Details]         │                     │
│  Date              │                     │
│  Location          │                     │
│  CTA               │                     │
│                    │                     │
└────────────────────┴─────────────────────┘
   Left 40%             Right 60%
```

Composition prompt fragment (top-headline):

> Landscape flyer composition, 16:9 aspect ratio. Top quarter: bold headline "<TITLE>" with optional subtitle "<SUBTITLE>". Middle half: <visual>. Bottom quarter: details line "<DATE> · <LOCATION> · <CTA>" arranged horizontally.

### A4 (1240×1754, 1:√2)

```
┌────────────────────────────┐
│   [margin]                 │  ← 1cm margin at print scale
│                            │
│   [Headline zone]          │  ← Top 20% (~350px)
│   Large display title      │
│   Optional subtitle        │
├────────────────────────────┤
│                            │
│                            │
│                            │
│   [Visual zone]            │  ← Middle 55% (~960px)
│   Dominant photo/visual    │
│                            │
│                            │
│                            │
├────────────────────────────┤
│   [Details zone]           │  ← Bottom 25% (~440px)
│   Date · Time              │
│   Location (full address)  │
│   CTA                      │
│   [Sponsor strip] (opt.)   │
│                            │
│   [margin]                 │
└────────────────────────────┘
```

Composition prompt fragment:

> A4 portrait flyer composition, 1:1.41 aspect ratio (print-ready feel at 150 DPI). 1cm margin on all sides. Top 20%: large display headline "<TITLE>" with optional subtitle. Middle 55%: dominant visual zone. Bottom 25%: details stack with date, full location, and CTA. Print-format conventions: more whitespace, less visual weight at the edges, reserved hierarchy.

---

## Photo integration

When `--photo <path>` is provided, the skill instructs the model to integrate the subject into the visual zone:

> Use the provided reference image as the central subject in the visual zone. Integrate naturally into the style-anchor backdrop. Preserve identity (face / pose / outfit) while letting the surrounding palette / texture / typography follow the chosen style.

Subject framing varies by aspect:

- `portrait`: headshot or 3/4 framing
- `square`: medium close-up — head + shoulders
- `story`: full-body or environmental — more vertical space allows wider framing
- `landscape`: 3/4 horizontal — subject left or right of center
- `a4`: editorial — full-frame photo, often subject centered

If you need a specific framing different from the default, pass it as part of `--style-mod`:

```bash
--style-mod "frame subject as upper-body portrait, look directly at camera"
```

---

## Anti-clutter rules (enforced by the prompt template)

1. **Headline doesn't compete with visual.** Title is bold + large but doesn't overlap the photo. Negative space between zones.

2. **Details zone is hierarchical.** Date is largest in the details stack; CTA is bold but smaller than headline; location is smallest.

3. **No more than 4 text elements** total (title + subtitle + date + location/CTA). Past 4, the AI model crowds the composition.

4. **One typeface family per flyer.** Style anchor specifies the typeface category — the model picks the actual rendering.

5. **No mid-zone bleed.** Photo doesn't bleed into headline zone or details zone. Each zone is visually separate (margin or color block break).

These are baked into the prompt — you don't need to repeat them.

---

## Custom composition

If the default zone layout doesn't fit, override:

- `--composition center-stacked` — title centered + visual full-width + details centered (squarer feel)
- `--composition side-headline` — title on the side (landscape only — see above)
- `--composition photo-fullbleed` — visual zone fills the entire frame with text overlaid (more design-y, harder to read text)
- `--composition retro-poster` — chunky title at top, illustrated middle, details inside a colored box at bottom (1970s magazine ad feel)

These map to different prompt templates in `common/runners/cli/flyer.py`. v1 supports the first three; the rest are planned.

---

## Validation

The flyer-maker validates the assembled prompt before sending to the model:

- Headline word count (warn if >6, hard limit at 12)
- Details word count per element (warn if a single field > 15 words)
- Total text element count (warn if >4)
- Photo accessibility (if `--photo`, the file/URL must exist + be readable)

Warnings appear on stderr; hard limits exit non-zero.
