# Model picker — gif-maker (Mode B)

For generation mode (`--prompt --model`). Mode A doesn't pick a model — it converts.

## Default: `veo-3-1-fast`

Cheapest fast video generation. Output: 720p MP4, 5-8 seconds default (we trim to 1-3s for GIF).

| Strength | Score |
|---|---|
| Cost | best (~$0.40/sec) |
| Speed | fast (~30s wall time) |
| Motion quality | very good |
| Photoreal | excellent |
| Animation / cartoon | good (improving) |

**Use for**: most short loops, social GIFs, lightweight quick generations.

---

## Best motion: `kling-3`

Kling AI 3.0 — currently best in class for smooth, cinematic motion. Output: 1080p MP4 at higher fidelity.

| Strength | Score |
|---|---|
| Cost | medium (~$0.50/sec) |
| Speed | medium (~60s wall time) |
| Motion quality | best |
| Photoreal | excellent |
| Animation / cartoon | very good |
| Camera moves | best (best at slow pans/zooms) |

**Use for**: client-facing GIFs, hero loops, anything where motion smoothness matters.

---

## Animation-focused: `fal-video`

Fal.ai hosted models — pass `--replicate-model` or `--fal-model` to pick a specific animation-focused model:

- `fal-ai/hunyuan-video` — abstract / artistic motion
- `fal-ai/ltx-video` — fast generation
- `fal-ai/wan-2-1` — motion-focused
- `fal-ai/mochi-1` — Mochi (Stanford)

**Use for**: stylized / abstract loops, when you need a specific model behavior not in Veo / Kling.

---

## Premium: `sora-2`

OpenAI Sora 2 — currently behind feature flag `SORA_ENABLED=1`.

| Strength | Score |
|---|---|
| Cost | high (~$1.00/sec) |
| Speed | slow (~90s wall time) |
| Motion quality | best |
| Photoreal | best |
| Long-take coherence | best |

**Use for**: when nothing else works. Most short-loop use cases don't need Sora's expense.

---

## Avoid for GIFs

- **Runway Gen-4 / Gen-4 Turbo / Aleph**: great for full reels (8-30s), overkill for 2-3s loops. Use them via reel-builder, not gif-maker.
- **`replicate-video`** unless you have a specific Replicate model in mind — most hosted Replicate video models are slower and lower quality than Veo/Kling.

---

## Cost guide (Mode B)

Approximate, May 2026.

| Provider | Per-second cost | 3-sec total |
|---|---|---|
| `veo-3-1-fast` | $0.40 | $1.20 |
| `veo-3-1` | $0.50 | $1.50 |
| `kling-3` | $0.50 | $1.50 |
| `fal-video` (varies) | $0.20-0.60 | $0.60-1.80 |
| `gen-4-turbo` | $1.00 | $3.00 |
| `sora-2` | $1.00 | $3.00 |
| `sora-2-pro` | $2.00 | $6.00 |

For exploratory work: `veo-3-1-fast`. For shipping: `kling-3` or `veo-3-1`.

---

## Tips for GIF-friendly prompts

GIFs benefit from:

- **Looping motion**: "subject moves left to right, then back — seamless loop"
- **Limited palette**: "flat illustration, 4-color palette" (renders cleanly in 256 colors)
- **Abstract / cartoon**: avoids photoreal banding
- **Short, simple**: 2-3 seconds, single action, no complex narrative

Less ideal:

- Photoreal portraits with subtle lighting → bands when converted to GIF
- Complex multi-subject scenes → too much detail lost in 256 colors
- Slow zooms on photoreal content → motion looks fine, but gradient banding shows
