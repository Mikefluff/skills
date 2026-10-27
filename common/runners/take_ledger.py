"""The take ledger — every paid render of a film as a labelled asset the edit can reuse.

<out>/takes.json is a list, one entry per take (old entries keep their keys; these are added):

  created       the render's time, read off its file name (20261019-133210-t30.mp4)
  duration      seconds, by ffprobe
  prompt        what it was rendered from; prompt_source says where that came from: "manifest" (exact),
                "<history plan> body, may differ", or "body: current plan, may differ"
  size, move    read off that prompt by shot_coverage (close | medium | wide, and the camera's own words)
  moves         a real camera move (crane, track, orbit, drone...), not a push-in
  status        "in cut" (the manifest's take for a shot in the plan, or a shot's "clip"), "alternate"
                (unused, nothing known wrong) or "rejected"; reason says why a take is not the one in the cut
  usable        [[start, end], ...] seconds worth cutting from; by default the whole take after its first 0.2 s
  content       one line on what the take shows, written after looking at it

Hand-set status, reason, usable and content are never overwritten. An older "verdict": "rejected" counts.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from . import shot_coverage

HEAD = 0.2  # a take's first frames settle; cut from after them
_STAMP = re.compile(r"(\d{8})-(\d{6})-")


def created(file: str) -> str | None:
    m = _STAMP.search(Path(file).name)
    if not m:
        return None
    return datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")


def duration(path: Path) -> float | None:
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                              str(path)], capture_output=True, text=True, timeout=30, check=False).stdout
        return round(float(out.strip()), 2)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def rejected(take: dict[str, Any]) -> bool:
    return take.get("status") == "rejected" or take.get("verdict") == "rejected"


def camera(prompt: str) -> dict[str, Any]:
    """{size, move, moves} read off a shot body or a render prompt."""
    read = shot_coverage.read_shot({"label": "x", "body": prompt}) or {}
    return {"size": read.get("size") or "?", "move": shot_coverage.move_phrase(prompt),
            "moves": bool(read.get("moves"))}


def in_cut(plan: dict[str, Any], manifest: list[dict[str, Any]]) -> set[str]:
    """File names of the takes the cut uses: each live shot's manifest output, or its "clip"."""
    live = {s["label"]: s for s in plan.get("shots") or [] if not s.get("cut")}
    files = {Path(s["clip"]).name for s in live.values() if s.get("clip")}
    files |= {Path(i["output_path"]).name for i in manifest
              if i.get("label") in live and i.get("status") == "succeeded" and i.get("output_path")
              and not live[i["label"]].get("clip")}
    return files


def _body(shot: dict[str, Any]) -> str:
    return shot.get("body") or shot.get("prompt") or ""


def history_body(take: dict[str, Any], history: list[tuple[str, dict[str, Any], float]]) -> tuple[str, str]:
    """(body, source) from the earliest saved plan written after the take landed that has its label."""
    when = created(take["file"])
    stamp = datetime.strptime(when, "%Y-%m-%d %H:%M:%S").timestamp() if when else 0.0
    for name, plan, mtime in sorted(history, key=lambda h: h[2]):
        if mtime < stamp:
            continue
        shot = next((s for s in plan.get("shots") or [] if s.get("label") == take["label"]), None)
        if shot and _body(shot):
            return _body(shot), f"{name} body, may differ"
    return "", ""


def _prompt(take: dict[str, Any], plan: dict[str, Any], manifest: dict[str, dict[str, Any]],
            history: list[tuple[str, dict[str, Any], float]]) -> tuple[str, str]:
    item = manifest.get(Path(take["file"]).name)
    if item and item.get("prompt"):
        return item["prompt"], "manifest"
    body, source = history_body(take, history)
    if body:
        return body, source
    shot = next((s for s in plan.get("shots") or [] if s.get("label") == take["label"]), None)
    return (_body(shot), "body: current plan, may differ") if shot and _body(shot) else ("", "")


def _status(take: dict[str, Any], cut: set[str]) -> str:
    if rejected(take):
        return "rejected"
    return "in cut" if Path(take["file"]).name in cut else "alternate"


def enrich(take: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    """Fill the take's missing fields; ctx = {plan, out, cut, manifest (file name → item), history}."""
    take.setdefault("created", created(take["file"]))
    if take.get("duration") is None:
        take["duration"] = duration(ctx["out"] / take["file"])
    if not take.get("prompt"):
        take["prompt"], take["prompt_source"] = _prompt(take, ctx["plan"], ctx["manifest"], ctx["history"])
    for key, value in camera(take["prompt"]).items():
        take.setdefault(key, value)
    take["status"] = _status(take, ctx["cut"])
    take.setdefault("reason", "")
    if not take.get("usable") and take.get("duration"):
        take["usable"] = [[HEAD, take["duration"]]]
    return take


def context(plan: dict[str, Any], history: list[tuple[str, dict[str, Any], float]] | None = None) -> dict[str, Any]:
    out = Path(plan.get("output_dir") or ".")
    path = out / "manifest.json"
    items = (json.loads(path.read_text(encoding="utf-8")).get("items") or []) if path.is_file() else []
    return {"plan": plan, "out": out, "cut": in_cut(plan, items), "history": history or [],
            "manifest": {Path(i["output_path"]).name: i for i in items if i.get("output_path")}}


def untracked(ledger: list[dict[str, Any]], out: Path) -> list[dict[str, Any]]:
    """Clips in <out>/shots the ledger has never seen (a hand-cut composite, a take recorded before the ledger)."""
    known = {Path(t["file"]).name for t in ledger}
    found = []
    for path in sorted((out / "shots").glob("*.mp4")):
        if path.name not in known:
            m = re.search(r"\d{6}-([^.]+)\.mp4$", path.name)
            label = m.group(1) if m else path.stem.split("-")[0]
            found.append({"label": label, "file": f"shots/{path.name}", "route": "?", "how": "",
                          "cost_usd": 0.0, "untracked": True})
    return found


def _supersedes(take: dict[str, Any], old: dict[str, Any]) -> bool:
    return old["label"] == take["label"] and old["file"] != take["file"] and not rejected(old) \
        and old.get("status", "in cut") == "in cut"


def land(ledger: list[dict[str, Any]], take: dict[str, Any]) -> list[dict[str, Any]]:
    """Add a new take as the one in the cut; its label's previous take in the cut becomes an alternate."""
    for old in filter(lambda t: _supersedes(take, t), ledger):
        old["status"] = "alternate"
        old["reason"] = old.get("reason") or f"superseded by {Path(take['file']).name}"
    same = next((t for t in ledger if t["file"] == take["file"]), None)
    if same is None:
        ledger.append(take)
        return ledger
    hand = ("status", "reason", "usable", "content")  # recorded before as untracked: the render's facts win
    same.update({k: v for k, v in take.items() if k not in hand or not same.get(k)})
    same.pop("untracked", None)
    return ledger


def backfill(plan: dict[str, Any], ledger: list[dict[str, Any]],
             history: list[tuple[str, dict[str, Any], float]] | None = None) -> list[dict[str, Any]]:
    """Every take enriched, untracked clips added; statuses follow the plan and the manifest."""
    ctx = context(plan, history)
    ledger = ledger + untracked(ledger, ctx["out"])
    for take in ledger:
        enrich(take, ctx)
    return ledger


def find(ledger: list[dict[str, Any]], file: str) -> dict[str, Any]:
    """The take whose file name is `file` (a path, a name or a stem)."""
    name = Path(file).name
    hits = [t for t in ledger if Path(t["file"]).name in (name, f"{name}.mp4")]
    if len(hits) != 1:
        raise KeyError(f"{file}: {len(hits)} takes match")
    return hits[0]


def set_fields(take: dict[str, Any], pairs: list[str]) -> None:
    """key=value pairs (status=rejected reason="..." content="..."); "rejected" also sets the old verdict."""
    for pair in pairs:
        key, _, value = pair.partition("=")
        take[key.strip()] = value.strip().strip('"')
    if take.get("status") == "rejected":
        take["verdict"] = "rejected"
    elif take.get("verdict") == "rejected":
        take.pop("verdict")


def windows(text: str) -> list[list[float]]:
    """"1.0-3.4,5-6.2" → [[1.0, 3.4], [5.0, 6.2]]."""
    out = []
    for part in filter(None, (p.strip() for p in text.split(","))):
        start, end = (float(x) for x in part.split("-"))
        if end <= start:
            raise ValueError(f"{part}: the window ends before it starts")
        out.append([start, end])
    return out


def anchor(label: str, labels: list[str]) -> str:
    """Where an alternate goes by default: its own shot, else the shot that replaced it (t30 → t30r)."""
    if label in labels:
        return label
    return next((lab for lab in labels if lab.startswith(label)), "<label in the cut>")


def insert_entry(take: dict[str, Any], labels: list[str]) -> dict[str, Any]:
    """The reel_insert entry that puts this take's first usable window into the cut as a clip shot."""
    start, end = (take.get("usable") or [[HEAD, take.get("duration") or HEAD + 1]])[0]
    stamp = (_STAMP.search(Path(take["file"]).name) or [None, None, "x"])[2][:4]
    shot = {"label": f"{take['label']}_{stamp}", "clip": take["file"], "trim_start": start,
            "trim_seconds": round(end - start, 2)}
    return {"insert_after": anchor(take["label"], labels), "shot": shot}
