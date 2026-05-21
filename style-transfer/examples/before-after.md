# style-transfer — calibration

3 example sessions.

---

## Example 1 — Portrait to watercolor

### User says

> Переведи мой портрет (`./me.jpg`) в акварель.

### Plan

```
style-transfer --image ./me.jpg --style watercolor --execute
```

### What happens

1. Default model: `flux-kontext` (best at natural-language style transfer).
2. Style anchor: "transform into a watercolor painting, soft washes of color, visible brush strokes, bleeding edges, paper texture visible".
3. Cost: ~$0.05.
4. Output: `./generated/stylized/me-watercolor.png`.

### Notes

- Face preserved ~70% (recognizable as you, but in watercolor aesthetic).
- For stronger identity preserve: `--model nano-banana-pro`.

---

## Example 2 — Urban scene to cyberpunk

### User says

> Сними улицу из Бруклина (`./street.jpg`) в киберпанк.

### Plan

```
style-transfer --image ./street.jpg --style cyberpunk --execute
```

### What happens

1. Flux Kontext default.
2. Style anchor: "cyberpunk neon aesthetic, neon glow, holographic accents, dark background with vibrant pink/cyan/yellow neons, retrofuturistic feel".
3. Cost: ~$0.05.
4. Output: `./generated/stylized/street-cyberpunk.png`.

### Notes

- Cyberpunk preset is aggressive — neon overlay dominates, original architecture remains but transformed.
- For subtler effect: `--prompt-mod "subtle cyberpunk hints, not over-saturated, mostly preserved urban scene"`.

---

## Example 3 — Custom style — 1920s Soviet propaganda

### User says

> Хочу свой портрет в стиле советского пропагандистского плаката 1920-х — конструктивизм, красный + черный, геометричные формы.

### Plan

```
style-transfer
  --image ./me.jpg
  --style custom
  --prompt-mod "1920s Soviet constructivist propaganda poster style, bold red and black palette, geometric typography influences, heroic figure framing, Rodchenko-era aesthetic without direct artist reference, angular shapes"
  --execute
```

### What happens

1. Custom style mode — entire prompt is the `--prompt-mod`.
2. Cost: ~$0.05.
3. Output: `./generated/stylized/me-custom.png`.

### Notes

- Used descriptive style language ("Rodchenko-era aesthetic") not direct artist reference.
- Identity preserve ~50% (heavy stylization).

---

## Anti-patterns (don't do this)

### Apply 2 strong styles in one pass

❌ `--style cyberpunk --prompt-mod "also with watercolor brush strokes and pixar 3D rendering"`.

Result: model can't reconcile, outputs confused mess.

✓ Apply styles sequentially: style 1 → save → style 2 on the result.

### Living artist name in prompt-mod

❌ `--prompt-mod "in the exact style of [living artist X]"`.

Ethical/legal concerns. Model may approximate signature work.

✓ Describe the era + technique + aesthetic instead.

### Expect identity-preserve in heavy styles

❌ Use `--style cyberpunk` on a portrait expecting the person to look exactly like themselves.

Heavy styles transform faces 30-50%. Default behavior.

✓ For ID-priority: `--model nano-banana-pro` + lighter style like `watercolor` / `sketch`.

### Style-transfer a low-quality JPEG

❌ Input is a 480p heavily-compressed JPEG.

Result: artifacts propagate; style applies inconsistently.

✓ Use highest-quality source available. For low-res sources: upscale first via `upscaler`, then style-transfer.

### Frame-by-frame video style-transfer

❌ Extract frames, style-transfer each, re-assemble.

Temporal coherence breaks; result flickers.

✓ Use video-specific tools (Runway Gen-4 Aleph V2V, Kaiber).
