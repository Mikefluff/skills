# gif-maker — calibration

3 example sessions.

---

## Example 1 — Convert existing reel to social GIF

### User says

> У меня есть готовый reel `reel.mp4`. Сделай из него короткую гифку 2 секунды для твиттера, квадратный аспект.

### Plan (Mode A)

```
gif-maker
  --input ./reel.mp4
  --aspect 1:1
  --duration 2.0
  --start 1.5
  --fps 12
  --width 720
  --output ./twitter-gif.gif
```

### What happens

1. ffmpeg detected.
2. Source MP4 cropped center to 1:1, trimmed from 1.5s to 3.5s (2 seconds total).
3. 2-pass palette generation: palettegen → palette.png (deleted after) → paletteuse with bayer dithering.
4. Output: `./twitter-gif.gif` (~600-900 KB).

### Notes

- Twitter accepts up to 15 MB GIFs but anything under 2 MB loads fast.
- For maximum Twitter-card-preview compatibility: keep under 1 MB.

---

## Example 2 — Generate abstract loop from prompt

### User says

> Сгенерируй короткий зацикленный фрагмент: волны нейронной сетки переливаются цветами, абстракция, 3 секунды, для шапки твиттера.

### Plan (Mode B)

```
gif-maker
  --prompt "Abstract neural mesh waves rippling and shifting colors smoothly, seamless loop with ending matching the start, vibrant cyan-to-magenta gradient palette, flat illustration aesthetic, 3 seconds"
  --model veo-3-1-fast
  --duration 3.0
  --aspect 2:1
  --width 1080
  --fps 12
  --execute
  --yes
```

### What happens

1. Pre-flight: `veo-3-1-fast` available (GEMINI_API_KEY present), estimated cost ~$1.20.
2. Generate via Veo: poll-with-timeout, returns MP4.
3. Save intermediate MP4: `./generated/gif/_source/20260521-XXXXXX-gif-source.mp4`.
4. Center-crop to 2:1 (1080×540), trim to 3s, palette-convert.
5. Output: `./generated/gif/gif-source.gif` (~1.5-2.5 MB).

### Notes

- "Flat illustration aesthetic" in the prompt prevents banding when converting to 256 colors.
- "Seamless loop with ending matching the start" hints the model toward cyclical motion.
- 2:1 aspect (1080×540) is good for Twitter header card preview.

---

## Example 3 — Convert long video, trim + downscale aggressively

### User says

> У меня 30-секундный mp4 с длинной анимацией. Нужна гифка ~1.5 секунды самого яркого момента (около 12-й секунды), маленькая, для слака.

### Plan (Mode A)

```
gif-maker
  --input ./animation-long.mp4
  --start 12.0
  --duration 1.5
  --aspect 1:1
  --width 480
  --fps 10
  --output ./slack-reaction.gif
```

### What happens

1. ffmpeg trims to [12.0s, 13.5s].
2. Center-crops 16:9 source to 1:1.
3. Scales to 480px width.
4. fps lowered to 10 (Slack reactions don't need 12fps).
5. 2-pass palette → small GIF (~200-400 KB).

### Notes

- `--width 480 --fps 10` is the "tiny GIF" recipe — under 500 KB for short clips, fast to load anywhere.
- Slack file upload limit is 50 MB but reactions / inline embeds should stay <2 MB for performance.

---

## Anti-patterns (don't do this)

### Trying to GIF a 30-second photoreal video

❌ `gif-maker --input full-reel.mp4 --duration 30`

Result: 30+ MB GIF with heavy banding. Useless.

✓ Either trim to 1-3 seconds, or skip GIF and use MP4 with autoplay-loop HTML.

### Photoreal portrait → GIF

❌ Mode B prompt asking for photoreal close-up shots.

Result: visible color banding on skin, eyes, hair.

✓ Use flat illustration / cartoon / abstract aesthetic in Mode B prompts:

```
--prompt "Animated character in flat illustration style, 4-color palette, simple action"
```

### High fps for marginal smoothness

❌ `--fps 30 --width 1080 --duration 5` — produces 8-15 MB GIF.

✓ 12fps at 720px is the social-media sweet spot. Go higher only if you can host an MP4 instead.

### Long source, no trim

❌ Convert a 2-minute video to GIF without `--duration`.

Result: enormous file, slow to load, often rejected by platforms.

✓ Always trim. If unsure of the right segment, preview the source first.
