# What this produces, and what it does not

The temptation with a 3D generator is to describe the output as "a 3D model" and
let the user assume the rest. The gap between a mesh and a usable asset is where
the disappointment lives, so it is written down here.

---

## The file

GLB by default: geometry, texture and materials in one binary. Opens in Blender,
Unity, Unreal, Godot, and previews natively on Android and on iOS via Quick Look.

A GLB is not a `.blend`, a `.max` or a `.c4d`. There is no construction history,
no modifier stack, no named collections. What you get is the result.

---

## Topology

The mesh is generated, not modelled. In practice that means:

- **Triangles, not clean quads**, unless the tier explicitly promises a quad mesh.
  Fine for a static prop, wrong for anything that will deform.
- **No edge loops where an animator needs them.** A generated face has no loop
  around the mouth, so it does not deform correctly when rigged. Retopologise
  before rigging, or use it as a sculpting base.
- **Uneven density.** Detail concentrates where the model thought detail was, not
  where your engine's LOD system wants it.

`--face-limit` caps the polygon count, which helps a real-time budget and does
nothing for the loop problem.

---

## Printing

**Do not promise a printable model.** Nothing in this pipeline checks the two
things a printer needs:

- **Watertight.** Generated meshes routinely contain holes and non-manifold
  edges that slice into garbage or fail outright.
- **Self-supporting.** Thin features that survive on screen snap in PLA.

The honest workflow is to run the GLB through a mesh repair pass — Blender's 3D
Print Toolbox, Meshmixer, or the slicer's own repair — and inspect it. That is a
separate job from generating it, and this skill does not do it.

---

## Rigging and animation

Not attempted. A generated mesh has no armature, no weights, no blend shapes.
For a character you intend to animate, treat the output as a base to retopologise
and rig, not as a finished asset.

---

## What it is genuinely good for

- Background props and set dressing, where topology never gets inspected.
- Blockout and previz geometry, replaced later.
- AR previews and product spins, where GLB is the delivery format anyway.
- A sculpting base that saves the first two hours.
- Turning a product photo into something that rotates on a page.
