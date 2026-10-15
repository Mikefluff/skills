"""Blender side of the film previs — runs inside Blender, headless.

  Blender -b --factory-startup --python previs_scene.py -- <job.json>

The job (written by `cli/reel_previs.py`) lists shots, each with its set's
props, its camera keys already expanded, hero keys, fire cues, length and the
directory its frames go to. Every shot is built from an empty scene, so shots
never leak into each other. Clay on purpose: grey shapes, one sun, a dim
world, and blocks that light up when fired — Seedance is told to keep the
camera, timing and blocking and to replace every surface.

Uses only bpy and the standard library; no imports from this repository.
"""

import json
import math
import sys

import bpy


def _job() -> dict:
    return json.loads(open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8").read())


def _material(name, rgb, emission=0.0):
    m = bpy.data.materials.new(name)
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = 0.85
    bsdf.inputs["Emission Color"].default_value = (1, 1, 1, 1)
    bsdf.inputs["Emission Strength"].default_value = emission
    return m


TONE = {"light": (0.6, 0.6, 0.6), "dark": (0.25, 0.25, 0.25), "hero": (0.75, 0.45, 0.3)}


def _box(at, size, mat):
    bpy.ops.mesh.primitive_cube_add(location=at)
    o = bpy.context.object
    o.scale = [s / 2 for s in size]
    o.data.materials.append(mat)
    return o


def _cylinder(at, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=at, vertices=12)
    o = bpy.context.object
    o.data.materials.append(mat)
    return o


def _clear():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)


def _props(props, fps):
    """Build the set; return {id: material} for the blocks that can be fired."""
    shared = {tone: _material(tone, rgb) for tone, rgb in TONE.items()}
    fireable = {}
    for n, p in enumerate(props):
        kind, tone = p["kind"], p.get("tone", "light")
        mat = _material(f"cue-{p['id']}", (0.85, 0.85, 0.85)) if p.get("id") else shared[tone]
        if kind == "box":
            _box(p["at"], p["size"], mat)
        elif kind == "cylinder":
            _cylinder(p["at"], p.get("radius", 0.2), p.get("depth", 1.7), mat)
        elif kind == "truss":
            y0, y1 = p["y"]
            w, h = p.get("width", 9), p.get("height", 6)
            y = y0
            while y <= y1:
                for x in (-w / 2, w / 2):
                    _box((x, y, h / 2), (0.3, 0.3, h), mat)
                _box((0, y, h), (w + 0.3, 0.3, 0.3), mat)
                y += p.get("step", 5)
        elif kind == "crowd":
            (cx, cy), (sx, sy) = p["at"], p["size"]
            cols, rows = max(1, int(sx / 0.55)), max(1, int(sy / 0.65))
            for i in range(cols * rows):
                x = cx - sx / 2 + (i % cols + 0.5) * sx / cols
                y = cy - sy / 2 + (i // cols + 0.5) * sy / rows
                _cylinder((x, y, p.get("z", 0.85)), 0.17, 1.7, mat)
        if p.get("id"):
            fireable[p["id"]] = mat
    return fireable


def _hero(keys, fps):
    """Body, head and hat brim under one empty that walks and turns on the keys."""
    rig = bpy.data.objects.new("hero", None)
    bpy.context.scene.collection.objects.link(rig)
    skin, dark = _material("hero-skin", TONE["hero"]), _material("hero-hat", TONE["dark"])
    # A face the model can read in a close-up: hat crown and brim, round dark
    # glasses and a nose, all on the side he faces (+y in his own frame).
    parts = [_cylinder((0, 0, 0.95), 0.22, 1.2, skin), _cylinder((0, 0, 1.84), 0.3, 0.04, dark),
             _cylinder((0, 0, 1.92), 0.15, 0.16, dark)]
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0, 0, 1.72))
    parts.append(bpy.context.object)
    parts[-1].data.materials.append(skin)
    for x in (-0.055, 0.055):
        lens = _cylinder((x, 0.13, 1.745), 0.045, 0.02, dark)
        lens.rotation_euler = (math.radians(90), 0, 0)
        parts.append(lens)
    bpy.ops.mesh.primitive_cone_add(radius1=0.025, depth=0.06, location=(0, 0.15, 1.7), rotation=(math.radians(-90), 0, 0))
    parts.append(bpy.context.object)
    parts[-1].data.materials.append(skin)
    for part in parts:
        part.parent = rig
    for k in keys:
        f = 1 + round(k["t"] * fps)
        x, y = k["pos"][:2]
        rig.location = (x, y, k["pos"][2] if len(k["pos"]) > 2 else 0)
        rig.rotation_euler = (0, 0, math.radians(k.get("facing", 0)))
        rig.keyframe_insert("location", frame=f)
        rig.keyframe_insert("rotation_euler", frame=f)


def _camera(keys, lens, shake, fps):
    """A rig that travels and aims; the camera inside it only rolls.

    Track-to cannot roll, so the aim lives on the rig and the roll (dutch
    angle, a snorricam spin) on the camera within it. Each key may carry
    "ease": "ease" (default, accelerate and settle), "linear" (constant speed)
    or "snap" (hold, then jump — a whip pan or a crash zoom when the next key
    is a few frames later).
    """
    scene = bpy.context.scene
    rig = bpy.data.objects.new("rig", None)
    scene.collection.objects.link(rig)
    data = bpy.data.cameras.new("cam")
    data.lens = lens
    cam = bpy.data.objects.new("cam", data)
    scene.collection.objects.link(cam)
    cam.parent = rig
    scene.camera = cam
    target = bpy.data.objects.new("look", None)
    scene.collection.objects.link(target)
    track = rig.constraints.new("TRACK_TO")
    track.target, track.track_axis, track.up_axis = target, "TRACK_NEGATIVE_Z", "UP_Y"
    for k in keys:
        f = 1 + round(k["t"] * fps)
        rig.location, target.location = k["pos"], k["look"]
        rig.keyframe_insert("location", frame=f)
        target.keyframe_insert("location", frame=f)
        cam.rotation_euler = (0, 0, math.radians(k.get("roll", 0)))
        cam.keyframe_insert("rotation_euler", frame=f)
        if "lens" in k:
            data.lens = k["lens"]
            data.keyframe_insert("lens", frame=f)
    _interpolate(keys, fps, [rig, target, cam], data)
    if shake:
        for curve in _fcurves(rig):
            if curve.data_path == "location":
                noise = curve.modifiers.new("NOISE")
                noise.scale, noise.strength = 6, shake


def _interpolate(keys, fps, objects, data):
    """Apply each key's "ease" to the segment that leaves it."""
    modes = {1 + round(k["t"] * fps): k.get("ease", "ease") for k in keys}
    for owner in [*objects, data]:
        for curve in _fcurves(owner):
            for point in curve.keyframe_points:
                mode = modes.get(round(point.co[0]), "ease")
                point.interpolation = {"linear": "LINEAR", "snap": "CONSTANT"}.get(mode, "BEZIER")


def _fcurves(obj):
    """F-curves of an object's action — flat on old Blender, in a slot's channelbag since 4.4."""
    anim = obj.animation_data
    if not anim or not anim.action:
        return []
    if hasattr(anim.action, "fcurves"):
        return list(anim.action.fcurves)
    from bpy_extras import anim_utils

    bag = anim_utils.action_get_channelbag_for_slot(anim.action, anim.action_slot)
    return list(bag.fcurves) if bag else []


def _fire(fireable, cues, fps):
    for cue in cues:
        socket = fireable[cue["id"]].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        on = 1 + round(cue["t"] * fps)
        socket.default_value = 0
        socket.keyframe_insert("default_value", frame=max(1, on - 1))
        socket.default_value = cue.get("strength", 6)
        socket.keyframe_insert("default_value", frame=on + 1)
        if "off" in cue:
            off = 1 + round(cue["off"] * fps)
            socket.keyframe_insert("default_value", frame=off)
            socket.default_value = 0
            socket.keyframe_insert("default_value", frame=off + 2)


def render(shot, size, fps):
    _clear()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.fps = fps
    scene.frame_start, scene.frame_end = 1, max(2, round(shot["seconds"] * fps))
    scene.render.image_settings.file_format = "JPEG"
    scene.render.filepath = shot["frames"] + "/f"
    try:
        scene.eevee.taa_render_samples = 8
    except AttributeError:
        pass
    world = bpy.data.worlds.new("w")
    scene.world = world
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.12, 0.12, 0.13, 1)
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 10))
    sun = bpy.context.object
    sun.data.energy, sun.rotation_euler = 2.5, (0.6, 0.2, 0.3)
    fireable = _props([*shot["props"], *shot.get("extra", [])], fps)
    if shot.get("hero"):
        _hero(shot["hero"], fps)
    _camera(shot["camera"], shot.get("lens", 24), shot.get("shake", 0), fps)
    _fire(fireable, shot.get("fire") or [], fps)
    bpy.ops.render.render(animation=True)


job = _job()
for shot in job["shots"]:
    render(shot, tuple(job["size"]), job["fps"])
