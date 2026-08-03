---
name: style-check
description: "Read-only pre-commit lint over writer/prose-edit/essay-write. Takes a staged diff (or a specified file / commit range) and flags neuro-slop, synthetic structures, voice drift in prose. Read-only — never edits. Use before `git commit`, as a post-commit check, or as a pre-commit hook."
license: MIT
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

<objective>
Universal read-only style linter for prose projects. Does not write, does not edit, does not commit — only checks.

Use cases:
- before `git commit` — check staged changes for neuro-slop
- post-commit — check the last commit
- manual run on a file / line range
- pre-commit hook (if the user wires it into `.git/hooks/pre-commit`)

The skill picks which rule layer to apply (writer / prose-edit / essay-write) based on file path. Default routing is illustrative; configure your own path patterns — see [references/routing.md](references/routing.md):
- fiction project files (e.g. `fiction/*.md`, `novels/**/*.tex`) → fiction layer (prose-edit)
- non-fiction project files (e.g. `essays/*.md`, `longreads/*.md`) → non-fiction layer (essay-write)
- generic prose / notes → base writer
- code files (`.py`, `.js`, `.ts`, …) → skipped silently
</objective>

<instructions>

## DEPENDENCY

This skill applies rules from:
- `writer/SKILL.md` — baseline anti-neuro-slop (25 categories) + structural synthetic markers
- `prose-edit/SKILL.md` — fiction layer
- `essay-write/SKILL.md` — non-fiction layer

The skill DOES NOT write or edit. It reads files, runs rules, returns a structured report.

## FILE-FORMAT AGNOSTIC

Accepts any text format: `.md`, `.tex`, `.txt`, `.rst`, plain text. Auto-skips binary files and known source-code extensions.

## ROUTING

The skill picks a rule set by file path (fiction → writer+prose-edit, non-fiction → writer+essay-write, anything else → writer only; code is skipped). The default routing table is illustrative — adapt the patterns to your project's directory layout. Full routing table, edge cases, extension-skip list, and a "configuring your own routing" note — see [references/routing.md](references/routing.md).

## MODES

### `staged` (default) — check staged changes
```bash
git diff --cached --name-only
```
For each staged file:
1. If binary or a code extension — skip
2. Pull added/changed lines: `git diff --cached -U0 <file>`
3. Apply the matching rule set (per routing)
4. Emit a report

### `last` — check the last commit
```bash
git diff HEAD~1 HEAD --name-only
```
Same pipeline, scoped to the last commit.

### `range <from>..<to>` — check a commit range
```bash
git diff <from>..<to> --name-only
```

### `file <path>` — check the whole file
Not a diff; a full pass over the file. Useful for older files.

### `file <path> <line1>:<line2>` — check a line range
Full pass on the indicated fragment.

### `detect` — "was this written by AI?"
Not a lint pass but an audit with a verdict. Triggers: «проверь на ИИ», «палится ли текст», «это нейросеть писала?», "is this AI-written".

Run the linter, then score findings by *family* (лексика / структура / коммуникация), not by raw count — hits from a single family are the author's style, not a model. Any class A copy-paste artifact (`turn0search3`, `oaicite`, `utm_source=chatgpt.com`) settles it on its own without a cluster.

Returns a table of quotes with a verdict. Does not rewrite. Full scale, family taxonomy, output shape and the limits of what soft signals can prove — [references/detect-mode.md](references/detect-mode.md).

## OUTPUT FORMAT

Structured report grouped by file, then by violations (L<line> CATEGORY «quote» → rule/advice), plus a `=== SUMMARY ===` block with counters by layer and severity breakdown. Full reference template — in [references/output-format.md](references/output-format.md); a separate calibration sample — in [examples/sample-report.md](examples/sample-report.md).

## SEVERITY LEVELS

Three levels: **BLOCKING** (canon drift, uncited claim, fabricated source, broken markup), **WARNING** (neuro-slop ≥2 matches, staccato/inversion/double-neg, tautology/meta-ref/anglicism, academic pathos, viral format), **INFO** (single-match L1, metaphor overload, style drift). Full category-by-level breakdown — in [references/severity.md](references/severity.md).

## EXIT CODE (if invoked as a pre-commit hook)

When wired as a git hook:
- `0` — only INFO, commit allowed
- `1` — WARNING present, ask the author (or show-and-continue, depending on configuration)
- `2` — BLOCKING present, abort the commit

In a normal (non-hook) call, exit code is not used — just the report.

## INTEGRATION

The skill does not install the hook itself. If the user asks — emit installation instructions for a `.git/hooks/pre-commit` wrapper. Ready-made bash snippet and installation steps — in [references/pre-commit-hook.md](references/pre-commit-hook.md).

## WHAT NOT TO DO

- **Does not edit files.** Reads and reports only. For editing — use `writer`/`prose-edit`/`essay-write`.
- **Does not spawn sub-agents.** Lightweight read-only skill, everything goes through Read+Grep+Bash directly.
- **Does not fabricate sources to check fabrication.** It only marks suspicious citations as `UNVERIFIED_SOURCE` — verification is the author's job.
- **Does not assert authorship from soft signals.** In `detect` mode, flawless grammar, dryness and a wide vocabulary prove nothing. Report the markers with quotes; let the reader conclude. Missing a machine-written text is cheaper than accusing a living author.
- **Does not block commits automatically without exit code.** When run as a normal skill — report only. Blocking happens only via an installed hook.
- **Does not touch code.** `.py`, `.js`, `.ts`, `.go` and similar — silently skipped.

</instructions>

## REFERENCES (load on demand)

| File | When to load |
| --- | --- |
| [references/detect-mode.md](references/detect-mode.md) | The user asks whether a text was written by AI — verdict scale, family taxonomy, class A artifacts, and where to stop. |
| [references/routing.md](references/routing.md) | Deciding which rule set applies to a given path / extension; need edge cases or want to configure your own routing patterns. |
| [references/severity.md](references/severity.md) | Need to classify a violation as BLOCKING / WARNING / INFO or want the full category list. |
| [references/output-format.md](references/output-format.md) | Producing the final report — need the full template with the SUMMARY block. |
| [references/pre-commit-hook.md](references/pre-commit-hook.md) | The user asks to install style-check as a git pre-commit hook — need the bash snippet and steps. |
| [references/validation-taxonomy.md](references/validation-taxonomy.md) | Producing structured JSON validation output for CI/CD or tooling — hookAnalysis, contentAnalysis, scoreReasons enum, metrics, formattingRecommended. |
| [examples/sample-report.md](examples/sample-report.md) | Need tone/detail calibration — reference sample. |
