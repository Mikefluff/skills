#!/usr/bin/env python3
"""Fail when a documented command passes a flag the CLI does not accept.

The skills document two different things that both look like flags. `--execute`
and `--variants 4` on a `/logo-maker` line are skill-level conventions: Claude
reads them and writes a plan. Those cannot be checked against anything, and are
not the subject here.

What can be checked is the literal command — `python3 -m common.runners.cli.cover
--plan-file plan.json --yes`, or a `scripts/run.py` invocation. A reader copies
those verbatim, and argparse answers with `unrecognized arguments` rather than
anything useful about what the doc meant.

Every CLI module exposes a zero-arg `build_parser()` so its surface can be read
without running it. That is the whole mechanism: ask the parser, compare, report.

Usage:
    python3 scripts/check-cli-docs.py            # check, exit 1 on drift
    python3 scripts/check-cli-docs.py --list     # every command found
"""
from __future__ import annotations

import argparse
import importlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ROOTS = ("skills", "docs")

# `python3 -m common.runners.cli.cover --plan-file ...`
MODULE_CALL = re.compile(r"common\.runners\.cli\.(?P<mod>[a-z_]+)(?P<rest>[^\n`]*)")
# `python3 ~/.claude/skills/video-prompt/scripts/run.py --model ...` and friends
RUN_PY = re.compile(r"(?:(?P<skill>[a-z][a-z0-9-]*)/)?scripts/run\.py(?P<rest>[^\n`]*)")
FLAG = re.compile(r"(?<![\w-])--[a-z0-9][a-z0-9-]*")


def _module_for_skill() -> dict[str, str]:
    """skill name -> the cli module its run.py delegates to."""
    mapping = {}
    for run in sorted((ROOT / "skills").glob("*/scripts/run.py")):
        found = re.search(r"from common\.runners\.cli import ([a-z_]+)", run.read_text(encoding="utf-8"))
        if found:
            mapping[run.parts[-3]] = found.group(1)
    return mapping


SKILL_MODULE = _module_for_skill()


def _accepted(module: str) -> set[str] | None:
    """Every long option the module's parser knows, subcommands included."""
    try:
        mod = importlib.import_module(f"common.runners.cli.{module}")
    except ModuleNotFoundError:
        return None
    build = getattr(mod, "build_parser", None)
    if not callable(build):
        return None
    flags: set[str] = set()

    def walk(parser: argparse.ArgumentParser) -> None:
        for action in parser._actions:
            flags.update(o for o in action.option_strings if o.startswith("--"))
            if isinstance(action, argparse._SubParsersAction):
                for sub in action.choices.values():
                    walk(sub)

    walk(build())
    return flags


def _logical_lines(text: str):
    """Join shell continuations so a wrapped command reads as one line."""
    buffer, start = "", 0
    for lineno, line in enumerate(text.splitlines(), 1):
        if not buffer:
            start = lineno
        stripped = line.rstrip()
        if stripped.endswith("\\"):
            buffer += stripped[:-1] + " "
            continue
        yield start, buffer + stripped
        buffer = ""
    if buffer:
        yield start, buffer


def _commands(path: pathlib.Path, owner: str | None):
    """Yield (lineno, module, flags) for every literal CLI call in the file."""
    for lineno, line in _logical_lines(path.read_text(encoding="utf-8")):
        for found in MODULE_CALL.finditer(line):
            yield lineno, found.group("mod"), FLAG.findall(found.group("rest"))
        for found in RUN_PY.finditer(line):
            skill = found.group("skill") or owner
            module = SKILL_MODULE.get(skill or "")
            if module:
                yield lineno, module, FLAG.findall(found.group("rest"))


def audit() -> tuple[list[str], int]:
    failures: list[str] = []
    checked = 0
    for root in ROOTS:
        for path in sorted((ROOT / root).rglob("*.md")):
            owner = path.parts[len(ROOT.parts) + 1] if root == "skills" else None
            for lineno, module, flags in _commands(path, owner):
                accepted = _accepted(module)
                if accepted is None:
                    continue
                checked += 1
                unknown = [f for f in flags if f not in accepted]
                if unknown:
                    rel = path.relative_to(ROOT).as_posix()
                    failures.append(
                        f"  ✗ {rel}:{lineno}\n"
                        f"      common.runners.cli.{module} does not accept {', '.join(unknown)}\n"
                        f"      it accepts: {', '.join(sorted(accepted))}"
                    )
    return failures, checked


def main() -> int:
    if "--list" in sys.argv:
        for root in ROOTS:
            for path in sorted((ROOT / root).rglob("*.md")):
                owner = path.parts[len(ROOT.parts) + 1] if root == "skills" else None
                for lineno, module, flags in _commands(path, owner):
                    rel = path.relative_to(ROOT).as_posix()
                    print(f"{rel}:{lineno}  {module}  {' '.join(flags) or '(no flags)'}")
        return 0

    failures, checked = audit()
    if failures:
        print(f"cli-docs: FAILED — {len(failures)} of {checked} documented commands would not run")
        print("\n".join(failures))
        return 1
    print(f"cli-docs: OK ({checked} documented commands match their parser)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
