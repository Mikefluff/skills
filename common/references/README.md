# Shared references

This directory holds reference material used by **multiple skills**.
Individual skills link into `common/references/*.md` from their own
`references/banned-patterns.md` (or equivalent) instead of duplicating
the rules.

When `install.sh --copy-from .` runs, this directory is copied to
`~/.claude/skills/common/references/` so that the relative paths
inside skills stay resolvable on installed systems.

## Files

| File | Used by |
| --- | --- |
| [`banned-patterns-hype.md`](banned-patterns-hype.md) | `cold-email`, `landing-copy`, `release-notes` |
| [`banned-patterns-preambles.md`](banned-patterns-preambles.md) | `cold-email`, `landing-copy`, `release-notes` |
| [`banned-patterns-empty-cta.md`](banned-patterns-empty-cta.md) | `landing-copy`, `microcopy` |

## How to extend

If you find a new anti-pattern that applies to ≥2 skills:

1. Add it to the appropriate file here.
2. Update the skill's local `banned-patterns.md` to cross-link (don't duplicate).
3. If the pattern is regex-detectable, also add it to
   `writer/scripts/lint.py` under the appropriate category
   (MARKETING_HYPE / WEAK_OPENER / EMPTY_CTA / VAGUE_BENEFIT).

The base linter in `writer/scripts/lint.py` is the source of truth for
**automated detection**. Files here are the source of truth for the
**rationale and full taxonomy** — including patterns that are too
context-dependent to regex.
