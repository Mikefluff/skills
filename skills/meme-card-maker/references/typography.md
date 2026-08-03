# Typography conventions — meme-card-maker

The classic meme look is fundamentally about typography. Get this right and 80% of the meme works.

---

## The Impact convention

**Font**: Impact (or Impact-feel — Anton, Oswald Bold Condensed, Bebas Neue Bold as fallbacks).
**Color**: white fill.
**Outline**: thick black stroke (5-8% of font height).
**Case**: ALL CAPS (English). Mixed case for Cyrillic (`--lang ru`).
**Alignment**: centered horizontally.
**Placement**: top caption near top edge, bottom caption near bottom edge.

**Prompt cue** (built into all generated prompts):

> "white text with thick black stroke outline, Impact font, all caps, classic internet meme typography, centered, top caption at top edge and bottom caption at bottom edge"

---

## Why Impact specifically

- High legibility at low res (mobile, thumbnail previews)
- Bold-condensed shape allows long captions in narrow space
- Cultural canon — readers immediately recognize "meme"
- Stroke outline survives JPEG compression artifacts

Substitutes that work (less ideal):
- Anton (modern open-source Impact alternative)
- Oswald Bold Condensed
- Bebas Neue Bold

Substitutes that DON'T work for memes:
- Helvetica / Inter / system sans — too clean, reads "editorial"
- Serif fonts — wrong cultural vocabulary
- Display fonts — too distinctive

---

## When to deviate

### Use a different font when:

1. **Brand-specific meme campaign** — your brand has a distinct font and the joke benefits from on-brand identity. Use `--style-mod "use [Brand Font] in place of Impact, maintain bold + stroke convention"`.

2. **Multilingual / Cyrillic** — Impact has poor Cyrillic support. Default `--lang ru` switches to "geometric bold Cyrillic sans (Akrobat, Geometria, Bebas Neue Cyrillic) with white fill + black stroke".

3. **Deepfried / ironic memes** — these often deliberately use mangled Impact or other distorted fonts. Add `--style-mod "deepfried meme aesthetic, distorted typography, intentional low quality"`.

### Stroke outline rules:

- **Always present** on captions over busy backgrounds (most memes)
- **Optional** on clean / single-color backgrounds (rare meme situation)
- **Thickness** scales with font size — about 5-8% of the cap height

---

## Caption length rules

Per caption (top OR bottom):

- **Ideal**: 3-7 words
- **Max**: 10 words
- **Past 10**: text wraps to multiple lines + becomes hard to read. The point of meme typography is instant readability at thumbnail size.

If your joke needs >10 words per caption:
- Split into top + bottom (the natural meme structure)
- Or use `expanding-brain` (4 panels = 4 captions = up to 40 words total)
- Or reconsider whether it's a meme or a longer-form quote (use `quote-card-maker`)

---

## Punctuation conventions

- **No periods** — meme captions don't end with periods (kills the rhythm)
- **Em-dashes (—) and ellipses (...)** — work, but use sparingly
- **Exclamation marks** — use 1, max 2. "!!!!" reads as Boomer humor (which may be intentional)
- **Question marks** — fine, especially for "two-buttons" template

---

## Color variants

Default is white-on-black-stroke. Variants:

1. **Yellow-on-black-stroke** — for emphasis / "deepfried" feel
2. **Red-on-black-stroke** — for warnings / strong emphasis
3. **Black-on-white-stroke** — inverted, for special composition cases

Cue via `--style-mod "yellow fill with black stroke for the bottom caption only"`.

---

## Cyrillic-specific notes

For `--lang ru`:

1. **Don't ALL-CAPS Cyrillic** — harder to read than Latin ALL-CAPS due to letterform shapes.
2. **Use bold-condensed Cyrillic** — Bebas Neue Cyrillic, Geometria, Akrobat work well.
3. **Stroke convention identical** — white fill + black stroke.
4. **Mixed-case is OK** for Cyrillic memes — convention is less strict than English meme tradition.

Example: "КОГДА ПИШЕШЬ КОД В 3 НОЧИ" can render but "Когда пишешь код в 3 ночи" reads better.

---

## Multi-caption layouts

For templates with >2 captions (`expanding-brain`):

1. **Vertical stacking** — captions ordered top to bottom matching the visual panels.
2. **Same typography rules** apply to each.
3. **Visual hierarchy via size** — first / smallest panel can have smaller text; "galaxy brain" panel can have largest text.

The skill's v1 supports 2 captions natively. For 4-panel templates, encode all 4 in `--top` separated by ` / ` and the model will distribute them.
