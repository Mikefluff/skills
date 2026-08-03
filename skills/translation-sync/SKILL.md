---
name: translation-sync
description: "Read-only parity checker for multilingual translations (RU↔EN↔PT-BR). Validates typography, terminology consistency, anchor-quote canonical translations, names/diminutives, and realia footnotes. Produces a parity report; never edits. Use before committing a translated chapter to catch drift and 'smoothed' numbers."
license: MIT
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

<objective>
Read-only parity auditor for trilingual book translations across RU, EN, PT-BR. Operates over any directory layout that mirrors source and target languages (e.g. `your-book/{ru,en,pt-br}/chapters/*.{md,tex,txt}`) and flags drift between language versions.

Use cases:
- before `git commit` — check staged changes in any of the three language directories
- chapter audit — run a full parity check on a chapter file across all three languages
- post-commit — verify the last commit didn't introduce drift
- range — diff across commit range when catching up after a depth-pass
- pre-commit hook — if the user wires it into `.git/hooks/pre-commit`

This skill **does not translate**. It does not propose translations, does not auto-fix typography, does not edit files. It reads, compares, and reports.
</objective>

## ROLE

Translation parity auditor. Never a translator. Never an editor.

The user owns every translation decision. This skill catches the mechanical drift the eye misses: a canon term that quietly shifted, a smoothed number, an anchor quote that got "improved", a missing footnote on a cultural realia term, the wrong dash in the wrong language.

If a finding is debatable, surface it and let the author decide. If the canon registry in [references/terminology.md](references/terminology.md) is silent on a term, **do not invent** a ruling — flag the unknown and move on.

## LANGUAGES

Three target languages, each with distinct typographic and stylistic constraints:

- **RU** — «ёлочки» for outer quotes, `\enquote{...}` for inner. Em-dash `---` with non-breaking space after for direct speech. Numbers spelled out except years and decimals. Real foreign names stay in Latin script.
- **EN** — TeX-style `` ``...'' `` for outer, `` `...' `` for inner quotes. Em-dash `---` **with spaces** (illustrative house rule, against AmE norm — keeps rhythm parity with RU/PT-BR). Numbers spelled out with hyphens (`twenty-eight`). Russian names transliterated by the table in [references/names-and-realia.md](references/names-and-realia.md).
- **PT-BR** — TeX-style `` ``...'' `` for outer, `` `...' `` for inner (English style, not French «...» — illustrative house rule). Em-dash `---` with spaces. Numbers spelled out without hyphens (`vinte e oito`). Russian names transliterated; Latin-script names stay Latin.

Full per-language typography table in [references/typography.md](references/typography.md).

## MODES

### `staged` (default) — check staged diff
```bash
git diff --cached --name-only
```
For each staged prose file (`.md` / `.tex` / `.txt` / `.rst`) under a per-language directory tree:
1. Detect target language by path segment (`/ru/`, `/en/`, `/pt-br/`)
2. Pull added/changed lines: `git diff --cached -U0 <file>`
3. Run pipeline (typography for that language; if RU file changed, also flag "EN/PT-BR may be stale")
4. Aggregate findings

### `chapter <book> <chN>` — full parity check across all three languages
Read the source chapter and its two sibling translations (e.g. `<book>/ru/chapters/<chN>`, `<book>/en/chapters/<chN>`, `<book>/pt-br/chapters/<chN>`). Run the full 15-point checklist from [references/checklist.md](references/checklist.md) across all three.

### `range <from>..<to>` — diff across commit range
```bash
git diff <from>..<to> --name-only
```
Pipeline as in `staged`. Useful after a RU depth-pass to verify EN/PT-BR caught up.

### `file <path>` — single file check
Full pass on one file. Typography + terminology + smoothing + names. Anchor-quote check skipped (needs sibling files).

### `file <path> <line1>:<line2>` — line-range check on a single file

## PIPELINE

For each in-scope file, run six passes. Each pass references its own rule file:

1. **Typography** — quote style, dashes, ellipsis, numerals for the file's target language. Rules: [references/typography.md](references/typography.md).
2. **Terminology consistency** — canon terms must match the registry across the three languages. "Do not translate" markers respected (e.g. `Pointer Architecture` stays English everywhere). Rules: [references/terminology.md](references/terminology.md).
3. **Anchor-quote canon** — fixed translations for load-bearing quotations must be preserved verbatim. No "improvements", no extenders. Rules: [references/anchor-quotes.md](references/anchor-quotes.md).
4. **Names & realia** — real people in Latin script in all languages; Russian patronymics not transliterated mechanically; diminutives table respected (full / short / affectionate forms map per character); cultural realia (place names, institutions, brands) carry footnote on first mention. Rules: [references/names-and-realia.md](references/names-and-realia.md).
5. **No smoothing** — numbers, durations, exact years, street names, brand names stay literal. `900 ms` does not become `under a second`. Rules: [references/what-not-to-smooth.md](references/what-not-to-smooth.md).
6. **15-point checklist aggregate** — the final pre-commit run-through. List: [references/checklist.md](references/checklist.md).

## OUTPUT FORMAT

Structured report grouped by file, then by check category. Each finding cites line number, the offending excerpt, and the canonical rule (or expected canonical form).

```
=== translation-sync ===
Mode: chapter your-book ch05
Languages: ru en pt-br

[TYPOGRAPHY] your-book/en/chapters/ch05.md
  L42 — straight quotes "..." in EN context — should be ``...'' (TeX outer)
  L88 — em-dash without spaces in EN context — house rule: em-dash with spaces

[TERMINOLOGY] ru → en
  L120 ru "Term X" → en "Term X" — OK (do not translate)
  L156 ru "supporting structure" → en "support structure" — drifts from canon:
       terminology.md lists this term as "load-bearing structure"

[ANCHOR_QUOTES] ru → pt-br
  L201 ru "Anchor quote A" (canonical RU form)
       pt-br "smoothed paraphrase" — drift; canonical PT-BR per
       anchor-quotes.md §finale must be preserved verbatim

[NAMES_REALIA] ru → en
  L302 ru "diminutive form" → en "incorrect transliteration"
       — wrong: canonical EN form per names-and-realia.md §diminutives
  L315 ru "Local Place" → en "Local Place" — no first-mention footnote
       in this chapter (names-and-realia.md §cultural realia)

[NO_SMOOTHING] ru → en
  L412 ru "900 milliseconds" → en "under a second" — smoothing forbidden
       (what-not-to-smooth.md §numbers)

=== SUMMARY ===
Files checked: 3 (ru, en, pt-br)
Findings:
  - typography:    2 (warning)
  - terminology:   1 (blocking)
  - anchor quote:  1 (blocking)
  - names/realia:  2 (1 blocking, 1 warning)
  - smoothing:     1 (blocking)
```

Full annotated sample in [examples/sample-parity-report.md](examples/sample-parity-report.md).

## SEVERITY

- **BLOCKING** — must fix before commit:
  - Terminology drift on a canon term registered in `terminology.md`
  - Anchor-quote drift (any deviation from canonical translation in `anchor-quotes.md`)
  - Smoothed number, duration, or year (`what-not-to-smooth.md`)
  - Missing or malformed first-mention footnote on cultural realia
  - Real person's name transcribed to Cyrillic (or Russian name not transliterated in EN/PT-BR per the table)

- **WARNING** — review before commit:
  - Typography mismatch (wrong quote style, wrong dash spacing, three-dot ellipsis instead of `…` or `\dots`)
  - Inconsistent diminutive usage inside a single chapter (mixing `Dan` and `Daniel` for the same character)
  - Added extender that didn't exist in source (`my friend`, `you see`, `como assim`)
  - Bracketed digression flattened into separate sentence

- **INFO** — author's call:
  - Rhythm adjustment within tolerance (EN compacter, PT-BR softer — expected; only flag if it loses a concrete image)
  - Idiom swap from literal to equivalent (`close the loop` for `закрыть гештальт`)
  - Stylistic difference in sentence length

## EXIT CODE (when wired as git pre-commit hook)

- `0` — only INFO findings; commit allowed
- `1` — at least one WARNING; commit allowed but author should review
- `2` — at least one BLOCKING; commit aborted

In normal (non-hook) invocation, exit code is not used; only the report.

## WHAT NOT TO DO

- **Do not translate.** This skill audits; translation is the user's call. If a term is missing from the canon, flag the gap and recommend adding to `terminology.md` — do not invent a translation.
- **Do not auto-fix typography.** Flag and let the user decide. The user may have stylistic reasons for an "incorrect" dash.
- **Do not load translation-memory tools, glossary engines, or external CAT integrations.** Pure markdown skill — Read + Grep + Bash only.
- **Do not edit any files.** Read-only.
- **Do not run inside `loop`.** This is a one-shot pre-commit check.
- **Do not flag rhythm differences as drift.** EN is ~30% more compact than RU; PT-BR is mellower. Differences in sentence count, line breaks, paragraph rhythm are expected. Only flag if a concrete image or number was lost.
- **Do not transcribe real people.** Real Latin-script names stay Latin in all languages, including the Cyrillic source. Russian historical figures get standard transliteration in EN/PT-BR; never the reverse.

## REFERENCES (load on demand)

| File | When to load |
| --- | --- |
| [references/checklist.md](references/checklist.md) | Pre-commit 15-point run-through; order of operations for a chapter audit. |
| [references/typography.md](references/typography.md) | Per-language quote, dash, ellipsis, numeral rules — every typography finding. |
| [references/terminology.md](references/terminology.md) | Canon-term registry — every `[TERMINOLOGY]` finding cites a row here. |
| [references/anchor-quotes.md](references/anchor-quotes.md) | Fixed translations of load-bearing quotations — every `[ANCHOR_QUOTES]` finding cites a row here. |
| [references/names-and-realia.md](references/names-and-realia.md) | Real-person rules, Russian transliteration table, patronymics, diminutives, cultural realia footnote pattern. |
| [references/what-not-to-smooth.md](references/what-not-to-smooth.md) | List of categories that must remain specific (numbers, dates, streets, brands) with before/after examples. |
| [examples/sample-parity-report.md](examples/sample-parity-report.md) | Calibration sample of the report format. |
