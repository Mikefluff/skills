# SEVERITY LEVELS

Categories ranked by severity:

**BLOCKING** — must fix before committing:
- `CANON_DRIFT` (mismatch with a story bible — applies when working on a fiction series with a documented canon)
- `UNCITED_CLAIM` (scientific claim without a source in non-fiction)
- `FABRICATED_SOURCE` (detector suspects a fabricated source: unknown journal + not found on arXiv/Crossref)
- `BROKEN_MARKUP` (syntactic error in `.tex` / `.md` / `.rst` that breaks the build or renderer)

**WARNING** — worth a look:
- Every writer L1 category (neuro-slop) with >2 matches
- `STACCATO`, `DOUBLE_NEG`, `INVERSION`, `INCOMPLETE_PREDICATE` (writer L2)
- `TAVTOLOGY`, `META_REF`, `ANGLICISM` (prose-edit)
- `ACADEMIC_PATHOS`, `LECTURER_TONE`, `VIRAL_FORMAT` (essay-write)

**INFO** — author's discretion:
- Writer L1 with a single match (often organic)
- `METAPHOR_OVERLOAD` (above the recommended count, not critical)
- `STYLE_DRIFT` (mild signs the voice is slipping)

---

## Post-rewrite signatures (what to look for AFTER your own rewrite)

Concrete patterns that recur in machine-assisted rewrites. Run as a post-audit AFTER applying a writer-pass, before committing. The same handful of errors keep showing up in model-edits, so each rewrite has to be re-checked against this short list.

### Punch-line duplicates

```
Truck.\nTruck
```

A short phrase repeated across a `\n` (e.g. `"Truck.\nTruck went past in silence"`) → your own edit glued two variants together and left both. Re-read neighbouring lines, remove the duplicate.

### Calque "not X, but Y" at line start

```
^[^,]*not [^,]+, but
```

`"not X, but Y"` at line start — a calque that revives even after an explicit ban. Rewrite as the positive `"Y, not X"` or split into two sentences.

### Adverb stumps without a noun

```
(just|over|without)\s+—\s*$
```

`"just —"`, `"over —"` at line end → the editor inserted a dash and never finished. Complete the complement or remove the dash.

### Suspicious N+Gen inversions

```
[a-z]+a\s+[a-z]+
```

Possible inversion N+Gen → Gen+N — `"engineer's son"` rendered as `"the son of an engineer"` (or the reverse, depending on house style) (see writer/references/structural-prose.md, section "N+Gen → Gen+N"). Coarse heuristic, lots of false positives — check each hit visually. Especially watch for it in short dialogue replies.
