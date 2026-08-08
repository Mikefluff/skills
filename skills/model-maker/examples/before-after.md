# model-maker calibration

Three runs showing input → expected shape of the output.

---

## Example 1 — game prop from text

### User request

> model-maker "a weathered iron lantern for a game"

### What happens

1. Subject is one object and concrete enough. No clarification needed.

2. Prompt written in 3D grammar — form, material, scale, style; no camera, no
   lighting:

   > A weathered iron lantern, hexagonal glass housing, ring handle on top,
   > pitted dark metal, hard-surface, life-size

3. Tier: textured (default). A prop that goes straight into a scene wants its
   material baked in.

4. Cost: $0.40, over the $0.10 threshold, so the runner asks first.

5. Executes:

   ```bash
   python3 -m common.runners.cli.model3d --model tripo-v3 \
     --prompt "A weathered iron lantern, hexagonal glass housing, ring handle on top, pitted dark metal, hard-surface, life-size" \
     --yes
   ```

6. Output: `./generated/model/20260808-143000-tripo-v3.glb`

### What to notice

- No "cinematic", no "8k", no "volumetric light". None of it survives into
  geometry, and lighting words bake shadows that are wrong from every other angle.
- "Ring handle on top" is a silhouette instruction. That is the kind of detail
  these models obey.
- The glass housing comes back as solid geometry, not transparent. Transparency
  is a material setting in the target engine.

---

## Example 2 — product mesh from a photo

### User request

> model-maker --image-url ./sneaker.jpg "back of the shoe is plain, no logo"

### What happens

1. `--image-url` switches to image-to-3D. The photo is the specification.

2. The prompt is deliberately short: it says only what the photo cannot show.
   Re-describing the visible sneaker would fight the pixels and produce a mesh
   that splits the difference.

3. Cost: $0.40, same tier.

4. Output: `./generated/model/20260808-143512-tripo-v3.glb`

### What to notice

- One photo means one viewpoint. The far side is inferred, which is exactly why
  the prompt addresses it and nothing else.
- Laces come back fused or missing — thin unsupported features are the known
  failure. Say so rather than letting the user find it in Blender.
- For a product spin on a web page this is finished work. For a hero asset it is
  a starting mesh.

---

## Example 3 — untextured base for re-materialising

### User request

> model-maker "low-poly fox, game asset, I'll texture it myself in Substance"

### What happens

1. The user has already said what they want: geometry only.

2. `--no-texture` roughly halves the cost, and skipping a texture that will be
   thrown away is the whole point.

3. `--face-limit 5000` because "game asset" implies a real-time budget. Ask
   which engine if it matters; 5k is a safe default for a prop.

   ```bash
   python3 -m common.runners.cli.model3d --model tripo-v3 \
     --prompt "A low-poly red fox, sitting, tail curled around its feet, oversized head, game-asset proportions" \
     --no-texture --face-limit 5000 --yes
   ```

4. Output: bare mesh, ready for UV work.

### What to notice

- The polygon cap controls density, not layout. The mesh is still triangles with
  no edge loops, so it is a sculpting and texturing base rather than something to
  rig.
- Telling the user that up front is the difference between a useful asset and a
  complaint two hours later.
