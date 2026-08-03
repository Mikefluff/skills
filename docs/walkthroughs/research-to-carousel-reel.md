---
title: "Research → carousel → reel (end-to-end)"
persona: "Founder / marketer building content from research"
time: "6-15 minutes"
skills:
  - research-brief
  - carousel-builder
  - reel-builder
  - image-prompt
  - video-prompt
  - music-prompt
---

# Walkthrough — research → carousel → reel (end-to-end)

You have a topic. You want to:
1. Gather context with cited sources (research-brief).
2. Turn it into an 8-slide carousel for LinkedIn (carousel-builder).
3. Turn it into a 15-second vertical reel for Instagram / TikTok (reel-builder).

All three skills compose. The research brief feeds both downstream skills via `--research <path>`.

Time budget end-to-end: 5-15 minutes wall time depending on depth, model choice, and API latency. Cost: $0-$10 depending on what you execute (research is free; carousel ~$0.50; reel ~$2-5).

---

## Step 0 — One-time setup

1. Install (if not done):
   ```bash
   curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash
   ```

   The installer copies skills + style library + auto-creates `.runners-venv` with Python deps. For reel-builder, it also offers to install ffmpeg.

2. Set the env vars for providers you want to use. Pick a subset:
   ```bash
   export GEMINI_API_KEY=...         # Veo 3.1 + Imagen + Nano Banana Pro + Lyria 3 Pro
   export OPENAI_API_KEY=...         # gpt-image-2 + Sora 2 + TTS
   export BFL_API_KEY=...            # Flux 2 Pro / Flux Kontext / Flux Schnell
   export SUNO_API_KEY=...           # Suno music
   export SUNO_API_ENABLED=1         # explicit opt-in (anti-accidental-spend gate)
   export LYRIA_API_ENABLED=1        # if using Lyria
   ```

   See `.env.example` in the repo for the full matrix. Skills stay prompt-only for any provider whose key isn't set — no crashes, just falls back to printing the prompt for manual paste.

---

## Step 1 — Research

In a new Claude Code session, say:

> research-brief "AI productivity tools for solo founders in 2026" --depth standard --for carousel

Claude invokes the `research-brief` skill. It:
1. Runs 7-10 WebSearch queries across 4-5 clusters (foundational / recent / contrarian / data).
2. WebFetches the top results.
3. Synthesizes TL;DR + Key facts (cited) + Notable quotes + 3 Suggested angles + Open questions.
4. Saves to `./generated/research/ai-productivity-tools-solo-founders-20260521.md`.

Output (stdout):
```
Brief written to ./generated/research/ai-productivity-tools-solo-founders-20260521.md
(11 sources, TL;DR: Solo founders in 2026 have shifted from agentic-...)
```

Cost: $0 (WebSearch + WebFetch are free).

Time: 2-4 minutes.

If you want a deeper dive (more sources, longer brief):
> research-brief "<topic>" --depth deep --format article-ready

---

## Step 2 — Carousel from the brief

Continue in the same session:

> carousel-builder --research ./generated/research/ai-productivity-tools-solo-founders-20260521.md --platform linkedin --slides 8 --style auto --model auto --execute

Claude invokes `carousel-builder`. It:
1. Reads the brief. Picks angle #1 from the Suggested angles.
2. Splits into 8 slides: hook → 5 points (drawn from Key facts) → quote slide → CTA.
3. `--style auto`: derives tags `[tech, b2b, professional, modern]` → picks `kinfolk-minimal` (top library match for LinkedIn editorial). Logs `swiss-grid-poster`, `gradient-mesh-modern` as alternatives.
4. `--model auto`: chooses `flux-2-pro` (best overall consistency for non-text-heavy carousels).
5. Builds 8 per-slide prompts (style anchor + slide content + composition hint + aspect 1:1 for LinkedIn).
6. Estimates total cost: 8 × $0.06 = $0.48. Under default $1.50 carousel budget — no confirmation prompted.
7. Runs batch with parallelism 3. ~50s wall time.
8. Composes captions.md with LinkedIn structure: 200-char hook + 3-para body + question CTA + 4 hashtags. Per-slide alt-text.

Output:
```
./generated/carousel/ai-productivity-tools-solo-founders/
  slide-1.png ... slide-8.png   (1080×1080 each, ~250KB)
  captions.md                    (LinkedIn paste-ready)
  manifest.json                  (for --resume)
  style-used.md                  (snapshot for reproducibility)
  prompts.md                     (per-slide prompts for manual fallback)
```

stdout:
```
Carousel: ./generated/carousel/ai-productivity-tools-solo-founders/  (8/8 slides succeeded)
Captions: ./generated/carousel/ai-productivity-tools-solo-founders/captions.md
```

Cost: $0.48.

Time: 1 minute.

### Variations

If you want Instagram (4:5 portrait + embedded text):
> carousel-builder --research <path> --platform instagram --text-mode embedded --style swiss-grid-poster --model ideogram-3-quality --execute

If you want to preview prompts before spending:
> carousel-builder --research <path> --prompts-only

Saves `prompts.md` only. Inspect, then run with `--execute` if satisfied.

If a slide failed:
> carousel-builder --resume --output ./generated/carousel/<slug>/

Re-runs only the failed slides from manifest.

---

## Step 3 — Reel from the same brief

Continue:

> reel-builder --research ./generated/research/ai-productivity-tools-solo-founders-20260521.md --shots 3 --shot-duration 5 --style chazelle-musical-glow --music-style cinematic-orchestral --aspect vertical --captions on --execute

Claude invokes `reel-builder`. It:
1. Reads the brief. Picks ONE angle suitable for video narrative.
2. Drafts a 3-shot screenplay (via viral-text template):
   - Shot 1 (hook, 0-5s): close-up hands on laptop, golden-hour. Caption: "The solo stack."
   - Shot 2 (beat, 5-10s): wider scene with 4 tools visualized. Caption: "73% of founders use 4+ tools."
   - Shot 3 (payoff, 10-15s): subject closes laptop, smile. Caption: "Save 8 hours a week."
3. Resolves video style: `chazelle-musical-glow` from library — kinetic, magic-hour, Steadicam. Anchor appended to all 3 shot prompts.
4. Resolves music style: `cinematic-orchestral` — Lyria 3 Pro field-driven prompt with strings + brass swell.
5. Provider auto-pick: video → `veo-3-1` (kinetic-friendly + dialogue + native audio). Music → `lyria-3-pro` (clean licensing).
6. Estimate: 3 × 5s × $0.40 (Veo) + 17s × $0.10/min (Lyria) = $6.00 + $0.03 = $6.03. **Over** default $4.00 reel budget — confirmation prompted: "Batch: 4 reel items, total estimated cost $6.0300 USD. WARNING: exceeds default reel budget ($4.00). Proceed? [y/N]". You answer `y`.
7. Generates 3 shots in parallel (parallelism 2) + music concurrently. ~120s wall time.
8. ffmpeg concat shots → mix Lyria track → burn 3 captions → final.mp4.

Output:
```
./generated/reel/ai-productivity-tools-solo-founders/
  final.mp4              (15s, 1080×1920, ~3-5MB)
  shots/
    shot-1.mp4
    shot-2.mp4
    shot-3.mp4
  music.mp3              (17s)
  script.md
  manifest.json
  style-used.md
```

stdout:
```
Reel: ./generated/reel/ai-productivity-tools-solo-founders/final.mp4
Components: ./generated/reel/ai-productivity-tools-solo-founders/{shots/, music.mp3, script.md}
```

Cost: $6.03 (over budget — you confirmed).

Time: 2-3 minutes.

### Variations

If you want cheaper:
> reel-builder --research <path> --video-provider veo-3-1-fast --music-provider stable-audio-2-5 --execute

Cost drops to ~$2.30.

If you want longer:
> reel-builder --research <path> --shots 4 --shot-duration 5 --execute

20s reel, +$2.

If you want to preview the script/prompts only:
> reel-builder --research <path> --prompts-only

Saves `script.md` without running providers.

---

## Step 4 — Post

You now have:
- 8 LinkedIn carousel slides in `./generated/carousel/.../slide-*.png` + captions in `captions.md`
- 15-second vertical reel in `./generated/reel/.../final.mp4`
- Research brief with cited sources at `./generated/research/...md` (useful for fact-checking comments)

### Step 4 — publish

`post-publisher` takes either output directory and sends it. Nothing goes out
without a confirmation: dry-run is the default, and `--yes` still asks per
platform.

```bash
# see what would happen, change nothing
post-publisher ./generated/carousel/<slug>/ --platform linkedin,instagram

# stage the Instagram post without publishing it
post-publisher ./generated/carousel/<slug>/ --platform instagram --draft --yes

# the reel into TikTok's inbox, to finish in the app
post-publisher ./generated/reel/<slug>/ --platform tiktok --draft --yes
```

The caption is read from `captions.md` automatically — check what it extracted
in the dry-run preview before adding `--yes`.

Accounts have to be connected once first; see
[`post-publisher/references/oauth-setup.md`](../../post-publisher/references/oauth-setup.md).
Telegram needs no OAuth and Threads is the simplest of the OAuth ones, so those
are the right places to start. Where the API path is closed — an unaudited
TikTok app, a personal Instagram account — uploading by hand is still the
answer, and `references/browser-fallback.md` covers doing that with the browser
while keeping the receipt honest.

---

## Summary

Total wall time: ~6-10 minutes for one topic → one brief → one carousel + one reel.

Total cost (with the defaults above): $6.50 ($0 + $0.48 + $6.03).

Cheaper variant (--video-provider veo-3-1-fast --music-provider stable-audio-2-5): ~$2.80.

The three skills compose: each output is the next input. Research is the upstream feeder. Carousel and reel are sibling outputs from the same research.

If you'd skip the brief and go straight from `--topic`: works too, but the carousel/reel will draft their own context internally via viral-text/essay-write, which is faster but less factually grounded.

For repeated runs on similar topics: the same `--style <id>` + same provider produces consistent brand-look. The `style-used.md` snapshot lets you reproduce exact runs later.

---

## Troubleshooting

- **No GEMINI_API_KEY set**: skills fall back to `--prompts-only`. You'll get script.md + prompts.md you can paste manually into provider UIs.
- **ffmpeg missing**: reel-builder generates shots + music separately, prints the manual ffmpeg stitch command. Install: `brew install ffmpeg` (Mac) or `apt-get install -y ffmpeg` (Debian/Ubuntu).
- **Budget exceeded warning** appears once per batch. Pass `--yes` after you've reviewed the cost.
- **Slide / shot failed**: `--resume <output-dir>` re-runs only the failed components.
- **Style drift across slides** (carousel): pick one library style + one model. Don't mix.
- **Reel feels off**: run `--prompts-only` first to inspect script.md before spending. The script is the most important file — get it right before generating.

See also:
- `carousel-builder/references/troubleshoot.md` for carousel-specific issues
- `reel-builder/references/troubleshoot.md` for reel-specific issues
- `research-brief/references/methodology.md` for query clustering rules
