---
name: model-maker
description: "Generate a 3D model (GLB mesh) from a text description or a reference photo via Tripo. Textured or bare geometry, polygon budget, PBR materials. Output is a real file for Blender / Unity / Unreal / AR, not a render. Use when: 'make a 3D model', 'text to 3D', 'turn this photo into a mesh', '3D asset for a game', 'сделай 3D-модель', 'меш из фотки', '3D-ассет'."

license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
Text or a single reference photo → one 3D mesh file, saved locally. Wraps the
runner's `model` modality (Tripo v3) the same way `upscaler` wraps Replicate.

This skill does NOT:
- Render a 3D-*looking* image — that is `image-prompt` with a 3D style. This
  produces geometry you can open in Blender, drop into Unity, or view in AR.
- Rig, animate, or retopologise. What comes back is a static mesh.
- Guarantee a printable model. Watertightness is not checked; see
  [references/limits.md](references/limits.md) before sending anything to a printer.
- Produce a scene. One prompt is one object.
</objective>

## ROLE

Turn a description into a mesh: write the prompt in the grammar 3D generators
actually read, pick the tier, call the runner, report where the file landed and
what it cost.

## PIPELINE

1. **Establish the subject.** One object, named concretely. "A low-poly red fox,
   sitting, tail curled" is a subject. "Something foxlike for a game" is not, and
   the mesh will show it.

2. **Write the prompt.** 3D prompting is not image prompting — no camera, no
   lighting, no lens. Describe form, silhouette, material and scale. Full grammar
   in [references/prompt-grammar.md](references/prompt-grammar.md).

3. **Pick the tier.** Textured is the default and roughly doubles the cost of
   bare geometry. Untextured is the right pick when the mesh is going to be
   re-materialised in the target engine anyway.

4. **Estimate + confirm.** `--cost-only` first when the user has not seen a price
   for this skill before. Every generation is over the $0.10 confirmation
   threshold, so the runner will ask unless `--yes` is passed.

5. **Execute.**

   ```bash
   python3 -m common.runners.cli.model3d \
     --model tripo-v3 \
     --prompt "<the written prompt>" \
     --yes
   ```

   From a photo, add `--image-url ./ref.jpg`. The prompt then becomes a hint
   rather than the whole specification.

6. **Report.** Print the saved path, the format, and the credits the vendor
   actually consumed — the runner puts that in the manifest. Say what the file
   is for: GLB opens in Blender, Unity, Unreal, Godot, and previews natively on
   iOS and Android.

## FLAGS

- `--prompt "<text>"` — the subject description
- `--image-url <path|url>` — reference photo; switches to image-to-3D
- `--no-texture` — bare geometry, cheaper
- `--pbr` — physically-based materials rather than baked colour
- `--face-limit N` — polygon budget, when the target engine has one
- `--model-version <string>` — override the pinned vendor model
- `--cost-only` / `--yes` / `--check` / `--output <dir>`

## CONSTRAINTS

- **Needs `TRIPO_API_KEY`.** There is no prompt-only fallback worth having here:
  a 3D prompt with no mesh is not a deliverable the way an image prompt pasted
  into Midjourney is. Without the key, say so and stop.

- **The download link expires in five minutes.** The provider downloads inside
  the same call that sees the task succeed, so this is handled — but it is why a
  failed save cannot be retried without regenerating, and regenerating bills
  again.

- **One object per call.** Multi-object scenes come back fused and unusable.
  Generate separately and assemble in the target tool.

- **Do not promise print-readiness.** See
  [references/limits.md](references/limits.md).

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/prompt-grammar.md](references/prompt-grammar.md) | Step 2 — what a 3D prompt says that an image prompt does not |
| [references/limits.md](references/limits.md) | Before promising anything about printing, rigging, or topology |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — three calibration runs:
a game prop from text, a product mesh from a photo, and an untextured base for
re-materialising.
