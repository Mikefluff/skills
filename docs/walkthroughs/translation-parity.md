---
title: "Verify translation parity across RU/EN/PT-BR before commit"
persona: "translator / multilingual book author / localization editor"
time: "5-15 minutes per chapter"
skills:
  - translation-sync
---

# Catch translation drift before it ships

Scenario: you just finished a depth-pass on the RU chapter `your-book/ru/chapters/ch07.md`. The EN and PT-BR drafts already exist — done by you or a co-translator. You want to commit all three together, but you're worried about the usual silent killers:

- a canon term that quietly shifted (`Pointer Architecture` got translated to `опорная структура` somewhere)
- typography mismatch (`-` instead of `---`, ASCII quotes in PT-BR)
- a number that got smoothed (`900 ms` became `under a second`)
- a name with the wrong transliteration
- a missing cultural-realia footnote

This is exactly what `translation-sync` is for. It's read-only — produces a structured parity report, never edits files.

## Step 1. Run the parity check

```
/translation-sync chapter your-book ch07
```

The skill reads all three sibling files:

- `your-book/ru/chapters/ch07.md`
- `your-book/en/chapters/ch07.md`
- `your-book/pt-br/chapters/ch07.md`

And runs the 6-pass pipeline (see [translation-sync/SKILL.md](../../translation-sync/SKILL.md) for the full description):

1. Typography per language
2. Terminology consistency vs canon
3. Anchor-quote canonical translation
4. Names & realia
5. No-smoothing of numbers / brands / dates
6. 15-point checklist aggregate

## Step 2. Read the report

Illustrative output (mixed severity, abbreviated):

```
=== translation-sync ===
Mode: chapter your-book ch07
Languages: ru en pt-br

[TYPOGRAPHY] your-book/en/chapters/ch07.md
  L42 — straight quotes "Pointer Architecture" in EN context
        — should be ``Pointer Architecture'' (TeX outer)
  L88 — em-dash without spaces ("said—he")
        — house rule: em-dash with spaces ("said --- he")

[TERMINOLOGY] ru → en
  L156 ru "Pointer Architecture" → en "поинтерная архитектура"
        — DRIFT: terminology.md row #14 marks this term as
          "do not translate" — keep "Pointer Architecture" verbatim

[ANCHOR_QUOTES] ru → pt-br
  L201 ru "Время — это разница между двумя соседними решениями."
        (canonical RU, anchor-quotes.md §ch07-finale)
        pt-br "O tempo é o que sobra entre escolhas."
        — DRIFT: canonical PT-BR per anchor-quotes.md §ch07-finale must be
          "O tempo é a diferença entre duas escolhas vizinhas." — verbatim.

[NAMES_REALIA] ru → en
  L302 ru "Митя" (Дмитрий, diminutive)
        en "Mitia"
        — should be "Mitya" per names-and-realia.md §diminutives §row Дмитрий

[NO_SMOOTHING] ru → en
  L412 ru "900 миллисекунд"
        en "under a second"
        — smoothing forbidden: keep "900 milliseconds"
          (what-not-to-smooth.md §numbers)

[INFO] your-book/pt-br/chapters/ch07.md
  L99  — sentence count diverges from RU (4 vs 3) — within rhythm tolerance,
         author's call

=== SUMMARY ===
Files checked: 3 (ru, en, pt-br)
Findings:
  - typography:    2 (warning)
  - terminology:   1 (blocking)
  - anchor quote:  1 (blocking)
  - names/realia:  1 (blocking)
  - smoothing:     1 (blocking)
  - info:          1
Severity totals: 4 BLOCKING · 2 WARNING · 1 INFO
```

## Step 3. Understand what each finding type means

### [TYPOGRAPHY]

Per-language conventions for quotes, dashes, ellipsis, numerals. RU uses «ёлочки» for outer quotes, EN uses TeX-style `` ``...'' ``, PT-BR also uses `` ``...'' `` (house rule, see [typography.md](../../translation-sync/references/typography.md)). A `-` where `---` is expected is a typo, not a stylistic choice — usually **WARNING**.

### [TERMINOLOGY]

Canon terms (from your `references/terminology.md` registry — your own per project) must stay consistent across all three languages. Some are translated (canonical translation per row), some are marked "do not translate" (e.g. `Pointer Architecture` stays English everywhere). Drift is always **BLOCKING** — the canon is the canon.

### [ANCHOR_QUOTES]

Load-bearing quotations from the book whose translations have been hand-tuned and locked. Skill checks each anchor quote against its canonical row in `anchor-quotes.md`. Any deviation — "improvement", extender, paraphrase — is **BLOCKING**. The author has already decided on the canonical translation; the skill enforces it.

### [NAMES_REALIA]

- Real people: Latin script everywhere, including the Cyrillic source.
- Russian names: transliterated by your table (see [names-and-realia.md](../../translation-sync/references/names-and-realia.md)) in EN/PT-BR. Never the reverse direction (don't transcribe a real Latin-script name into Cyrillic).
- Patronymics: don't transliterate mechanically — usually drop in EN/PT-BR.
- Diminutives: each character has a full/short/affectionate form map; mixing `Dan` and `Daniel` for the same character mid-chapter is **WARNING**.
- Cultural realia (place names, institutions, brands): need a first-mention footnote per chapter. Missing footnote — **BLOCKING**.

### [NO_SMOOTHING]

Numbers, durations, exact years, street names, brand names stay literal. `900 ms` does not become `under a second`. `Yuzhnoye Butovo` does not become `a Moscow district`. `2007` does not become `the mid-2000s`. **BLOCKING** by default — these are concrete anchors that carry meaning. See [what-not-to-smooth.md](../../translation-sync/references/what-not-to-smooth.md) for the full list.

### [INFO]

Rhythm differences, idiom swaps (literal → equivalent), small sentence-count drift. EN is ~30% more compact than RU; PT-BR is mellower; differences are expected. Only flagged when the author should be aware, never as a blocker.

## Step 4. Fix what's BLOCKING

The skill **does not edit files**. You apply fixes by hand:

1. Open `your-book/en/chapters/ch07.md`
2. Revert L156: `поинтерная архитектура` → `Pointer Architecture`
3. Fix L302: `Mitia` → `Mitya`
4. Fix L412: restore `900 milliseconds`
5. Open `your-book/pt-br/chapters/ch07.md`
6. Revert L201 to canonical PT-BR

Then rerun:

```
/translation-sync chapter your-book ch07
```

Until only INFO is left (or zero findings).

## Step 5 (optional). Wire as a git pre-commit hook

`translation-sync` returns exit codes (`0` clean / `1` warning / `2` blocking) so it slots into a hook. The skill itself doesn't install the hook — see [pre-commit-hook.md](pre-commit-hook.md) for the general pattern; the same approach applies, just point the hook at `translation-sync` instead of `style-check`.

Quick variant in `.git/hooks/pre-commit`:

```bash
#!/usr/bin/env bash
# Run translation-sync on staged diff; abort on BLOCKING.
claude -p "/translation-sync staged" --output-format json | jq -e '.exit_code != 2' >/dev/null
exit $?
```

## Configuring the terminology canon for your book

Each project has its own canon. The default registry format lives in [translation-sync/references/terminology.md](../../translation-sync/references/terminology.md). Format (illustrative):

```markdown
## Canon terms

| RU | EN | PT-BR | Note |
|---|---|---|---|
| Pointer Architecture | Pointer Architecture | Pointer Architecture | DO_NOT_TRANSLATE |
| опорная конструкция | load-bearing structure | estrutura portante | |
| Кибернетический Гость | The Cybernetic Guest | O Hóspede Cibernético | |
```

When you introduce a new term in the source, add a row to your registry **before** translating it in EN/PT-BR. Otherwise the skill will flag a `[TERMINOLOGY]` finding the first time it shows up — and rightly so.

Same pattern for `anchor-quotes.md` (one section per chapter, one row per anchor quote with RU + EN + PT-BR canonical forms).

## Troubleshooting

### I'm only editing one language right now

Don't run `chapter` mode — it expects parity. Use `staged` instead:

```
/translation-sync staged
```

It detects each staged file's target language by path segment (`/ru/` / `/en/` / `/pt-br/`) and applies only the typography + terminology + smoothing + names checks. The cross-language anchor-quote and parity passes are skipped. If you only edited RU, the report will note "EN/PT-BR may be stale" — that's an informational nudge, not a blocker.

### I introduced a new term in this chapter

Add it to `references/terminology.md` **first**, then commit the chapter. If you commit in the other order, the skill will flag `[TERMINOLOGY] unknown term — not in registry` as `[INFO]` (the conservative default — never invents a ruling).

### Anchor quote drift is intentional — I want to update the canonical form

Update the row in `references/anchor-quotes.md` and commit that file alongside the chapters in the same commit. The skill will then accept the new canonical form. Don't try to override per-finding — the canon is the canon, change it deliberately.

### I have a name not in the transliteration table

Same pattern — add the row to `references/names-and-realia.md` with the canonical EN/PT-BR forms. Until you do, the skill will flag the name as `[INFO] unknown transliteration` (not a blocker — but you should canonize it).

### EN and PT-BR have different sentence counts than RU

Rhythm differences are expected (EN compact, PT-BR mellow). Only flagged as INFO. Don't try to enforce 1:1 sentence parity — that produces worse translations. Only flag if a concrete number or image was lost.

### Pre-commit hook is slow

`translation-sync` reads three files per chapter. On a typical chapter (8000 words × 3 = 24000 words) it's fast. If you have a large repo and the hook drags, scope the staged mode tighter — see [pre-commit-hook.md](pre-commit-hook.md) for `--name-only --diff-filter=AM` patterns.

## See also

- [pre-commit-hook.md](pre-commit-hook.md) — automate `translation-sync` on every commit
- [fiction-chapter.md](fiction-chapter.md) — chapter-level fiction workflow (where translation usually starts)
- [translation-sync/references/checklist.md](../../translation-sync/references/checklist.md) — the 15-point pre-commit checklist
- [docs/FAQ.md](../FAQ.md) — common questions
