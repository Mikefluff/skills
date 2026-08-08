# 3D prompt grammar

A 3D prompt and an image prompt describe different things, and half of what
makes an image prompt good makes a 3D prompt worse.

There is no camera. There is no lens, no depth of field, no golden hour, no
composition. The generator is building geometry that will be lit by whatever
engine the mesh ends up in, so lighting words either do nothing or get baked into
the texture as a shadow that is wrong from every other angle.

---

## What to say instead

| Axis | Say | Not |
|---|---|---|
| Form | "rounded, chunky proportions, thick limbs" | "beautiful", "detailed" |
| Silhouette | "tall narrow spire, wide base" | "epic", "imposing" |
| Material | "brushed copper, matte ceramic base" | "8k texture", "photorealistic" |
| Scale cue | "hand-sized", "life-size chair" | "huge", "tiny" |
| Style | "low-poly", "stylised cartoon", "hard-surface sci-fi" | "trending on ArtStation" |
| Pose | "sitting, tail curled around the feet" | "dynamic", "action-packed" |

The rule underneath: **anything a sculptor could act on belongs in the prompt;
anything a photographer would act on does not.**

---

## Shape of a good prompt

One object, then form, then material, then style. Twenty to forty words is the
band where these models behave — past that they start dropping clauses rather
than obeying them.

```text
A low-poly red fox, sitting, tail curled around its feet, oversized head,
stylised flat-shaded fur, matte finish, game-asset proportions

A hand-sized ceramic teapot, squat rounded body, thick curved spout, matte
white glaze with a single cobalt band, hard-surface

A weathered iron lantern, hexagonal glass housing, ring handle on top,
pitted metal, hard-surface, life-size
```

---

## From a photo

With `--image-url`, the image is the specification and the prompt becomes a hint
for what the image cannot show — the back of the object, mostly.

> back of the jacket is plain, no print

Do not re-describe what is visible in the photo. The generator is already
looking at it, and a description that disagrees with the pixels produces a mesh
that splits the difference.

---

## Things that reliably fail

- **Scenes.** "A fox in a forest" returns a fox fused to a lump of forest. One
  object per call, assemble in the target tool.
- **Text on the model.** Lettering comes back as noise-shaped geometry. Add text
  as a texture or a decal in the engine.
- **Thin, unsupported features.** Whiskers, wires, chain links, spokes — either
  absent or fused. Model them separately or accept the loss.
- **Interiors.** These generators produce a shell. "A house you can walk into"
  gets you a house-shaped exterior.
- **Exact dimensions.** "12 cm tall" is not honoured. Scale in the engine, where
  it is a single number.
