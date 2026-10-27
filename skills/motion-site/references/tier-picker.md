# Tier picker & archetype catalog

Decide **webgl vs light** per effect, then pick a **direction** from the catalog.
State the pick and why before building.

## webgl vs light

Use **webgl** (Three.js / R3F + GLSL) only when the effect needs the GPU:

- thousands of moving points (particle fields, morphs)
- a procedural surface that must react continuously (fluid, noise, raymarched)
- real 3D: models, characters, depth, a camera that moves through space
- per-pixel refraction / transmission (true liquid glass), displacement, fresnel
- postprocessing (bloom, DOF, chromatic aberration) over a live scene

Use **light** (CSS / SVG / GSAP / Framer Motion) for everything else — and prefer
it when either tier would do. Cheaper, reduced-motion-trivial, no GPU, no teardown:

- scroll reveals, staggers, counters, pinned text
- parallax, sticky scroll galleries, horizontal scroll sections
- kinetic type (split chars/lines, mask reveals)
- marquees, magnetic buttons, hover micro-interactions
- gradient-mesh / aurora backgrounds that don't need per-pixel simulation
- SVG path draw, stroke, and morph

**The test:** if a gradient, a blur, a mask, and a transform get you there, it is a
light effect. Reach for a shader or a 3D scene only when those cannot.

Downgrade rule: a webgl effect must have a light-tier or static fallback for mobile
/ low-end / `Save-Data` / reduced-motion (craft-floor.md). If you cannot describe
that fallback, the effect is too heavy for the brief.

## Archetype catalog

Each is a *starting direction*, not a template. It maps to a tier and the
reference(s) to load, then you build it for this brief.

| Archetype | Tier | What it is | Load |
|---|---|---|---|
| `particle-self` | webgl | Points scatter → assemble into a logo/shape, drift, react to cursor; often scroll-linked | particles.md (+ scroll-3d.md) |
| `scroll-3d` | webgl | A 3D object/scene animated by scroll — camera dolly, rotate, pinned section reveal | scroll-3d.md (+ materials-3d.md) |
| `fluid-gradient` | webgl | Full-bleed animated gradient driven by flow/curl noise in a fragment shader | shaders.md |
| `aurora` | light→webgl | Soft drifting color fields. Light: layered blurred blobs + CSS. Heavy: noise shader | light-motion.md / shaders.md |
| `liquid-glass` | webgl | Refractive glass panel/blob over content — `MeshTransmissionMaterial` | materials-3d.md (+ postprocessing.md) |
| `metaball` | webgl | Blobs that merge — raymarched SDF or threshold-filtered points | shaders.md |
| `noise-field` | webgl | Procedural noise surface/plane, displaced or colored by FBM | shaders.md |
| `starfield` | webgl | Depth starfield / warp tunnel, speed-linked to scroll or hover | particles.md |
| `kinetic-type` | light | Headline that splits, masks, staggers, or reveals on scroll | light-motion.md |
| `marquee` | light | Seamless infinite scrolling strip, speed reacts to scroll velocity | light-motion.md |
| `magnetic` | light | Buttons/links that pull toward the cursor, elastic return | light-motion.md |
| `sticky-gallery` | light | Pinned section, cards/images move horizontally as you scroll vertically | light-motion.md (+ compose-page.md) |
| `image-distortion` | webgl | Images on planes with hover/scroll displacement (RGB shift, ripple) | shaders.md (+ materials-3d.md) |
| `3d-viewer` | webgl | Interactive product model — orbit, auto-spin, HDRI lighting | materials-3d.md |
| `3d-character` | webgl | A rigged/posed glTF character, idle or scroll-posed, with env lighting | materials-3d.md |

When the brief names none, infer from the vibe words: "premium / refined /
Apple-like" → liquid-glass or scroll-3d; "energetic / crypto / AI" → particle-self
or fluid-gradient; "editorial / agency" → kinetic-type + sticky-gallery + marquee;
"product launch" → 3d-viewer or scroll-3d. Offer one direction, build it, note the
alternative in one line rather than listing a menu.

## `--variants N`

Produce N genuinely different directions of the *same section* (e.g. a hero as
particle-self, as fluid-gradient, and as kinetic-type), not N tweaks of one. Cap
N ≤ 3 — more spends build time no one reads. Each variant is its own file under
`./generated/motion-site/<slug>/variant-<n>/`.
