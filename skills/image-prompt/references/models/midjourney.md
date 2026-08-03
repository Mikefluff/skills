# Midjourney models

Aesthetic-first generator. v7 is GA, v8 in early access.

---

## Midjourney v7

**Strengths**: best aesthetic / editorial / "vibes" / brand-design output; strongest "wow" factor; refined coherence over v6.
**Weaknesses**: text-in-image still poor; multi-subject compositions still drift; weaker at strict instruction-following than gpt-image-2 or Imagen 4.
**Execute via**: prompt-only — no public API. Web / Discord only.

### Syntax

Parameters use `--` flags:
- `--ar 16:9` — aspect ratio (default 1:1). Common: `16:9`, `9:16`, `4:5`, `2:3`, `3:2`
- `--s 250` — stylization 0-1000, default 100. Lower in v7 than v6.
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

## Midjourney v8 (preview)

**Execute via**: prompt-only — no public API. Web / Discord early-access only.

- In early access at time of writing, not GA.
- Mostly aesthetic refinement over v7; same flag system.
- No production use yet — outputs are subject to change.
- Wait for GA before locking brand workflows on it.
- Knowledge of v8-specific flags is still thin; treat as v7 + better aesthetics.

---

## v6 → v7 migration

- `--cref` is gone; replaced by `--oref` (Omni Reference) for character / identity lock.
- Default stylization shifted lower; old `--s 250` prompts now read as overstyled.
- `--raw` is retained and still the photoreal switch.
- Reroll behavior differs — v7 rerolls land closer to the original grid; use `--c` for variation.
- `--style raw` (v6 form) still parses but `--raw` is the v7 canonical flag.
