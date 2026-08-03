# Sample Parity Report

> CALIBRATION SAMPLE — this is what the skill's report should look like.

Use this as the reference for tone, layout, and level of detail. Paths and line numbers below are fictitious but the failure modes are real.

```
=== translation-sync ===
Mode: chapter your-book ch11
Languages: ru en pt-br
Routing: typography (per-lang) + terminology + anchor-quotes + names/realia + no-smoothing

[TYPOGRAPHY] your-book/en/chapters/ch11.md
  L42 — straight quotes "voice modulator" in EN context
        → should be ``voice modulator'' (TeX outer)
        (typography.md §Quotes)
  L88 — em-dash without spaces: word---word
        → house rule: em-dash with spaces ( --- )
        (typography.md §Dashes)
  L142 — three literal dots "..."
        → should be `…` or `\dots`
        (typography.md §Ellipsis)

[TYPOGRAPHY] your-book/pt-br/chapters/ch11.md
  L67 — French «...» quotes in PT-BR context
        → house rule: TeX-style ``...'' (English style)
        (typography.md §Quotes)

[TERMINOLOGY] ru → en
  L120 ru "Proper Noun X" → en "Proper Noun X" — OK (do not translate)
  L156 ru "supporting structure" → en "support structure"
        → DRIFT from canon: terminology.md lists no entry for this term
        but the recurring concept is rendered as "load-bearing structure" elsewhere
        → recommend: standardize and register
        (terminology.md §Book-specific — open candidate)
  L201 ru "flow term" → en "stream"
        → DRIFT: canonical is "flow" or "current" (open question)
        chapter 11 currently uses "stream" — neither option
        (terminology.md §Shared concepts)
  L312 ru "integrator concept" → en "integrator agent"
        → DRIFT: canonical EN is "integrator" (one word, no suffix)
        (terminology.md §Shared concepts)

[TERMINOLOGY] ru → pt-br
  L156 ru "supporting structure" → pt-br "estrutura de apoio"
        → DRIFT: see EN finding above; PT-BR likewise unregistered
  L201 ru "flow term" → pt-br "fluxo"
        → OK (canonical)

[ANCHOR_QUOTES] ru → en
  L302 ru "Anchor quote — Character A, ch.11" (canonical short form)
        en "The expanded English with an added connective and extra clause"
        → DRIFT from canonical: locked EN form is shorter and punchier
        word count and punctuation must match (anchor-quotes.md §Book A)
  L315 ru "Anchor quote — Character B" (canonical, terse)
        en "I am an analyst. It is the same thing, only without funding and with a pistol"
        → DRIFT from canonical contracted form; verbatim match required
        (anchor-quotes.md §Book A)

[ANCHOR_QUOTES] ru → pt-br
  L302 ru "Anchor quote — Character A, ch.11"
        pt-br "Locked PT-BR canonical form"
        → OK (canonical)

[NAMES_REALIA] ru → en
  L201 ru "diminutive form of Character C" → en "incorrect transliteration"
        → WRONG: canonical EN form per names-and-realia.md §diminutives
        (names-and-realia.md §Fictional characters)
  L256 ru "Real Person" → en "Real Person" — OK
  L289 ru "Local Place" → en "Local Place"
        → first mention in this chapter has NO footnote
        → required: short explanatory footnote (e.g. "Local Place, brief description")
        (names-and-realia.md §Cultural realia)
  L401 ru "Formal patronymic address from secretary"
        en "literal patronymic transliteration"
        → WARNING: mechanical patronymic transliteration in non-document context
        consider: "Mr Surname" or short form
        (names-and-realia.md §Patronymics)

[NAMES_REALIA] ru → pt-br
  L289 ru "Local Place" → pt-br "Local Place"
        → first mention has no footnote (same issue as EN)

[NO_SMOOTHING] ru → en
  L412 ru "900 milliseconds" → en "under a second"
        → BLOCKING: smoothing forbidden
        canon: "900 milliseconds"
        (what-not-to-smooth.md §Numbers)
  L445 ru "17 days" → en "a couple of weeks"
        → BLOCKING: smoothing forbidden
        canon: "17 days"
        (what-not-to-smooth.md §Numbers)
  L478 ru "BrandName" → en "a regional bank"
        → BLOCKING: brand name replaced with generic
        canon: "BrandName" (kept literal)
        (what-not-to-smooth.md §Brand names)

[NO_SMOOTHING] ru → pt-br
  L412 ru "900 milliseconds" → pt-br "900 milissegundos" — OK
  L445 ru "17 days" → pt-br "17 dias" — OK
  L478 ru "BrandName" → pt-br "BrandName" — OK

=== SUMMARY ===
Files checked: 3 (your-book: ru ch11.md, en ch11.md, pt-br ch11.md)
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
  - Add the missing first-mention footnotes for the local-place name in EN and PT-BR.
  - Standardize "supporting structure" — propose adding to terminology.md.
  - Resolve "flow term" → flow / current open question, then re-sync EN ch11.

Exit code (if invoked as pre-commit hook): 2 (BLOCKING present)
```

---

## How to read this report

- **Sections** correspond to the six pipeline stages: typography, terminology, anchor-quotes, names/realia, no-smoothing.
- **`ru → en` / `ru → pt-br` headers** group findings by source-to-target language pair.
- **Line numbers** are from the target-language file (where the drift was found), not the source.
- **Each finding** includes: line, source snippet, target snippet, the drift diagnosis, and the reference file + section that owns the rule.
- **`OK` entries** are shown selectively — only where they help confirm that a checked rule passed (useful for the user to see that the pipeline did consider that line).
- **`SUMMARY`** counts findings by category and severity, then proposes an action order: smoothing first (mistranslation), then anchors (canon), then footnotes (mechanical), then registry updates (housekeeping).
