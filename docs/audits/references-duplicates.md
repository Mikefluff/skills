# References-duplicates audit

**Date**: 2026-05-20
**Question**: Are there enough content duplicates across `*/references/` to justify a `core/` shared-base refactor?
**Verdict**: **No.** The current per-skill organization is correct. No refactor needed.

---

## Method

Cataloged all reference files across skills. Diff-checked filename-clashes. Searched for keyword overlap on canonical structural concepts (staccato, double-negation, intensifier ladder, balance hedges).

## Files inventoried

| File | Lines | Scope |
|---|---|---|
| `writer/references/structural-prose.md` | 243 | Canonical structural patterns (staccato, double-neg, "просто" обрубки, реплики, огрызки) — RU + EN |
| `writer/references/neuroslop-categories.md` | 497 | 23-category linter catalogue — RU + EN |
| `writer/references/typography.md` | varies | Typography rules (quotes, dashes, numerals) — RU + EN |
| `writer/references/ru-calques.md` | varies | RU calques only |
| `prose-edit/references/voice.md` | 113 | Fiction voice patterns (cross-links to writer/structural-prose) — RU + EN |
| `viral-text/references/viral-rules.md` | 141 | Viral content rules (hooks, NLP question, CTA) — RU + EN |
| `essay-write/references/banned-constructions.md` | 40 | Essay-only bans (academic pathos, viral devices in non-fic) |
| `pelevin-digression/references/banned-constructions.md` | 95 | Pelevin-only bans (aphoristic closers, manifesto-tail) |
| Skills tone-shifter, cold-email | various | New v1.2.0 — no overlap with others |

## Filename-clashes investigated

Two `banned-constructions.md` files exist (essay-write/, pelevin-digression/). Diff confirms they cover **disjoint content** — essay register vs Pelevin-vector register. Same filename, different scopes. Acceptable; consolidating would lose scope clarity.

## Content-overlap probes

- Staccato concept: defined ONCE in `writer/references/structural-prose.md`. `prose-edit/references/voice.md` references it via cross-link ("Cross-link: writer structural-prose.md 'EN staccato'."), does not redefine.
- Double-negation: defined ONCE in `writer/references/structural-prose.md`. Not redefined elsewhere.
- AI-style signatures: defined ONCE in `writer/references/neuroslop-categories.md`. Other skills' references add scope-specific layers (essay-write adds "essay-only bans", viral-text adds "viral hook patterns"), they do not redefine the catalogue.

## Architecture (current)

```
writer/references/
├── structural-prose.md       ← canonical structural patterns
├── neuroslop-categories.md   ← canonical regex catalogue
├── typography.md             ← canonical typography
└── ru-calques.md             ← canonical calques (RU only)

<wrapper-skill>/references/
└── *.md                      ← additive, scope-specific; cross-links back to writer/
```

Wrappers compose by cross-linking, not by duplicating. The Claude Code skill matcher loads references on demand — there is no need to physically merge.

## Implication for new skills

When adding a skill that needs structural / neuroslop / typography rules — DO cross-link to `writer/references/<file>.md`, DON'T copy. The cross-link is honored both by Claude Code (which can load referenced files on demand) and by `scripts/validate.sh` (which checks link resolution).

## Out-of-scope decision

No `core/` directory. No shared-base layer migration. `writer/` IS the shared base — the architecture already treats it that way through skill `deps:` in `skills.json` and through reference cross-links.

This audit was prompted by an earlier note flagging "duplicate references at filename-level". On inspection, those are orthogonal-content same-filename files, not duplicates. The skill collection's reference organization is sound.
