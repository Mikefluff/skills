# Quality tuning — gif-maker

GIF is a 1989 format with hard constraints: 256-color palette, no real audio, no proper alpha. Quality optimization is mostly about working AROUND these limits.

---

## File size

GIF size scales with: `fps × width × duration × visual_complexity`.

Rough estimates for a 1080×1080 source:

| fps | width | duration | typical size |
|---|---|---|---|
| 12 | 720 | 2s | 500-900 KB |
| 12 | 720 | 3s | 800-1.5 MB |
| 15 | 720 | 3s | 1.2-2.2 MB |
| 24 | 720 | 3s | 2-4 MB |
| 12 | 480 | 2s | 250-500 KB |
| 24 | 1080 | 5s | 8-15 MB |

**For Twitter cards / OG previews**: aim under 1 MB.
**For Slack / Discord**: under 2 MB.
**For email signatures / inline embeds**: under 500 KB.

---

## Color banding

**Symptom**: gradients or skin tones show visible color bands.

**Cause**: 256-color palette can't represent smooth color transitions.

**Fixes**:

1. **Use dithering** (built-in). Skill uses `paletteuse=dither=bayer:bayer_scale=5` which is the best size/quality tradeoff. For even better quality (larger file): set `bayer_scale=2` or use error-diffusion dithering manually.
2. **Source matters more than dithering**. Photoreal video → always bands. Cartoon / illustration / flat color animation → almost no banding.
3. **Reduce source dynamic range**: in Mode B, prompt for "flat illustration", "limited palette", "saturated cartoon aesthetic" — these convert to GIF without visible banding.

---

## Motion looks choppy

**Symptom**: animation looks jumpy or stutters.

**Causes + fixes**:

1. **fps too low.** Default 12fps. Bump to 15 or 18 for smoother motion. Tradeoff: larger file.
2. **Source video frame rate doesn't divide evenly into target fps.** Source at 24fps converted to 13fps creates uneven sampling. Match target fps to a factor of source (24 → 12, 8, or 24).
3. **Source has too much motion variance.** Smooth pans / slow zooms convert better than chaotic action.

---

## Looping isn't seamless

**Symptom**: GIF jumps at the loop point (frame N back to frame 1).

**Cause**: source video doesn't naturally loop.

**Fixes**:

1. **Mode B**: in the prompt, explicitly cue "seamless loop, starting state = ending state, perfectly cyclic motion".
2. **Mode A**: trim source so start frame visually matches end frame. Use `--start` and `--duration` to dial it in.
3. **Manual loop construction**: use ffmpeg to create a "ping-pong" loop (forward then reverse), which always loops seamlessly:

```bash
ffmpeg -i source.mp4 -filter_complex "[0:v]reverse[r];[0:v][r]concat" pingpong.mp4
gif-maker --input pingpong.mp4 --output looping.gif
```

---

## File still too large

If you've optimized fps, width, and duration and still need it smaller:

1. **Lower color count** (manual ffmpeg, not exposed via this skill yet):
   ```bash
   ffmpeg -i source.mp4 -vf "fps=10,scale=480:-1:flags=lanczos,palettegen=max_colors=128" palette.png
   ffmpeg -i source.mp4 -i palette.png -filter_complex "fps=10,scale=480:-1[v];[v][1:v]paletteuse" output.gif
   ```
   128 or 64 colors loses fidelity but cuts size 30-50%.

2. **Switch to WebP / APNG**: smaller + better quality. But less universally supported (some Slack / email / Twitter card previews don't render WebP).

3. **Use MP4 with autoplay**: most modern platforms (Twitter, Slack, Discord) accept MP4 with autoplay + loop, with audio muted. Much smaller than GIF for the same visual quality.

---

## Hosting / distribution

| Platform | Max GIF size | Recommendation |
|---|---|---|
| Twitter | 15 MB | <2 MB for fast load |
| Slack | 50 MB | <5 MB |
| Discord (free tier) | 8 MB | <5 MB |
| Discord Nitro | 100 MB | <20 MB |
| GitHub README | 10 MB | <5 MB |
| Email signature | 1 MB max practical | <500 KB |
| OG image | 5 MB | <2 MB |

For >5 MB GIFs, use MP4 with `<video autoplay loop muted playsinline>` HTML, or a hosted GIF service (Giphy, Imgur).

---

## When NOT to use GIF

- **>5 second clips** → use MP4 (autoplay loop in HTML, or reel-builder for shorts)
- **Audio matters** → use MP4
- **Photoreal high-color video** → use WebP or MP4 (GIF will band visibly)
- **Alpha transparency needed** → use APNG or WebP

GIF is best for: short, animated, limited-palette, motion-driven content where universal browser support matters more than file size.
