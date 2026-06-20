---
name: subtitle-burner
description: "Burn captions / subtitles onto a video via ffmpeg. Supports SRT, WebVTT, plain text. Presets: modern (white on black lower-third), minimal, bold (yellow, denser). Subcommands: burn, preview. Pure ffmpeg. Use when: 'add subtitles to my video', 'burn captions onto this MP4', 'subtitle my reel', 'добавь субтитры к видео', 'жёстко вшей субтитры'."

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
Burn captions onto an existing video file. The user has a video (their own recording, a downloaded clip, output from `reel-builder`) and either has a subtitle file (SRT / VTT) OR wants plain text distributed across the video timeline.

Distinct from `reel-builder`:
- reel-builder generates the video itself (T2V) + can optionally burn its own captions.
- This skill takes an EXISTING video as input. No generation.

This skill does NOT:
- Generate the video — the input is yours.
- Auto-transcribe audio to captions — requires Whisper, planned for a separate `transcribe` skill (see ROADMAP).
- Translate captions between languages — pass already-translated subtitles.
- Re-encode video at different resolutions / formats beyond what ffmpeg's drawtext requires (output matches input resolution + codec where possible).
- Add audio (TTS overlay) — use `voiceover-maker` for that.
- Mix multiple subtitle tracks — single track per run.

Requires `ffmpeg` on PATH. install.sh offers to install it; otherwise `brew install ffmpeg` (Mac) / `apt-get install -y ffmpeg` (Debian).
</objective>

## ROLE

Read the input video + subtitle source → parse cues (SRT / VTT / plain text) → call ffmpeg drawtext filter for each cue with chosen styling → save the subtitled video → print the path.

## PIPELINE

1. **Resolve input video**:
   - `<video>` path — local MP4 / MOV / WebM.
   - Must exist + be readable.

2. **Resolve subtitle source**:
   - `--subtitle <file>` — SRT / VTT / TXT file
   - `--inline "<text>"` — single caption applied to the entire video
   - File extension determines parser (`.srt` / `.vtt` / `.txt`)

3. **Parse cues**:
   - SRT: standard subtitle format with `index → timecode → text` blocks.
   - VTT: WebVTT with `WEBVTT` header.
   - TXT: plain text, one cue per line, distributed evenly across the video duration (ffprobe used for duration detection).
   - Inline: one cue starting at 0:00, ending at end-of-video.

4. **Apply style preset** — see `references/ffmpeg-styling.md`:
   - `modern` (default): white text, black 60% backplate, lower-third, 48pt
   - `minimal`: white text, no backplate, lower-third, 42pt
   - `bold`: yellow text, dense black backplate, larger 56pt
   - Custom: override per-flag (`--font-size`, `--font-color`, `--box-color`)

5. **Burn via ffmpeg** — calls `common.runners.ffmpeg.burn_captions`. drawtext filter sequence, re-encodes video, copies audio.

6. **Output**:
   ```
   <video-dir>/<video-stem>-subtitled<ext>
   ```
   or `--output <path>` for explicit destination.

## MODES

### Burn

```
subtitle-burner burn <video> --subtitle <file>
subtitle-burner burn <video> --inline "<single caption>"
subtitle-burner burn <video> --subtitle <file> --style modern|minimal|bold
subtitle-burner burn <video> --subtitle <file> --font-size 56 --font-color white
subtitle-burner burn <video> --subtitle <file> --output ./final.mp4
```

### Preview (no burn)

```
subtitle-burner preview --subtitle <file>
subtitle-burner preview --subtitle <txt-file> --video <video>   # txt requires video for timing
subtitle-burner preview --inline "<text>"
```

Prints the parsed cue list (index, start/end timestamps, text) without burning. Useful to verify timing before committing.

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/subtitle-formats.md](references/subtitle-formats.md) | SRT vs. VTT vs. plain-text — when to use which, format specifics, parsing edge cases |
| [references/ffmpeg-styling.md](references/ffmpeg-styling.md) | Style presets + per-flag customization, font selection, multilingual glyph support |
| [references/troubleshoot.md](references/troubleshoot.md) | When captions don't render, font missing, sync drift, etc. |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: burn an SRT onto a TikTok export, plain-text captions distributed across a 30s reel, single inline caption for an entire 5s clip.

## CONSTRAINTS

- **ffmpeg required.** No API calls; the skill is a pure ffmpeg wrapper. install.sh detects + offers install at setup time.

- **Subtitle source parsing is strict.** SRT must have valid timecodes (HH:MM:SS,mmm); VTT must have `WEBVTT` header; TXT must have ≥1 non-empty line.

- **Plain text is distributed evenly.** N lines across the video duration. Works for short videos with clear logical breaks; less ideal for narrative content where timing must match audio cues. For audio-synced captions, use a real subtitle tool (Whisper / Premiere / DaVinci) to produce SRT first.

- **Output preserves video codec where possible.** ffmpeg's drawtext requires re-encoding the video stream, so the output IS re-encoded (audio is copied as-is). For large files this can take seconds-to-minutes depending on duration.

- **Default font may lack non-Latin glyphs.** Cyrillic / CJK / Arabic captions may render as boxes on systems with only Latin-only default fonts. Workaround: specify `--font /path/to/font-with-coverage.ttf` (currently planned — set `FFMPEG_CAPTION_FONT` env var as a workaround in v1).

- **Style presets are starting points.** Most users want some tweak. The CLI accepts per-flag override (font-size, font-color, box-color).

- **Position is lower-third by default.** Hardcoded in `ffmpeg.py:burn_captions`. To change position: edit the drawtext filter in `common/runners/ffmpeg.py` directly (or PR a `--position` flag).

- **Single text track per run.** For multiple tracks (e.g., translation overlay + original): run twice, second time using the output of the first as input.

- **No subtitle file is generated.** Captions are burned INTO the video pixels — not soft-subtitles you can toggle off in a player. For toggleable subtitles, embed as a separate track via ffmpeg's `-c:s mov_text` (not handled by this skill).

- **Never modifies the input file.** Always writes to a new file (`<video>-subtitled<ext>` or `--output`).

## INVOCATION HINTS

When the user says any of:

- "add subtitles to my video", "burn captions onto this MP4"
- "subtitle my reel", "caption this video"
- "make the captions yellow and bold" (style customization)
- "I have an SRT file, apply it to this video"
- "добавь субтитры к видео", "вшей субтитры"
- "сделай надписи на видео"

Defaults: `burn <video> --subtitle <file> --style modern`. If only `--inline` text is given (no file), default to single-caption-across-whole-video.

If the user mentions a STYLE preference ("bold yellow" → `--style bold`; "minimal no background" → `--style minimal`; default "modern with black backplate"):

If the user mentions an SRT/VTT file → use `--subtitle <file>`.

If the user mentions plain text (no file) AND a short list → use `--inline` for single caption OR write the text to a temp file and use it as `--subtitle <tmp>.txt`.

This skill is distinct from:
- `reel-builder` — that GENERATES video + can burn captions inline. This is for existing video.
- `voiceover-maker` — that generates audio. This burns visual captions.
- `subtitle-translator` (planned, see ROADMAP) — translation; this is rendering.
