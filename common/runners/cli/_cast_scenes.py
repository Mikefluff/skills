"""Scene casting for a drama: each scene's references and composed prompt, from the bible.

Split out of `cli/reel_cast.py`, which re-exports `cast_scenes` and the helpers here;
this half renders nothing — it only rewrites the plan's scenes.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from .. import config
from .. import drama
from ..errors import RunnerError

_HOSTED = ("reference_images", "reference_audio", "reference_videos", "media_host")


def _board_frame(plan: dict[str, Any], scene: dict[str, Any]) -> str | None:
    """The storyboard frame drawn for this shot, if reel_board has drawn it."""
    frames = {int(f.get("shot", 0)): f["id"] for f in (plan.get("board") or {}).get("frames") or []}
    fid = frames.get(int(scene.get("index", 0)))
    path = Path(plan.get("output_dir") or ".") / "board" / f"{fid}.jpg"
    return str(path) if fid and path.is_file() else None


def _first_frame_scene(plan: dict[str, Any], scene: dict[str, Any]) -> None:
    """A first-frame route (Wan): the storyboard frame opens the shot, its own prompt moves it, nothing else is sent."""
    frame = _board_frame(plan, scene)
    if not frame:
        raise RunnerError(f"{scene.get('label')}: no storyboard frame; run reel_board before a first-frame route")
    if not scene.get("motion"):
        raise RunnerError(f"{scene.get('label')}: no `motion` prompt; run the MOTION call of drama-system-prompt.md")
    kwargs = {k: v for k, v in (scene.get("kwargs") or {}).items() if k not in _HOSTED}
    scene["kwargs"] = {**kwargs, "first_frame": frame, "resolution": "480p", "generate_audio": True}
    # The shot's own sound (the body's <...>) is generated with it: the cut keeps it under the cast's take.
    sounds = re.findall(r"<([^<>]+)>", scene.get("body", ""))
    scene["prompt"] = scene["motion"] + (f" Sound: {'; '.join(sounds)}, close and clear." if sounds else "")


def _open_on_frame_scene(plan: dict[str, Any], scene: dict[str, Any], bible: dict[str, Any]) -> None:
    """"open_on_frame": the shot opens exactly on its own storyboard frame (image to video) and the body moves
    it; no cast, place, voice or previs goes with it."""
    frame = _board_frame(plan, scene)
    if not frame:
        raise RunnerError(f"{scene.get('label')}: open_on_frame needs its storyboard frame; run reel_board first")
    png = Path(frame).with_suffix(".png")  # the frame as drawn; the jpg beside it is the contact sheet's copy
    kwargs = {k: v for k, v in (scene.get("kwargs") or {}).items() if k not in (*_HOSTED, "last_frame")}
    scene["kwargs"] = {**kwargs, "first_frame": str(png if png.is_file() else frame)}
    look = f"\n[Overall style]: {bible['look']}" if bible.get("look") else ""
    scene["prompt"] = scene["body"].strip() + look


def _rendered(plan: dict[str, Any]) -> dict[str, Path]:
    """label → its rendered clip, from the reel manifest."""
    manifest = Path(plan.get("output_dir") or ".") / "manifest.json"
    items = json.loads(manifest.read_text(encoding="utf-8")).get("items") or [] if manifest.is_file() else []
    return {i["label"]: Path(i["output_path"]) for i in items
            if i.get("status") == "succeeded" and i.get("output_path") and Path(i["output_path"]).is_file()}


def _bridge_seams(plan: dict[str, Any], scene: dict[str, Any], clips: dict[str, Path]) -> dict[str, tuple[Path, float]]:
    """end → (clip, second) to pull the bridge's first / last frame from."""
    by_label = {s["label"]: s for s in plan["shots"]}
    # "from_image" / "to_image": an end pinned to a still (a frame with its lettering drawn in) instead of a shot
    a = by_label.get(scene["bridge"].get("from", ""))
    b = by_label.get(scene["bridge"].get("to", ""))
    if any(s is not None and s["label"] not in clips for s in (a, b)):
        raise RunnerError(f"{scene['label']}: render the shots on both sides before the bridge between them")
    seams = {}
    if a is not None:
        seams["first"] = (clips[a["label"]], float(a.get("trim_start") or 0) + float(a["trim_seconds"]) - 0.05)
    if b is not None:
        seams["last"] = (clips[b["label"]], float(b.get("trim_start") or 0))
    return seams


def _grab_frame(clip: Path, at: float, frame: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(0.0, at):.3f}", "-i", str(clip),
                    "-frames:v", "1", "-q:v", "2", str(frame)], check=True, capture_output=True)


def _bridge_scene(plan: dict[str, Any], scene: dict[str, Any], clips: dict[str, Path], bible: dict[str, Any]) -> None:
    """A transition the generation draws: it opens on the last frame the cut uses of one shot and ends on the
    first frame it uses of the next, so both seams match frame for frame. Needs both shots rendered."""
    seams = _bridge_seams(plan, scene, clips)
    out = Path(plan["output_dir"]) / "bridges"
    out.mkdir(parents=True, exist_ok=True)
    kwargs = {k: v for k, v in (scene.get("kwargs") or {}).items() if k not in _HOSTED}
    for end, (clip, at) in seams.items():
        frame = out / f"{scene['label']}.{end}.jpg"
        _grab_frame(clip, at, frame)
        kwargs[f"{end}_frame"] = str(frame)
    pinned = {"first_frame": scene["bridge"].get("from_image"), "last_frame": scene["bridge"].get("to_image")}
    kwargs.update({k: v for k, v in pinned.items() if v})
    scene["kwargs"] = kwargs
    look = f"\n[Overall style]: {bible['look']}" if bible.get("look") else ""
    scene["prompt"] = scene["body"].strip() + look


def _extend_scene(plan: dict[str, Any], scene: dict[str, Any], clips: dict[str, Path], bible: dict[str, Any]) -> None:
    """A shot that continues a rendered one instead of starting over: the earlier clip goes in as Video 1 and
    the generation carries its performance, props, light and camera on past its last frame. The faces and the
    place still go in as images, so nobody drifts in the new seconds."""
    source = scene["extend"]["from"]
    if source not in clips:
        raise RunnerError(f"{scene['label']}: render {source} before the shot that extends it")
    refs, _ = drama.references(scene, bible)
    kwargs = {k: v for k, v in (scene.get("kwargs") or {}).items()
              if k not in ("reference_images", "reference_videos", "first_frame", "last_frame", "media_host")}
    # an extension keeps its source's frame; the vendor refuses any ratio but "adaptive"
    kwargs.update(reference_videos=[str(clips[source])], reference_images=refs, aspect_ratio="adaptive")
    scene["kwargs"] = kwargs
    lines = drama.references(scene, bible)[1]
    scene["prompt"] = "\n".join([
        "Extend Video 1: continue it seamlessly from its last frame, the same moment going on — the same people, "
        "place, light, lens and camera position at the join — and then:",
        *lines, f"[Overall style]: {bible['look']}" if bible.get("look") else "", scene["body"].strip()])


def _continuation(plan: dict[str, Any], scene: dict[str, Any], clips: dict[str, Path], bible: dict[str, Any]) -> None:
    """A bridge or an extension: built from clips already rendered."""
    if not scene.get("bridge"):
        _extend_scene(plan, scene, clips, bible)
        return
    ends = [scene["bridge"].get(k) for k in ("from", "to") if scene["bridge"].get(k)]
    if scene["label"] in clips and any(e not in clips for e in ends):
        return  # rendered already; a neighbour being redone does not make it unbuildable
    _bridge_scene(plan, scene, clips, bible)


def _attach_voices(plan: dict[str, Any], scene: dict[str, Any], bible: dict[str, Any], kwargs: dict[str, Any]) -> None:
    audio, _ = drama.voices(scene, bible)
    if not audio:
        kwargs.pop("reference_audio", None)
        return
    kwargs["reference_audio"] = audio
    if plan.get("media_host"):
        kwargs["media_host"] = plan["media_host"]


def _extra_refs(scene: dict[str, Any], kwargs: dict[str, Any]) -> None:
    """"extra_refs": a prop the shot must show as it was seen before ({"path", "says"}), after the cast and place."""
    for extra in scene.get("extra_refs") or []:
        kwargs["reference_images"] = [*kwargs["reference_images"], extra["path"]]
        refs = kwargs["reference_images"]
        scene["prompt"] = f"Image {len(refs)} is {extra['says']}\n" + scene["prompt"]


def _keyframe(plan: dict[str, Any], scene: dict[str, Any], kwargs: dict[str, Any]) -> None:
    """The approved storyboard frame goes last, named, so the generation opens on our composition."""
    # "no_keyframe": a frame a vendor's filter refuses (it read the drawing as someone else's character)
    frame = None if scene.get("no_keyframe") else _board_frame(plan, scene)
    if not frame:
        return
    refs = kwargs["reference_images"]
    kwargs["reference_images"] = [*refs, frame]
    scene["prompt"] = (f"Image {len(refs) + 1} is the storyboard keyframe: open on its composition, framing, "
                       "lens and light.\n" + scene["prompt"])


def _reference_scene(plan: dict[str, Any], scene: dict[str, Any], bible: dict[str, Any]) -> None:
    """A reference route: cast and place as images, speakers as audio, the prompt composed from the bible."""
    # "no_location_ref": the place's plate carries something the shot must not have (a second cake)
    placed = {k: v for k, v in scene.items() if k != "location"} if scene.get("no_location_ref") else scene
    refs, _ = drama.references(placed, bible)
    kwargs = scene.setdefault("kwargs", {})
    kwargs["reference_images"] = refs
    _attach_voices(plan, scene, bible, kwargs)
    kwargs.setdefault("aspect_ratio", bible.get("aspect_ratio", "16:9"))
    kwargs.setdefault("generate_audio", True)
    scene["prompt"] = drama.compose(placed, bible)
    _extra_refs(scene, kwargs)
    _keyframe(plan, scene, kwargs)
    if kwargs.get("reference_videos"):
        # the camera is the previs (reel_previs), not a sentence: film-system-prompt.md PART 4
        scene["prompt"] = ("Video 1 is a clay-render previs. Strictly follow its camera movement, speed, path and "
                           "framing changes, the blocking, and the moment each grey block lights up; replace every "
                           "grey shape with the real scene.\n" + scene["prompt"])


def _fresh(plan: dict[str, Any], scene: dict[str, Any], bible: dict[str, Any]) -> None:
    """A shot generated from scratch, sent the way its provider takes it."""
    slug = scene.get("video_provider") or plan.get("video_provider")
    provider = config.get_provider(slug) if slug else None
    if getattr(provider, "first_frame_only", False):
        _first_frame_scene(plan, scene)
    else:
        _reference_scene(plan, scene, bible)


def cast_scenes(plan: dict[str, Any], bible: dict[str, Any]) -> None:
    """Each scene's references and composed prompt, from the bible. A scene may name its own `video_provider`."""
    print("".join(f"  preflight {note}\n" for note in drama.preflight(plan, bible)), end="", file=sys.stderr)
    clips = None
    for scene in plan["shots"]:
        if scene.get("clip"):
            continue  # cut by hand (a composite); the cut takes the file as it is
        if scene.get("open_on_frame"):
            _open_on_frame_scene(plan, scene, bible)
        elif scene.get("bridge") or scene.get("extend"):
            clips = clips if clips is not None else _rendered(plan)
            _continuation(plan, scene, clips, bible)
        else:
            _fresh(plan, scene, bible)
