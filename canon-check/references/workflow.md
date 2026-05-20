# WORKFLOW — 3-step canon-check protocol

A three-step protocol, each step a concrete set of commands. The skill follows this protocol on every invocation.

---

## STEP 1 — Extract entities

Pull from the text under review (a chapter or staged diff) three classes of entity:

### 1a. Characters

Capitalized words (any script), ≥ 2 characters. Some hits will be false positives (sentence-starts, toponyms), so the second pass filters through the list of established names from the bible.

```bash
# All capitalized tokens from a chapter (works for Latin + Cyrillic; extend per script):
grep -oE '[A-Z][a-z]{2,}|[А-ЯЁ][а-яё]{2,}' <book>/<lang>/chapters/<chN>.{md,tex} | sort -u

# Cross-reference with known names from the bible (Markdown headings or LaTeX subsections):
grep -oE '^#+\s+[A-Z][^[:space:]]+|\\textbf\{[A-Z][^}]{1,40}\}' <book>/notes/story-bible.* | sort -u
```

Known names — compare the two lists; the leftover tokens are candidates for "new entity / silent canon".

### 1b. Artifacts

Project-specific dictionary. Built from the bible's `Physical invariants` / `Artifacts` section. Each book has its own. Typical artifacts you might track: heirlooms, instruments, weapons, named documents, signature objects, key-numbers ("the 11 cracks", "the 900 ms lag", "the 0.3 percent").

```bash
# Grep a specific artifact across all chapters:
grep -rn -i "<artifact-keyword>" <book>/<lang>/chapters/
```

**NB:** an artifact may appear in a parent book and its sequel with the SAME identity but DIFFERENT locations — relocations are explicitly canonized in the sequel and should NOT be retro-projected back into the parent book.

### 1c. Locations

From the bible's `Locations` / `Locations of weight` section. The base set varies per book; build the dictionary from each book's bible.

```bash
grep -rn "<location-1>\|<location-2>\|<location-3>" <book>/<lang>/chapters/
```

---

## STEP 2 — Trust the text, not memory

For each extracted entity:

### 2a. Read the bible entry

```bash
# Find the section about this entity in the bible:
grep -n -B 1 -A 10 "<entity>" <book>/notes/story-bible.*
```

Read the whole section, not just one line. The bible is the only source the user has explicitly marked as canon.

### 2b. Collect every appearance of the entity in other chapters

```bash
# All chapters of the same book:
grep -rn "<entity>" <book>/<lang>/chapters/

# If the book is a sequel — also search the parent book's chapters:
grep -rn "<entity>" <parent-book>/<lang>/chapters/ <sequel-book>/<lang>/chapters/
```

Read **every appearance**. Cite in the report only what you actually read. Do not cite from memory.

### 2c. Compare with the current text

Look for specific drift classes:

| Drift class | Example | Where to look in the bible |
| --- | --- | --- |
| **Age** | bible: Character is 7 in ch.13; text: 10 years 8 months | `Names, ages, dates` |
| **Physical invariant** | grip, lag, count (cracks, seconds, percentages) | `Physical invariants` |
| **Anchor quote** | locked short utterance, exact word count and punctuation | `Anchor quotes` |
| **Loaded gesture** | a documented action pattern (e.g. character always exits without saying goodbye) | `Loaded gestures` |
| **Artifact location** | artifact's canonical room / owner | `Locations` / `Artifacts` |
| **Artifact gender / pronoun** | canonically `she`, accidentally `it` / `he` | `Anchor quotes` |
| **Name continuity** | descriptor ("the redhead") vs locked full name | search across all chapters mandatory |

**Priority rule** (repeating — critical):

1. Published chapter = ground truth.
2. Story bible = ground truth, when it doesn't contradict a published chapter.
3. Model memory = NEVER ground truth. Grep first.

---

## STEP 3 — Flag, don't auto-write

If step 2 found:

- **A new entity** (name / artifact / location in the text, none in the bible) → **WARNING (silent canon)**. Do not auto-append to the bible. Tell the user: "entity X appears in ch07:142 and ch09:88 with no bible entry — add?"

- **A contradiction with the bible** → **BLOCKING**. Cite file:line + bible §X.Y + bible quote + text quote.

- **A contradiction between chapters, bible silent** → **WARNING (cross-chapter drift)**. Cite both lines + propose the user resolve.

- **A detail expansion** (new fact about a known entity, no contradiction) → **INFO (canon expansion)**. Optionally suggest adding to the bible.

**Never edit the chapter or the bible.** Only the report.

---

## Quick reference: standard one-liners

```bash
# All mentions of a character across the whole series:
grep -rn "<character>" <book>/<lang>/chapters/ <parent-book>/<lang>/chapters/

# All anchor quotes in the bible (for regression on translations or rewrites):
grep -n -A 1 "Anchor quotes" <book>/notes/story-bible.*

# All physical invariants — quick list of key numbers / gestures:
awk '/Physical invariants/,/^#|\\subsection/' <book>/notes/story-bible.*

# Find every chapter mentioning an artifact:
grep -rl "<artifact-keyword>" <book>/<lang>/chapters/
```
