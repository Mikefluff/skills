# style-suggest — before/after calibration runs

3 example invocations showing how text descriptions / reference images become structured library entries.

---

## Example 1 — text-only description → new style

### User input

```
style-suggest --describe "Nordic minimalism — snow-white background with subtle warm-gray paper grain, a single pop of vermillion red accent, geometric sans-serif typography (think Helsinki magazine / Marimekko-era restraint), generous negative space, asymmetric grid with thin black hairlines, occasional small geometric primitives (circle, square, triangle) as decorative anchors. The mood is calm, considered, expensive-quiet. Use for premium B2B / Scandinavian-brand content / mindful-tech communication."
```

### LLM analysis (excerpt)

> **Decision**: `action=new`, no existing style covers Nordic / quiet-premium territory. Closest mismatches: `art-deco` (ornamental luxury vs restrained luxury), `glamour` (glossy vs matte-quiet), `blueprint` (technical-engineering vs editorial-quiet), `brutalist` (harsh-critique vs calm-premium).
>
> **Suggestion**: full entry with id=`NORDIC-MINIMAL`, slug=`nordic-minimal`, name="NORDIC MINIMAL / QUIET-PREMIUM", all 9 schema fields populated, body_notes with "When NOT to use" + "Variation hints", auto_pick_signal mapping for the matrix.

### Saved files

- `common/visual-prompt-library/styles/nordic-minimal.md` (full frontmatter + body)
- `_index.md` row appended
- `_auto-pick.md` row appended

### Downstream usage

```
carousel-builder --style nordic-minimal --topic "<your-topic>"
cover-maker --style nordic-minimal --title "<your-title>" ...
```

The new style is immediately available across all 6 visual skills via the shared chain — no other code changes.

---

## Example 2 — reference image → new style (hypothetical, when --ref provided)

### User input

```
style-suggest --ref ~/Downloads/wes-anderson-grand-budapest-still.jpg --describe "the aesthetic of this film still"
```

### LLM analysis (excerpt)

> The image attached shows a symmetrical pastel composition with rose-pink and butter-yellow tones, central architectural framing, slightly oversaturated palette, frontal flat camera framing, and miniaturist set-design feel. The image is base64-encoded and passed to the multimodal model (Anthropic Claude / GPT-4o) as a separate content part.
>
> **Decision**: `action=new`, no existing style covers symmetric-pastel-miniature territory. The closest is `vaporwave` (ironic kitsch) but vaporwave is gradient-electronic while this is matte-pastel-architectural.
>
> **Suggestion**: full entry with id=`SYMMETRIC-PASTEL`, slug=`symmetric-pastel`, typography like "thin geometric display + italic typewriter mono", composition signatures like "centered architectural framing / dollhouse-flat composition / quartet of pastel rectangles / lower-third gold ribbon", elements like "miniature buildings, vintage signage, pastel awnings, butter-yellow accents, rose-pink panels...".

The user is told NOT to inject the name "Wes Anderson" into image-gen prompts (image models may infringe), but the body_notes can reference "films like Grand Budapest Hotel" for orientation only.

---

## Example 3 — duplicate detection (no save)

### User input

```
style-suggest --describe "deep academia vibe — leather-bound books, ivy-covered libraries, oxblood and forest-green palette, serif typography, candle-lit warmth, a sense of long study and old wisdom"
```

### LLM analysis (excerpt)

> **Decision**: `action=duplicate`, matchId=`scientific`, similarity=0.78
>
> **Reasoning**: The existing `scientific` style covers the academic-serif-restrained-credible register comprehensively (classical Caslon-style serif, journal-page asymmetry, deep institutional blue / burgundy / forest green accents, manila cream background). The user's "deep academia" vocabulary maps directly to `scientific` with a hint of darker-tone variation; not different enough to warrant a separate library entry. Recommend using `--style scientific` directly, optionally with `--style-mod "darker register, candle-lit warmth, oxblood and ivy-green accents instead of institutional blue"`.

### What the skill prints

```
DUPLICATE detected (similarity 0.78):
  Existing style: scientific
  Reasoning: ...
  Suggested invocation: --style scientific --style-mod "darker register, candle-lit warmth, oxblood and ivy-green accents instead of institutional blue"

Pass --force-new if you want to create a separate library entry anyway.
```

No files written. No `_index.md` / `_auto-pick.md` changes.
