# audio-mix-maker — calibration

3 example sessions.

---

## Example 1 — Silent screen recording + background music

### User says

> Сделал screen recording демо приложения (без звука). Подложи под него музыку.

### Plan (replace mode)

```
audio-mix-maker
  --video ./screen-recording.mp4
  --audio ./generated/music/upbeat-tech.mp3
  --mode replace
  --volume 0.8
  --fade-out 1.0
  --output ./demo-with-music.mp4
```

### What happens

1. ffmpeg detected.
2. Replace mode: drops video's original (silent) audio.
3. Maps music as sole audio track.
4. Encodes AAC 192kbps.
5. Output: `./demo-with-music.mp4` with the demo + upbeat music.

### Notes

- Replace mode is correct here — source has no audio worth preserving.
- 1-second fade-out softens the end (vs hard cut).

---

## Example 2 — Voiceover-driven explainer + background music (DUCK mode)

### User says

> Записал видео для туториала с голосом за кадром. Хочу подложить музыку под голос, чтобы она тихла, когда я говорю.

### Plan (duck mode)

```
audio-mix-maker
  --video ./tutorial-with-voiceover.mp4
  --audio ./generated/music/ambient-bed.mp3
  --mode duck
  --volume 0.6
  --duck-amount 0.5
  --fade-in 1.0
  --fade-out 1.5
  --output ./tutorial-final.mp4
```

### What happens

1. ffmpeg detected.
2. Duck mode: sidechain compressor analyzes voice track.
3. When you speak, music auto-attenuates to 50% (--duck-amount 0.5).
4. Between sentences / during pauses, music returns to full volume.
5. 1s fade-in at start, 1.5s fade-out at end.
6. Output: `./tutorial-final.mp4` with professional broadcast-style mix.

### Notes

- Duck mode is THE pro feature here — listeners stay focused on speech, music fills the gaps.
- For more aggressive ducking: `--duck-amount 0.4`. For lighter: 0.7.

---

## Example 3 — B-roll with original audio + music bed (OVERLAY mode)

### User says

> Снял атмосферное видео из Бруклина — хочу сохранить уличные звуки и добавить музыку поверх.

### Plan (overlay mode)

```
audio-mix-maker
  --video ./brooklyn-broll.mp4
  --audio ./generated/music/cinematic-cello.mp3
  --mode overlay
  --volume 0.4
  --fade-in 2.0
  --fade-out 3.0
  --output ./brooklyn-final.mp4
```

### What happens

1. Overlay mode: both tracks mixed.
2. Music at 40% (`--volume 0.4`) — sits as a "bed" under the street sounds.
3. 2s fade-in for cinematic opening.
4. 3s fade-out for slow tail.
5. Output: `./brooklyn-final.mp4` with street ambient + music underneath.

### Notes

- Lower `--volume` for documentary feel (music doesn't compete with ambient).
- Long fade-in/out = cinematic; short fades = punchy social.

---

## Anti-patterns (don't do this)

### Use `duck` mode on silent source

❌ Source has no speech, you use `--mode duck` expecting some smart behavior.

Result: behaves identically to overlay (nothing to duck against).

✓ For silent source → `--mode replace`. For ambient-no-speech source → `--mode overlay`.

### Use `replace` mode on a dialogue clip

❌ Source has narration, you `--mode replace` — narration is lost.

✓ For dialogue → `--mode duck` (keeps speech audible).

### High `--volume` on already-loud music

❌ `--volume 1.5` on a mastered track.

Result: digital clipping, harsh peaks.

✓ Default 0.8 is safe. Bump only if music is quiet.

### Hard cuts (no fade)

❌ `--fade-out 0` on a video that ends abruptly.

Result: music ends with a click / pop.

✓ Always at least `--fade-out 0.3` for clean ends. Cinematic: 1-3 seconds.

### Mix music + SFX + voiceover in one call

❌ Try to combine 3 audio sources in a single skill call.

v1 supports ONE audio track. For multi-track: chain calls or use a DAW.
