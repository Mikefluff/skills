#!/usr/bin/env python3
"""Fail when a skill quotes a model price the billing table does not support.

`common/references/model-pricing.md` is generated from `cost.PRICE_TABLE`, so it
cannot lie. Everything else can: the skills quote prices in prose, in decision
tables and in worked examples, and 195 such lines were written by hand. Thirteen
of them had gone stale — `nano-banana-pro` at $0.05 an image when the runner
bills $0.134, a $0.45 thumbnail batch that actually costs $1.21, `veo-3-1` priced
per clip against a per-second table. A number in a doc is read as a promise, and
these were understating the bill by up to 2.7x.

The rule: a line that names a model and quotes a dollar figure is a claim about
that model. The claim has to be the unit price, or the unit price times a batch
size the file has declared.

Declarations are HTML comments, effective until the next one or end of file:

    <!-- prices: batch=8 -->        a table of 8-slide runs: 1x and 8x pass
    <!-- prices: batch=3,9 -->      several columns: 1x, 3x and 9x pass
    <!-- prices: batch=any -->      last resort; leave a note saying why
    <!-- prices: ignore -->         not our price (vendor list, competitor, plan)
    <!-- prices: reset -->          back to unit-only

Usage:
    python3 scripts/check-prices.py            # check, exit 1 on drift
    python3 scripts/check-prices.py --list     # every claim and how it resolved
"""
from __future__ import annotations

import pathlib
import re
import sys
import typing

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.runners.cost import PRICE_TABLE  # noqa: E402

# Generated from the table, so checking it against the table proves nothing.
EXEMPT = {"common/references/model-pricing.md"}

ROOTS = ("skills", "docs", "common")

# Longest first: `nano-banana-2-lite` has to win over `nano-banana-2`.
SLUGS = sorted(PRICE_TABLE, key=len, reverse=True)

DIRECTIVE = re.compile(r"<!--\s*prices:\s*(?P<body>[^>]*?)\s*-->", re.I)
INLINE_CODE = re.compile(r"`[^`]*`")
MONEY = re.compile(r"\$\s?([0-9]+(?:\.[0-9]+)?)")

# A line naming a quality tier or a 4K variant is claiming that specific price,
# not whichever entry happens to make the arithmetic work.
UNIT_HINTS = {
    "low": ("low",),
    "medium": ("medium", "(med)"),
    "high": ("high",),
    "per_image_4k": ("4k",),
    "per_second_4k": ("4k",),
    "per_minute": ("per minute", "/minute", "per min"),
    "per_1k_chars": ("1000 char", "1k char", "1 000 char", "per 1k"),
}

MAX_BATCH = 64


def _tolerance(value: float) -> float:
    """Docs round. $1.072 is written $1.07, and $0.134 x 3 is written $0.40."""
    return max(0.006, 0.02 * value)


def _candidate_units(slug: str, line: str) -> list[dict[str, float]]:
    """Units to try, most specific first.

    A tier named on the line is the one being priced, so `gpt-image-2 (high)`
    must resolve against the high price rather than against whichever entry
    makes the arithmetic work. But the hint is a hint: a line can mention 4K in
    passing while quoting the standard rate, so the full table stays as a
    fallback rather than being replaced.
    """
    units = {k: float(v) for k, v in PRICE_TABLE[slug].items()}
    low = line.lower()
    hinted = {
        key: price
        for key, price in units.items()
        if key in UNIT_HINTS and any(h in low for h in UNIT_HINTS[key])
    }
    return [hinted, units] if hinted else [units]


def _explains(quoted: float, units: dict[str, float], batches: set[float] | None) -> str | None:
    """Return a human-readable derivation, or None if the number is unsupported."""
    allowed = [float(n) for n in range(1, MAX_BATCH + 1)] if batches is None else sorted(batches)
    for key, unit in sorted(units.items(), key=lambda kv: kv[1]):
        if unit <= 0:
            continue
        for n in allowed:
            if abs(quoted - n * unit) <= _tolerance(n * unit):
                return f"{n:g}x ${unit} ({key})" if n != 1 else f"${unit} ({key})"
    return None


def _parse_directive(body: str) -> tuple[str, set[float] | None]:
    """('ignore'|'batch'|'reset', allowed multipliers) — 'any' means unbounded.

    Multipliers may be fractional. A per-minute model quoted for a 30-second
    clip is `batch=0.5`, which is a real case: `lyria-3-clip` bills $0.10 a
    minute and every skill that uses it quotes the $0.05 half-minute.
    """
    # A directive may carry its own justification: `ignore — pipeline total`.
    # Everything past the dash is for the reader, and an unexplained `ignore` is
    # the one worth being suspicious of.
    body = re.split(r"\s+[—–]\s+|\s+--\s+|\s+#\s+", body.strip(), maxsplit=1)[0].lower()
    if body == "ignore":
        return "ignore", None
    if body == "reset":
        return "reset", {1}
    match = re.fullmatch(r"batch\s*=\s*(.+)", body)
    if not match:
        raise ValueError(f"unrecognised prices directive: {body!r}")
    spec = match.group(1).strip()
    if spec == "any":
        return "batch", None
    counts = {1.0}
    for part in spec.split(","):
        part = part.strip()
        try:
            n = float(part)
        except ValueError:
            raise ValueError(f"batch size must be a number, got {part!r}") from None
        if not 0 < n <= MAX_BATCH:
            raise ValueError(f"batch size must be within (0, {MAX_BATCH}], got {part!r}")
        counts.add(n)
    return "batch", counts


class Claim(typing.NamedTuple):
    """One line that names a model and quotes a figure."""

    lineno: int
    slugs: list[str]
    quoted: list[float]
    batches: set[float] | None
    line: str


def _priced(lineno: int, line: str, batches: set[float] | None) -> Claim | None:
    """A Claim if this line names a model and quotes a figure, else None.

    A line may name more than one model — "an 8-slide run on nano-banana-pro
    lands at $1.07, a 4K run doubles to $1.92; iterate on nano-banana-2-lite".
    Which model the figure belongs to is not recoverable from the text, so the
    claim stands if any model named can account for it. Ambiguity should not
    fail a build; a number no model on the line can produce still should.
    """
    if "$" not in line:
        return None
    slugs = [s for s in SLUGS if s in line]
    quoted = [float(q) for q in MONEY.findall(line)] if slugs else []
    return Claim(lineno, slugs, quoted, batches, line.strip()) if quoted else None


def _claims(path: pathlib.Path):
    """Yield a Claim for every priced line, honouring the file's directives."""
    mode, batches = "batch", {1}
    fenced = False
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        # A directive shown as an example is documentation, not a declaration —
        # the roadmap describing `<!-- prices: batch=N -->` must not be read as
        # declaring a batch of "N". Only directive detection ignores code spans;
        # claims are read from the raw line, because slugs are normally written
        # in backticks and sample CLI output is where a stale estimate hides best.
        directive = None if fenced else DIRECTIVE.search(INLINE_CODE.sub(" ", line))
        if directive:
            try:
                mode, batches = _parse_directive(directive.group("body"))
            except ValueError as exc:
                # A malformed directive is a finding, not a crash — otherwise a
                # typo in one file hides every claim in the rest of the tree.
                yield Claim(lineno, [], [], batches, f"{exc}")
            continue
        claim = None if mode == "ignore" else _priced(lineno, line, batches)
        if claim:
            yield claim


def _docs():
    """Every markdown file the checker owns, in a stable order."""
    for root in ROOTS:
        for path in sorted((ROOT / root).rglob("*.md")):
            rel = path.relative_to(ROOT).as_posix()
            if rel not in EXEMPT:
                yield rel, path


def _derivation(claim: Claim) -> str | None:
    """How the line's figures resolve against the table, or None if none do.

    One line often carries a price and a budget cap in the same sentence. If any
    figure on it resolves, the claim is anchored to the table.
    """
    return next(
        (
            d
            for d in (
                _explains(q, units, claim.batches)
                for s in claim.slugs
                for units in _candidate_units(s, claim.line)
                for q in claim.quoted
            )
            if d
        ),
        None,
    )


def _report(rel: str, claim: Claim) -> str:
    allowed = (
        "any" if claim.batches is None else ",".join(f"{n:g}" for n in sorted(claim.batches))
    )
    priced = "; ".join(
        f"{s}: " + ", ".join(f"{k}=${v}" for k, v in sorted(PRICE_TABLE[s].items()))
        for s in claim.slugs
    )
    return (
        f"  ✗ {rel}:{claim.lineno}\n"
        f"      {claim.line[:100]}\n"
        f"      quotes {claim.quoted} — table says {priced} (batch sizes allowed: {allowed})"
    )


def audit() -> tuple[list[str], int]:
    """Return (failures, number of claims checked)."""
    failures: list[str] = []
    checked = 0
    for rel, path in _docs():
        for claim in _claims(path):
            if not claim.slugs:  # malformed directive, reported verbatim
                failures.append(f"  ✗ {rel}:{claim.lineno}\n      {claim.line}")
                continue
            checked += 1
            if _derivation(claim) is None:
                failures.append(_report(rel, claim))
    return failures, checked


def main() -> int:
    if "--list" in sys.argv:
        for rel, path in _docs():
            for claim in _claims(path):
                how = _derivation(claim) or "UNSUPPORTED"
                print(f"{rel}:{claim.lineno}  {'/'.join(claim.slugs)}  {claim.quoted} → {how}")
        return 0

    failures, checked = audit()
    if failures:
        print(f"prices: FAILED — {len(failures)} of {checked} claims contradict cost.PRICE_TABLE")
        print("\n".join(failures))
        print("\n  Fix the number, or declare the batch size:  <!-- prices: batch=N -->")
        return 1
    print(f"prices: OK ({checked} price claims match cost.PRICE_TABLE)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
