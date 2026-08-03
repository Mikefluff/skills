# OUTPUT FORMAT

Structured report, grouped by file, then by violation cluster.

```
=== style-check ===
Mode: staged | last | range <a>..<b> | file <path>
Routing: writer + prose-edit | writer + essay-write | writer only

[FILE 1] fiction/chapter05.md
  Routing: writer + prose-edit
  ----
  L142 STACCATO  «He did so. He walked. He fell silent.»
                 → 3+ one-clause sentences in a row (writer L2)

  L156 NEURAL_METAPHOR  «the theory is cracking at the seams»
                        → neuro-slop (writer L1 cat 22). Replace: «the theory does not hold»

  L201 TAVTOLOGY  «an open opening»
                  → root repeats inside root (prose-edit cleanness #5)

  L256 CANON_DRIFT  reference to Character A's grip — cross-check against your story bible
                    (prose-edit canon check)

  L289 META_REF  «as in chapter 4 of the previous book»
                 → references to the author's own books in narrator voice are banned

  L312 ANGLICISM  «post-door»
                  → Latin script inside an otherwise non-English authorial voice

[FILE 2] essays/draft03.md
  Routing: writer + essay-write
  ----
  L42 UNCITED_CLAIM  «studies show that»
                     → no concrete source (essay-write sourcing)

  L88 ACADEMIC_PATHOS  «let us consider the following aspect»
                       → lecturer tone (essay-write bans)

  L115 METAPHOR_OVERLOAD  7 similes in one chapter (recommended 3-5)

  L142 VIRAL_FORMAT  numbered list «1. / 2. / 3.»
                     → viral device inside non-fiction

=== SUMMARY ===
Files checked: 2
Total violations:
  - writer L1 (20-category regex): 1
  - writer L2 (structural): 2
  - prose-edit fiction layer: 3
  - essay-write non-fiction layer: 4

Severity:
  - BLOCKING (must fix before commit): canon drift, uncited claim
  - WARNING (worth a look): staccato, neural metaphor, tautology, meta-ref, anglicism, academic pathos, viral format
  - INFO (author's discretion): metaphor overload
```
