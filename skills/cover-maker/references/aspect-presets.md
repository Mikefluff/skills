# Aspect presets — cover-maker

Pixel dimensions per medium.

---

## Medium → aspect

| `--medium` | Dimensions | Ratio | Target |
|---|---|---|---|
| `album` | 3000×3000 | 1:1 | Spotify / Apple Music / Bandcamp / Tidal album cover |
| `book` | 1600×2400 | 2:3 | Amazon KDP / Apple Books / paperback POD |
| `podcast` | 3000×3000 | 1:1 | Apple Podcasts (3000×3000 min) / Spotify Podcasts / Overcast |
| `magazine` | 1600×2400 | 2:3 | Print magazine cover convention; digital subscription apps |
| `report` | 1240×1754 | 1:√2 | A4 portrait at 150 DPI (preview); upscale to 2480×3508 for 300 DPI print |
| `deck-cover` | 1920×1080 | 16:9 | Slide deck title slide |
| `linkedin-doc` | 1080×1080 | 1:1 | LinkedIn document cover |
| `instagram-cover` | 1080×1350 | 4:5 | IG portrait feed (cover image) |

---

## Custom aspect

Pass `--aspect WxH` to override the medium default:

```bash
cover-maker --title "Single" --creator "Artist" --medium album --aspect 1080x1080 --execute   # smaller, cheaper for web preview
```

---

## Standard model size limits

Some providers don't honor arbitrary dimensions:

- **flux-schnell**: defaults to 1024×1024 regardless
- **nano-banana-pro**: honors most sizes, may round
- **gpt-image-2**: honors documented sizes (1024², 1024×1536, 1536×1024, etc.) — non-standard requests get the nearest match
- **ideogram-3-quality**: honors most aspect ratios
- **nano-banana-pro**: honors common aspects (1:1, 4:3, 3:4, 16:9, 9:16)

If the output is off-spec by a few pixels, resize in your image editor.

---

## Print resolutions

The default sizes are RGB at 150 DPI (preview-quality). For true print:

| Medium | Skill output | True print (300 DPI) | Method |
|---|---|---|---|
| `album` | 3000×3000 | 3600×3600 for liner notes / vinyl | Upscale 1.2× in Photoshop / Affinity |
| `book` | 1600×2400 | 1800×2700 for 6×9" hardcover | Upscale 1.13× |
| `podcast` | 3000×3000 | 3000×3000 is ALREADY high — most podcasts don't need 300 DPI | OK as-is |
| `magazine` | 1600×2400 | 2480×3720 for 8.27×12.4" cover | Upscale 1.55× |
| `report` | 1240×1754 | 2480×3508 for A4 print | Upscale 2× |
| `deck-cover` | 1920×1080 | 1920×1080 is FHD slide standard | OK as-is |

Upscaling: use Photoshop's "Preserve Details 2.0" or Affinity's Lanczos. AI upscalers (Real-ESRGAN via Replicate) work too — see `bg-remover` / future `upscaler` skill.

CMYK conversion: don't do this in the skill output (it's RGB). Open in a DTP tool and convert RGB → CMYK before sending to print.

---

## Aspect-aware composition

The composition template adapts to the aspect. See `composition-zones.md` for per-medium templates.

- 1:1 aspects: balanced; title typically top, visual middle, optional creator at bottom
- 2:3 portrait: top-heavy title, middle visual, bottom creator
- 16:9 landscape: side-by-side OR top-bottom (skill defaults to top-headline; pass `--composition side-headline` for split)
- 1:√2 (A4): top-zone title with more margin, dominant middle, bottom org strip

If the chosen aspect doesn't fit any preset cleanly, the skill defaults to the "1:1 balanced" template.

---

## File naming

Per-variant output files:

```
<medium>-v1.png
<medium>-v2.png
<medium>-v3.png
```

Or if `--variants 1`:

```
<medium>.png
```

Examples:

- `./generated/cover/slow-software-book/book-v1.png`
- `./generated/cover/slow-software-book/book-v2.png`
- `./generated/cover/lunar-vault-album/album-v1.png`
- `./generated/cover/lunar-vault-album/album-v2.png`

---

## Slug rules

Same as other skills:

- Kebab-case lowercase of `--title`
- Append `-<medium>` if not already in title
- Max 40 chars before suffix
- ASCII (transliterate non-Latin)

Override via `--output <dir>`.

---

## Cross-medium runs

To produce the SAME cover at multiple mediums (e.g., album + podcast + LinkedIn-doc for a launch):

```bash
cover-maker --title "Lunar Vault" --creator "Alex" --medium album --variants 2 --execute
cover-maker --title "Lunar Vault" --creator "Alex" --medium podcast --variants 2 --execute
cover-maker --title "Lunar Vault" --creator "Alex" --medium linkedin-doc --variants 2 --execute
```

Three runs because each medium has different composition + aspect. To maintain visual consistency across runs:

- Same `--style <id>` for all three
- Same `--model <slug>` for all three
- Same `--photo` reference (if any)

The composition adapts per medium, but the palette / typography / mood stay the same.
