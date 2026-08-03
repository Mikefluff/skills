# banner-maker — calibration

3 example sessions.

---

## Example 1 — SaaS launch (OG + LinkedIn ad)

### User says

> Запускаем новый SaaS — нужны OG-картинка для блога и LinkedIn ad. Headline "Ship 10x faster", CTA "Start free trial", бренд "Acme Cloud".

### Plan

```
banner-maker
  --headline "Ship 10x faster"
  --cta "Start free trial"
  --brand "Acme Cloud"
  --subhead "AI-native dev workflow"
  --presets og,linkedin-ad
  --style swiss-grid-poster
  --variants 2
  --model ideogram-3-quality
  --execute
```

### What happens

1. Skill picks `ideogram-3-quality` for text strength.
2. `swiss-grid-poster` anchor — white BG, black geometric sans, single accent CTA button.
3. 2 presets × 2 variants = 4 renders.
4. Outputs:
   - `./generated/banner/acme-cloud-launch/og.png` (1200×630)
   - `./generated/banner/acme-cloud-launch/linkedin-ad.png` (1200×627)
   - `manifest.json`, `prompts.md`, `style-used.md`
5. Estimated cost ~$0.32.

### Next steps

- Compress to JPG for upload (saves 50-70%).
- For Twitter card preview: use the og.png directly (same 1200×630 spec works).

---

## Example 2 — Google Display campaign (leaderboard + medium rectangle)

### User says

> Google Display campaign — нужны leaderboard и medium rectangle. Headline "Build faster", CTA "Try free", вибрант гражиент.

### Plan

```
banner-maker
  --headline "Build faster"
  --cta "Try free"
  --brand "Acme"
  --presets leaderboard,medium-rectangle
  --style gradient-mesh-modern
  --variants 3
  --execute
```

### What happens

1. `gradient-mesh-modern` style: vibrant gradient BG, white text, contrasting CTA.
2. 2 presets × 3 variants = 6 renders.
3. Outputs in `./generated/banner/acme-display/`.
4. Estimated cost ~$0.48.

### Notes

- Leaderboard (1456×180) → headline ONE line, CTA pill on the right.
- Medium-rectangle (600×500) → near-square, balanced composition.
- For Google Display upload: compress to <150 KB per banner. Use `pngquant` or convert to JPG.

---

## Example 3 — Conference event Twitter card

### User says

> Twitter header для нашей конференции — "DevConf 2026, Brooklyn, June 20-22", CTA "Get your ticket".

### Plan

```
banner-maker
  --headline "DevConf 2026"
  --subhead "Brooklyn · June 20-22"
  --cta "Get your ticket"
  --brand "DevConf"
  --presets twitter-card
  --style brutalist-grid
  --style-mod "high-energy, bold typography, slight grain texture, event-poster feel"
  --variants 3
  --execute
```

### What happens

1. `brutalist-grid` for high-energy event feel.
2. Single preset (twitter-card 1500×500) × 3 variants.
3. Composition accounts for left 30% (avatar overlay on mobile).
4. Outputs in `./generated/banner/devconf-2026/`.

### Notes

- For events, often better to use `flyer-maker --aspects landscape` if you want multiple aspects of the same event creative.
- This skill is for the Twitter header specifically — single preset, dialed for the platform.

---

## Anti-patterns (don't do this)

### Long headline in extreme-horizontal preset

❌ `banner-maker --headline "Build, ship, and scale your next great application in record time" --presets leaderboard`

Result: text crammed or truncated, illegible.

✓ Either shorten headline or drop the leaderboard preset.

### Verbose CTA

❌ `--cta "Click here to learn more about our amazing product today"`

Result: CTA overflows button, looks bad.

✓ "Learn more" / "Try free" / "Get demo" — 1-3 words max.

### Mixing many style anchors

❌ `--style swiss-grid-poster --style-mod "with gradient background and brutalist typography and editorial magazine layout"`

Result: confused composition, model can't reconcile.

✓ Pick ONE primary style. Add ONE small style-mod tweak. Don't pile.

### Expecting exact logo replication

❌ "Use my exact logo at exactly these pixel coordinates"

Result: image-gen models approximate; exact mark replacement is impossible.

✓ Generate banner WITHOUT logo. Composite your real logo on top in Figma / Affinity. Use `--logo <path>` only for brand-mark inspiration, not pixel-replication.

### Too many text elements

❌ `--headline "..." --subhead "..." --cta "..." --style-mod "with tagline, pricing, feature bullets, social proof"`

Result: cluttered banner, looks like spam.

✓ Headline + 1 subhead + 1 CTA. That's it. Save the bullets for the landing page.
