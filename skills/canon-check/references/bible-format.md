# BIBLE FORMAT — typical structure of a story bible

Each book in a series typically holds its canon in a single document — usually `<book>/notes/story-bible.{md,tex,txt,rst}`. The skill reads it as plain text and locates sections by name.

**Before applying — verify against the actual file.** Project-specific bibles vary in section names and ordering. The structure below is a recommended template; adapt to your project. If a section is not found by its expected name, list the document's headings (`grep -n "^#\|^\\\\section\|^\\\\subsection" <bible>`) and pick the closest match.

---

## Recommended structure (for any single-book bible)

```
CANON OVERVIEW — what must not change in translations or sequels
  Names, ages, dates             ← life-facts, profession anchors
  Physical invariants            ← grips, counts, lags, gestures, named objects
  Anchor quotes (not to paraphrase) ← load-bearing lines, with cross-language translations
  Loaded gestures                ← action patterns with plot weight
  Subject-mechanics              ← in-universe terminology not to confuse
  Single-fact items              ← isolated canonical facts
  Fixed locations                ← named places, addresses, weight

MAIN CHARACTERS
  <Character A>, <Character B>, ...

SUPPORTING CHARACTERS
  <Character N>, <Character M>, ...
```

For a sequel or series book, also include:

```
INHERITED CANON FROM PARENT BOOK — details that cannot be re-projected back
  (typically a copy/excerpt from the parent book's "Canon overview" section)

SEQUEL-SPECIFIC CANON
  Names, ages, dates             ← new characters / shifted ages
  Artifacts                      ← objects introduced in this book
  (etc.)
```

For non-fiction with a biographical canon, structure is similar but the "characters" are real people and the "locations" carry weight from real biography:

```
BIOGRAPHICAL CANON
  Timeline                       ← life events, dates
  People and relationships       ← named individuals and their roles
  Loaded locations               ← real places with documentary weight
```

---

## Where the canon may live for non-fiction projects

Non-fiction biographical projects sometimes split canon across two sources:

1. The book's own `notes/story-bible.{md,tex,...}` — formal structure (timelines, named individuals, locations).
2. An external memory file or notes document the user maintains — extended biographical detail, character arcs, side memoirs.

For non-fiction canon-check, the skill should read **both sources** when available. The location and naming of any external memory file is project-specific; configure it in [routing.md](routing.md) and reference it explicitly.

When sources disagree, ask the user — never guess. External memory may be outdated; the bible may be incomplete.

---

## How to add new entries to the bible

**The skill does not do this.** Canon is updated by the user. But if asked "how do I add this?" — the following template applies (LaTeX shown; Markdown / plain-text equivalents work identically).

### Character

```latex
\subsection{<Name Surname>}
\textbf{<Name>.} <age>, <profession>, <location>.
<One or two additional lines of canon facts.>
```

Place in `Main characters` or `Supporting characters` by role weight.

### Artifact / physical invariant

In `Physical invariants`:

```latex
\item \textbf{<Artifact name>:} <concrete fact, count, gesture, location>.
```

Specifics — not "a few" but a number; not "a pause" but `900 ms`.

### Anchor quote

In `Anchor quotes (not to paraphrase)`:

```latex
\item \textbf{<<quote>>} (<character>, ch.~<N>) --- <what it locks>. EN: \textit{<<English>>}. PT-BR: \textit{<<Portuguese>>}.
```

The quote ships with its translations — on the next translation pass, the translator does not "improve by meaning".

### Location

In `Fixed locations`:

```latex
\item \textbf{<Place name>.} <Who lives / works / passes through; concrete details (address, floor, apt no. if any).>
```

---

## Versioning the bible

Header comment, e.g. `% v3.2 — synchronized with depth-pass of YYYY-MM-DD ...`. After any canon update, the user bumps the version manually. The skill does not touch the version, but may quote it in the report (for traceability: "bible v3.2 §3.2 says X").
