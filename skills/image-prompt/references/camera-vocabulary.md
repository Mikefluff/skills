# Camera + lens vocabulary

Use when the image should look like a **photograph** (photorealistic models: Midjourney v6, Flux, Nano Banana, SDXL realistic checkpoints). Skip entirely for illustration / 3D / abstract — it confuses non-photo models.

---

## Lens choice by use case

| Lens | Aperture range | What it does | Use when |
|---|---|---|---|
| **24mm** | f/4-f/16 | Very wide, slight distortion at edges | Landscape, architecture, environmental wide shots |
| **35mm** | f/2.8-f/11 | Wide enough for context, low distortion | Documentary, street, environmental portrait |
| **50mm** ("nifty fifty") | f/1.8-f/8 | "Normal" — matches human eye | Versatile — product, portrait, scene |
| **85mm** | f/1.4-f/2.8 | Classic portrait — flattering compression | Headshots, beauty, fashion |
| **100mm macro** | f/2.8-f/8 | Close-up detail | Macro / product details |
| **135mm** | f/1.8-f/2.8 | Even more compression, isolates subject | Sports, fashion |
| **70-200mm zoom** | f/2.8-f/4 | Versatile telephoto | Events, sports |
| **Wide-angle 16mm** | f/4-f/16 | Dramatic perspective | Real estate, architecture, surreal |

Use these as **paste-ready tags** in the prompt: `"85mm lens, f/1.8"` / `"35mm wide, f/4"` / `"100mm macro, f/2.8"`.

---

## Aperture (f-stop) — controls depth of field

| Aperture | Depth of field | Look |
|---|---|---|
| f/1.4 | Razor-thin | Background totally blurred, dreamy bokeh |
| f/1.8 | Shallow | Sharp eyes, soft everything else |
| f/2.8 | Shallow | Sharp subject, soft background |
| f/4 | Medium-shallow | Subject and immediate context sharp |
| f/5.6 | Medium | Most of frame in focus |
| f/8 | Deep | Almost everything sharp |
| f/11 | Very deep | Foreground to infinity sharp |
| f/16+ | Maximum DOF | Sharp everywhere; slight diffraction softness |

Match aperture to lens choice:
- Portrait (85mm): f/1.4 to f/2.8
- Product (50mm): f/4 to f/8
- Architecture (24mm): f/8 to f/16
- Landscape (any wide): f/8 to f/16

---

## Camera body / format hints

Tells the model what kind of camera "took" the photo:

| Tag | Effect |
|---|---|
| "Full-frame DSLR" | Modern, clean, professional |
| "Mirrorless" | Modern, slightly different rendering |
| "Medium format" | Higher detail, slightly different tonality |
| "35mm film" | Grain + warm tones + slight imperfection |
| "Polaroid" | Square format, soft, vintage |
| "Smartphone photo" | Casual, slight digital noise |
| "Disposable camera" | Heavy grain, color shifts, casual |
| "Hasselblad" | Premium, high-detail, fashion |
| "Leica" | Classic, considered composition |

---

## Quality tags (almost always include for photorealistic)

Append to the end of the prompt:

- `8K` or `4K` — high resolution implication
- `photorealistic` — the magic word
- `ultra-realistic`
- `hyper-detailed`
- `sharp focus`
- `tack-sharp`
- `cinematic`
- `editorial`
- `magazine-quality`
- `professional photography`
- `award-winning`

**Don't stack all of them.** Pick 3-4 that fit. Example: `"8K, ultra-realistic, sharp focus, cinematic color grading"`.

---

## Composition hints

### Framing

| Tag | What it means |
|---|---|
| "Close-up" | Subject fills frame |
| "Medium shot" | Subject from waist up |
| "Wide shot" | Subject + significant environment |
| "Extreme close-up" | Single feature (eye, lips, hand) |
| "Full body" | Head to feet |
| "Three-quarter" | Subject at 3/4 angle, knees up |
| "Bird's eye view" | Looking straight down |
| "Worm's eye view" | Looking straight up |
| "Dutch angle" | Tilted horizon, unease |
| "Over-the-shoulder" | Behind one subject, looking at another |

### Rule of thirds and asymmetry

- "Subject off-center to the right, negative space on the left" — composition
- "Centered composition" — formal, symmetric
- "Asymmetric composition with diagonal energy"
- "Tight crop, edges of subject visible"

### Foreground / midground / background

- "Foreground bokeh of out-of-focus leaves, subject in midground sharp, dreamy soft background"
- "Subject in sharp midground, blurry foreground (over-the-shoulder framing)"

---

## Color and tone

### Color grades

- **Teal and orange**: classic cinematic (shadows teal, highlights warm)
- **Bleach bypass**: high contrast, desaturated
- **Cross-processed**: cool shadows, warm highlights, slight color shift
- **Sepia**: warm brown monochrome
- **Cool / cold**: blue-heavy
- **Warm**: amber/orange-heavy
- **Muted**: low saturation throughout
- **Vibrant / saturated**: punchy colors

### Specific film stocks (great for "shot on film" looks)

- "Kodak Portra 400" — warm, soft, classic portrait film
- "Kodak Tri-X" — black and white, grainy, documentary
- "Fuji Velvia" — saturated, landscape film
- "Cinestill 800T" — tungsten-balanced, halo around lights
- "Ilford HP5" — black and white, classic newspaper feel

These produce instantly-recognizable looks. Worth using when you want "shot on film" aesthetic.

---

## Anti-patterns

❌ Camera tags on illustrations:
> "Watercolor illustration, 85mm lens, f/1.8"
The model gets confused. Either it's a photo (use camera) or it's an illustration (skip camera).

❌ Too many camera tags:
> "85mm lens, 50mm lens, full-frame, medium format, Hasselblad, Leica, Polaroid"
Pick one camera/lens combo.

❌ Wrong aperture for the lens choice:
> "24mm lens, f/1.4" (wide-angle is rarely f/1.4 — most are f/2.8 or slower)
Stick to realistic combos.

❌ "Professional camera" / "high-end equipment":
Empty calorie. Replace with specific lens + body tags.

✅ Real-world combos that work:
- Portrait: "85mm lens, f/1.8, shot on full-frame DSLR"
- Product: "50mm prime, f/4, medium format Hasselblad, studio lighting"
- Landscape: "24mm wide-angle, f/11, full-frame, tripod-stable sharp focus"
- Documentary: "35mm, f/2.8, Kodak Tri-X film grain"
- Editorial portrait: "85mm, f/1.4, Kodak Portra 400 film tones"

---

## Quick-reference cheat sheet

```
Headshot:      85mm, f/1.8, full-frame, sharp focus on eyes
Product:       50mm, f/4, 8K, commercial advertising style
Landscape:     24mm, f/11, golden hour, ultra-detailed
Street:        35mm, f/2.8, Tri-X grain, candid
Cinematic:     35mm anamorphic, f/2, teal-and-orange grade
Beauty:        85mm, f/2.8, butterfly lighting, retouched-natural skin
Macro detail:  100mm macro, f/2.8, soft shallow depth of field
```
