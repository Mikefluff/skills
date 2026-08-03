#!/usr/bin/env python3
"""check-code-quality.py — structural gates for the Python layer.

Five checks, each answering a question review keeps having to ask by hand:

  module-size      is this a god file?
  function-size    can this function be read in one screen?
  complexity       how many branches does one reader have to hold?
  parameters       is this signature a bag?
  contract         does every Publisher/Provider actually honour its ABC?
  layering         does a lower layer import an upper one?

## Why a baseline rather than a hard line

19k lines of Python existed before these thresholds did. A gate that fails the
whole repo on day one gets disabled on day two. So this uses the same shape as
`check-launch-copy.py`: a frozen list of known violations that the gate ignores,
and a hard failure for anything NOT on that list.

The list may only shrink. Adding to it requires `--freeze`, which is a
deliberate act with a diff a reviewer can see, and the gate reports how many
entries remain so the number stays visible.

The contract and layering checks have no baseline. They are invariants, not
debts — a publisher that skips its ABC is broken now, not gradually.

Usage:
    python3 scripts/check-code-quality.py            # gate
    python3 scripts/check-code-quality.py --report   # everything, baseline included
    python3 scripts/check-code-quality.py --freeze   # re-freeze (shrinking only)
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "scripts" / "code-quality-baseline.json"

MAX_MODULE_LINES = 400
MAX_LIST_MODULE_LINES = 900  # a list is not a control flow — see _is_declaration_module
MAX_FUNCTION_LINES = 50
MAX_COMPLEXITY = 12
MAX_PARAMETERS = 5  # excluding self/cls

# A failure listing every violation is a wall nobody reads; --report has them all.
MAX_REPORTED = 15

INVARIANT_KINDS = frozenset({"contract", "layering", "syntax"})

SKIP_DIRS = {"__pycache__", ".git", ".runners-venv", "node_modules", "generated"}

# Lower layers must not import upper ones. Keys are path fragments, values are
# fragments they may not import.
FORBIDDEN_IMPORTS = {
    "common/runners/publishers/": ["cli."],
    "common/runners/providers/": ["cli.", "publishers."],
    "common/runners/storage/": ["cli.", "publishers.", "providers."],
}


@dataclass(frozen=True)
class Violation:
    kind: str
    path: str
    symbol: str
    line: int
    detail: str

    def key(self) -> str:
        """Stable identity across edits: no line number, since adding a comment
        above a function must not silently un-freeze it."""
        return f"{self.kind}|{self.path}|{self.symbol}"

    def __str__(self) -> str:
        where = f"{self.path}:{self.line}"
        symbol = f" {self.symbol}()" if self.symbol != "-" else ""
        return f"{self.kind:14} {where}{symbol} — {self.detail}"


def python_files() -> list[Path]:
    out = []
    for p in sorted(ROOT.rglob("*.py")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    return out


def complexity(node: ast.AST) -> int:
    """Branch count. Not McCabe to the letter — close enough to rank by, and
    cheap enough to run on every commit."""
    score = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.Assert)):
            score += 1
        elif isinstance(child, ast.BoolOp):
            score += len(child.values) - 1
        elif isinstance(child, ast.comprehension):
            score += 1 + len(child.ifs)
        elif isinstance(child, ast.IfExp):
            score += 1
        elif isinstance(child, ast.Match):
            score += len(child.cases)
    return score


def scan_module(path: Path) -> list[Violation]:
    rel = str(path.relative_to(ROOT))
    text = path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [Violation("syntax", rel, "-", exc.lineno or 1, str(exc))]

    found = _check_module_size(rel, text, tree)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found.extend(_check_function(rel, node))
    found.extend(scan_layering(rel, tree))
    return found


def _is_declaration_module(tree: ast.Module) -> bool:
    """True when a module only declares data — no functions, no classes.

    The module cap exists so a reader does not have to hold a whole god file
    in their head. That cost is about control flow, not length: a catalogue of
    500 regexes is scanned, not followed, and halving it to satisfy a line
    count makes it harder to read rather than easier.

    Tests already had this exemption by path. Measuring the shape instead of
    naming the file means a data module cannot smuggle logic in behind the
    larger cap — one def or class and it is back under the normal 400.
    """
    return not any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        for node in tree.body
    )


def _check_module_size(rel: str, text: str, tree: ast.Module) -> list[Violation]:
    lines = text.count("\n") + 1
    is_list = rel.startswith("tests/") or _is_declaration_module(tree)
    cap = MAX_LIST_MODULE_LINES if is_list else MAX_MODULE_LINES
    if lines <= cap:
        return []
    return [Violation("module-size", rel, "-", 1, f"{lines} lines, limit {cap} — split it")]


def _check_function(rel: str, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[Violation]:
    found = []
    length = (node.end_lineno or node.lineno) - node.lineno + 1
    if length > MAX_FUNCTION_LINES:
        found.append(
            Violation(
                "function-size", rel, node.name, node.lineno,
                f"{length} lines, limit {MAX_FUNCTION_LINES}",
            )
        )
    score = complexity(node)
    if score > MAX_COMPLEXITY:
        found.append(
            Violation(
                "complexity", rel, node.name, node.lineno,
                f"complexity {score}, limit {MAX_COMPLEXITY}",
            )
        )
    params = [a.arg for a in node.args.args + node.args.kwonlyargs if a.arg not in {"self", "cls"}]
    if len(params) > MAX_PARAMETERS:
        found.append(
            Violation(
                "parameters", rel, node.name, node.lineno,
                f"{len(params)} parameters, limit {MAX_PARAMETERS}",
            )
        )
    return found


def scan_layering(rel: str, tree: ast.Module) -> list[Violation]:
    """A lower layer importing an upper one is an architecture break, not debt."""
    found = []
    for prefix, forbidden in FORBIDDEN_IMPORTS.items():
        if not rel.startswith(prefix):
            continue
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.ImportFrom):
                names.append(node.module or "")
            elif isinstance(node, ast.Import):
                names.extend(a.name for a in node.names)
            for name in names:
                for bad in forbidden:
                    if bad.rstrip(".") in name.split("."):
                        found.append(
                            Violation(
                                "layering", rel, "-", node.lineno,
                                f"imports '{name}' — {prefix} must not depend on {bad}",
                            )
                        )
    return found


def scan_contracts() -> list[Violation]:
    """Every concrete Publisher must honour the ABC: implement publish() and
    declare the class attributes the CLI reads before it ever calls anything.

    Checked by import rather than by AST — an attribute inherited from a base
    is still honoured, and only the runtime knows that.
    """
    sys.path.insert(0, str(ROOT))
    found: list[Violation] = []
    try:
        from common.runners import config
        from common.runners.publishers.base import Publisher

        config.load_all_publishers()
    except Exception as exc:  # noqa: BLE001 — a broken import IS the finding
        return [Violation("contract", "common/runners/publishers/", "-", 1, f"import failed: {exc}")]

    required = ["name", "supports", "requires_env", "supports_draft", "needs_public_media_url"]
    for pub in config.all_publishers():
        rel = f"common/runners/publishers/{pub.name}.py"
        if not isinstance(pub, Publisher):
            found.append(Violation("contract", rel, pub.name, 1, "does not subclass Publisher"))
            continue
        for attr in required:
            if getattr(pub, attr, None) is None:
                found.append(Violation("contract", rel, pub.name, 1, f"missing '{attr}'"))
        if not pub.supports:
            found.append(Violation("contract", rel, pub.name, 1, "declares no supported post kinds"))
        if type(pub).publish is Publisher.publish:
            found.append(Violation("contract", rel, pub.name, 1, "does not implement publish()"))
        # preflight is concrete on purpose; overriding it skips the generic
        # checks every platform needs. Extend via _extra_preflight instead.
        if type(pub).preflight is not Publisher.preflight:
            found.append(
                Violation("contract", rel, pub.name, 1, "overrides preflight(); use _extra_preflight()")
            )
        if pub.requires_oauth and pub.oauth_app() is None:
            found.append(
                Violation("contract", rel, pub.name, 1, "requires_oauth but registers no OAuthApp")
            )
    return found


def load_baseline() -> set[str]:
    if not BASELINE_PATH.is_file():
        return set()
    return set(json.loads(BASELINE_PATH.read_text(encoding="utf-8")).get("frozen", []))


def write_baseline(keys: set[str], counts: dict[str, int]) -> None:
    payload = {
        "_comment": (
            "Known structural debt, frozen so the gate gives a hard failure on anything new. "
            "This list may only SHRINK. Regenerate with scripts/check-code-quality.py --freeze; "
            "the script refuses to grow it."
        ),
        "thresholds": {
            "module_lines": MAX_MODULE_LINES,
            "list_module_lines": MAX_LIST_MODULE_LINES,
            "function_lines": MAX_FUNCTION_LINES,
            "complexity": MAX_COMPLEXITY,
            "parameters": MAX_PARAMETERS,
        },
        "counts": counts,
        "frozen": sorted(keys),
    }
    BASELINE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def collect() -> list[Violation]:
    found: list[Violation] = []
    for path in python_files():
        found.extend(scan_module(path))
    found.extend(scan_contracts())
    return found


def partition(found: list[Violation], baseline: set[str]) -> tuple[list, list, list]:
    """(invariants, new debt, paid-off keys).

    Contract and layering findings are never baselined — a publisher that skips
    its ABC is broken now, not gradually.
    """
    hard = [v for v in found if v.kind in INVARIANT_KINDS]
    debt = [v for v in found if v.kind not in INVARIANT_KINDS]
    new = [v for v in debt if v.key() not in baseline]
    stale = sorted(baseline - {v.key() for v in debt})
    return hard, new, stale


def do_freeze(found: list[Violation], baseline: set[str], counts: dict[str, int]) -> int:
    debt = [v for v in found if v.kind not in INVARIANT_KINDS]
    keys = {v.key() for v in debt}
    # Bootstrapping is not growth. Without this the very first --freeze refuses
    # itself, because "0 known violations -> 116" reads as an increase.
    bootstrapping = not BASELINE_PATH.is_file()
    if not bootstrapping and len(keys) > len(baseline):
        grew = sorted(k for k in keys if k not in baseline)
        print(f"refusing to grow the baseline by {len(keys) - len(baseline)}:", file=sys.stderr)
        for k in grew[:10]:
            print(f"  + {k}", file=sys.stderr)
        print("\nFix them, or raise a threshold on purpose.", file=sys.stderr)
        return 1
    write_baseline(keys, counts)
    print(f"baseline frozen: {len(keys)} entries (was {len(baseline)})")
    return 0


def do_report(found: list[Violation], baseline: set[str]) -> int:
    hard, new, _ = partition(found, baseline)
    for v in sorted(found, key=lambda v: (v.kind, v.path, v.line)):
        print(f"{' ' if v.key() in baseline else '!'} {v}")
    print(f"\ntotal {len(found)} · frozen {len(baseline)} · new {len(new)} · hard {len(hard)}")
    return 0


def do_gate(found: list[Violation], baseline: set[str]) -> int:
    hard, new, stale = partition(found, baseline)

    if hard:
        print(f"  ✗ {len(hard)} contract/layering violation(s) — these are never baselined:")
        for v in hard:
            print(f"      {v}")
    if new:
        print(f"  ✗ {len(new)} new structural violation(s):")
        shown = sorted(new, key=lambda v: (v.kind, v.path))[:MAX_REPORTED]
        for v in shown:
            print(f"      {v}")
        if len(new) > MAX_REPORTED:
            print(f"      … and {len(new) - MAX_REPORTED} more — see --report")
        print("      Fix them, or run --freeze if a threshold is genuinely wrong.")
    if hard or new:
        return 1

    if stale:
        print(f"  ✓ code quality OK ({len(baseline) - len(stale)} frozen, {len(stale)} paid off)")
        print(f"      Run --freeze to shrink the baseline by {len(stale)}.")
    else:
        print(f"  ✓ code quality OK ({len(baseline)} known violations, no new ones)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--report", action="store_true", help="print every violation, baseline included")
    ap.add_argument("--freeze", action="store_true", help="rewrite the baseline (shrinking only)")
    args = ap.parse_args()

    found = collect()
    baseline = load_baseline()
    counts: dict[str, int] = {}
    for v in found:
        counts[v.kind] = counts.get(v.kind, 0) + 1

    if args.freeze:
        return do_freeze(found, baseline, counts)
    if args.report:
        return do_report(found, baseline)
    return do_gate(found, baseline)


if __name__ == "__main__":
    sys.exit(main())
