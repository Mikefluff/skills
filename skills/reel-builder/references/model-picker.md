# Model picker — video + music providers for reels

> Per-unit prices below are illustrative; the canonical table is
> [`common/references/model-pricing.md`](../../../common/references/model-pricing.md),
> generated from `common/runners/cost.py` — the same table that estimates your bill.
> Batch figures here are that unit price times the item count.

Decision trees for `--video-provider auto` and `--music-provider auto`.

---

## Video provider decision tree

```
1. --shot-duration > 8?
     yes → require provider with max ≥ shot-duration:
       (a) up to 10s: kling-3 / runway-gen-4-5 / runway-gen-4
       (b) up to 15s: kling-3 (only remaining long-shot option)
     no → all providers OK

2. Has shots with on-camera dialogue?
     yes → require provider with native audio + dialogue:
       veo-3-1 / veo-3-1-fast / veo-3-1-lite / kling-3
       (NOT runway-gen-4 / gen-4-5 — visual only)
     no → all OK

3. Style anchor implies high motion / dynamic camera?
     prefer veo-3-1 (best at complex camera moves)
     OR runway-gen-4-5 (best at long sustained motion)

4. Style anchor implies static / atmospheric?
     prefer kling-3 (excellent at locked-frame style)
     OR runway-gen-4 (good static control via Aleph keyframes)

5. Budget constrained or iterating?
     prefer veo-3-1-fast or runway-gen-4-turbo (cheaper)

6. Multi-shot with character carry-over?
     prefer kling-3 (Elements supports image-ref between shots)
     OR runway-gen-4 (Act-One identity preservation)

7. Available env vars?
     drop candidates whose env vars are missing
     fallback: fal-video / replicate router
```

### Default pick

`auto` with default settings (3 shots × 5s × vertical, no dialogue, captions on, instrumental music):
- **First choice**: `veo-3-1` if GEMINI_API_KEY is set (best balance of quality, cost, dialogue support).
- **Second choice**: `kling-3` if KLING keys set (good static + identity carry-over).
- **Third choice**: `runway-gen-4-turbo` if RUNWAY_API_KEY set (cheapest, visual-only).
- **Fallback**: `fal-video` or `replicate-video` router.

If user passes `--video-provider <slug>` explicitly: override the tree, validate env vars, exit if missing.

---

## Video capability matrix

| Slug | Provider | Max duration | Native audio | Dialogue | Image-ref | Identity carry-over | Cost / second | Latency |
|---|---|---|---|---|---|---|---|---|
| `veo-3-1` | Google | 8s | yes | yes | yes (I2V) | medium | $0.40 | 60-90s |
| `veo-3-1-fast` | Google | 8s | yes | yes | yes | medium | $0.12 | 30-60s |
| `veo-3-1-lite` | Google | 8s | yes | yes | yes | medium | $0.08 | 20-45s |
| `kling-3` | Kling AI | 15s | yes | yes | yes (Elements) | excellent | $0.12 | 45-90s |
| `runway-gen-4` | Runway | 10s | no (visual only) | no | yes | good (Act-One) | $0.10 | 45-90s |
| `runway-gen-4-5` | Runway | 10s | no (visual only) | no | yes | good | $0.12 | 45-90s |
| `runway-gen-4-turbo` | Runway | 10s | no | no | yes | good | $0.05 | 30-60s |
| `sora-2` | OpenAI | 10s | yes | yes | yes (cameos) | excellent (cameos) | $0.10 | **retired 2026-09-24** |
| `sora-2-pro` | OpenAI | 20s | yes | yes | yes | excellent | $0.50 | **retired 2026-09-24** |
| `aleph` | Runway | 10s (V2V edit) | source-dependent | n/a | yes (source video) | excellent | $0.18 | 60-90s |
| `fal-video` | fal.ai router | varies | varies | varies | varies | varies | $0.05-0.40 | varies |
| `replicate-video` | Replicate router | varies | usually no | no | sometimes | varies | $0.03-0.20 | varies |

---

## Music provider decision tree

```
1. Music style frontmatter `vocal_friendly: true` AND `--video-instrumental off`?
     → suno-v5-5 (best vocals, two-box)
     OR udio-v4 (longer-form, alternative)

2. Music style frontmatter `vocal_friendly: false` (instrumental genres)?
     → stable-audio-2-5 (best for instrumental + sound design)
     OR lyria-3-pro (clean licensing, orchestral)

3. `cinematic-orchestral` genre specifically?
     → lyria-3-pro (most license-clean for commercial)

4. Need exclude-styles control?
     → eleven-music (only one with explicit exclude-styles param)

5. Free / fastest / lowest quality OK?
     → musicgen (via replicate router) or stable-audio-open

6. Available env vars?
     drop candidates missing keys
     fallback: replicate-music
```

### Default pick

`auto` with default settings (`--video-instrumental on` for reels):
- **First choice**: `stable-audio-2-5` if STABLE_AUDIO key set (but unusual — usually goes through fal/replicate)
- **In practice**: `eleven-music` if ELEVENLABS_API_KEY is set — it is the only vocal-capable music model here with a first-party API. `suno-v5-5` needs a third-party gateway (`SUNO_API_URL`), so it is not a default.
- **Second**: `lyria-3-pro` if GEMINI + LYRIA_API_ENABLED=1 — clean licensing, best for orchestral. For a reel under 30s, `lyria-3-clip` is the cheaper tier.
- **Fallback**: `replicate-music` router (MusicGen).

---

## Music capability matrix

<!-- prices: batch=0.5 -->

| Slug | Provider | Max duration | Vocals | Instrumental | Exclude-styles | Cost per song | Latency | Notes |
|---|---|---|---|---|---|---|---|---|
| `suno-v5-5` | Suno (gateway) | ~4 min | excellent | yes | no | $0.10 | 30-60s | Two-box; English-strong; needs SUNO_API_URL — no official API |
| `udio-v4` | Udio | ~10 min | excellent | yes | no | $0.20 | 60-90s | Longest coherent songs |
| `lyria-3-pro` | Google | 3 min (hard cap) | yes | yes | no | $0.10/min | 30-90s | Field-driven; clean licensing; refuses artist mimicry |
| `lyria-3-clip` | Google | 30 sec | yes | yes | no | $0.05/clip | 15-40s | Speed tier — right size for a single reel bed |
| `eleven-music` | ElevenLabs | 10 min | good | yes | yes | $0.20/min | 30-90s | Runs music_v2. Exclude-styles is its differentiator |
| `stable-audio-2-5` | Stable Audio | ~3 min | weak (don't ask) | excellent | no | $0.05-0.10 | 20-60s | Best for sound design / instrumental |
| `musicgen` | Meta (via Replicate) | ~30s typical | poor | OK | no | $0.02-0.05 | 20-60s | Open-weights; lowest quality |

---

## Cost preview for a 15s reel (3 shots × 5s + 17s music)

Typical:

| Video | Music | Total |
|---|---|---|
| veo-3-1 × 3 = 15s × $0.40 = $6.00 | eleven-music = $0.07 | $6.07 |
| veo-3-1-fast × 3 = 15s × $0.12 = $1.80 | eleven-music = $0.07 | $1.87 |
| kling-3 × 3 = 15s × $0.12 = $1.80 | stable-audio = $0.10 | $1.90 |
| veo-3-1-lite × 3 = 15s × $0.08 = $1.20 | musicgen = $0.05 | $1.25 |
| runway-gen-4-turbo × 3 = 15s × $0.05 = $0.75 | musicgen = $0.05 | $0.80 |

Default budget cap: `SKILLS_REEL_BUDGET=4.00`. Override or pass `--yes`.

### Sora is leaving

OpenAI removes the Videos API and both Sora slugs on **2026-09-24**, with no
successor. They stay in the table above because they still run until then, and
they warn on every call. Reels that relied on Sora for >8s shots should move to
`kling-3` (15s); reels that relied on cameos should move to Kling Elements.

---

## When to override `auto`

Override video:
- **`veo-3-1`**: needed for best-quality reel, willing to pay
- **`veo-3-1-fast`**: iterating fast, accept slightly lower quality
- **`veo-3-1-lite`**: cheapest tier that still has audio
- **`kling-3`**: >8s single shot, locked-frame style, character carry-over
- **`runway-gen-4-5`**: sharpest motion when audio is not needed
- **`runway-gen-4`**: need V2V (modify existing footage) — use `aleph` mode
- **`runway-gen-4-turbo`**: cheapest visual-only

Override music:
- **`suno-v5-5`**: vocal-friendly genres, two-box flexibility — needs a gateway URL
- **`lyria-3-pro`**: commercial use, label-clean
- **`eleven-music`**: exclude-styles control, polished single-prompt
- **`stable-audio-2-5`**: pure instrumental, sound design focus

---

## "But what if no env vars are set?"

1. `--check`: tells you what's set and what's missing.
2. `--prompts-only`: skips execution, saves script.md + per-shot/music prompts. User can paste manually into provider UIs.
3. Setting up: easiest entry is `GEMINI_API_KEY` (covers Veo 3.1 + Lyria + Imagen for image-prompt) and `SUNO_API_KEY+SUNO_API_ENABLED=1` for music. Combined: ~$0.10-2.50 per 15s reel.
