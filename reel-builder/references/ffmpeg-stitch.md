# ffmpeg stitch — concat, mix, burn

How the post-generation ffmpeg pipeline assembles the final.mp4.

---

## Pipeline stages

```
shots/shot-1.mp4 ┐
shots/shot-2.mp4 ├─► concat_videos() ─► .concat.mp4 ─► mix_audio_over_video() ─► .with-music.mp4 ─► burn_captions() ─► final.mp4
shots/shot-3.mp4 ┘                                   ▲
                                                     │
                                            music.mp3 ┘
```

If `--captions off`, the last step is skipped and `.with-music.mp4` is copied to `final.mp4`.

If `--music-provider` failed but shots succeeded: `.with-music.mp4` is replaced with `.concat.mp4` (silent reel). Music failure is logged.

---

## Stage 1 — Concat

`common.runners.ffmpeg.concat_videos(shot_paths, output)`:

```bash
ffmpeg -y -f concat -safe 0 -i concat-list.txt -c copy final.mp4
```

Uses the concat demuxer with `-c copy` — no re-encoding. Fastest path, no quality loss.

Constraint: all input shots must have the SAME codec, frame rate, resolution, and pixel format. Provider outputs usually align since we lock per-reel to one provider. If they don't align, ffmpeg errors out — see Troubleshooting.

For 3 × 5s shots from same provider, concat takes <1s.

---

## Stage 2 — Mix music

`common.runners.ffmpeg.mix_audio_over_video(video, audio, output)`:

```bash
ffmpeg -y \
  -i .concat.mp4 \
  -i music.mp3 \
  -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k \
  -af "volume=0.8,afade=t=out:st=0:d=0.5" \
  -shortest \
  .with-music.mp4
```

Behavior:
- `-map 0:v -map 1:a`: take video from input 0 (concat), audio from input 1 (music). REPLACES any audio the shots had.
- `-c:v copy`: no video re-encode.
- `-c:a aac -b:a 192k`: re-encode music to AAC 192kbps (standard for MP4).
- `-af "volume=0.8,afade=t=out:st=0:d=0.5"`: 80% music volume, 0.5s fade-out at end.
- `-shortest`: clip to shorter of video / music (usually video).

Caveat: if shots had spoken dialogue audio (Veo / Sora / Kling generated), it's REPLACED by music. This is the v1 behavior. For ducking / overlay, see "Limitations" below.

For a 15s reel, mix takes ~2-3s.

---

## Stage 3 — Burn captions

`common.runners.ffmpeg.burn_captions(video, captions, output)`:

For each caption entry `(start_seconds, end_seconds, text)`:

```bash
ffmpeg -y -i .with-music.mp4 \
  -vf "drawtext=text='<text>':fontcolor=white:fontsize=48:box=1:boxcolor=black@0.6:boxborderw=20:x=(w-text_w)/2:y=h-(text_h*2.5):enable='between(t,0.0,5.0)'" \
  -c:a copy final.mp4
```

Multiple captions stack via comma-separated drawtext filters in one `-vf`.

Default styling:
- Font: ffmpeg default — usually DejaVuSans-Bold or similar on Linux/Mac
- Color: white
- Size: 48 (scales to ~7% of 1920p frame height)
- Backplate: black at 60% opacity for readability
- Position: horizontally centered, vertically at `h - 2.5 * text_height` (lower third)
- Timing: from start to end seconds, enabled only during that window

For text in non-Latin scripts (Cyrillic, CJK), the default font may not have glyphs. Workaround: specify `:fontfile=/path/to/font.ttf` in the drawtext filter. Currently hardcoded — see Limitations.

Captions are escaped for ffmpeg syntax (`:`, `,`, `\` are escaped). Single quotes in user-provided text get replaced with `’` (right single quotation mark) to avoid breaking the filter.

---

## ffmpeg gating

### Pre-execute check

`reel-builder --check`:

```
[check] ffmpeg: ffmpeg version 7.1 ... → OK
[check] Output dir writable: ./generated/reel/<slug>/ → OK
[check] Video provider env vars: GEMINI_API_KEY set → OK
[check] Music provider env vars: SUNO_API_KEY set + SUNO_API_ENABLED=1 → OK
[check] Video style 'wes-anderson-symmetric' loaded → OK
[check] Music style 'cinematic-orchestral' loaded → OK
Ready to --execute.
```

If `ffmpeg: not found`:
- Print install command for OS (`brew install ffmpeg` / `apt-get install -y ffmpeg`)
- Print `SKILLS_SKIP_FFMPEG=1` opt-out path (skill still generates shots + music, just doesn't stitch)
- Exit non-zero

### During execute

If ffmpeg is absent at execute time:
- Generate shots + music as normal
- Print at end:
  ```
  ffmpeg not found — stitch skipped. Components saved to:
    ./generated/reel/<slug>/shots/shot-{1,2,3}.mp4
    ./generated/reel/<slug>/music.mp3

  To finish manually, install ffmpeg, then run:
    ffmpeg -f concat -safe 0 -i <(printf "file 'shot-1.mp4'\nfile 'shot-2.mp4'\nfile 'shot-3.mp4'\n") -c copy concat.mp4
    ffmpeg -i concat.mp4 -i music.mp3 -map 0:v -map 1:a -c:v copy -c:a aac -shortest final.mp4
  ```
- Exit 0 (partial success — components saved).

If ffmpeg IS present but a stitch step fails:
- Print the exact failing command + ffmpeg stderr
- Save components as above
- Exit 1

---

## Limitations (v1)

1. **No audio ducking.** Music replaces shot audio. Spoken dialogue from shots is lost.
   - Workaround: use silent shots (no dialogue) + music. Or generate shots, manually mix in a DAW.

2. **No transitions.** Hard cuts only.
   - Workaround: manual edit in CapCut / DaVinci / Premiere after generation.

3. **No beat-sync.** Shots don't align to music BPM.
   - Workaround: pick music with steady BPM and shoot duration that's a clean multiple of beats. (e.g., 120 BPM = 0.5s per beat → 5s shot = 10 beats — clean).

4. **No per-shot caption styling.** All captions use the same drawtext style.
   - Workaround: edit captions externally in a real editor.

5. **Default font may lack non-Latin glyphs.** Cyrillic / CJK captions may render as boxes.
   - Workaround: specify a font file path with the right glyph coverage. Edit `ffmpeg.py` directly or pass through `--caption-font <path>` (currently hardcoded; planned).

6. **No transparent video output.** Final is .mp4 with H.264 + AAC.

7. **Per-shot duration must be the same.** Mixing 5s + 8s + 5s shots usually concats fine BUT the music timing assumes uniform shots. Custom timing per-shot is v2.4.0+.

---

## Recovery: stitch failed but components saved

User can re-run ONLY the stitch step:

```bash
cd ./generated/reel/<slug>/
ffmpeg -f concat -safe 0 -i <(printf "file 'shots/shot-1.mp4'\nfile 'shots/shot-2.mp4'\nfile 'shots/shot-3.mp4'\n") -c copy concat.mp4
ffmpeg -i concat.mp4 -i music.mp3 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -af "volume=0.8" -shortest final.mp4
```

Or `--resume` if the skill supports re-stitch (v1: yes, --resume re-runs ffmpeg if final.mp4 missing).

---

## Performance

Stitching is fast compared to API generation:
- Concat: <1s
- Mix audio: 1-3s
- Burn captions: 2-4s (re-encodes video)
- Total: ~3-8s post-API

Bottleneck is always API latency for the video shots (60-180s for 3 shots in parallel).

---

## ffmpeg version requirements

- Tested with ffmpeg 6.x and 7.x
- ffmpeg 5.x should work but isn't validated
- ffmpeg 4.x: drawtext filter has different defaults, fade syntax differs — upgrade
- Pre-4.x: incompatible — upgrade
