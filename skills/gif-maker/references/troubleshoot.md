# Troubleshooting — gif-maker

---

## ffmpeg not found

**Symptom**: `ffmpeg not found in PATH`.

**Fix**:

- macOS: `brew install ffmpeg`
- Debian / Ubuntu: `apt-get install -y ffmpeg`
- Windows: `winget install ffmpeg` or `choco install ffmpeg`
- Verify: `ffmpeg -version`

If install.sh skipped ffmpeg: re-run `bash install.sh` (will detect missing ffmpeg and install).

---

## Output GIF is too large

See `references/quality-tuning.md` — primary levers:

1. Lower `--fps` (12 → 8-10)
2. Lower `--width` (720 → 480)
3. Shorter `--duration`
4. Switch source to flat / illustrated aesthetic (Mode B)

---

## Output GIF has heavy color banding

**Symptom**: gradients show stripes; skin tones look posterized.

**Cause**: 256-color palette can't capture all source colors.

**Fix**:

1. Source is photoreal? Switch to a flatter aesthetic in Mode B prompt.
2. Try a different dithering: edit `common/runners/ffmpeg.py` mp4_to_gif() to use `dither=floyd_steinberg` instead of `bayer:bayer_scale=5`. Floyd-Steinberg is higher quality but larger file.
3. For high-quality animation: consider WebP instead (not supported by this skill).

---

## Motion looks choppy / stuttery

**Symptom**: animation jumps.

**Cause**: fps too low.

**Fix**: `--fps 15` or `--fps 18`. Tradeoff: larger file.

If source is 60fps and you're converting to 12fps, ffmpeg samples 1 of every 5 frames — this can look uneven. Match to a factor of source: 60 → 12, 15, 20, 30.

---

## Looping isn't seamless

**Symptom**: GIF jumps when looping (last frame back to first).

**Cause**: source video doesn't naturally loop.

**Fix options**:

1. **Mode B prompt**: cue "seamless loop, ending matches starting frame".
2. **Trim** in Mode A so the loop point is visually similar: experiment with `--start` and `--duration`.
3. **Ping-pong manually**:

```bash
ffmpeg -i source.mp4 -filter_complex "[0:v]reverse[r];[0:v][r]concat" pingpong.mp4
gif-maker --input pingpong.mp4
```

---

## Aspect crop loses important content

**Symptom**: subject's head cropped off when going 16:9 → 1:1.

**Cause**: aspect crop is CENTER-crop. Doesn't know what's the subject.

**Fix**:

1. Don't crop — keep source aspect (`--aspect` omitted).
2. Manual crop in ffmpeg with explicit offsets, then pass to gif-maker via `--input`.
3. Generate at target aspect in Mode B: `--aspect 1:1 --prompt "..."` (provider may or may not honor; verify intermediate MP4).

---

## Mode B: video provider not available

**Symptom**: `missing env: GEMINI_API_KEY` (for Veo) or similar.

**Fix**: set the relevant env var via `skills-keys`:

```
/skills-keys add GEMINI_API_KEY AIza...      # Veo (Google)
/skills-keys add KLING_ACCESS_KEY_ID ...     # Kling
/skills-keys add KLING_ACCESS_KEY_SECRET ... # Kling (pair)
/skills-keys add RUNWAY_API_KEY rwml_...     # Runway
/skills-keys add FAL_KEY fal_...             # fal.ai
```

Then verify: `/skills-keys verify GEMINI_API_KEY`.

---

## Mode B: video generation succeeds but conversion fails

**Symptom**: intermediate MP4 saved, conversion step errors.

**Cause**: ffmpeg incompatible with the MP4 codec (rare with modern providers).

**Fix**:

1. Manually run conversion on the saved MP4:
   ```
   gif-maker --input ./generated/gif/_source/<file>.mp4 --output ./out.gif
   ```
2. If still failing: inspect with `ffprobe ./generated/gif/_source/<file>.mp4` and check codec. H.264 baseline should always work; HEVC may need a re-encode step.

---

## GIF plays once and stops

**Symptom**: doesn't loop, plays one cycle.

**Cause**: looper flag wrong.

**Fix**: default is `loop=0` (infinite). If you accidentally got `loop=-1` (no loop), regenerate. The skill doesn't expose this flag in v1.

---

## Want audio in the loop

GIFs don't support audio. Options:

1. **MP4 instead**: HTML5 video with `autoplay loop muted playsinline`. Most modern platforms render this similarly to GIF, but with audio support.
2. **Use `reel-builder` for music** + render to MP4.
3. **Skip audio** — most quick-loop use cases (Twitter, Slack reactions) don't need it.

---

## Want captions / text overlay on the GIF

Not supported in v1 of gif-maker. Workaround:

1. Mode B: generate the MP4 first via `video-prompt --execute`.
2. Burn captions: `subtitle-burner --inline "<text>" --video <mp4>`.
3. Convert: `gif-maker --input <captioned.mp4>`.

---

## Source MP4 is much longer than needed

Trim before conversion:

```
gif-maker --input long-video.mp4 --start 12.5 --duration 2.5
```

Or with ffmpeg directly (faster, no re-encode):

```bash
ffmpeg -ss 12.5 -t 2.5 -i long-video.mp4 -c copy trimmed.mp4
gif-maker --input trimmed.mp4
```

---

## Background music in the source video pollutes nothing (GIF has no audio)

Confirmed: source audio is dropped. GIF output is silent by design.

---

## I want WebP / APNG instead of GIF

Not supported in v1. Reasons not to add yet:

- WebP: smaller + better quality, but Slack/email previews are inconsistent
- APNG: similar story, also patchy support

Workaround — manual ffmpeg:

```bash
# WebP animation
ffmpeg -i source.mp4 -vf "fps=12,scale=720:-1:flags=lanczos" -loop 0 output.webp

# APNG
ffmpeg -i source.mp4 -vf "fps=12,scale=720:-1:flags=lanczos" -plays 0 output.apng
```

These produce smaller files at higher quality. If GIF compatibility isn't required, prefer WebP for static-hosted content.
