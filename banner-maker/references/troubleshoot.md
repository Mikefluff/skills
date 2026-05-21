# Troubleshooting — banner-maker

---

## Text doesn't fit in extreme aspects

**Symptom**: leaderboard (1456×180) shows text crammed / cut off.

**Cause**: headline too long for the preset's vertical real estate.

**Fix**:

1. Shorten headline to ≤5 words for leaderboard / mobile-banner.
2. Remove subhead for extreme-horizontal presets (no room).
3. Use `--style swiss-grid-poster` which auto-handles tight aspects best.

---

## CTA gets lost / blends with headline

**Symptom**: CTA isn't visually distinct from headline.

**Cause**: model interpreted CTA as another text element.

**Fix**:

1. Cue button explicitly: `--style-mod "CTA in a distinct colored rectangle button, contrasting accent color, visually separated from headline"`.
2. Pick a style with strong CTA convention: `--style swiss-grid-poster` defaults to button-CTA.
3. Use shorter CTA: "Start trial" (2 words) > "Start your free trial today" (5 words).

---

## Brand mark / logo is missing or weird

**Symptom**: brand wordmark renders incorrectly or in a strange position.

**Cause**: image-gen models struggle to place an exact logo file at exact coordinates.

**Fix**:

1. Use `--logo <photo>` AND a brand-strong model: `--model nano-banana-pro`.
2. Or accept "brand region" placement: skill places a generic "logo zone"; you composite your real logo on top in Figma / Affinity Designer.
3. For brand-mark-critical campaigns: generate banner WITHOUT logo, then overlay logo in design tool. Cleaner result.

---

## Output looks too generic / templates-y

**Symptom**: output looks like a generic stock banner.

**Cause**: prompt was too vague.

**Fix**:

1. Specify visual element: `--style-mod "with a single abstract geometric shape in the right third, brand accent color"`.
2. Specify palette: `--style-mod "deep navy + electric coral palette, no other colors"`.
3. Reference brand tone: `--style-mod "for a developer-tools brand, technical / precise feel"`.

---

## Headline text is misspelled

**Symptom**: "Ship 10× faster" rendered as "Ship 1Ox faster" or similar.

**Cause**: image-gen text hallucination. Worst with symbols (×, →, %, &) and very small text.

**Fix**:

1. Confirm `--model ideogram-3-quality` (text-strong default).
2. Avoid special symbols in headline. "Ship 10x faster" (lowercase x) renders more reliably than "Ship 10× faster".
3. Re-roll: more variants (`--variants 3`) increases odds.
4. For critical accuracy: generate banner WITHOUT headline (visual only), then add typography in a vector tool.

---

## Palette doesn't match brand

**Symptom**: brand palette ignored.

**Cause**: vague palette hint.

**Fix**: use hex codes in `--style-mod`:

```
--style-mod "exact palette: #1A4D5C deep teal background + #F4E9D8 cream text + #E07A5F coral CTA button"
```

Or switch to `--model flux-2-pro` (best palette obedience).

---

## File size too large for Google Display

**Symptom**: PNG is 2-5 MB, Google Display caps at 150 KB at 1× resolution.

**Cause**: PNG is uncompressed; Google expects JPG/optimized PNG.

**Fix**:

1. Compress: `pngquant input.png` or `tinypng.com` or `imageoptim` (Mac).
2. Convert to JPG for non-transparent banners (saves significant size).
3. The skill outputs at 2× retina — for 1× upload, scale down to half dimensions first.

---

## Twitter-card cropped weird

**Symptom**: profile header has key content hidden by avatar / mobile cropping.

**Cause**: composition didn't account for Twitter's UI overlays.

**Fix**:

1. Keep key content (headline / CTA) in right 70% of frame.
2. Use `--style-mod "composition-aware: leave left 30% empty for avatar overlay on mobile"`.

---

## Image-text policy violation (Facebook ad rejected)

**Symptom**: Facebook ad rejected for "too much text on image".

**Cause**: Facebook's 20%-text-area rule (relaxed in 2023 but still flagged).

**Fix**:

1. Lower text density: shorter headline, no subhead.
2. Use Facebook's text overlay checker (developers.facebook.com/tools/text-overlay).
3. Pure-visual banner with text-as-CTA-button only often passes.

---

## All presets look the same

**Symptom**: og / linkedin-ad / facebook-ad all look identical.

**Cause**: aspect ratios are very similar (~1.91:1) so models render similarly.

**Fix**: this is expected — those 3 platforms share the same OG-standard size. If you need distinct creatives per platform, run separate batches with different `--style` or `--style-mod`.

---

## Want animated banners

This skill is static PNG only. For animation:

1. Generate the static banner here.
2. Use a separate tool (Bannerbear, Crello, Canva) to add motion.
3. Or hand-author HTML5 banner with the static PNG as a base layer.

The skill doesn't support animated banners in v1 due to platform-spec complexity (HTML5 banner formats vary per network).

---

## Cost is higher than expected

3 presets × `ideogram-3-quality` ($0.08) = $0.24 per batch. If running many variants:

- 6 presets × 3 variants × $0.08 = $1.44 per batch
- Track via `--cost-only` before committing
- Budget cap: `SKILLS_CAROUSEL_BUDGET=1.50` (inherited)

---

## Want to A/B test variants

Generate 3+ variants per preset, then manually pick winners:

```
banner-maker --headline "Ship 10x faster" --cta "Try it" --presets og --variants 5 --execute
banner-maker --headline "Build, ship, sleep" --cta "Try it" --presets og --variants 5 --execute
```

Different headlines (2 batches) × 5 variants each = 10 candidates to A/B test.
