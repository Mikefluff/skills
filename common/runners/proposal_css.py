"""Proposal stylesheet — base CSS, per-theme overrides, and the custom properties.

Split out of proposal_render.py, which had grown past the module-size gate.
This half is the look; proposal_render.py is the document structure. Keeping
them apart means a CSS tweak does not sit in the same file as the HTML the
renderer assembles.

Themes layer: every document gets _BASE_CSS, then the one _THEMES entry it
asked for, on top of the :root custom properties derived from the brand.
"""

from __future__ import annotations

from typing import Any

_BASE_CSS = """
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;background:var(--page);color:var(--text);
  font-family:var(--font-body);line-height:1.5;font-size:15px}
a{color:inherit;text-decoration:none}
.page{max-width:840px;margin:0 auto;background:var(--bg);
  padding:56px 60px 40px}
.masthead{display:flex;align-items:center;justify-content:space-between;
  gap:24px;padding-bottom:24px;border-bottom:1px solid var(--hair)}
.brand{display:flex;align-items:center;gap:14px;min-width:0}
.brand img{height:42px;width:auto;max-width:220px;object-fit:contain}
.brand .brand-name{font-family:var(--font-heading);font-weight:700;
  font-size:19px;letter-spacing:-.01em}
.doc-kicker{font-size:11px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--accent);font-weight:600;white-space:nowrap}
.hero{padding:40px 0 28px}
.hero .event-title{font-family:var(--font-heading);font-weight:700;
  font-size:40px;line-height:1.05;letter-spacing:-.02em;margin:0}
.hero .prepared{margin:10px 0 0;color:var(--muted);font-size:16px}
.hero .tagline{margin:18px 0 0;color:var(--muted);max-width:60ch}
.meta{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
  gap:2px 28px;margin:28px 0 0;padding:0}
.meta .row{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid var(--hair)}
.meta dt{color:var(--muted);font-size:12px;letter-spacing:.06em;
  text-transform:uppercase;min-width:96px;margin:0;padding-top:2px}
.meta dd{margin:0;font-weight:500}
.items{margin:36px 0 0;display:flex;flex-direction:column;gap:12px}
.item{display:grid;grid-template-columns:auto 1fr auto;gap:18px;align-items:center;
  padding:14px;border:1px solid var(--hair);border-radius:14px;
  background:var(--card);page-break-inside:avoid;break-inside:avoid}
.item.no-thumb{grid-template-columns:1fr auto}
.item .thumb{width:84px;height:84px;border-radius:10px;overflow:hidden;
  background:var(--hair);flex:none}
.item .thumb img{width:100%;height:100%;object-fit:cover;display:block}
.item .body{min-width:0}
.item .item-name{font-family:var(--font-heading);font-weight:600;font-size:17px;
  margin:0;letter-spacing:-.01em}
.item .item-name a{border-bottom:1.5px solid var(--accent);padding-bottom:1px}
.item .item-desc{margin:5px 0 0;color:var(--muted);font-size:13.5px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.item .qty{display:inline-block;margin-top:7px;font-size:12px;font-weight:600;
  color:var(--accent);background:var(--accent-soft);border-radius:999px;
  padding:2px 10px}
.item .item-price{font-family:var(--font-heading);font-weight:700;font-size:18px;
  white-space:nowrap;text-align:right}
.totals{margin:30px 0 0;padding-top:22px;border-top:2px solid var(--text)}
.totals .grand{display:flex;align-items:baseline;justify-content:space-between}
.totals .grand .label{font-family:var(--font-heading);font-weight:700;
  font-size:20px;letter-spacing:.02em;text-transform:uppercase}
.totals .grand .amount{font-family:var(--font-heading);font-weight:800;
  font-size:30px;color:var(--accent)}
.totals .note{margin:10px 0 0;font-size:12.5px;color:var(--muted)}
.colophon{margin:42px 0 0;padding-top:20px;border-top:1px solid var(--hair);
  display:flex;flex-wrap:wrap;gap:8px 22px;align-items:center;
  font-size:12.5px;color:var(--muted)}
.colophon a{color:var(--accent);font-weight:600}
.colophon .sep{opacity:.4}
@media (max-width:680px){.page{padding:32px 22px}.meta{grid-template-columns:1fr}
  .hero .event-title{font-size:30px}}
@media print{.page{padding:24px 0;max-width:none}body{font-size:12.5px}
  .item{border-color:var(--hair)}}
"""

_THEMES = {
    "editorial": """
:root{--page:#f2f1ec;--card:#ffffff;--hair:#e6e3da;--muted:#6c6a63}
.page{box-shadow:0 1px 40px rgba(0,0,0,.06)}
""",
    "invoice": """
:root{--page:#ffffff;--card:#ffffff;--hair:#e7e9ee;--muted:#697086}
.items{gap:0}
.item{border-radius:0;border-left:none;border-right:none;border-top:none}
.item:first-child{border-top:1px solid var(--hair)}
.item .thumb{width:60px;height:60px}
.hero .event-title{font-size:32px}
""",
    "dark": """
:root{--page:#0c0d10;--card:#16181d;--hair:#262a33;--muted:#9aa1ad}
.item .item-name a{border-bottom-color:var(--accent)}
.totals .grand .amount{text-shadow:0 0 28px var(--accent-soft)}
""",
}


def _theme_vars(brand: dict[str, Any], theme: str) -> str:
    accent = brand.get("accent") or "#1f6feb"
    accent2 = brand.get("accent2") or accent
    bg = "#16181d" if theme == "dark" else (brand.get("bg") if not brand.get("is_dark") else "#ffffff") or "#ffffff"
    text = "#f4f5f7" if theme == "dark" else "#16181d"
    fh = brand.get("font_heading") or "Inter"
    fb = brand.get("font_body") or fh or "Inter"
    # soft accent for chips/glows
    soft = _hex_alpha(accent, 0.14)
    return (
        f"--accent:{accent};--accent2:{accent2};--accent-soft:{soft};"
        f"--bg:{bg};--text:{text};"
        f"--font-heading:'{fh}',system-ui,sans-serif;"
        f"--font-body:'{fb}',system-ui,sans-serif;"
    )


def _hex_alpha(hexv: str, a: float) -> str:
    h = hexv.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except Exception:
        return f"rgba(31,111,235,{a})"
    return f"rgba({r},{g},{b},{a})"

