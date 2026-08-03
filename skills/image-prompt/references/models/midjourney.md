# Midjourney models

Aesthetic-first generator. V8.1 became the default in June 2026; v7 remains selectable.

---

## Midjourney V8.1

**Strengths**: best aesthetic / editorial / "vibes" / brand-design output; strongest "wow" factor; faster than v7 with tighter prompt following.
**Weaknesses**: text-in-image still poor; multi-subject compositions still drift; weaker at strict instruction-following than gpt-image-2 or Nano Banana 2.
**Execute via**: prompt-only — no public API. Web / Discord only.

### Syntax

Parameters use `--` flags:
- `--ar 16:9` — aspect ratio (default 1:1). Common: `16:9`, `9:16`, `4:5`, `2:3`, `3:2`
- `--s 250` — stylization 0-1000, default 100. Lower in V8 / v7 than v6.
- `--c 50` — chaos 0-100, higher = more variation between grid tiles
- `--w 0-3000` — weirdness, pushes unusual aesthetics
- `--no text, watermark` — negative prompt (comma-separated)
- `--raw` — drops the default Midjourney stylization, much more photoreal
- `--sref <code>` — style reference by code; `--sref random` for a random style code
- `--oref <url>` — Omni Reference (character / identity lock, replaces v6's `--cref`); costs 2× GPU minutes; not compatible with Fast / Draft / Conversational modes or `--q 4`
- `--p` — personalization profile (your trained taste)

### Prompt template

```
{subject + action + context}, {style tags}, {lighting}, {camera}, {texture} --ar 16:9 --s 100 --raw --sref <code> --no text, watermark, distorted anatomy
```

### Example

```
A confident business person leaning on marble countertop, sunlit Brooklyn loft kitchen, editorial photo, soft directional key light from window upper-left, 85mm lens f/1.8, full-frame DSLR, natural skin texture, visible pores, sharp focus on eyes, cinematic color grading --ar 4:5 --s 100 --raw --no text, watermark, distorted anatomy, plastic skin
```

With character lock:
```
<same prompt> --oref https://cdn.example.com/founder-headshot.jpg --ar 4:5 --raw
```

### Notes

- `--raw` is the single biggest lever for photoreal — default v7 is still slightly painterly
- Use `--oref` when you need the SAME person/character across shots; use `--sref` when you need the same LOOK (lighting / palette / mood) but a different subject
- `--oref` is GPU-expensive — batch only the keepers
- For people: still add "natural skin texture, visible pores, no plastic skin" — v7 skin is better but defaults remain smooth
- Text-in-image: don't bother, overlay in a design tool

---

## Midjourney v7 (legacy)

**Execute via**: prompt-only — no public API. Web / Discord only.

- Still selectable, and still the better-documented model.
- Same flag system as V8.1 — `--oref`, `--sref`, `--raw`, `--ar`, `--s`, `--c`, `--no` all carry over.
- Pin to v7 when an existing brand set was built on it; V8.1 renders the same prompt
  a little differently, which is exactly the drift you do not want mid-campaign.

---

## v6 → v7 migration

- `--cref` is gone; replaced by `--oref` (Omni Reference) for character / identity lock.
- Default stylization shifted lower; old `--s 250` prompts now read as overstyled.
- `--raw` is retained and still the photoreal switch.
- Reroll behavior differs — v7 rerolls land closer to the original grid; use `--c` for variation.
- `--style raw` (v6 form) still parses but `--raw` is the v7 canonical flag.
