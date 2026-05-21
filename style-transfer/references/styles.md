# Style presets — style-transfer

12 curated directions + `custom`. Each implies a different baseline prompt; the skill assembles the final prompt by combining the preset's anchor with optional `--prompt-mod`.

---

## `watercolor`

**Prompt anchor**: soft washes of color, visible brush strokes, bleeding edges, paper texture visible.

**Best for**: portraits, landscapes, still life — anything that benefits from softness.

**Identity preserve**: ~70%. Faces remain recognizable.

**Pitfall**: very saturated source colors may bleed unpredictably.

---

## `oil-painting`

**Prompt anchor**: thick oil painting, visible brush strokes, impasto texture, rich pigments, classical painting feel.

**Best for**: portraits with character, dramatic scenes, fruits/flowers, classical subjects.

**Identity preserve**: ~65%.

**Pitfall**: can look "muddy" if source has too many fine details. Best with clean, simple compositions.

---

## `sketch`

**Prompt anchor**: pencil sketch, graphite shading, cross-hatching, white paper background, no color.

**Best for**: portraits, architectural studies, hand-drawn aesthetic for blog headers.

**Identity preserve**: ~75% (no color simplifies; line structure stays).

**Pitfall**: loses color information (intentionally). For color sketch → add `--prompt-mod "with selective color accents"`.

---

## `line-art`

**Prompt anchor**: clean black line art, no shading, no color, just outlines on white background.

**Best for**: logos, icons, illustration style for documentation, coloring-page-style outputs.

**Identity preserve**: ~80% (geometric structure preserved).

**Pitfall**: complex source loses internal detail. Best with strong silhouettes.

---

## `ink-wash`

**Prompt anchor**: Chinese ink-wash painting style, sumi-e aesthetic, brush stroke economy, monochromatic ink tones, soft gradient washes.

**Best for**: nature scenes, minimal portraits, meditative compositions.

**Identity preserve**: ~60% (heavily stylized).

**Pitfall**: not all subjects fit — modern tech/urban scenes look weird.

---

## `cyberpunk`

**Prompt anchor**: cyberpunk neon aesthetic, neon glow, holographic accents, dark background with vibrant pink/cyan/yellow neons, retrofuturistic feel.

**Best for**: urban scenes, portraits with attitude, sci-fi vibes, gaming content.

**Identity preserve**: ~30% (heavy style overlay).

**Pitfall**: oversaturated, can feel cliché. Counter with `--prompt-mod "subtle cyberpunk hints, not over-saturated"`.

---

## `studio-ghibli`

**Prompt anchor**: Studio Ghibli animation style, hand-painted aesthetic, soft watercolor backgrounds, expressive characters, Miyazaki-inspired.

**Best for**: portraits, nature scenes, magical / nostalgic moods.

**Identity preserve**: ~50% (character stylization).

**Pitfall**: legally / ethically fraught for commercial use (clear derivative). For personal / non-commercial: usually fine. For commercial: pick "hand-painted animation" via `custom` instead.

---

## `pixar-3d`

**Prompt anchor**: Pixar 3D animation style, smooth surfaces, expressive features, cinematic lighting, vibrant colors.

**Best for**: family portraits as 3D characters, character design references.

**Identity preserve**: ~40%.

**Pitfall**: same as Ghibli — derivative of a specific studio. Use cautiously commercially.

---

## `manga`

**Prompt anchor**: Japanese manga style, black and white, screentone patterns, expressive line art, action lines.

**Best for**: portraits, action scenes, character designs.

**Identity preserve**: ~55%.

**Pitfall**: high contrast loses subtle features.

---

## `art-deco`

**Prompt anchor**: Art Deco poster style, geometric shapes, gold + black palette, 1920s aesthetic, symmetric composition.

**Best for**: portraits with elegance, architecture, event posters, brand imagery.

**Identity preserve**: ~50%.

**Pitfall**: forces geometric simplification; faces become stylized.

---

## `low-poly`

**Prompt anchor**: low-poly 3D aesthetic, flat triangular facets, limited palette, geometric simplification.

**Best for**: gaming assets, tech illustrations, abstract portraits.

**Identity preserve**: ~40%.

**Pitfall**: faces look angular/abstract; not for client portraits.

---

## `vaporwave`

**Prompt anchor**: vaporwave aesthetic, pastel pink/purple/cyan palette, retro 80s neon grid, glitch effects, dreamlike.

**Best for**: nostalgic / 80s revival content, music video stills, social media aesthetic posts.

**Identity preserve**: ~35%.

**Pitfall**: heavily stylized; works best on already-aesthetic source images.

---

## `custom`

For styles not in the preset list. Requires `--prompt-mod "<your description>"`.

**Examples**:

```
--style custom --prompt-mod "1920s Soviet constructivist poster style, bold red and black, geometric typography, heroic figures"

--style custom --prompt-mod "Studio Trigger anime style, sharp angular forms, neon accents, kinetic energy lines"

--style custom --prompt-mod "Edward Hopper urban realism style, melancholic lighting, isolated figures, 1940s American urban aesthetic"

--style custom --prompt-mod "Ghibli-adjacent hand-painted animation aesthetic, soft watercolor textures, no specific studio reference"
```

For ethically-cleaner descriptors: avoid living-artist names. Use era + technique + aesthetic descriptors.

---

## Decision tree

```
Portrait, soft & artistic         → watercolor
Portrait, dramatic & textured     → oil-painting
Portrait, monochrome              → sketch / line-art / manga / ink-wash
Sci-fi / urban / tech mood        → cyberpunk
Nostalgic / dreamy / magic        → studio-ghibli / vaporwave
Family-friendly 3D character      → pixar-3d
Bold poster aesthetic             → art-deco
Tech illustration                 → low-poly
80s nostalgia                     → vaporwave
Specific non-listed style         → custom + --prompt-mod
```
