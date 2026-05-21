# ffmpeg styling — subtitle-burner

Style presets + per-flag customization.

---

## Style presets

### `modern` (default)

Clean white text on black backplate. Most-used "social media subtitles" look.

- font-size: 48pt (~7% of 1920p frame height)
- font-color: white
- box-color: black at 60% opacity (`black@0.6`)
- box-border-width: 20px (padding around text)
- position: centered horizontally, lower-third vertically (`y = h - text_h*2.5`)

Best for:

- TikTok / IG Reels / YouTube Shorts where social-media-style captions are expected
- Tutorials / how-to videos
- Talking-head content

### `minimal`

Same white text + lower-third, no backplate. For when the video has clean backgrounds and captions can rely on the video's own contrast.

- font-size: 42pt
- font-color: white
- box-color: `black@0` (fully transparent)
- box-border-width: 0
- position: lower-third

Best for:

- High-contrast videos (e.g., a person against a clean wall) where text reads without backplate
- Editorial / cinematic content where backplates feel UI-y
- Branded content with a strong visual signature

Caveat: if the video has busy / variable backgrounds, text will be hard to read in spots. Use `modern` instead.

### `bold`

High-contrast yellow text + dense black backplate + larger size. For high-visibility / high-energy content.

- font-size: 56pt
- font-color: yellow
- box-color: `black@0.85` (very opaque)
- box-border-width: 24px
- position: lower-third

Best for:

- High-energy reels (sports, drill, edits with hard cuts)
- Outdoor / variable-lighting videos where contrast matters most
- TikTok meme / viral-format videos

---

## Per-flag customization

Override individual aspects of any preset:

```bash
subtitle-burner burn ./clip.mp4 --subtitle ./caps.srt --style modern --font-size 56
subtitle-burner burn ./clip.mp4 --subtitle ./caps.srt --style minimal --font-color cyan
subtitle-burner burn ./clip.mp4 --subtitle ./caps.srt --style bold --box-color "red@0.7"
```

Available overrides:

- `--font-size <int>` — font height in points (typical: 32-72)
- `--font-color <color>` — color name or hex. ffmpeg supports: `white`, `black`, `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `orange`, `pink`, `gray`, `0xRRGGBB` hex
- `--box-color <color@alpha>` — backplate color + opacity. Format: `black@0.6` (60% opacity black) or `0xRRGGBB@0.5`

---

## Position

Default position is lower-third (`y = h - text_h * 2.5`). This is hardcoded in `common/runners/ffmpeg.py:burn_captions`.

To change position:

1. Edit `ffmpeg.py:burn_captions`
2. Modify the `y=...` part of the drawtext filter
3. Common alternatives:
   - Top-third: `y=text_h*1.5`
   - Center: `y=(h-text_h)/2`
   - Custom pixel offset: `y=120` (120px from top)

For platform-specific safe zones (TikTok / IG Story):

- TikTok UI mask: top 80-220px + bottom 250-350px
- IG Story UI mask: top 220px + bottom 250px
- Safe lower-third for vertical 9:16 (1920px): y ≈ 1430 (avoids bottom UI mask)

---

## Font selection

By default, ffmpeg uses its built-in font (typically DejaVuSans-Bold on Linux/Mac).

This font has:
- Full Latin (ASCII + extended Latin diacritics)
- Cyrillic (basic Russian / Ukrainian / Bulgarian)
- Greek

It LACKS:
- CJK (Chinese / Japanese / Korean)
- Arabic / Hebrew
- Most decorative fonts

For non-default fonts (planned v2.7 — for now requires editing ffmpeg.py):

```python
# In ffmpeg.py burn_captions, add `:fontfile=...` to the drawtext filter:
f"drawtext=fontfile=/path/to/Inter-Bold.ttf:text='...':..."
```

Recommended fonts (widest script coverage):

- **Noto Sans** (Google) — every script, free. Install: `brew install --cask font-noto-sans` (Mac) or download from fonts.google.com.
- **Inter** (open-source) — Latin + Cyrillic, modern sans-serif
- **IBM Plex Sans** — Latin + Cyrillic + Greek
- **Source Sans Pro** (Adobe) — Latin + Cyrillic
- **Noto Sans CJK** — for Chinese / Japanese / Korean specifically

---

## Color reference

Common color choices for captions:

| Color name | Hex | Best for |
|---|---|---|
| `white` | #FFFFFF | Default; most contrast on dark/varied backgrounds |
| `yellow` | #FFFF00 | High-energy; viral / hook captions |
| `cyan` | #00FFFF | Cool / modern brand feel |
| `0xFFD700` | gold | Premium / luxury content |
| `0xFF6B6B` | coral | Warm / casual / friendly |
| `0x00C9A7` | mint | Tech / SaaS brand |

Backplate alpha guide:

| Alpha | Visual | Use case |
|---|---|---|
| `@0` | invisible | Minimal preset; clean backgrounds |
| `@0.4` | semi-transparent | Subtle backplate, video shows through |
| `@0.6` | medium opacity | Default; balances readability + video visibility |
| `@0.85` | dense | Bold preset; max readability on busy backgrounds |
| `@1.0` | fully opaque | TV-style hard backplate |

---

## Performance notes

`burn_captions` re-encodes the video stream (drawtext is a video filter; ffmpeg can't drawtext on a copied stream). Audio is copied (`-c:a copy`).

Re-encoding time:

- 1080p × 30s × default H.264: ~10-20s on a modern Mac
- 1080p × 60s: ~20-40s
- 4K × 30s: ~60-120s
- Vertical (1080×1920) × 30s: ~15-25s

Slower than a pure-copy operation (~1s). For massive video libraries, consider running the skill in parallel via shell `xargs -P`.

---

## Multiple subtitle tracks

The skill burns ONE track per run. To overlay two tracks (e.g., original + translation):

1. First burn: original captions
2. Second burn: input = output of first burn, subtitles = translation file

```bash
subtitle-burner burn clip.mp4 --subtitle clip-en.srt --output clip-en-burned.mp4
subtitle-burner burn clip-en-burned.mp4 --subtitle clip-es.srt --style minimal --output clip-bilingual.mp4
```

The second burn places translation captions at the same lower-third position (potentially overlapping). To stack them, edit position in the second burn (planned `--position` flag, or edit ffmpeg.py).

---

## Format conversion

Input video format and output video format match by default. If the input is `.mov` and the user wants `.mp4`:

```bash
subtitle-burner burn ./clip.mov --subtitle ./caps.srt --output ./clip.mp4
```

ffmpeg handles the container conversion automatically as part of the re-encode.

Supported containers: any ffmpeg can read (`.mp4`, `.mov`, `.webm`, `.mkv`, `.avi`, `.flv`, ...). Output uses container inferred from `--output` extension.

For WebM / VP9 output:

```bash
subtitle-burner burn ./clip.mp4 --subtitle ./caps.srt --output ./clip.webm
```

ffmpeg picks the appropriate codecs (vp9 + opus) automatically.
