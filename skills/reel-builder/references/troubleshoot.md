# Troubleshooting — reel-builder

Things that go wrong end-to-end and how to fix them.

---

## ffmpeg not found

**Symptom**: `ffmpeg: not found in PATH`.

**Fix**:
- Mac: `brew install ffmpeg`
- Debian/Ubuntu: `sudo apt-get install -y ffmpeg`
- Other: check ffmpeg.org for binaries.
- Skip stitch: `SKILLS_SKIP_FFMPEG=1 reel-builder ...` — generates shots + music separately, prints manual ffmpeg command.

---

## ffmpeg concat fails: "codec mismatch" / "DTS error"

**Symptom**:
```
[concat @ 0x...] DTS 12345 < 67890 out of order
[concat @ 0x...] Could not find codec parameters for stream
```

**Cause**: shots have different codecs / framerates / resolutions despite same provider.

**Fix**: re-encode during concat (slower but reliable):

```bash
ffmpeg -f concat -safe 0 -i concat-list.txt \
  -c:v libx264 -crf 18 -preset fast \
  -c:a aac \
  output.mp4
```

Edit `common/runners/ffmpeg.py:concat_videos()` to add fallback re-encode path. (Planned: auto-detect codec mismatch and switch.)

---

## "Provider returned a duration shorter than --shot-duration"

**Symptom**: shot 1 is 4.2s when you asked for 5s.

**Cause**: video providers honor "approximate" duration. Veo / Sora / Kling generate "around N seconds" — often slightly short.

**Fix**:
- Pad with last-frame freeze: edit shot manually (`ffmpeg -i shot.mp4 -vf "tpad=stop_mode=clone:stop_duration=0.8" -c:a copy shot-padded.mp4`).
- Or request slightly longer (--shot-duration 6 → reliably 5s).
- Or accept the slightly-short final.mp4.

---

## Generated shots look totally different from each other

**Symptom**: Shot 1 is golden-hour photo, shot 2 is dark blue cyberpunk, shot 3 is illustrated.

**Causes + fixes**:

1. **Shot anchor too short / vague.** Style library entries should be rich. If you're using a library style and still getting drift, the prompt-side content overwhelms the anchor.
   - Fix: re-run `--prompts-only` and inspect `prompts.md`. Tighten per-shot content to ≤50 words.

2. **Different model invocations.** Providers don't expose seeds. Use same provider (already enforced).

3. **Subject description differs across shots.** "Maria" in shot 1 vs "the woman" in shot 2 = two different people.
   - Fix: copy the FULL visual description verbatim across shots ("28yo woman, shoulder-length black hair, denim jacket, golden retriever at her feet, modern Brooklyn loft").

4. **Kling Elements / Sora cameos available but not used.** These features pass character reference between shots.
   - Fix: use Kling 3.0 with Elements for character carry-over, OR pass shot 1's last frame as `--image-url` for shot 2 (Veo I2V mode).

---

## Music doesn't match the video mood

**Symptom**: Video is cold sci-fi, music is upbeat synthwave.

**Causes + fixes**:

1. **`--music-style auto` picked wrong.** The video style's `Suggested music style` is curated but not always perfect for your specific topic.
   - Fix: pass `--music-style <id>` explicitly. Browse `common/style-library/music/_index.md` for options.

2. **Music style frontmatter says `energy: driving` but topic needs `calm`.**
   - Fix: filter library by `energy` field. `ambient-drone` and `lofi-hiphop-chill` are calm. `synthwave` and `cinematic-orchestral` are mid-to-driving.

3. **Suno generated something off-genre.** Sometimes Suno interprets prompts loosely.
   - Fix: re-generate just the music (`--resume` after deleting music.mp3 from output dir). Or paste the music Style box into Suno UI manually and pick a good take.

---

## "API rate limit hit on shot 2/3"

**Symptom**: Shot 1 succeeded, shot 2 returns 429.

**Cause**: Parallelism too high for vendor.

**Fix**:
- Lower `--parallelism 1` (sequential).
- Wait 30-60s, then `--resume`.
- Veo / Sora typically allow 2-3 concurrent. Kling allows 2. Suno allows 1-2.

---

## "Generation taking forever"

**Symptom**: Veo shot has been polling for 5 minutes.

**Causes + fixes**:

1. **Job queued behind other users.** Vendor backlog. Wait or check vendor dashboard.

2. **`--timeout` too short.** v1 defaults to 600s. For Sora 2 Pro (long shots), bump to 900s+.

3. **Job actually crashed server-side.** Vendor returns timeout without notification.
   - Fix: cancel, `--resume`. The skill will retry.

---

## "Captions render as boxes / empty"

**Symptom**: Cyrillic / Chinese / Arabic captions are unreadable.

**Cause**: ffmpeg's default font lacks glyphs.

**Fix**: edit `common/runners/ffmpeg.py:burn_captions()` to specify `:fontfile=/path/to/font.ttf`. Recommended fonts with broad coverage:
- Noto Sans (Google) — has all scripts
- Inter (open-source) — Latin + Cyrillic
- IBM Plex Sans (open-source) — Latin + Cyrillic + Greek + others

Set the env var `SKILLS_CAPTION_FONT=/path/to/font.ttf` (planned v2.4.0).

---

## "shot has spoken dialogue but no audio plays"

**Symptom**: User added `Spoken: "..."` to shot screenplay, but final.mp4 has only music — no dialogue audible.

**Cause**: v1 ffmpeg pipeline REPLACES the video's audio track with music. Spoken dialogue from Veo / Sora / Kling is discarded.

**Fix**:
- Generate the reel SILENT (no music): `--music-provider none` (v2.4.0+; v1 workaround: delete music.mp3 before stitch and use `--resume`).
- Or skip captions burn-in and add captions externally in a real editor.
- Real fix in v2.4.0: `--mix-mode duck` will keep dialogue at full volume and duck music under it.

---

## "Generated reel feels off in some way"

Hard to fix without specifics. Run through this checklist:

- Hook lands in first 1.5s? Re-watch — if not, the shot 1 prompt needs work.
- Captions readable on a phone? Test on 5" screen, not desktop. Font might be too small.
- Music starts too abruptly? Add 0.5s fade-IN: edit `ffmpeg.py` mix to add `afade=t=in:st=0:d=0.5`.
- Music feels too loud relative to ambient? Lower `volume=0.5` in ffmpeg.py temporarily.
- Final.mp4 plays slightly out-of-sync? Try `--shot-duration 6` instead of 5 — round numbers + music tempo sometimes drift on edge.

---

## "I want to re-do just one shot"

**Symptom**: Shot 2 is wrong but shots 1 + 3 are good.

**Fix**:
1. Open `manifest.json`.
2. Manually edit shot 2's entry: change `"status": "succeeded"` to `"status": "failed"`. Optionally change the `"prompt"` if you want to re-prompt.
3. Delete `shots/shot-2.mp4` (the file referenced in `output_path`).
4. Run `reel-builder --resume` (in the same output dir, or with `--output <dir>`).
5. Only shot 2 will re-generate. Stitch re-runs at end.

---

## "I want to keep the shots but change the music"

1. Delete `music.mp3` from output dir.
2. Manually edit `manifest.json` to remove the music entry (or mark it failed).
3. Optionally change `--music-style <new-id>` for re-run.
4. `--resume` — music regenerates, stitch re-runs.

---

## "Stitch fails with weird color"

**Symptom**: Final.mp4 has correct frames but colors look washed-out / oversaturated.

**Cause**: Pixel format mismatch between concat input and ffmpeg defaults.

**Fix**: re-encode with explicit pixel format:

```bash
ffmpeg -f concat -safe 0 -i concat-list.txt \
  -pix_fmt yuv420p \
  -c:v libx264 -crf 18 -preset fast \
  -c:a copy \
  output.mp4
```

Patch this into `concat_videos()` for permanent fix.

---

## Resume doesn't pick up where I left off

**Symptom**: --resume re-runs shots that I see saved on disk.

**Causes**:

1. **manifest.json corrupted or missing.**
   - Recovery: manually reconstruct from filenames. Or just delete the dir and start fresh.

2. **Output dir changed between runs.**
   - --resume reads from current dir + topic-slug → manifest. Pass `--output <same-dir>` to align.

3. **The prompts changed.** If you changed the script between runs, the new plan doesn't match the manifest's prompts.
   - Fix: --resume re-uses MANIFEST prompts, not regenerated ones. To use new prompts, delete manifest.json and re-run.
