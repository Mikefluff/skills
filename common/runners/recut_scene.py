"""Plan items into timed graphics: which HTML page appears when, and how it arrives.

One page per moving part. A number and its caption, two lines of a hook, each
row of a list: every part that enters on its own is its own page, laid out with
its siblings present but hidden, so the browser positions it exactly where it
will sit once all of them are on screen. The compositor then only has to fade
and slide whole images; nothing is ever re-laid-out between frames.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from string import Template
from typing import Callable

from . import recut_css as css
from .recut_plan import H, STACK_Y, Brand

CHIP_Y, BIG_Y, URL_Y = 1010, 960, 975
HOOK_UNTIL, BRAND_FROM = 2.9, 3.0


@dataclass(frozen=True)
class Cue:
    html: str
    t0: float
    t1: float
    anim: str = "pop"
    din: float = 0.3
    dout: float = 0.18


@dataclass(frozen=True)
class Panel:
    t0: float
    t1: float
    title: str
    rows: tuple[tuple[float, str], ...]  # (time on the new clock, text)
    style: str


@dataclass(frozen=True)
class Scene:
    brand: Brand
    at: Callable[[float], float]
    speech: float

    def page(self, body: str, extra: str = "") -> str:
        sheet = Template(css.BASE_CSS).substitute(
            accent=self.brand.accent, second=self.brand.second, ink=self.brand.ink,
            text_url=self.brand.text_font.as_uri(), display_url=self.brand.display_font.as_uri(),
            stack_y=STACK_Y, panel_h=H - STACK_Y,
        )
        return f"<!doctype html><html><head><meta charset='utf-8'><style>{sheet}{extra}</style></head><body>{body}</body></html>"

    def span(self, item: dict) -> tuple[float, float]:
        return self.at(item["at"][0]), self.at(item["at"][1])


def esc(text: str) -> str:
    return html.escape(str(text))


def _chip_page(scene: Scene, text: str, style: str, place: tuple[int, str]) -> str:
    y, anchor = place
    icon = css.CHIP_ICON.get(style, "ok")
    mark = f'<span class="ic">{css.ICONS[icon]}</span>' if icon else ""
    return scene.page(
        f'<div class="row" style="top:{y}px;transform:translateY({anchor})">'
        f'<div class="chip {style}">{mark}<span>{esc(text)}</span></div></div>'
    )


def _chip(scene: Scene, item: dict) -> list[Cue]:
    t0, t1 = scene.span(item)
    return [Cue(_chip_page(scene, item["text"], item.get("style", "plain"), (CHIP_Y, "-50%")), t0, t1)]


def _big(scene: Scene, item: dict) -> list[Cue]:
    t0, t1 = scene.span(item)
    style = item.get("style", "plain")
    number, sub = esc(item["text"]), esc(item.get("sub", ""))

    def page(show_number: bool) -> str:
        hid_n, hid_s = ("", " hid") if show_number else (" hid", "")
        return scene.page(f'<div class="row big {style}" style="top:{BIG_Y}px">'
                          f'<div class="num{hid_n}">{number}</div><div class="sub{hid_s}">{sub}</div></div>')

    cues = [Cue(page(True), t0, t1)]
    if sub:
        cues.append(Cue(page(False), t0 + 0.22, t1, "up"))
    return cues


def _vs(scene: Scene, item: dict) -> list[Cue]:
    """Two chips stacked, the second arriving when the speaker gets to it."""
    t0, t1 = scene.span(item)
    styles = item.get("style", ["ok", "warn"])
    top, bottom = item["text"]
    return [
        Cue(_chip_page(scene, top, styles[0], (CHIP_Y - 54, "-100%")), t0, t1),
        Cue(_chip_page(scene, bottom, styles[1], (CHIP_Y - 38, "0")), scene.at(item["second"]), t1),
    ]


def _tags(scene: Scene, item: dict) -> list[Cue]:
    _, t1 = scene.span(item)
    tags = item["tags"]
    cues = []
    for i, (when, _text) in enumerate(tags):
        body = "".join(f'<div class="chip tag{"" if j == i else " hid"}">{esc(text)}</div>'
                       for j, (_w, text) in enumerate(tags))
        cues.append(Cue(scene.page(f'<div class="row tags" style="top:{CHIP_Y}px">{body}</div>'), scene.at(when), t1))
    return cues


def _url(scene: Scene, item: dict) -> list[Cue]:
    t0, t1 = scene.span(item)
    domain, _, path = item["text"].partition("/")
    tail = f"/{esc(path)}" if path else ""
    bar = (f'<div class="bar"><span class="lk">{css.ICONS["lock"]}</span>'
           f'<span>{esc(domain)}<small>{tail}</small></span></div>')
    sub = esc(item.get("sub", ""))
    row = f'<div class="row url" style="top:{URL_Y}px">'
    cues = [Cue(scene.page(f'{row}{bar}<div class="sub hid">{sub}</div></div>'), t0, t1)]
    if sub:
        cues.append(Cue(scene.page(f'{row}<div class="hid">{bar}</div><div class="sub">{sub}</div></div>'), t0 + 0.25, t1, "up"))
    return cues


_BUILDERS = {"chip": _chip, "big": _big, "vs": _vs, "tags": _tags, "url": _url}


def item_cues(scene: Scene, items: list[dict]) -> list[Cue]:
    cues: list[Cue] = []
    for item in items:
        build = _BUILDERS.get(item["kind"])
        if build:
            cues.extend(build(scene, item))
    return cues


def hook_cues(scene: Scene, hook: list[str], until: float) -> list[Cue]:
    """The title in the first frames, then the wordmark for the rest of the reel."""
    first, second = esc(hook[0]), esc(hook[1] if len(hook) > 1 else "")

    def page(show_first: bool) -> str:
        hid_1, hid_2 = ("", " hid") if show_first else (" hid", "")
        return scene.page(f'<div class="hook"><div class="l1{hid_1}">{first}</div><div class="l2{hid_2}">{second}</div></div>')

    cues = [Cue(page(True), 0.0, HOOK_UNTIL, "left", din=0.01)]
    if second:
        cues.append(Cue(page(False), 0.25, HOOK_UNTIL, "left"))
    name, tld = scene.brand.wordmark
    if name:
        cues.append(Cue(scene.page(f'<div class="brand">{esc(name)}<em>{esc(tld)}</em></div>'), BRAND_FROM, until, "fade"))
    return cues


def panels_of(scene: Scene, items: list[dict], tail: dict | None) -> list[Panel]:
    """List panels on the new clock; the tail's rows are offsets from its start."""
    panels = []
    for item in items:
        if item["kind"] != "panel":
            continue
        t0, t1 = scene.span(item)
        rows = tuple((max(t0 + 0.12, scene.at(when) - 0.05), text) for when, text in item["rows"])
        panels.append(Panel(t0, min(scene.speech, t1), item["title"], rows, item.get("style", "num")))
    if tail:
        start = scene.speech
        rows = tuple((start + offset, text) for offset, text in tail["rows"])
        panels.append(Panel(start, start + tail["seconds"], tail["title"], rows, tail.get("style", "check")))
    return panels


def _panel_page(scene: Scene, panel: Panel, show: int | None) -> str:
    """`show=None` draws the sheet and its title; a number draws that row alone."""
    rows = ""
    for i, (_when, text) in enumerate(panel.rows):
        badge = str(i + 1) if panel.style == "num" else css.ICONS[css.PANEL_ICON[panel.style]]
        hidden = "" if show == i else "hid"
        rows += f'<li class="{hidden}"><div class="b">{badge}</div><span>{esc(text)}</span></li>'
    crowded = len(panel.rows) >= 5 or sum(len(text) for _w, text in panel.rows) > 95
    sheet = "visible" if show is None else "hidden"
    return scene.page(
        f'<div class="panel {panel.style} {"dense" if crowded else ""}" style="visibility:{sheet}">'
        f'<h2 style="visibility:{sheet}">{esc(panel.title)}</h2><ul style="visibility:visible">{rows}</ul></div>'
    )


def panel_cues(scene: Scene, panels: list[Panel]) -> list[Cue]:
    cues = []
    for panel in panels:
        cues.append(Cue(_panel_page(scene, panel, None), panel.t0, panel.t1, "up", din=0.22, dout=0.12))
        for i, (when, _text) in enumerate(panel.rows):
            cues.append(Cue(_panel_page(scene, panel, i), when, panel.t1, "left", dout=0.12))
    return cues


def _button(button: dict, first: bool, visible: bool) -> str:
    icon = css.ICONS.get(button.get("icon", ""), "")
    hidden = "" if visible else ' style="visibility:hidden"'
    return f'<div class="btn{" first" if first else ""}"{hidden}>{icon}{esc(button["text"])}</div>'


def end_cues(scene: Scene, end: dict, start: float) -> list[Cue]:
    """The closing card: backdrop, wordmark, tagline, then each button in turn."""
    art = f"url('{end['art_url']}')" if end.get("art_url") else "none"
    extra = Template(css.END_CSS).substitute(
        accent=scene.brand.accent, second=scene.brand.second, ink=scene.brand.ink, art=art)
    name, tld = scene.brand.wordmark
    buttons = end.get("buttons", [])
    parts = [
        ('<div class="end"><div class="art"></div></div>', 0.0, "fade"),
        (f'<div class="logo">{esc(name)}<em>{esc(tld)}</em></div>', 0.2, "pop"),
        (f'<div class="tagl">{"<br>".join(esc(line) for line in end.get("tagline", []))}</div>', 0.45, "up"),
    ]
    for i in range(len(buttons)):
        row = "".join(_button(b, j == 0, j == i) for j, b in enumerate(buttons))
        parts.append((f'<div class="btns">{row}</div>', 0.75 + 0.2 * i, "pop"))
    far = start + 3600.0
    return [Cue(scene.page(body, extra), start + delay, far, anim, din=0.25 if delay == 0 else 0.3, dout=0)
            for body, delay, anim in parts]
