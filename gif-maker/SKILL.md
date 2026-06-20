---
name: gif-maker
description: "Short looping GIF utility. Modes: (A) MP4-to-GIF with 2-pass palette optimization; (B) generate 1-3s clip via Veo/Sora/Kling/Runway/fal-video then convert. Aspect presets 1:1, 9:16, 16:9, 2:1. Use when: 'gif', 'looping animation', 'short loop', 'make a gif', 'сделай гифку', 'короткая зацикленная анимация'."

license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
GIF maker — short looping animation utility. Either take an existing MP4 and convert to optimized GIF, OR generate a 1-3 second clip via a video provider and convert.

Distinct from `reel-builder`:
- No script / music / captions — single short looping clip
- Output format is GIF, not MP4
- Much shorter duration (1-3s vs 8-30s)

Distinct from `video-prompt`:
- Output is GIF (palette-optimized), not MP4
- Wraps `video-prompt --execute` for generation mode, then converts
- Aspect crop and frame-rate optimization built-in

This skill does NOT:
- Generate long videos (>5s) — those are reels / shorts; use `reel-builder`
- Output WebP / APNG / animated AVIF — GIF only (most universally supported format)
- Background-removal frame-by-frame — GIF supports binary transparency but skill doesn't try
- Combine multiple clips into one GIF — single source → single GIF
</objective>

## ROLE

Two modes:

**Mode A — convert MP4 to GIF**:
Read an existing MP4 → apply optional aspect crop + trim → run 2-pass palette generation (palettegen + paletteuse) for high-quality color → save GIF.

**Mode B — generate then convert**:
Read prompt + provider → call video provider for a short clip → save intermediate MP4 → run conversion pipeline → save GIF.

## PIPELINE

### Mode A — `gif-maker --input <mp4>`

1. **Resolve input** — path to existing MP4.
2. **Detect ffmpeg** — fail if absent (print install instructions).
3. **Aspect crop (optional)** — center-crop to `--aspect 1:1|9:16|16:9|4:5|2:1|1:2`.
4. **Trim (optional)** — `--start <s> --duration <s>`.
5. **2-pass palette generation**:
   - Pass 1: `palettegen` → palette.png (256 colors, stats_mode=diff)
   - Pass 2: `paletteuse` with bayer dithering → output GIF
6. **Save** to `./generated/gif/<stem>.gif` (or `--output <path>`).

### Mode B — `gif-maker --prompt "..." --model <video-slug>`

1. **Resolve prompt** + model (default suggestion: `veo-3-1-fast` for cheapest, `kling-3` for best motion).
2. **Pre-flight**: check provider available + cost-confirm.
3. **Generate** — call video provider (poll if async).
4. **Save intermediate MP4** to `./generated/gif/_source/`.
5. **Run Mode A pipeline** on the intermediate.
6. **Final GIF** to `./generated/gif/<slug>.gif`.

## MODES

### Mode A — convert existing

- `gif-maker --input <path.mp4>` (required)

### Mode B — generate then convert

- `gif-maker --prompt "<text>" --model <video-slug>` (both required)
- `--prompt-file <path>` — alternative to `--prompt`
- `--duration <seconds>` — target generation length (default depends on model, typically 3-5s; we trim down to keep GIF small)

### Output controls (both modes)

- `--output <path>` — explicit output GIF path
- `--aspect 1:1|9:16|16:9|4:5|2:1|1:2` — center-crop to ratio
- `--fps N` — GIF frame rate (default 12; range 6-24)
- `--width N` — output width in px (default by aspect: 720 for landscape, 540 for portrait/square)
- `--start <s>` — trim start
- `--duration <s>` — trim length (Mode A) / target generation (Mode B)
- `--yes` — skip cost confirmation (Mode B)
- `--timeout <s>` — poll timeout for async video gen (default 600)

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/quality-tuning.md](references/quality-tuning.md) | When GIF is too large, colors look banded, or motion is choppy |
| [references/model-picker.md](references/model-picker.md) | Mode B — which video provider for which kind of clip (motion / talking head / abstract loop) |
| [references/troubleshoot.md](references/troubleshoot.md) | When ffmpeg fails, palette breaks, source is too long, etc. |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: convert existing reel to social GIF, generate abstract loop from prompt, convert long video to short looping GIF with trim.

## CONSTRAINTS

- **GIFs should be SHORT.** 1-3 seconds is the sweet spot. 5+ seconds creates huge files (>10MB), losing the "lightweight" advantage of GIF over MP4.

- **GIFs are large by nature.** Even with palette optimization, expect 500KB-3MB for 2-3 second clips. For smaller files: lower `--fps` (8-10), lower `--width` (480 or smaller), shorter `--duration`.

- **Lossy color via 256-color palette.** GIF max is 256 colors. Photoreal video → noticeable banding. Animated motion / illustrations / cartoons → great. Cue this in Mode B prompt: "flat illustration / animated / cartoon aesthetic" works better than "photoreal".

- **Aspect crop is center-crop.** Source aspect 16:9, target 1:1 → loses left+right portions.

- **Looping is implicit.** GIFs always loop by default (loop=0 = infinite). Source video should naturally loop or close-to-loop for best effect.

- **No audio.** GIFs don't support audio. If user needs audio + animation, that's MP4 territory (use `reel-builder` or `video-prompt --execute`).

- **ffmpeg required.** Install via `brew install ffmpeg` (Mac) / `apt-get install ffmpeg` (Debian). Without it, skill prints the manual ffmpeg command for the user to run.

- **Default fps 12.** 12fps is the GIF sweet spot. Higher fps = bigger file. Lower fps = choppy motion. Override only when needed.

- **Cost in Mode B** depends on the chosen video provider. Veo 3.1 Fast ~$0.40/sec; Kling 3 ~$0.50/sec; Sora 2 ~$1.00/sec. A 3-second clip = $1.20-$3.00.

- **No frame interpolation.** This skill doesn't upsample frame rates — it samples the existing video at `--fps`. For smoother motion, generate at higher native fps in Mode B.

- **Never print API keys** (Mode B). Mask in errors.

## INVOCATION HINTS

When the user says any of:

- "gif", "make a gif", "looping animation", "short loop"
- "convert this MP4 to GIF", "compress this video as a GIF"
- "сделай гифку", "короткая зацикленная анимация", "конвертируй в gif"
- "loop of X", "2-second loop of Y for Twitter"

Mode A is the default when `--input` is provided. Mode B requires both `--prompt` and `--model`.

Defaults: `--fps 12 --width <by-aspect>`. Mode B model default suggestion: `veo-3-1-fast` (cheapest, fast). For best motion: `kling-3`. For abstract / artistic: `fal-video` with hosted model id.

This skill is distinct from:
- `reel-builder` — full reels with script + music + captions, MP4 output
- `video-prompt` — single-clip MP4 generation
- `subtitle-burner` — captions on video (no animation)
- `bg-remover` — image utility, not video

If the user wants to add captions to the GIF: not supported in v1. Workaround: use `subtitle-burner --inline "<text>"` on the intermediate MP4 (Mode B) BEFORE conversion, then GIF the result.
