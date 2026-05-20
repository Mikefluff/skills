---
name: canon-check
description: "Read-only story-bible auditor for fiction series with a documented canon. Cross-references character / artifact / location mentions in chapters against the bible and flags drift. Produces a drift report — never edits files. Use before opening or committing a chapter, or when reintroducing an established entity."
license: MIT
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

<objective>
Read-only story-bible auditor for any book series that maintains a written canon. Before any insertion, rewrite, or commit — cross-references mentions of characters / artifacts / locations in the current text against the project's recorded canon. Flags drift. Does not edit the chapter or the bible.

**Why this skill exists.** The same canon-break patterns recur across long-form fiction projects: a character's documented physical invariant gets accidentally inverted in a later chapter; an artifact moves room without explanation; a recurring character appears under a generic descriptor when an established proper name already exists; a count or age stated in the bible doesn't match what the text actually shows. Each break is cheap to catch at lint time and expensive to catch in print.

Use cases:
- before opening a new chapter — confirm the names / artifacts / locations you're about to establish don't duplicate something already established;
- before `git commit` — staged diff vs canon;
- when mentioning a known character in a new scene — gather all their prior appearances + their bible entry;
- read-only audit of the bible itself (what gets mentioned in the text but never canonized).

**What the skill needs to know about your project:**
- where your chapter files live (any of `.md` / `.tex` / `.txt` / `.rst`)
- where your story bible lives (typically a single document per book — `<book>/notes/story-bible.{md,tex,txt}` or similar)
- which books are in the same series (so the skill can cross-reference inherited canon)

If the project follows the conventional layout (`<book>/{lang}/chapters/*` for chapters, `<book>/notes/story-bible.*` for the bible), the default routing works out of the box. Otherwise, override the routing patterns in [references/routing.md](references/routing.md).
</objective>

<instructions>

## ROLE

Story-bible auditor. **NOT a continuity editor.** The skill only signals discrepancies between:
- (a) the current draft,
- (b) the story bible,
- (c) other published chapters of the same book.

The user decides. The skill does not edit the chapter or the bible.

## CORE PRINCIPLE — TRUST THE TEXT, NOT MEMORY

When a contradiction appears between "what the current chapter says", "what the bible says", and "what the model 'remembers'" — the resolution priority is:

1. **Published chapters of the same book** = ground truth. Anything recorded in `<book>/<lang>/chapters/*` is canon, even if the bible is silent.
2. **The story bible** = next canon tier. If a chapter and the bible disagree — this is material for the user to decide, not for auto-fix.
3. **Model memory / claims about prior text** = LEAST trusted source. If you "remember" otherwise, you are wrong. Grep and re-read.

Never cite prior text from memory. Always `grep` + `Read` before stating "in chapter X it was Y".

## ROUTING

The skill picks the bible to apply based on file path. Full table — in [references/routing.md](references/routing.md). Briefly (illustrative defaults; adapt to your project):

```
<book>/{ru,en,pt-br,...}/chapters/*.{md,tex,txt,rst}  → <book>/notes/story-bible.{md,tex,txt}
sequel-book/<lang>/chapters/*                         → sequel-book/notes/story-bible.* + parent-book/notes/story-bible.*
                                                       (for inherited-canon sections)
any other path                                        → SKIP silently
```

## MODES

### `chapter <book> <chN>` — full canon scan of a chapter

```bash
# Example:
canon-check chapter your-book ch07
# → scans <book>/<lang>/chapters/ch07.{md,tex,...}
#   (plus other-language siblings if present — but the bible is one)
```

Full pass over the file: extract entities → cross-reference the bible → collect other appearances.

### `staged` — staged diff

```bash
git diff --cached --name-only
# for each known-book chapter file — pass over added/changed lines
```

### `entity <book> <name>` — all appearances of an entity

```bash
canon-check entity your-book "Character A"
# → bible entry + list of every file and line where it appears
```

Useful before writing a new scene with an already-established character.

### `audit-bible <book>` — structural bible audit

Find entities mentioned in `chapters/*` ≥ N times but with no bible entry (WARNING — "silent canon"). Does not edit the bible — just lists.

## PIPELINE (short version; full version — in [references/workflow.md](references/workflow.md))

**Step 1. Extract entities from the text under review.**
- **Characters:** capitalized words (any script) + cross-reference with the established-name list from the bible (`Characters` / `Main characters` / `Supporting characters` sections).
- **Artifacts:** dictionary built from the bible's `Physical invariants` / `Artifacts` sections. Each book maintains its own dictionary.
- **Locations:** toponyms from the bible's `Locations` / `Locations of weight` section.

**Step 2. For each entity — gather context.**

```bash
# bible entry:
grep -n -A 5 "<entity>" <book>/notes/story-bible.*

# other appearances in chapters:
grep -rn "<entity>" <book>/<lang>/chapters/
```

Read everything. Don't quote from memory.

**Step 3. Compare with the current text.**

Look for contradictions:
- attribute (age, profession, location, colour) diverges from the bible or from another chapter
- gesture / physical invariant (handedness, lag, count) altered
- anchor quote paraphrased
- artifact changed location / owner / grammatical gender
- character appears without a name, even though the bible already locks them under a proper name

**Step 4. If a new entity — flag for the user.**

If a clearly new entity appears in the text (proper noun, artifact) that has no bible entry — **WARNING, not auto-add**. The skill does not edit the bible. The user decides: canonize or remove.

Full list of detection classes and pattern-detection recipes — in [references/known-incidents.md](references/known-incidents.md).

## SEVERITY LEVELS

- **BLOCKING** — text contradicts a concrete bible entry (example: bible "Character A is right-handed, grip = thumb+index on top"; text "took it left-handed"). Or: text contradicts another published chapter of the same book.
- **WARNING (silent canon)** — entity appears in the text ≥ 2 times (in this chapter or others), but has no bible entry. Should be added.
- **WARNING (cross-chapter drift)** — bible silent, but two chapters give different attributes for the same entity.
- **INFO (canon expansion)** — a new detail introduced about an already-canonized entity (not a contradiction — an expansion). Optionally add to the bible.

## EXIT CODE (if invoked as a pre-commit hook)

- `0` — only INFO. Commit allowed.
- `1` — WARNING (silent canon / cross-chapter drift). Ask the user.
- `2` — BLOCKING (clear contradiction). Abort the commit.

In normal calls the exit code is not used — only the report.

## INTEGRATION

The skill does not install the hook itself. If the user asks — the standard pattern from style-check: `.git/hooks/pre-commit` calls a Claude Code wrapper with `/canon-check staged`. The skill does not edit `.git/hooks/` itself.

## OUTPUT FORMAT

Structured report with three sections (by severity) + SUMMARY with bible coverage. Reference template — in [examples/sample-report.md](examples/sample-report.md).

## WHAT NOT TO DO

- **Does not edit chapters.** Reports only. Edits — via `prose-edit` or by hand.
- **Does not edit the story bible.** The user updates the bible after deciding which version is canonical.
- **Does not trust its own memory** about prior chapters — always `grep` + `Read`. If you "remember" it differently from what the text says — the text wins.
- **Does not auto-canonize.** A new entity → WARNING for the user, not a silent bible append.
- **Does not spawn sub-agents.** Read-only, everything via Read + Grep + Bash.
- **Does not touch code.** `.py`, `.js`, `.ts`, `.go` — skip.
- **Does not run inside `/loop` or `/schedule`.** This is an interactive audit, not a cron job.

</instructions>

## REFERENCES (load on demand)

| File | When to load |
| --- | --- |
| [references/workflow.md](references/workflow.md) | Need exact grep commands for entity extraction and canon cross-reference. 3-step protocol with examples. |
| [references/bible-format.md](references/bible-format.md) | Need the typical structure of a story bible — what sections to expect, where new entries go. |
| [references/known-incidents.md](references/known-incidents.md) | Need calibration on the general classes of canon break this skill is designed to catch (with detection recipes). |
| [references/routing.md](references/routing.md) | Deciding which bible to apply to a given file path. |
| [examples/sample-report.md](examples/sample-report.md) | Need tone/detail calibration for the report. |
