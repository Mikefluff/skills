"""One episode, start to finish: source clip in, finished reel out.

The whole picture is a single ffmpeg graph — the speaker trimmed and reframed,
cutaways faded over it, the overlay track on top — and a single encode, so the
source is decoded once and never passes through an intermediate file. Sound is
the speaker's own track, levelled, with the music bed ducked under it.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field, replace
from pathlib import Path

from . import recut_framing as framing
from . import recut_layers as layers_mod
from . import recut_scene as scene_mod
from . import recut_timeline as tl
from .recut_plan import FPS, H, STACK_Y, W, Plan

END_SECONDS = 2.8
_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def duration_of(path: Path) -> float:
    out = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).stdout
    return float(out.strip() or 0.0)


def silences_of(path: Path) -> list[tl.Span]:
    err = _run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "silencedetect=noise=-30dB:d=0.3", "-f", "null", "-"]).stderr
    return tl.parse_silences(err)


def _frame(t: float) -> float:
    return round(t * FPS) / FPS


@dataclass
class Edit:
    """Everything decided about one episode before a frame is drawn."""
    plan: Plan
    ep: dict
    timeline: tl.Timeline
    words: list[dict]
    scene: scene_mod.Scene
    panels: list[scene_mod.Panel]
    groups: list[dict] = field(default_factory=list)
    segments: list[framing.Segment] = field(default_factory=list)

    @property
    def speech(self) -> float:
        return self.timeline.total

    @property
    def tail_seconds(self) -> float:
        tail = self.ep.get("tail")
        return float(tail["seconds"]) if tail else 0.0

    @property
    def end_seconds(self) -> float:
        return float(self.plan.end.get("seconds", END_SECONDS))

    @property
    def total(self) -> float:
        return _frame(self.speech + self.tail_seconds + self.end_seconds)

    @property
    def source(self) -> Path:
        return self.plan.path(self.ep["src"])

    @property
    def work(self) -> Path:
        folder = self.plan.work / self.ep["slug"]
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def stacked(self, t: float) -> bool:
        return any(p.t0 - 1e-3 <= t < p.t1 for p in self.panels)


def decide(plan: Plan, ep: dict) -> Edit:
    """Timeline, captions and framing for an episode — no rendering, no cost."""
    source = plan.path(ep["src"])
    raw = json.loads(plan.path(ep["words"]).read_text(encoding="utf-8"))["words"]
    timeline = tl.plan_timeline(
        duration_of(source), max(w["end"] for w in raw), silences_of(source),
        float(ep.get("start", 0.0)), tuple(tuple(c) for c in ep.get("cuts", [])),
    )
    words = tl.remap_words(raw, timeline, tuple(tuple(f) for f in ep.get("word_fix", [])))
    scene = scene_mod.Scene(plan.brand, timeline.at, timeline.total)
    edit = Edit(plan, ep, timeline, words, scene, scene_mod.panels_of(scene, ep.get("items", []), ep.get("tail")))
    edit.groups = tl.caption_groups(words)
    pauses = sorted({_frame(b["t0"]) for a, b in zip(edit.groups, edit.groups[1:])
                     if b["words"][0]["t"] - a["words"][-1]["e"] > 0.3} | set(timeline.cuts))
    spans = [(_frame(p.t0), _frame(p.t1)) for p in edit.panels if p.t0 < edit.speech]
    edit.segments = framing.framing_segments(edit.speech, spans, pauses, timeline.cuts)
    last = "stack" if ep.get("tail") else edit.segments[-1][2]
    edit.segments.append((edit.speech, edit.total, last))
    return edit


def _cues(edit: Edit) -> list[scene_mod.Cue]:
    ep, scene = edit.ep, edit.scene
    end_at = _frame(edit.speech + edit.tail_seconds)
    end = dict(edit.plan.end)
    if end.get("art"):
        end["art_url"] = edit.plan.path(end["art"]).as_uri()
    return (scene_mod.hook_cues(scene, ep["hook"], end_at)
            + scene_mod.item_cues(scene, ep.get("items", []))
            + scene_mod.panel_cues(scene, edit.panels)
            + scene_mod.end_cues(scene, end, end_at))


def _cutaway_spans(edit: Edit) -> list[tuple[Path, float, float]]:
    spans = []
    for item in edit.ep.get("items", []):
        if item["kind"] == "broll":
            t0, t1 = edit.scene.span(item)
            spans.append((edit.plan.path(item["asset"]), _frame(t0), _frame(t1)))
    tail = edit.ep.get("tail")
    if tail and tail.get("asset"):
        spans.append((edit.plan.path(tail["asset"]), edit.speech, _frame(edit.speech + edit.tail_seconds + 0.3)))
    return [s for s in spans if s[2] - s[1] >= 0.6]


def _cutaway_filter(asset: Path, seconds: float, height: int, index: int) -> tuple[str, list[str]]:
    """A clip is slowed to cover its slot; a still gets a slow push in or out."""
    if asset.suffix.lower() not in _IMAGE_SUFFIXES:
        rate = max(1.0, seconds / max(0.5, duration_of(asset) - 0.25))
        graph = (f"trim=start=0.12,setpts={rate:.4f}*(PTS-STARTPTS),fps={FPS},"
                 f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{height}:(iw-{W})/2:(ih-{height})*0.42,setsar=1")
        return graph, ["-t", f"{seconds:.3f}", "-an"]
    n = round(seconds * FPS)
    zoom = f"1.0+0.10*on/{n}" if index % 2 == 0 else f"1.10-0.10*on/{n}"
    graph = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{height * 2},setsar=1,"
             f"zoompan=z='{zoom}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*0.45':d={n}:s={W}x{height}:fps={FPS}")
    return graph, ["-frames:v", str(n)]


def _cutaways(edit: Edit) -> list[tuple[Path, float, float]]:
    """Each cutaway cut to its slot and height; over a panel it fills only the top."""
    ready = []
    for index, (asset, t0, t1) in enumerate(_cutaway_spans(edit)):
        height = STACK_Y + 60 if edit.stacked(t0 + 0.05) else H
        seconds = t1 - t0
        clip = edit.work / f"cut{index}_{asset.stem}_{int(seconds * 100)}_{height}.mp4"
        if not clip.exists():
            graph, limit = _cutaway_filter(asset, seconds, height, index)
            done = _run(["ffmpeg", "-v", "error", "-y", "-i", str(asset), "-vf", graph, *limit,
                         "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p", str(clip)])
            if done.returncode:
                raise RuntimeError(f"cutaway {asset.name} failed: {done.stderr[-300:]}")
        ready.append((clip, t0, t1))
    return ready


def _picture_graph(edit: Edit, cutaways: list[tuple[Path, float, float]]) -> list[str]:
    keep, total = edit.timeline.keep, edit.total
    presets = edit.plan.presets(edit.ep)
    fx, fy = edit.ep["face"]
    zoom = framing.zoom_expr(edit.segments, presets)
    face_y = framing.face_y_expr(edit.segments, presets, fy)
    floor = framing.floor_expr(edit.segments)
    select = "+".join(f"between(t,{a:.4f},{b - 1 / FPS / 2:.4f})" for a, b in keep)
    ink = edit.plan.brand.ink.lstrip("#")
    # fps before tpad: after select the stream has no frame rate and tpad adds nothing.
    graph = [
        f"[0:v]fps={FPS},select='{select}',setpts=N/{FPS}/TB,fps={FPS},"
        f"tpad=stop_mode=clone:stop_duration={total - edit.speech + 0.2:.3f},"
        f"scale=w='trunc({W}*({zoom})/2)*2':h='trunc({H}*({zoom})/2)*2':eval=frame:flags=bicubic,setsar=1[spk]",
        f"color=c=0x{ink}:s={W}x{H}:r={FPS}:d={total:.3f}[bgc]",
        f"[bgc][spk]overlay=x='max(min(0,{W / 2}-{fx}*w),{W}-w)':"
        f"y='max(min(0,({face_y})-{fy}*h),({floor})-h)':eval=frame:shortest=1[v0]",
    ]
    for i, (_clip, t0, t1) in enumerate(cutaways):
        seconds = t1 - t0
        graph.append(f"[{i + 1}:v]format=yuva420p,fade=t=in:st=0:d=0.16:alpha=1,"
                     f"fade=t=out:st={seconds - 0.16:.3f}:d=0.16:alpha=1,setpts=PTS+{t0:.3f}/TB[b{i}]")
        graph.append(f"[v{i}][b{i}]overlay=x=0:y=0:eof_action=pass:enable='between(t,{t0:.3f},{t1:.3f})'[v{i + 1}]")
    graph.append(f"[v{len(cutaways)}][{len(cutaways) + 1}:v]overlay=0:0:format=auto,format=yuv420p,trim=duration={total:.3f}[vout]")
    return graph


def _sound_graph(edit: Edit, music_input: int | None) -> list[str]:
    total = edit.total
    select = "+".join(f"between(t,{a:.4f},{b:.4f})" for a, b in edit.timeline.keep)
    voice = (f"[0:a]aselect='{select}',asetpts=N/SR/TB,highpass=f=70,"
             "acompressor=threshold=-20dB:ratio=3:attack=8:release=160:makeup=2,"
             f"loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000,apad=whole_dur={total:.3f}")
    if music_input is None:
        return [f"{voice},alimiter=limit=0.89,atrim=duration={total:.3f}[aout]"]
    level = float(edit.plan.music.get("level", 0.2))
    rise = edit.speech + edit.tail_seconds - 0.3  # the bed comes up under the end card
    return [
        f"{voice},asplit=2[vo][sc]",
        f"[{music_input}:a]aresample=48000,atrim=duration={total:.3f},"
        f"volume='if(lt(t,{rise:.3f}),{level},{level}+0.5*min(1,(t-{rise:.3f})/0.6))':eval=frame,"
        f"afade=t=in:d=0.5,afade=t=out:st={total - 0.9:.3f}:d=0.9[mu0]",
        "[mu0][sc]sidechaincompress=threshold=0.02:ratio=7:attack=15:release=350[mu]",
        f"[vo][mu]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.89,atrim=duration={total:.3f}[aout]",
    ]


def _command(edit: Edit, cutaways: list, preview: bool) -> tuple[list[str], Path]:
    inputs = ["-i", str(edit.source)]
    for clip, _t0, _t1 in cutaways:
        inputs += ["-i", str(clip)]
    inputs += ["-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0"]
    music_input = None
    if edit.plan.music:
        bed = edit.plan.path(edit.plan.music["file"])
        room = max(1, int(duration_of(bed) - edit.total))
        inputs += ["-stream_loop", "-1", "-ss", str((edit.ep["n"] * 7) % room), "-i", str(bed)]
        music_input = len(cutaways) + 2
    graph = _picture_graph(edit, cutaways) + _sound_graph(edit, music_input)
    (edit.work / "graph.txt").write_text(";\n".join(graph), encoding="utf-8")
    edit.plan.out.mkdir(parents=True, exist_ok=True)
    out = edit.plan.out / f"{edit.ep['slug']}.mp4"
    encode = ["-c:v", "libx264", "-preset", "veryfast" if preview else "medium", "-crf", "26" if preview else "18",
              "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", str(FPS),
              "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart"]
    return (["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(graph),
             "-map", "[vout]", "-map", "[aout]", *encode, str(out)], out)


def report(edit: Edit, cutaways: list | None = None) -> dict:
    """What the edit did, for a reader who has not watched it yet."""
    return {
        "n": edit.ep["n"], "slug": edit.ep["slug"], "seconds": edit.total, "speech": edit.speech,
        "removed": [(round(a, 2), round(b, 2)) for a, b in edit.timeline.removed],
        "framing": [(round(a, 2), round(b, 2), mode) for a, b, mode in edit.segments],
        "cutaways": [(clip.name, a, b) for clip, a, b in (cutaways or [])],
        "captions": [" ".join(w["text"] for w in group["words"]) for group in edit.groups],
    }


def build(plan: Plan, ep: dict, chrome: str, preview: bool = False) -> Path:
    """Render one episode. Raises RuntimeError with ffmpeg's last words on failure."""
    edit = decide(plan, ep)
    # Whole frames, and long enough to be read: a graphic never flashes for one frame.
    cues = [replace(c, t0=_frame(c.t0), t1=_frame(max(c.t1, c.t0 + 0.3))) for c in _cues(edit)]
    stills = layers_mod.render_pages([cue.html for cue in cues], plan.work / "png", chrome)
    stack = [layers_mod.Layer(image, x, y, cue) for (image, x, y), cue in zip(stills, cues)]
    captions = layers_mod.Captions(edit.groups, plan.brand)
    cutaways = _cutaways(edit)
    command, out = _command(edit, cutaways, preview)
    log = edit.work / "ffmpeg.err"
    with log.open("w", encoding="utf-8") as errors:
        encoder = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=errors)
        try:
            for frame in layers_mod.frames(stack, captions, edit.total, edit.speech, edit.stacked):
                encoder.stdin.write(frame)
            encoder.stdin.close()
        except BrokenPipeError:
            pass
        code = encoder.wait()
    (edit.work / "info.json").write_text(json.dumps(report(edit, cutaways), ensure_ascii=False, indent=1), encoding="utf-8")
    if code:
        raise RuntimeError(f"ffmpeg failed for {ep['slug']}: {log.read_text(encoding='utf-8')[-600:]}")
    return out
