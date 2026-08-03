# Troubleshooting — audio-mix-maker

---

## ffmpeg not found

**Fix**: `brew install ffmpeg` (Mac) / `apt-get install -y ffmpeg` (Debian).

Verify: `ffmpeg -version`. install.sh offers auto-install.

---

## Output has no audio at all

**Symptom**: mixed MP4 plays but with silence.

**Causes + fixes**:

1. **Source audio file is silent or corrupted.** Verify: `ffmpeg -i music.mp3 -f null -` (should report stream info).
2. **Mode is `replace` but `--audio` is invalid.** Check the path.
3. **Volume set to 0.** Verify `--volume` is >0.

---

## Music clips / distorts

**Symptom**: music has digital clipping (harsh peaks, distortion).

**Cause**: `--volume` too high, or source music already mastered loud.

**Fix**:

1. Lower `--volume` to 0.6-0.7.
2. Or normalize the input music file first: `ffmpeg -i music.mp3 -af "loudnorm" music-normalized.mp3`.

---

## Ducking is too aggressive (music nearly silent)

**Symptom**: in duck mode, music drops to silence whenever there's any sound.

**Cause**: `--duck-amount` too low.

**Fix**: bump to 0.7-0.8. Default 0.6 is "balanced"; some sources need lighter ducking.

---

## Ducking is too subtle (music doesn't lower enough)

**Symptom**: in duck mode, music still overpowers speech.

**Cause**: `--duck-amount` too high, or source speech is too quiet.

**Fix**:

1. Lower `--duck-amount` to 0.4-0.5.
2. Or normalize speech-track first: extract source audio, normalize, recombine via `replace` mode then add music via overlay (more manual steps).

---

## Source video lost (output has wrong video)

**Symptom**: output video doesn't match input.

**Cause**: very rare — usually an arg-order issue.

**Fix**: verify `--video <path>` points to the correct file.

---

## Output file size much larger than input

**Symptom**: 30 MB input → 100 MB output.

**Cause**: audio re-encoded as AAC, plus container overhead. Should be minor — if 3× larger, something's odd.

**Fix**:

1. Check the music file isn't huge (uncompressed WAV at 48kHz adds up).
2. Re-encode music to MP3 / AAC first if it's WAV: `ffmpeg -i music.wav -c:a aac -b:a 192k music.aac`.

---

## Wrong duration (output is shorter than expected)

**Symptom**: 60s video + 90s music → 60s output (correct, intentional via `-shortest`).
OR: 60s video + 30s music → 30s output (intentional truncation).

**Cause**: ffmpeg uses `-shortest` to align to the shorter track.

**Fix**:

1. To get a full-length output even when music is shorter: pre-loop the music or trim it to match video length.
2. To preserve full video even with shorter music: trim/loop music to match: `ffmpeg -stream_loop -1 -i music.mp3 -t 60 music-looped.mp3`.

---

## Fade-out feels choppy

**Symptom**: fade-out cuts mid-fade.

**Cause**: `--fade-out` longer than the available time at end of track.

**Fix**: reduce `--fade-out` to 0.3-0.5 seconds for short videos; 1-2 seconds for longer pieces.

---

## Want a different audio codec / bitrate

Default output is AAC 192kbps. To change: this skill v1 doesn't expose codec flags. Workaround — run the manual ffmpeg command:

```bash
ffmpeg -i video.mp4 -i music.mp3 -map 0:v -map 1:a -c:v copy -c:a libmp3lame -b:a 256k -shortest output.mp4
```

---

## Want multi-track mix (music + SFX + voiceover)

v1 mixes ONE music track. For multi-track:

1. Mix music + voiceover first (replace mode if no source audio): `audio-mix-maker --video video.mp4 --audio voiceover.mp3 --mode replace`.
2. Mix SFX on top of that result (overlay): `audio-mix-maker --video video-mixed.mp4 --audio sfx.mp3 --mode overlay`.
3. Mix music last (duck): `audio-mix-maker --video video-mixed-mixed.mp4 --audio music.mp3 --mode duck`.

For complex multitrack: use a DAW (Audacity, Reaper, Logic) or a NLE (DaVinci Resolve, Premiere).

---

## Loop a short music clip to match a long video

ffmpeg one-liner:

```bash
ffmpeg -stream_loop -1 -i short-music.mp3 -t <video-duration-seconds> music-looped.mp3
audio-mix-maker --video video.mp4 --audio music-looped.mp3
```

Get video duration first: `ffprobe -v error -show_entries format=duration video.mp4`.

---

## Audio sync drift

**Symptom**: audio slowly drifts out of sync with video.

**Causes + fixes**:

1. **Variable framerate source video.** Re-encode source to constant framerate first: `ffmpeg -i source.mp4 -vsync cfr -r 30 cfr.mp4`.
2. **Sample rate mismatch.** Convert music to 48kHz first: `ffmpeg -i music.mp3 -ar 48000 music-48k.mp3`.
