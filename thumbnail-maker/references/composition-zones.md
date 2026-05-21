# Composition zones — thumbnail-maker

Per-placement templates for 16:9 thumbnails.

---

## Three placements

The skill ships with 3 default placements (variant per placement):

### `left` (face left, text right)

```
┌─────────────────────────────────────┐
│ ┌──────────┐                        │
│ │          │   BIG BOLD TITLE       │
│ │   FACE   │   SECOND LINE          │
│ │          │                        │
│ └──────────┘                        │
└─────────────────────────────────────┘
```

Face occupies left 40-50%. Title fills right 50-60%, large + bold.

### `right` (face right, text left)

Mirror of left. Face right, text left.

### `center` (face center-bottom, text top)

```
┌─────────────────────────────────────┐
│       BIG BOLD TITLE                │
│       SECOND LINE                   │
│                                     │
│         ┌──────────┐                │
│         │   FACE   │                │
│         └──────────┘                │
└─────────────────────────────────────┘
```

Title top 40%. Face center-bottom occupying 40-50% width.

---

## Other placements (opt in)

- `top` — face top, text bottom (inverted from `center`)
- `bottom` — face bottom-band only (less common, used for product showcases)
- `face-only` — no text, full-frame face (rare; usually you want text)
- `text-only` — no face, full-text thumbnail (use when no photo provided)

---

## Composition prompt fragment

For `left` placement:

> 16:9 YouTube thumbnail composition. Subject's face (from reference photo) on the LEFT 40-50% of frame, looking toward camera or slightly off-camera with engaging expression. Bold display title "<TITLE>" fills the RIGHT 50-60% of frame, in high-contrast color with stroke or drop-shadow for readability against any background. Vibrant + high-saturation color palette. Subject's expression should feel inviting / curious / surprised — NOT artificial shock. Background can be simplified / abstracted to keep focus on subject and text.

For `right`: same but mirror.

For `center`: face center-bottom + title top-half.

---

## Without a face photo

If no `--photo` provided, the skill generates a thumbnail with:

- Big title dominant (75% of frame)
- Optional illustrative element (a single icon / shape / object related to title)
- High-contrast palette

The "face placement" variants still apply but they vary the illustrative element placement instead.

---

## Typography conventions

- **Headline**: bold display sans-serif (Inter Bold, Helvetica Bold, IBM Plex Sans Bold, etc.) by default
- **Stroke or drop shadow** by convention — improves readability against varied backgrounds
- **Bright color** (yellow / red / cyan / orange) for top-of-mind contrast
- **Sentence case or Title Case** — ALL CAPS works for high-energy / sports / drama content; sentence case for educational / calm
- **Max 7 words** — past that, becomes illegible at thumbnail scale

---

## Variants per placement

Default `--variants 1` (single take per placement = 3 total).

Bump to `--variants 3` for 9 total (3 placements × 3 takes each). Useful when:

- The first set didn't feel right and you want more options
- A/B testing thumbnail performance after publishing

Past 9 total, you're probably over-spending. Iterate on copy / style instead.

---

## Anti-clutter

1. **One face per thumbnail.** Multiple faces compete.
2. **One title per thumbnail.** No subtitle unless really needed.
3. **High contrast.** Title must read at 320×180px (mobile thumbnail).
4. **No more than 2 text elements** total.
5. **Background simplified.** Don't compete with face / title.

---

## Per-type variations

### `--type youtube` (default)

- 1920×1080
- Vibrant + high-saturation
- Bold typography with stroke/shadow
- Face + title aesthetic

### `--type blog`

- 1200×630 (OG image standard)
- More editorial / restrained
- Photographic OR illustrative
- Smaller more elegant typography

### `--type podcast-episode`

- 1920×1080
- Brand-consistent with the main podcast cover (use same `--style`)
- Episode-specific title overlay
- Guest face if a guest is featured

These are softer biases on the same template — not radically different layouts.
