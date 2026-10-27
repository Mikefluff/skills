"""What a paid command is about to buy, and why — printed before its cost confirmation.

Every item gets one reason, so a run that buys more than was asked for says so
before the money goes: `reel --redo t40` once rendered forty missing shots with it.
"""

from __future__ import annotations

import sys
from decimal import Decimal

ASKED = "asked (--only/--redo)"
FAILED = "failed last time"
MISSING = "missing"
CHANGED = "changed since last render"
RERUN = "rendered before (no --resume)"
_ORDER = (ASKED, FAILED, MISSING, CHANGED, RERUN)

Line = tuple[str, Decimal | None, str]  # (label, dollars or None when unpriced, reason)

_ITEMISED = 12
_FIRST = 5


def _cost(dollars: Decimal | None) -> str:
    return "$?" if dollars is None else f"${dollars:.2f}"


def total(lines: list[Line]) -> Decimal:
    return sum((d for _, d, _ in lines if d is not None), Decimal("0"))


def format_lines(lines: list[Line]) -> list[str]:
    """One row per item; past a dozen, a row per reason with its count and first labels."""
    if len(lines) <= _ITEMISED:
        width = max((len(label) for label, _, _ in lines), default=0)
        return [f"  {label:<{width}}  {_cost(d):>7}  {why}" for label, d, why in lines]
    out = []
    for why in sorted({w for _, _, w in lines}, key=lambda w: (_ORDER + (w,)).index(w)):
        mine = [line for line in lines if line[2] == why]
        labels = ", ".join(label for label, _, _ in mine[:_FIRST]) + (", …" if len(mine) > _FIRST else "")
        out.append(f"  {why}: {len(mine)} ({_cost(total(mine))}) — {labels}")
    return out


def show(what: str, lines: list[Line], warnings: list[str] | None = None) -> None:
    """Print the summary to stderr; nothing at all when nothing is bought."""
    if not lines:
        return
    print(f"{what} to buy: {len(lines)} item(s), {_cost(total(lines))}", file=sys.stderr)
    for row in format_lines(lines):
        print(row, file=sys.stderr)
    for warning in warnings or []:
        print(f"  warning: {warning}", file=sys.stderr)
