"""Blender side of the film previs — runs inside Blender, headless.

  Blender -b --factory-startup --python previs_scene.py -- <job.json>

The job (written by `cli/reel_previs.py`) lists shots, each with its set's
props, its camera keys already expanded, hero keys or a cast of actors, fire
cues, length and the directory its frames go to. Every shot is built from an
empty scene, so shots never leak into each other. Clay on purpose, drawn by
Workbench: flat shapes with cast shadows, cavity and outlines so depth and
camera travel read, each actor in their own colour, props that move on keys,
and blocks that flash bright when fired — Seedance is told to keep the camera,
timing and blocking and to replace every surface.

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
FLASH = (1.0, 0.93, 0.62)


def _paint(obj, rgb):
    """Workbench draws the object's own colour; a fire cue keys it."""
    obj.color = (*rgb, 1)
    return obj


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


def _truss(p, mat):
    y0, y1 = p["y"]
    w, h = p.get("width", 9), p.get("height", 6)
    made, y = [], y0
    while y <= y1:
        for x in (-w / 2, w / 2):
            made.append(_box((x, y, h / 2), (0.3, 0.3, h), mat))
        made.append(_box((0, y, h), (w + 0.3, 0.3, 0.3), mat))
        y += p.get("step", 5)
    return made


def _crowd(p, mat):
    (cx, cy), (sx, sy) = p["at"], p["size"]
    cols, rows = max(1, int(sx / 0.55)), max(1, int(sy / 0.65))
    made = []
    for i in range(cols * rows):
        x = cx - sx / 2 + (i % cols + 0.5) * sx / cols
        y = cy - sy / 2 + (i // cols + 0.5) * sy / rows
        made.append(_cylinder((x, y, p.get("z", 0.85)), 0.17, 1.7, mat))
    return made


BUILD = {
    "box": lambda p, mat: [_box(p["at"], p["size"], mat)],
    "cylinder": lambda p, mat: [_cylinder(p["at"], p.get("radius", 0.2), p.get("depth", 1.7), mat)],
    "truss": _truss,
    "crowd": _crowd,
}


def _props(props, fps):
    """Build the set; return {id: [objects]} for the blocks that can be fired. A prop with "anim" keys
    ({t, at, scale, rot}) moves: the cake rises, a rocket flies, a garland drops."""
    shared = {tone: _material(tone, rgb) for tone, rgb in TONE.items()}
    fireable = {}
    for p in props:
        tone = p.get("tone", "light")
        made = BUILD.get(p["kind"], lambda p, mat: [])(p, shared[tone])
        base = p.get("color") or ((0.82, 0.82, 0.82) if p.get("id") else TONE[tone])
        for obj in made:
            _paint(obj, base)
        if p.get("anim") and len(made) == 1:
            _animate(made[0], p, fps)
        if p.get("id"):
            fireable.setdefault(p["id"], []).extend(made)
    return fireable


def _animate(obj, prop, fps):
    """Keys on one prop: "at" moves it, "scale" multiplies its size, "rot" turns it (degrees)."""
    rest = tuple(obj.scale)
    for k in prop["anim"]:
        f = 1 + round(k["t"] * fps)
        if "at" in k:
            obj.location = k["at"]
            obj.keyframe_insert("location", frame=f)
        if "scale" in k:
            obj.scale = tuple(r * m for r, m in zip(rest, k["scale"]))
            obj.keyframe_insert("scale", frame=f)
        if "rot" in k:
            obj.rotation_euler = tuple(math.radians(a) for a in k["rot"])
            obj.keyframe_insert("rotation_euler", frame=f)


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
        _paint(part, TONE["dark"] if part.data.materials[0] is dark else TONE["hero"])
    for k in keys:
        f = 1 + round(k["t"] * fps)
        x, y = k["pos"][:2]
        rig.location = (x, y, k["pos"][2] if len(k["pos"]) > 2 else 0)
        rig.rotation_euler = (0, 0, math.radians(k.get("facing", 0)))
        rig.keyframe_insert("location", frame=f)
        rig.keyframe_insert("rotation_euler", frame=f)


# Poses an actor key can name: arm angles (degrees from hanging, raised forward-up) and the body's
# squash, lift and tilt — enough for squash-and-stretch blocking, not animation.
POSES = {
    "stand": {"arms": (10, 10)}, "arms_up": {"arms": (170, 170)}, "arms_out": {"arms": (90, 90), "spread": True},
    "point": {"arms": (10, 95)}, "wave": {"arms": (10, 150)}, "crouch": {"arms": (40, 40), "squash": 0.72},
    "jump": {"arms": (160, 160), "squash": 1.12, "lift": 0.35}, "fall": {"arms": (120, 120), "tilt": -75},
    "lean": {"arms": (40, 40), "tilt": 15}, "hug": {"arms": (80, 80)}, "sit": {"arms": (20, 20), "squash": 0.6},
}
HAIR = {"big", "bun", "ponytail", "short", "long", "turban", "hood", "none"}


def _sphere(at, radius, rgb, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=at, segments=16, ring_count=8)
    o = bpy.context.object
    o.scale = scale
    return _paint(o, rgb)


def _hair(actor, head_r, top):
    """The hair shape: behind and above the face, never over it — the face is what the shot is about."""
    hair_rgb = tuple(actor.get("hair_color") or (0.35, 0.22, 0.15))
    shapes = {"big": [((0, -head_r * 0.75, top + head_r * 0.9), head_r * 1.3, (1.15, 0.85, 1.45)),
                      ((0, -head_r * 0.9, top - head_r * 0.6), head_r * 1.1, (1.2, 0.6, 1.3))],
              "bun": [((0, -head_r * 0.2, top + head_r * 1.15), head_r * 0.55, (1, 1, 1)),
                      ((0, -head_r * 0.1, top + head_r * 0.35), head_r * 1.02, (1, 1, 0.8))],
              "ponytail": [((0, -head_r * 0.1, top + head_r * 0.35), head_r * 1.03, (1, 1, 0.8)),
                           ((head_r * 0.6, -head_r * 0.7, top + head_r * 0.6), head_r * 0.5, (0.8, 0.8, 1.8))],
              "short": [((0, -head_r * 0.1, top + head_r * 0.45), head_r * 1.02, (1, 1, 0.7))],
              "long": [((0, -head_r * 0.35, top - head_r * 0.2), head_r * 1.25, (1.05, 0.8, 1.6))],
              "turban": [((0, 0, top + head_r * 0.55), head_r * 1.05, (1, 1, 0.8))],
              "hood": [((0, -head_r * 0.45, top + head_r * 0.15), head_r * 1.2, (1.05, 0.85, 1.1))]}
    return [_sphere(at, r, hair_rgb, sc) for at, r, sc in shapes.get(actor.get("hair", "short"), [])]


def _figure(rgb, skin, girth, body_h, head_r):
    """Barrel body, head, troll ears, nose and eyes."""
    parts = [_paint(_cylinder((0, 0, body_h / 2), girth, body_h, _material("a", rgb)), rgb),
             _sphere((0, 0, body_h), girth, rgb, (1, 1, 0.6)),
             _sphere((0, 0, body_h * 0.18), girth * 1.05, rgb, (1, 1, 0.5)),
             _sphere((0, 0, body_h + head_r), head_r, skin)]
    for side in (-1, 1):  # troll ears: flat cones out to the sides
        bpy.ops.mesh.primitive_cone_add(radius1=head_r * 0.35, depth=head_r * 0.9, vertices=8,
                                        location=(side * head_r * 1.1, 0, body_h + head_r * 1.05),
                                        rotation=(0, math.radians(side * 70), 0))
        parts.append(_paint(bpy.context.object, skin))
    parts.append(_sphere((0, head_r * 0.98, body_h + head_r * 0.9), head_r * 0.18, (0.95, 0.5, 0.55)))
    for x in (-0.38, 0.38):  # eyes, so the facing reads in a close-up
        parts.append(_sphere((x * head_r, head_r * 0.88, body_h + head_r * 1.15), head_r * 0.13, (0.1, 0.1, 0.12)))
    return parts


def _arms(rig, rgb, h, girth, body_h):
    """[(side, shoulder)]: an arm under each shoulder empty, which the keys rotate."""
    arms = []
    for side in (-1, 1):
        shoulder = bpy.data.objects.new(f"shoulder{side}", None)
        bpy.context.scene.collection.objects.link(shoulder)
        shoulder.location = (side * (girth + h * 0.04), 0, body_h * 0.9)
        shoulder.parent = rig
        arm = _paint(_cylinder((0, 0, -h * 0.17), h * 0.065, h * 0.34, _material("arm", rgb)), rgb)
        arm.parent = shoulder
        arms.append((side, shoulder))
    return arms


def _pose_key(rig, arms, k, fps):
    """One actor key: place, turn, squash and tilt the rig, then raise the arms."""
    f = 1 + round(k["t"] * fps)
    pose = POSES.get(k.get("pose", "stand"), POSES["stand"])
    x, y = k["pos"][:2]
    z = (k["pos"][2] if len(k["pos"]) > 2 else 0) + pose.get("lift", 0)
    rig.location = (x, y, z)
    rig.rotation_euler = (math.radians(pose.get("tilt", 0)), 0, math.radians(k.get("facing", 0)))
    squash = pose.get("squash", 1.0)
    rig.scale = (1 / math.sqrt(squash), 1 / math.sqrt(squash), squash)
    for key in ("location", "rotation_euler", "scale"):
        rig.keyframe_insert(key, frame=f)
    spread = pose.get("spread")
    for (side, shoulder), angle in zip(arms, pose["arms"]):
        # raise forward-up (about x), splayed out to the side for arms_out
        out = math.radians(side * angle) if spread else 0
        shoulder.rotation_euler = (0 if spread else math.radians(-angle), out, 0)
        shoulder.keyframe_insert("rotation_euler", frame=f)


def _actor(actor, fps):
    """A troll-proportioned figure — big head, ears, nose, a hair shape, arms on shoulders — in the actor's
    colour, under one rig that walks, turns, squashes and tilts on its keys. Faces +y in its own frame."""
    h = float(actor.get("height", 1.2))
    rgb, skin = tuple(actor.get("color") or TONE["hero"]), tuple(actor.get("skin") or (0.85, 0.62, 0.55))
    rig = bpy.data.objects.new(actor.get("id", "actor"), None)
    bpy.context.scene.collection.objects.link(rig)
    head_r = h * (0.22 if h < 0.8 else 0.17)
    body_h = h - 2 * head_r
    girth = h * (0.24 if h < 0.8 else 0.2)  # plush trolls: a soft barrel, not a pole
    parts = _figure(rgb, skin, girth, body_h, head_r) + _hair(actor, head_r, body_h + head_r)
    arms = _arms(rig, rgb, h, girth, body_h)
    for part in parts:
        part.parent = rig
    for k in actor["keys"]:
        _pose_key(rig, arms, k, fps)


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
    """A cue flashes its blocks bright (and back down at "off")."""
    for cue in cues:
        for obj in fireable[cue["id"]]:
            base = tuple(obj.color)
            on = 1 + round(cue["t"] * fps)
            obj.keyframe_insert("color", frame=max(1, on - 1))
            obj.color = (*FLASH, 1)
            obj.keyframe_insert("color", frame=on + 1)
            if "off" in cue:
                off = 1 + round(cue["off"] * fps)
                obj.keyframe_insert("color", frame=off)
                obj.color = base
                obj.keyframe_insert("color", frame=off + 2)
            obj.color = base


def render(shot, size, fps):
    _clear()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.fps = fps
    scene.frame_start, scene.frame_end = 1, max(2, round(shot["seconds"] * fps))
    scene.render.image_settings.file_format = "JPEG"
    scene.render.filepath = shot["frames"] + "/f"
    shading = scene.display.shading
    shading.light, shading.color_type = "STUDIO", "OBJECT"
    shading.show_shadows, shading.shadow_intensity = True, 0.55
    shading.show_cavity, shading.cavity_type = True, "BOTH"
    shading.show_object_outline, shading.object_outline_color = True, (0.08, 0.08, 0.09)
    shading.background_type, shading.background_color = "VIEWPORT", (0.16, 0.17, 0.19)
    scene.display.light_direction = (0.45, -0.35, 0.82)
    scene.display.render_aa = "8"
    fireable = _props([*shot["props"], *shot.get("extra", [])], fps)
    if shot.get("hero"):
        _hero(shot["hero"], fps)
    for actor in shot.get("actors") or []:
        _actor(actor, fps)
    _camera(shot["camera"], shot.get("lens", 24), shot.get("shake", 0), fps)
    _fire(fireable, shot.get("fire") or [], fps)
    bpy.ops.render.render(animation=True)


job = _job()
for shot in job["shots"]:
    render(shot, tuple(job["size"]), job["fps"])
