# ROUTING — which rule set to apply

The skill picks a rule layer by file path. The patterns below are **illustrative defaults**; adapt them to your project's actual directory layout.

## Default pattern (illustrative)

```
fiction/**/*.{md,tex,txt}          → writer + prose-edit
novels/**/*.{md,tex,txt}           → writer + prose-edit
essays/**/*.{md,tex,txt,rst}       → writer + essay-write
longreads/**/*.{md,txt}            → writer + essay-write
preprints/**/*.{md,tex}            → writer (+ essay-write for narrative sections)
notes/**/*.md, README.md, *.md     → writer
any other text file                → writer
```

If the file is code (`.py`, `.js`, `.ts`, `.go`, `.rs`, `.java`, `.c`, `.cpp`, `.h`, `.rb`, `.php`, `.swift`, `.kt`, etc.) — skip silently. Not the skill's job.

## File extensions accepted

`.md`, `.tex`, `.txt`, `.rst`, plain text — all routed through the same rule machinery. Markup (LaTeX commands, Markdown syntax, restructured-text directives) is ignored by the linter, which only inspects the prose content.

## Configuring your own routing

The routing patterns above are not hard-wired. To adapt the skill to your project:

1. Identify which directories hold **fiction prose** (novels, short stories, chapters) and route them through `writer + prose-edit`.
2. Identify which directories hold **non-fiction prose** (essays, longreads, op-eds, book chapters of non-fiction) and route them through `writer + essay-write`.
3. Everything else with prose-like text — base `writer`.
4. Code files — skip.

You can implement this by:
- editing this routing table to match your real paths, OR
- letting the model infer routing from filename heuristics on each invocation (e.g. "this is in `essays/` → non-fiction layer"), OR
- prefacing the skill call with an explicit routing override ("treat this file as fiction layer").

The skill defers to the most specific available signal — explicit user instruction beats path-pattern matching beats filename heuristic.

## Edge cases

- **Mixed-content files** (a notebook with prose and code blocks) — prose blocks get linted, code blocks get skipped.
- **Empty files / files with only markup** — skip with an `INFO` note.
- **Symlinks** — follow once, skip if the target is binary or code.
- **Files inside `.git/`, `node_modules/`, `vendor/`, `build/`, `dist/`** — skip.
