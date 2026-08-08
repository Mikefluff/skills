# logo-maker — calibration

3 example sessions.

---

## Example 1 — SaaS wordmark

### User says

> Сделай логотип для SaaS "Lunar Vault" — нужен wordmark, минималистичный, deep teal + warm cream палитра.

### Plan

```
logo-maker
  --brand "Lunar Vault"
  --style wordmark
  --palette "two tones — deep teal #1A4D5C and warm cream #F4E9D8"
  --variants 4
  --model ideogram-3-quality
  --execute
```

### What happens

1. Skill picks `ideogram-3-quality` for text-strong rendering.
2. Assembles 4 stochastic prompts of: "Logo wordmark: 'Lunar Vault' in clean geometric sans-serif, two-tone palette (deep teal letters, warm cream background), isolated on white background, no shadows, vector aesthetic, single horizontal lockup, designed to read at small sizes."
3. Batch runs 4 calls in parallel.
4. Outputs:
   - `./generated/logo/lunar-vault/logo-v1.png` through `logo-v4.png`
   - `manifest.json` with model + cost
   - `prompts.md`
5. Estimated cost ~$0.32.

### Next steps

1. Open all 4 in Preview side-by-side. Pick the best.
2. To get transparent BG: `bg-remover --image ./generated/logo/lunar-vault/logo-v2.png --output ./brand/wordmark.png --execute`.
3. To get SVG: open the PNG in Illustrator → Image Trace → expand.

---

## Example 2 — Illustrated coffee roaster mascot

### User says

> Need a logo for "Brooklyn Bean Co" — coffee roaster, illustrated mascot style, warm earthy palette.

### Plan

```
logo-maker
  --brand "Brooklyn Bean Co"
  --tagline "Roasted in Brooklyn since 2024"
  --style illustrated
  --palette "earthy palette — burnt orange, deep brown, cream paper, single sage green accent"
  --style-mod "vintage Americana feel, flat illustration aesthetic, single character mascot — friendly bean character holding a steaming cup"
  --variants 6
  --model gpt-image-2
  --execute
```

### What happens

1. Skill switches to `gpt-image-2` (better for illustrated logos with character).
2. Assembles 6 prompts cueing flat-illustration aesthetic, single mascot, vintage palette.
3. Higher variant count (6) because illustrated logos benefit from more selection options.
4. Outputs in `./generated/logo/brooklyn-bean-co/`.

### Notes

<!-- prices: batch=6 -->

- 6 variants × gpt-image-2 (medium) ≈ $0.30.
- Mascot logos REQUIRE selection — first run usually has 1-2 that "click", 4-5 that don't. Generate more variants than you think you need.

---

## Example 3 — Geometric emblem for architecture studio

### User says

> Эмблема для архитектурной студии "Axis & Atrium" — нужно ощущение Bauhaus, парметрика, геометрия.

### Plan

```
logo-maker
  --brand "Axis & Atrium"
  --style geometric
  --palette "monochrome black on white, single accent — chrome silver line"
  --style-mod "Bauhaus 1923 inspiration, intersecting triangles + circle, parametric construction, ampersand integrated into the geometric form"
  --variants 4
  --model gpt-image-2
  --execute
```

### What happens

1. Picks gpt-image-2 — better geometry handling than ideogram for this case.
2. Variants explore different intersecting geometries.
3. Outputs to `./generated/logo/axis-atrium/`.

### Anti-pattern (don't do this)

❌ "Modern minimalist clean professional logo for architecture firm"

This is too vague. The model defaults to generic options.

✓ Cue the era ("Bauhaus 1923 / Russian Constructivism / Swiss International Style"), the construction method ("intersecting triangles", "parametric grid"), and the visual signature ("single accent line in chrome silver").

---

## Anti-patterns (across examples)

### Mixing wordmark + illustrated in one batch

❌ `--style wordmark` + `--style-mod "with an illustrated coffee bean next to the text"`.

✓ Pick ONE direction. If you want both: generate wordmark + illustrated separately, then combine manually in a vector tool.

### Long brand names with cursive

❌ "Mont Blanc Vintage Vineyards Estate" + `--style typographic` with cursive script.

Result: garbled text in all variants.

✓ Abbreviate or pick a more legible typography style: `--style typographic --style-mod "blackletter / display sans / Bodoni didone — high legibility"`.

### Expecting trademark uniqueness

❌ "Generate me a logo that doesn't conflict with any existing trademark."

This skill cannot verify uniqueness. Always run a trademark search before commercial use.

### Too many text elements in emblem

❌ "BREW HOUSE EST 2024 ARTISAN COFFEE BROOKLYN NY HAND ROASTED SINCE FOREVER"

✓ 2 text rings max. Top: brand name. Bottom: founding year + city.
