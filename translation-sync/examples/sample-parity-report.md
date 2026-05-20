# Sample Parity Report

> CALIBRATION SAMPLE — this is what the skill's report should look like.

Use this as the reference for tone, layout, and level of detail. Paths and line numbers below are fictitious but the failure modes are real.

```
=== translation-sync ===
Mode: chapter god-academy ch11
Languages: ru en pt-br
Routing: typography (per-lang) + terminology + anchor-quotes + names/realia + no-smoothing

[TYPOGRAPHY] books/god-academy/en/chapters/ch11.tex
  L42 — straight quotes "voice modulator" in EN context
        → should be ``voice modulator'' (TeX outer)
        (typography.md §Quotes)
  L88 — em-dash without spaces: word---word
        → house rule: em-dash with spaces ( --- )
        (typography.md §Dashes)
  L142 — three literal dots "..." 
        → should be `…` or `\dots`
        (typography.md §Ellipsis)

[TYPOGRAPHY] books/god-academy/pt-br/chapters/ch11.tex
  L67 — French «...» quotes in PT-BR context
        → house rule: TeX-style ``...'' (English style)
        (typography.md §Quotes)

[TERMINOLOGY] ru → en
  L120 ru "Pointer Architecture" → en "Pointer Architecture" — OK (do not translate)
  L156 ru "опорная структура" → en "support structure"
        → DRIFT from canon: terminology.md lists no entry for "опорная структура"
        but the recurring HC term is rendered as "load-bearing structure" elsewhere
        → recommend: standardize and register
        (terminology.md §HC specific — open candidate)
  L201 ru "поток 118" → en "stream 118"
        → DRIFT: canonical is "flow 118" or "current 118" (open question)
        chapter 11 currently uses "stream" — neither option
        (terminology.md §Reality stack)
  L312 ru "интегратор" → en "integrator agent"
        → DRIFT: canonical EN is "integrator" (one word, no suffix)
        (terminology.md §Reality stack)

[TERMINOLOGY] ru → pt-br
  L156 ru "опорная структура" → pt-br "estrutura de apoio"
        → DRIFT: see EN finding above; PT-BR likewise unregistered
  L201 ru "поток 118" → pt-br "fluxo 118"
        → OK (canonical)

[ANCHOR_QUOTES] ru → en
  L302 ru "Программа — одна. Режим — выбираете вы" (Dan, ch.11)
        en "The program is one, and the mode is yours to choose"
        → DRIFT from canonical: "The program is one. The mode is your choice"
        word count and punctuation must match (anchor-quotes.md АБ)
  L315 ru "Я — аналитик. Это то же самое, только без гранта и с пистолетом" (Artyom)
        en "I am an analyst. It's the same thing, only without funding and with a pistol"
        → DRIFT from canonical: "I'm an analyst. Same thing, just without the grant and with a gun"
        (anchor-quotes.md АБ)

[ANCHOR_QUOTES] ru → pt-br
  L302 ru "Программа — одна. Режим — выбираете вы"
        pt-br "O programa é um. O modo, você escolhe"
        → OK (canonical)

[NAMES_REALIA] ru → en
  L201 ru "Серёжа" → en "Sergei"
        → WRONG: canonical EN is "Seryozha"
        (names-and-realia.md §Russian fictional characters)
  L256 ru "Sam Battle" → en "Sam Battle" — OK
  L289 ru "Лубянка" → en "Lubyanka"
        → first mention in this chapter has NO footnote
        → required: "Lubyanka, FSB headquarters in central Moscow"
        (names-and-realia.md §Cultural realia)
  L401 ru "Артём Сергеевич" (formal address from secretary)
        en "Artyom Sergeyevich"
        → WARNING: mechanical patronymic transliteration in non-document context
        consider: "Mr Val" or "Artyom"
        (names-and-realia.md §Patronymics)

[NAMES_REALIA] ru → pt-br
  L289 ru "Лубянка" → pt-br "Lubyanka"
        → first mention has no footnote (same issue as EN)

[NO_SMOOTHING] ru → en
  L412 ru "900 миллисекунд" → en "under a second"
        → BLOCKING: smoothing forbidden
        canon: "900 milliseconds"
        (what-not-to-smooth.md §Numbers)
  L445 ru "17 дней" → en "a couple of weeks"
        → BLOCKING: smoothing forbidden
        canon: "17 days"
        (what-not-to-smooth.md §Numbers)
  L478 ru "Тинькофф" → en "a Russian bank"
        → BLOCKING: brand name replaced with generic
        canon: "Tinkoff"
        (what-not-to-smooth.md §Brand names)

[NO_SMOOTHING] ru → pt-br
  L412 ru "900 миллисекунд" → pt-br "900 milissegundos" — OK
  L445 ru "17 дней" → pt-br "17 dias" — OK
  L478 ru "Тинькофф" → pt-br "Tinkoff" — OK

=== SUMMARY ===
Files checked: 3 (god-academy: ru ch11.tex, en ch11.tex, pt-br ch11.tex)
Findings:
  - typography:    4 (4 warning)
  - terminology:   4 (3 blocking, 1 warning)
  - anchor quote:  2 (2 blocking)
  - names/realia:  4 (2 blocking, 2 warning)
  - smoothing:     3 (3 blocking — all in EN)

Severity totals:
  BLOCKING: 10
  WARNING:   7
  INFO:      0

Recommended action:
  - Fix the three EN smoothing failures FIRST (these are pure mistranslation).
  - Restore the two anchor quotes to canonical form (word-for-word).
  - Add the missing Lubyanka first-mention footnotes in EN and PT-BR.
  - Standardize "опорная структура" — propose adding to terminology.md.
  - Resolve "поток 118" → flow / current open question, then re-sync EN ch11.

Exit code (if invoked as pre-commit hook): 2 (BLOCKING present)
```

---

## How to read this report

- **Sections** correspond to the six pipeline stages: typography, terminology, anchor-quotes, names/realia, no-smoothing.
- **`ru → en` / `ru → pt-br` headers** group findings by source-to-target language pair.
- **Line numbers** are from the target-language file (where the drift was found), not the RU source.
- **Each finding** includes: line, source snippet, target snippet, the drift diagnosis, and the reference file + section that owns the rule.
- **`OK` entries** are shown selectively — only where they help confirm that a checked rule passed (useful for the author to see that the pipeline did consider that line).
- **`SUMMARY`** counts findings by category and severity, then proposes an action order: smoothing first (mistranslation), then anchors (canon), then footnotes (mechanical), then registry updates (housekeeping).
