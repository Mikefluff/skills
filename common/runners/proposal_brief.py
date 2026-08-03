"""The proposal authoring brief — the markdown the orchestrator works from.

Split out of proposal_kit.py, which had grown past the module-size gate.
proposal_kit turns HTML into a PDF and sources photos; this writes the document
that tells the orchestrator what to build and what it may not change.

The brief is prompt material, so its wording is the interface. Sections 1-3 are
assembled from the offer; section 4 is fixed prose kept as a constant, because
mixing forty lines of instructions into the code that fills three holes made
both harder to read.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .proposal_kit import _fmt_price

@dataclass(frozen=True)
class BriefContext:
    """What the authoring brief knows besides the offer and the brand."""

    screenshot: Path | None = None
    logo_local: Path | None = None
    lang: str = "en"


def _brief_look(brand: dict[str, Any], screenshot: Path | None) -> list[str]:
    """Section 1 — the screenshot is the ground truth, not the tokens."""
    if screenshot:
        shot_line = (
            f"- **Screenshot:** `{screenshot}` — OPEN IT (Read tool). Match its mood "
            "(dark/light), type scale, accent usage, logo placement, imagery feel."
        )
    else:
        shot_line = (
            "- **Screenshot:** none (no headless browser found) — rely on tokens below "
            "and, if possible, fetch the site yourself."
        )
    return ["## 1. Look at the brand", shot_line, f"- **Site:** {brand.get('url') or '—'}", ""]


def _brief_tokens(brand: dict[str, Any], logo_local: Path | None) -> list[str]:
    """Section 2 — the resolved brand tokens, and how to treat the logo."""
    if logo_local:
        logo_line = (
            f"- Logo (local): `{logo_local}` — **may be a monochrome/white SVG**. On a "
            "dark header use as-is; on a light header tint via "
            "`filter:brightness(0) invert(1)` for white, or place on a dark/accent plate. "
            "Always pair with the brand NAME so identity survives."
        )
    else:
        logo_line = f"- Logo (remote): {brand.get('logo_url') or '—'}"

    return [
        "## 2. Brand tokens (resolved)",
        f"- Name: **{brand.get('name') or '—'}**  ·  Tagline: {brand.get('tagline') or '—'}",
        f"- Accent: `{brand.get('accent')}`  ·  Secondary: `{brand.get('accent2')}`",
        f"- Background: `{brand.get('bg')}`  ·  Text: `{brand.get('text')}`  ·  "
        f"is_dark (heuristic): `{brand.get('is_dark')}` — TRUST THE SCREENSHOT over this flag.",
        f"- Fonts: heading **{brand.get('font_heading') or '—'}**, body "
        f"**{brand.get('font_body') or '—'}**",
        f"- Google Fonts: `{brand.get('google_fonts_url') or '—'}`",
        logo_line,
        "",
    ]


def _brief_warnings(plan: dict[str, Any]) -> list[str]:
    """Anything the orchestrator must ask about rather than quietly resolve."""
    out: list[str] = []
    if plan.get("total_mismatch"):
        out.append(
            f"\n> ⚠ Stated total ({plan.get('total_stated')}) ≠ computed subtotal. Use "
            "computed; mention the discrepancy to the user."
        )
    for outlier in plan.get("price_outliers", []):
        out.append(
            f"\n> ⚠ **'{outlier['name']}' is {outlier['share'] * 100:.0f}% of the total** "
            f"({outlier['price']}). Almost certainly a typo — ASK the user before using it. "
            "Do not silently rewrite."
        )
    return out


def _brief_offer(plan: dict[str, Any]) -> list[str]:
    """Section 3 — the numbers, verbatim."""
    client = plan.get("client", {})
    cur = plan.get("currency", "")

    out = ["## 3. The offer (render EXACTLY — never invent or silently change numbers)"]
    fields = [(k, v) for k, v in client.items() if v]
    if fields:
        out.append("**Client:** " + "  ·  ".join(f"{k}: {v}" for k, v in fields))
    out.append(
        f"**Currency:** {cur}  ·  **Computed subtotal:** "
        f"{_fmt_price({'price': plan.get('subtotal_computed', 0)})} {cur}"
    )
    out += _brief_warnings(plan)
    out += [
        "\n**Line items** (qty is a separate column — price is the line total as written):\n",
        "| # | Item | Qty | Price | Link | Photo (og:image) |",
        "|---|------|-----|-------|------|------------------|",
    ]
    for i, item in enumerate(plan.get("items", []), 1):
        out.append(
            f"| {i} | {item.get('name','')} | {item.get('qty') or ''} | "
            f"{_fmt_price(item)} {item.get('currency') or cur} | {item.get('url') or ''} | "
            f"{item.get('thumb') or '—'} |"
        )
    out.append("")
    return out


def write_brief(
    brief_path: Path,
    plan: dict[str, Any],
    brand: dict[str, Any],
    context: BriefContext = BriefContext(),
) -> None:
    """Write the markdown brief the orchestrator authors the proposal from."""
    lines = [
        "# Proposal authoring brief\n",
        "> You (the orchestrator) are authoring a bespoke, **brand-faithful** HTML "
        "proposal. Do NOT fill a generic template — mirror the brand site's visual "
        "language. Read the screenshot below FIRST.\n",
    ]
    lines += _brief_look(brand, context.screenshot)
    lines += _brief_tokens(brand, context.logo_local)
    lines += _brief_offer(plan)
    steps = _AUTHORING_STEPS.replace("<<FOLDER>>", str(brief_path.parent))
    # rstrip so the joined document ends exactly where the last line does,
    # rather than gaining a blank one from the constant's closing newline.
    lines += steps.replace("<<LANG>>", context.lang).rstrip("\n").split("\n")

    brief_path.write_text("\n".join(lines), encoding="utf-8")


# Section 4 is fixed prose — the instructions do not vary with the offer.
# It embeds CSS, so the two dynamic values are token-replaced rather than
# .format()-ed: the print rules are full of literal { } braces.
_AUTHORING_STEPS = """\
## 4. Author the proposal
1. Write a single self-contained **`proposal.html`** into this folder (`<<FOLDER>>`). Inline CSS + the Google Fonts link above.
2. Mirror the screenshot: same dark/light mood, type weight/case, accent colour, logo treatment, generous rhythm. Make it look like THIS brand.
3. **Group items into 4–7 logical categories** named for the client's domain (e.g. Звук и свет / Доп оборудование / Артисты / Декорации / Сервис) — never one long pile. Give each a **large, scannable header** (big type, accent marker) so the client sees the sections at a glance, plus its item count and **per-category subtotal**. Order categories sensibly. Lead the hero with a **prominent Date / Time / Location block** (large) — those are what the client checks first.
4. **Vary density — don't render everything large.** Showpiece / high-value items get a big photo card; utility / low-cost items (controllers, stands, staff, logistics) get a **compact 2-column row** (small 44px thumb + name + price). This keeps it readable and not sprawling. Use your judgment per item.
5. Each item: real `og:image` photo (reference the Tilda URLs directly — they hotlink fine), name linking to its catalogue URL, a quantity chip where given, the price. Items whose `Photo` column already points at `img/…` are **AI-generated on-brand** stand-ins (picked because the offer had no link) — use them, and note to the user they can swap in a real photo. Never leave a blank/placeholder if a photo can be sourced.
6. Exact prices + clickable links. Computed subtotal as the grand total.
7. Language: **<<LANG>>** labels.
8. **Print CSS — required, the PDF depends on it:**
   - `@page{size:A4;margin:0}` so there are NO white page margins (full-bleed).
   - Running header AND footer that repeat on EVERY page with uniform spacing — use the **table head/foot** pattern (a `position:fixed` band can't reserve per-page space and looks broken on inner pages):
     ```html
     <table class="sheet"><thead><tr><td><div class="rh">logo + name + doc title</div></td></tr></thead>
     <tfoot><tr><td><div class="rf">contact · site</div></td></tr></tfoot>
     <tbody><tr><td> …all content (hero, item grid, total)… </td></tr></tbody></table>
     ```
     ```css
     table.sheet{width:100%;border-collapse:collapse}
     table.sheet>thead,table.sheet>tfoot{display:none}      /* screen */
     @media print{ @page{size:A4;margin:0} html,body{background:<page-bg>}
       table.sheet>thead{display:table-header-group}        /* repeats every page */
       table.sheet>tfoot{display:table-footer-group}
       table.sheet>thead>tr>td{padding:0 0 20px}   /* uniform gap UNDER header every page */
       table.sheet>tfoot>tr>td{padding:20px 0 0}    /* uniform gap ABOVE footer every page */
       .screen-header,.screen-footer{display:none}          /* hide scroll-view chrome */
       .card,.row,.total{break-inside:avoid;page-break-inside:avoid}
       .cat-h{break-after:avoid;page-break-after:avoid} }  /* category header not orphaned */
     ```
   - Put the gap padding on the thead/tfoot `<td>` (NOT on the content cell) — it sits inside the repeated group, so the breathing space is identical on every page; content-cell padding only spaces the first/last page and looks crooked on inner ones.
   - The `.rh`/`.rf` bands carry the dark/brand background + the accent hairline so they look like real letterhead colophons.
9. Verify: screenshot your `proposal.html`, Read it back; iterate until on-brand.
10. PDF: `skills/proposal-maker/scripts/run.py --pdf-from <…/proposal.html>` — renders via the browser then Ghostscript-shrinks photos (~15 MB → ~0.5 MB), links preserved.

_Offline / no-LLM fallback: re-run with `--quick` to render a deterministic themed template instead._
"""


