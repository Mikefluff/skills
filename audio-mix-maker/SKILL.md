---
name: audio-mix-maker
description: "Mix a music / audio track onto an existing video via ffmpeg. Three modes: replace (drop original audio), overlay (mix both audible), duck (sidechain-compressor lowers music when speech is detected). Volume + fade-in + fade-out controls. No API calls — pure ffmpeg. Use when the user says 'mix this music onto the video', 'add background music to video', 'duck the music under voiceover', 'смешай музыку с видео', 'фоновая музыка для видео'."
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
Mix a music / audio track onto an existing video with ffmpeg-driven post-processing. Returns a new MP4 with the music mixed according to the chosen mode.

Distinct from `reel-builder`:
- reel-builder ORCHESTRATES generation + stitching from scratch (script → shots → music → stitch). This skill is JUST the final-mix step on assets you already have.
- No script / no video / music generation — bring your own.

Distinct from `subtitle-burner`:
- subtitle-burner adds CAPTIONS. This skill adds AUDIO MIX.
- Both are pure-ffmpeg utilities — they share the lightweight wrapper pattern.

Distinct from `voiceover-maker`:
- voiceover-maker GENERATES TTS. This skill MIXES audio onto video.

This skill does NOT:
- Generate music (use `music-prompt --execute` first)
- Generate voiceover (use `voiceover-maker --execute` first)
- Stitch multiple video clips (use `reel-builder` for that, or raw ffmpeg `concat`)
- Cut / trim video segments (use ffmpeg / DaVinci Resolve / Premiere)
- Sync audio to specific moments (use a NLE — Final Cut / Premiere / DaVinci)
</objective>

## ROLE

Read video + music + mode + volume/fade controls → run ffmpeg with the right filter chain → save mixed MP4.

## PIPELINE

1. **Resolve inputs**:
   - `--video <path>` — source MP4 / MOV / WebM (required)
   - `--audio <path>` — music / SFX / voiceover (required)

2. **Pick mode**:
   - `--mode replace` (default) — drop the video's original audio, use music as sole track
   - `--mode overlay` — mix music ON TOP of original audio (both audible at constant volume)
   - `--mode duck` — overlay with sidechain compression (music auto-lowers when speech detected)

3. **Volume + fade controls**:
   - `--volume <multiplier>` — 0.0-2.0 music volume (default 0.8)
   - `--fade-in <seconds>` — fade in duration (default 0)
   - `--fade-out <seconds>` — fade out duration (default 0.5)
   - `--duck-amount <0-1>` — duck mode only: how much music attenuates (default 0.6)

4. **Detect ffmpeg** — print install instructions if missing.

5. **Run ffmpeg** — encoded as one of three filter chains depending on mode.

6. **Save**:
   - Default: `<video-stem>-mixed<ext>` next to source
   - Custom: `--output <path>`

## MODES

### Required

- `audio-mix-maker --video <path> --audio <path>`

### Mix mode

- `--mode replace|overlay|duck` (default `replace`)

### Volume

- `--volume <0.0-2.0>` (default 0.8)
- `--fade-in <seconds>` (default 0)
- `--fade-out <seconds>` (default 0.5)
- `--duck-amount <0.0-1.0>` (default 0.6, duck mode only)

### Output

- `--output <path>` (default: `<video-stem>-mixed<ext>`)

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/modes.md](references/modes.md) | Step 2 — when to pick replace vs overlay vs duck, and how each affects the listener |
| [references/troubleshoot.md](references/troubleshoot.md) | When ffmpeg fails, audio is clipped, ducking too aggressive / too subtle |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 3 calibration runs: silent screen recording + background music (replace), voiceover-driven explainer + background music (duck), b-roll with original audio + music bed (overlay).

## CONSTRAINTS

- **ffmpeg required.** Install: `brew install ffmpeg` (Mac) / `apt-get install -y ffmpeg` (Debian). install.sh offers auto-install.

- **Video codec preserved.** This skill uses `-c:v copy` — no re-encode of video frames. Output video quality identical to source.

- **Audio re-encoded.** Output audio is AAC 192kbps (industry standard for video).

- **Music length usually exceeds video.** Skill uses `-shortest` flag — output truncates at the shorter of (video duration, music duration). Music is faded out at the cut point if `--fade-out > 0`.

- **Duck mode requires speech in the video.** If there's no speech / dialogue, duck mode behaves like overlay. For pure music-on-music: use overlay.

- **Volume max is ~2.0.** Past 2× the source volume, distortion appears. For louder music: re-master the input audio file first.

- **Fade timing is from the video start.** Fade-in starts at t=0; fade-out completes at the end of the shorter track. Custom mid-clip fades require DaVinci / Premiere / manual ffmpeg.

- **Output is MP4 by default.** If source is MOV / WebM, output preserves the container.

- **Cost = $0.** No API calls — local ffmpeg only.

- **No multitrack mixing.** v1 mixes ONE music track onto video. For multi-track (music + SFX + voiceover): chain calls or use a DAW.

- **Sample rate / channel layout handled implicitly.** ffmpeg resamples as needed. For exact control: use raw ffmpeg.

## INVOCATION HINTS

When the user says any of:

- "mix this music onto the video", "add background music"
- "duck the music under the voiceover", "lower music when speech"
- "replace audio with music"
- "смешай музыку с видео", "фоновая музыка для видео"
- "подложи трек под видосик"

If the user describes a podcast / explainer / interview workflow with voiceover, suggest `--mode duck`. If pure music video / silent footage, suggest `--mode replace`.

Defaults: `--mode replace --volume 0.8 --fade-out 0.5`. No `--execute` flag — the skill always executes (it's a local-only utility, no cost).

This skill is distinct from:
- `reel-builder` — generates + stitches; this is final-mix only
- `subtitle-burner` — captions, not audio
- `voiceover-maker` — generates TTS; this mixes
- `music-prompt` — generates music; this consumes the output of music-prompt
- `gif-maker` — produces GIF, no audio
