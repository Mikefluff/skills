# quote-card-maker — calibration

3 example sessions.

---

## Example 1 — Philosophy quote in editorial style

### User says

> Сделай цитату Кьеркегора "Anxiety is the dizziness of freedom." для постов в Instagram и Twitter — нужно editorial-magazine ощущение.

### Plan

```
quote-card-maker
  --quote "Anxiety is the dizziness of freedom."
  --attribution "— Søren Kierkegaard"
  --context "from The Concept of Anxiety, 1844"
  --aspects square,portrait
  --style minimal-serif
  --variants 1
  --model ideogram-3-quality
  --execute
```

### What happens

1. Skill picks `ideogram-3-quality` (text-strong; default).
2. Loads `minimal-serif` anchor: cream background, classical serif (Bodoni feel), italic attribution.
3. Assembles 2 prompts (square + portrait), each cueing 60-70% type dominance, attribution recedes.
4. Outputs:
   - `./generated/quote/kierkegaard-anxiety/square.png` (1080×1080)
   - `./generated/quote/kierkegaard-anxiety/portrait.png` (1080×1350)
   - `manifest.json`, `prompts.md`, `style-used.md`
5. Estimated cost ~$0.16.

### Next steps

- Schedule both via Buffer / Later — Twitter takes square, Instagram takes portrait.
- For a series: re-run with different Kierkegaard quotes, keeping same style for consistency.

---

## Example 2 — Marketing aphorism in vibrant style

### User says

> Quote card for LinkedIn — "The best time to plant a tree was 20 years ago. The second best time is now." — make it vibrant, contemporary, SaaS-energy.

### Plan

```
quote-card-maker
  --quote "The best time to plant a tree was 20 years ago. The second best time is now."
  --attribution "— Chinese proverb"
  --aspects square,landscape
  --style gradient-mesh-modern
  --style-mod "vibrant teal-to-violet gradient, modern geometric sans-serif, optimistic energy"
  --variants 2
  --execute
```

### What happens

1. `ideogram-3-quality` (default for text strength).
2. `gradient-mesh-modern` library anchor: vibrant gradient BG, geometric sans, white type.
3. 2 variants per aspect = 4 total renders.
4. Outputs in `./generated/quote/chinese-proverb-trees/`.
5. Estimated cost ~$0.32.

### Notes

- This quote is 17 words — at the upper edge. Still readable in square format, ideal in landscape.
- Landscape (1200×630) doubles as LinkedIn header / Twitter card preview.

---

## Example 3 — RU literature quote in russian-constructivist style

### User says

> "Если в первом акте на стене висит ружьё, то в последнем оно должно выстрелить." — Чехов. Сделай в конструктивистском стиле, story-формат для Instagram.

### Plan

```
quote-card-maker
  --quote "Если в первом акте на стене висит ружьё, то в последнем оно должно выстрелить."
  --attribution "— А.П. Чехов"
  --lang ru
  --aspects story
  --style russian-constructivist
  --style-mod "two-tone red and black on cream, heavy Cyrillic display type, single diagonal line accent"
  --variants 2
  --execute
```

### What happens

1. `--lang ru` triggers Cyrillic typography hint.
2. `russian-constructivist` library anchor: heavy Cyrillic display, red/black/cream palette.
3. Story format (1080×1920) — quote sits in upper-middle 60%, attribution at bottom.
4. 2 variants for selection.
5. Outputs in `./generated/quote/chekhov-gun/`.

### Anti-pattern (don't do this)

❌ Mix `--lang en` with a Russian quote — model attempts Latin-glyph approximation, looks bad.

✓ Always pass `--lang ru` for Cyrillic quotes.

❌ Long quote (60 words) in single quote-card. Result: text too small to read.

✓ Use `carousel-builder` for long-form quotes — split across multiple slides.

---

## Anti-patterns (across examples)

### Quote >20 words in single card

❌ A 40-word Tolstoy paragraph on one square card.

Result: type tiny, illegible on mobile.

✓ Use `carousel-builder --slides 3-4 --style minimal-serif` and split the paragraph across slides.

### Attribution longer than quote

❌ Quote: "Yes." Attribution: "— Anton Pavlovich Chekhov, Russian playwright and short-story writer, 1898 letter to Suvorin"

Result: attribution overwhelms the quote.

✓ Short attribution; long context goes in `--context` (which the prompt template renders as secondary).

### Wrong style for quote tone

❌ A heavy philosophical quote in `gradient-mesh-modern` (feels jarring — vibrant SaaS energy clashes with somber content).

✓ Match style to tone. Philosophical → minimal-serif or editorial-magazine.

### Expecting consistent results across many runs

The model is stochastic. Each `--variants 2` run gives 2 different interpretations. For a consistent series of quotes: pick the visual approach in the FIRST run, then run subsequent quotes with the same `--style + --style-mod` for visual consistency.
