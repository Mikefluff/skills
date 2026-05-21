# subtitle-burner — calibration

3 example sessions.

---

## Example 1 — Burn SRT onto a TikTok export

### User says

> Add subtitles to my TikTok video. The captions are in `captions.srt`.

### Command

```
subtitle-burner burn ./tiktok-export.mp4 --subtitle ./captions.srt --style modern
```

### What happens

1. Reads `./tiktok-export.mp4` (a 30-second vertical 1080×1920 video).
2. Parses `./captions.srt` — gets 8 cues with their timecodes.
3. Applies `modern` style preset:
   - White text, 48pt
   - Black backplate at 60% opacity
   - Lower-third position (avoids TikTok's bottom UI mask)
4. ffmpeg drawtext filter: 8 cues stacked, each enabled during its time window.
5. Re-encodes the video. Audio copied.
6. Saves to `./tiktok-export-subtitled.mp4`.

stdout:

```
Burning 8 cue(s) into ./tiktok-export.mp4
  Output: ./tiktok-export-subtitled.mp4
  Style: modern (font_size=48, color=white)

Burned: ./tiktok-export-subtitled.mp4
```

Wall time: ~15s for the 30s vertical clip.

### What to notice

- ffmpeg is the bottleneck (re-encode time). The actual cue parsing is instant.
- Default `modern` style is what most TikTok videos use — white text + black backplate.
- Output file naming: `<original-stem>-subtitled<ext>`. Easy to tell apart from input.

---

## Example 2 — Plain text distributed across a reel

### User says

> I have a 30-second reel showing my morning routine. Add these captions, spread across the video:
> - Wake up
> - Coffee
> - Stretch
> - Write
> - Out the door

### What happens

1. Saves the 5 lines to a temp .txt file: `/tmp/morning-routine.txt`.

2. Runs:

```
subtitle-burner burn ./morning.mp4 --subtitle /tmp/morning-routine.txt --style modern
```

3. The skill detects `.txt` extension. Probes video duration via ffprobe — gets 30.0 seconds.

4. Distributes evenly: 5 cues × 6 seconds each (with 200ms gaps).

5. Burns + saves to `./morning-subtitled.mp4`.

6. Cue list (printed in stderr):

```
  ✓ Burning 5 cue(s) into ./morning.mp4
     ...
```

Verifying with preview first (recommended workflow):

```
subtitle-burner preview --subtitle /tmp/morning-routine.txt --video ./morning.mp4
```

```
# 5 cue(s) parsed from /tmp/morning-routine.txt

  1.    0.00s →    5.96s  ( 5.96s)  Wake up
  2.    6.16s →   12.12s  ( 5.96s)  Coffee
  3.   12.32s →   18.28s  ( 5.96s)  Stretch
  4.   18.48s →   24.44s  ( 5.96s)  Write
  5.   24.64s →   30.00s  ( 5.36s)  Out the door
```

Good — confirms timing. Then burn.

### What to notice

- Plain-text mode is the right tool here: short fixed list, doesn't need precise timing.
- `preview` first → `burn` second is a common pattern. The CLI supports it.
- Last cue is slightly shorter (5.36s vs 5.96s) — that's the rounding tail. Doesn't matter for the use case.

---

## Example 3 — Single inline caption for a 5s clip

### User says

> I have a 5-second clip showing my product. Just one caption across the whole thing: "FINALLY HERE."

### Command

```
subtitle-burner burn ./product-reveal.mp4 --inline "FINALLY HERE." --style bold
```

### What happens

1. Single cue from 0.00s to 5.00s.
2. `bold` preset: yellow text, 56pt, dense black backplate. High-impact.
3. Burns + saves to `./product-reveal-subtitled.mp4`.

### What to notice

- `--inline` for single-message overlays. No file needed.
- `bold` style for high-energy / hook content.
- Total command time: ~5s for the 5s clip (ffmpeg encode time).

---

## Anti-pattern (don't do this)

### Burning over already-subtitled video

❌

```
subtitle-burner burn ./clip-subtitled.mp4 --subtitle ./new-captions.srt
```

Result: TWO sets of captions, both at lower-third, overlapping. Unreadable.

✓ Always burn ONCE per source video. If you need different captions, start from the original (unsubtitled) file.

### Burning translation as second pass (without position change)

❌ Burning English captions, then burning Spanish captions on top — both at lower-third.

Result: English + Spanish stacked at the same position.

✓ Burn one. If you need bilingual, either:
1. Combine both into a single SRT (with stacked text per cue).
2. Edit `ffmpeg.py` to support a second cue stream with different position (top-third).

### Using `--inline` for narration-paced content

❌ A 60-second tutorial with one inline caption "Subscribe to the channel".

Result: caption persists for full minute, blocking the tutorial visuals.

✓ Use an SRT with timed cues, or split the tutorial into sections and burn per-section captions.

### Burning low-res video and expecting captions to scale up

❌ Input is 480p with `--font-size 48` (default for 1080p).

Result: text is huge relative to the video, takes up half the frame.

✓ Scale font-size to ~6-8% of video height: `--font-size 28` for 480p, `36` for 720p.

### Forgetting to remove HTML tags from old SRTs

❌ Old SRT with `<i>italic text</i>` tags.

Result: literal `<i>...</i>` appears on screen.

✓ Strip tags first:

```bash
sed -i '' 's/<[^>]*>//g' captions.srt
```

Then burn.
