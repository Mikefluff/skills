# Troubleshooting — subtitle-burner

When captions don't render correctly.

---

## ffmpeg not found

**Symptom**: `ffmpeg: not found in PATH`.

**Fix**:

- Mac: `brew install ffmpeg`
- Debian/Ubuntu: `sudo apt-get install -y ffmpeg`
- Other: ffmpeg.org/download.html

The collection's install.sh offers ffmpeg auto-install at setup time. Re-run `install.sh --update` if you missed it.

---

## Captions render as boxes / empty rectangles

**Symptom**: Cyrillic / Chinese / Arabic captions show as `□□□□`.

**Cause**: System's default ffmpeg font lacks glyphs for the script.

**Fix**:

1. Install Noto Sans (broadest coverage):
   - Mac: `brew install --cask font-noto-sans`
   - Linux: `sudo apt-get install fonts-noto`

2. Edit `common/runners/ffmpeg.py:burn_captions` — add `:fontfile=/path/to/NotoSans-Bold.ttf` to the drawtext filter.

3. Or (planned v2.7): set `FFMPEG_CAPTION_FONT=/path/to/font.ttf` env var.

---

## Captions are too small / too large

**Symptom**: Default 48pt looks tiny on a 4K video or huge on a 480p clip.

**Cause**: Font size is in points (absolute), not relative to video height.

**Fix**: pass explicit `--font-size`:

```bash
# For 4K (2160p): bump to ~80pt
subtitle-burner burn ./4k.mp4 --subtitle ./caps.srt --font-size 80

# For 480p: drop to ~28pt
subtitle-burner burn ./480p.mp4 --subtitle ./caps.srt --font-size 28
```

Rule of thumb: font-size ≈ 6-8% of video height in pixels.

| Resolution | Recommended font-size |
|---|---|
| 480p | 28-32 |
| 720p | 36-42 |
| 1080p | 48-56 (default) |
| 1440p | 60-72 |
| 2160p (4K) | 72-96 |

---

## Captions don't match the audio (timing drift)

**Symptom**: Caption appears 2 seconds before the matching speech.

**Causes**:

1. **SRT timing was wrong**. Verify with `preview`:
   ```
   subtitle-burner preview --subtitle ./caps.srt
   ```
   Compare timestamps against where the audio actually says those words. Fix the SRT in a subtitle editor (Subtitle Edit / Aegisub).

2. **Source video has variable framerate.** drawtext applies based on time, not frame number — should be fine. But if the video has been re-encoded with VFR, the timing may drift.
   - Fix: re-encode the source to constant framerate first:
     ```bash
     ffmpeg -i source.mp4 -r 30 -c:v libx264 -c:a copy source-cfr.mp4
     subtitle-burner burn source-cfr.mp4 --subtitle ./caps.srt
     ```

3. **Subtitles generated against a different cut of the video.** If you edited the video AFTER generating subtitles, timing won't match.
   - Fix: re-generate subtitles against the current cut.

---

## ffmpeg error: "drawtext: Invalid argument"

**Symptom**: ffmpeg fails with cryptic drawtext error.

**Causes**:

1. **Special characters in caption text aren't escaped properly.** The skill escapes `:`, `,`, `\` — but some edge cases (deeply nested quotes, control characters) slip through.
   - Fix: clean the SRT — remove control characters, replace nested quotes.

2. **Too many cues at once.** ffmpeg's `-vf` filter chain has a length limit. Past ~200 cues, the command line is too long.
   - Fix: split the SRT into chunks, burn each chunk into a sub-video, concat with ffmpeg.

3. **Bad characters in font path** (if `--font-file` planned). Wrap font path in quotes.

---

## Audio is missing in output

**Symptom**: Subtitled video plays but has no sound.

**Cause**: Input video had no audio track, or audio codec wasn't copied properly.

**Fix**:

1. Check input has audio: `ffprobe input.mp4 | grep Audio`.
2. If audio is present but missing in output: rerun with explicit audio handling. Edit `ffmpeg.py:burn_captions` to add `-c:a aac -b:a 192k` instead of `-c:a copy`.

---

## Output file is corrupted / won't play

**Symptom**: Output MP4 won't open in QuickTime / VLC.

**Causes**:

1. **ffmpeg crashed mid-encode** (disk full, OOM). Check the file size — much smaller than expected = aborted encode.
   - Fix: free disk space, re-run.

2. **Container format mismatch.** Input is `.webm` but output set to `.mp4` without re-encoding.
   - Fix: usually auto-handled. If it fails, force explicit codecs in `ffmpeg.py`.

---

## Captions are positioned wrong (top instead of bottom, off-screen, etc.)

**Symptom**: Captions appear above the safe zone or partially off-screen.

**Cause**: Default position `y = h - text_h * 2.5` assumes lower-third. May not fit certain aspect ratios.

**Fix**: edit `ffmpeg.py:burn_captions` and change the `y` formula:

- Centered: `y=(h-text_h)/2`
- Top-third: `y=text_h*1.5`
- Custom pixel: `y=120` (120px from top)

---

## Plain-text captions feel mismatched to video pacing

**Symptom**: 30s video with 5 TXT cues = 6s per cue. But the video has logical sections of 4s + 8s + 5s + 7s + 6s. Even distribution feels off.

**Cause**: Plain-text mode distributes EVENLY. Doesn't know your video's pacing.

**Fix**:

1. Generate an SRT with per-cue timing instead. Use a subtitle editor (Subtitle Edit, Aegisub, free Subly tier).
2. Or: split your video at the logical breaks, burn each section separately, concat.

---

## SRT has caption blocks with no text (just timestamps)

**Symptom**: SRT has blocks like:

```
1
00:00:00,000 --> 00:00:03,000

2
00:00:03,000 --> 00:00:06,000
Real caption
```

Cue 1 has no text. Skill silently skips it. Output has cue 2 onwards.

If you wanted cue 1 to be blank (e.g., title card with silence): use a single-space text instead of empty:

```
1
00:00:00,000 --> 00:00:03,000
 

2
00:00:03,000 --> 00:00:06,000
Real caption
```

(But really — just don't have blank cues. The skill ignores them by design.)

---

## Inline tag pollution

**Symptom**: SRT text includes inline HTML tags (`<i>`, `<b>`, `<font color>`) — they render literally in the output.

**Cause**: Skill doesn't strip HTML; passes through to ffmpeg drawtext, which renders the tags as text.

**Fix**: strip tags from SRT first:

```bash
sed -i '' 's/<[^>]*>//g' captions.srt  # Mac
sed -i 's/<[^>]*>//g' captions.srt    # Linux
```

VTT tags are stripped automatically by the parser. SRT inline tags are not (legacy decision — SRT spec doesn't define them).

---

## Output is too dark / colors look washed out

**Symptom**: Subtitled video has different colors than input.

**Cause**: ffmpeg re-encoded with default H.264 settings — may not match input's color space / bit depth.

**Fix**: specify explicit codec params in `ffmpeg.py:burn_captions`:

```python
cmd = [
    ffmpeg_bin, "-y", "-loglevel", "error",
    "-i", str(video),
    "-vf", vf,
    "-c:a", "copy",
    "-c:v", "libx264", "-preset", "slow", "-crf", "18",  # higher quality
    "-pix_fmt", "yuv420p",  # ensures wide compat
    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
    str(output),
]
```

(Patch `ffmpeg.py` directly; planned v2.7 `--quality` flag will surface this.)

---

## Want to burn captions on multiple videos at once

The skill processes one video per run. For batch:

```bash
for video in ./clips/*.mp4; do
  srt="${video%.mp4}.srt"
  subtitle-burner burn "$video" --subtitle "$srt" --style modern
done
```

Or with parallelism via xargs:

```bash
find ./clips -name "*.mp4" -print0 | xargs -0 -P 4 -I {} sh -c '
  base="${1%.mp4}"
  subtitle-burner burn "$1" --subtitle "$base.srt" --style modern
' sh {}
```

---

## "I burned the wrong captions / wrong style — can I revert?"

The skill writes to a NEW file (`<video>-subtitled<ext>`). The input is never modified. Just delete the wrong output and re-run.

If you're using `--output <path>` and it's pointing at an existing file, the skill overwrites without prompt. Be careful with `--output`.
