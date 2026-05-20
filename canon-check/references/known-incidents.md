# KNOWN INCIDENT CATEGORIES — the canon-break patterns this skill is designed to catch

Each category: **what tends to break / what the canon usually fixes / how to detect it programmatically**. The skill cites these categories as calibration.

These five categories are the recurring shapes of canon failure across long-form fiction projects. Replace any project-specific entity name in the examples with your own — the **detection pattern** is what matters.

---

## CATEGORY 1 — Physical invariant drift

**What tends to break.** A character has a documented physical invariant — handedness, a specific grip, a tic, a count of something (cracks in a window, beats in a knock, eye colour, scar position). On a rewrite of a later chapter, the writer reaches for the gesture from memory and inverts it. Example shape: bible says "Character A is left-handed and grips with thumb + index on top, three fingers below"; chapter 07 has them take the cup right-handed, palm-up.

**What the canon usually fixes.** Concrete physical specifics — handedness, exact grip, a counted number tied to identity (e.g. "always carries seven coins"), a recurring gesture that recurs across scenes. The bible's `Physical invariants` section is the home for these.

**Detection class.** **Physical invariant drift** — the text references the character performing an action (takes, holds, picks up, clenches, embraces) but doesn't match the locked gesture.

**How to detect:**
```bash
# All mentions of the character in action context:
grep -n -B 1 -A 1 -E "<character-name>" <book>/<lang>/chapters/*.{md,tex} | \
  grep -iE "(took|held|picked|clutched|grasped|hand|grip|fist|palm)"

# Cross-reference with the invariant in the bible:
grep -n -A 1 "<invariant-name>" <book>/notes/story-bible.*
```

Severity: **BLOCKING.**

---

## CATEGORY 2 — Artifact location / pronoun / owner drift

**What tends to break.** A named artifact (an object with canon weight — an heirloom, an instrument, a stored item) accidentally moves between scenes: changes room, changes owner, changes grammatical gender / pronoun. Example shape: in Book A the artifact lives on a shelf in Character X's flat; on a rewrite in Book B the artifact relocates to "Character Y's room" with no in-scene transit. Or: the artifact is canonically referred to as `she` in established translations, and a later pass uses `it` / `he`.

**What the canon usually fixes.** Per-artifact entry naming: owner, location, grammatical gender (matters for translations), provenance, who has touched it. The bible's `Artifacts` / `Physical invariants` / `Locations` sections hold these.

**Detection class.** **Artifact location / pronoun drift** — the artifact changes owner, location, or pronoun between chapters or books.

**How to detect:**
```bash
# All mentions of the artifact in location context:
grep -rn -i -B 1 -A 1 "<artifact-name>" <book>/<lang>/chapters/

# Pronoun usage near the artifact name:
grep -rn -E "<artifact-name>.{0,80}(he |his |him |she |her |it |its )" <book>/<lang>/chapters/
```

Severity: **BLOCKING.**

---

## CATEGORY 3 — Generic-vs-canonical-name drift

**What tends to break.** A recurring character is established by full proper name in one chapter (with epithets, biography, paragraph of canonization), then re-appears in a later chapter under a generic descriptor — "the redhead", "the friend from out of town", "the second son", "the wife". The text loses continuity because the reader (and the search) can't link the two appearances.

**What the canon usually fixes.** A rule: generic-role descriptors ("the redhead", "the friend from X", "the second son", "the wife") almost always refer to a person who has **already been named in the text** elsewhere. The full name is the canon; the descriptor is a callback.

**Detection class.** **Generic-vs-canonical-name drift** — the text uses a descriptor instead of the established proper name.

**How to detect:**

```bash
# Descriptors by trait / role:
grep -rn -iE "(redhead|friend from|second son|wife|husband|the old man|the youngster)" <book>/<lang>/chapters/

# In parallel — search for full names in earlier chapters / interludes / memory:
grep -rn -iE "<known-full-name-or-pattern>" <book>/<lang>/chapters/
```

Severity: **BLOCKING** (this is not silent canon — it's a contradiction with an established proper name).

---

## CATEGORY 4 — Bible-prescribed count / age / temporal mismatch

**What tends to break.** The bible prescribes a count, age, or sequence — "Character laughs twice in this chapter", "Character is 7 when X happens, 17 when Y happens", "the event has three phases" — and the text doesn't match. Two sub-shapes:

- **Count mismatch.** Bible says 2 laughs in ch05; text contains 1. The first laugh is missing or got cut in editing.
- **Age / temporal drift.** Bible says Character is `7 in chapter 13`; text says `10 years and 8 months, over six phases`. Whole-cloth divergence.

**What the canon usually fixes.** Numeric and structural prescriptions — counts of events per chapter, character ages at specific scenes, phase counts in arcs, exact years of past events, lag values, durations.

**Detection class.** **Bible-prescribed count / temporal mismatch** — bible says N (occurrences / age / phases / years), text says M.

**How to detect:**

```bash
# Find numeric prescriptions in the bible:
grep -n -E "(two|three|four|five|N|[0-9]+) (laugh|appear|times|gesture|phase|year)" <book>/notes/story-bible.*

# Count event occurrences in a specific chapter:
grep -cn "<event-keyword>" <book>/<lang>/chapters/<chN>.{md,tex}

# Find all age mentions for a character in bible vs text:
grep -n -E "<character>.{0,30}(years old|year|age)" <book>/notes/story-bible.*
grep -rn -E "<character>.{0,80}(years old|year|age|months)" <book>/<lang>/chapters/
```

Severity: **WARNING** for count mismatch (the bible doesn't contradict itself; the text just doesn't fulfil the prescription) → **BLOCKING** for age / temporal contradiction (clear text-vs-bible mismatch).

---

## CATEGORY 5 — Silent canon (entity recurs without bible entry)

**What tends to break.** An entity (character, artifact, location) appears across two or more chapters with consistent attributes, but the bible has no entry for it. The detail accumulates in the text without ever being canonized — and on the next rewrite, someone re-invents it from scratch and breaks accidental coherence.

**What the canon usually fixes.** Anything that recurs ≥ 2 times in the prose should have at least a one-line bible entry. The bible doesn't store everything; it stores everything that recurs.

**Detection class.** **Silent canon** — entity present in text ≥ 2 times, no bible entry.

**How to detect:**

```bash
# Collect all capitalized tokens from chapters (rough — produces a candidate list):
grep -rhoE '[A-Z][a-z]{2,}|[А-ЯЁ][а-яё]{2,}' <book>/<lang>/chapters/ | sort | uniq -c | sort -rn | head -50

# For each candidate, check whether it has a bible entry:
grep -n "<candidate>" <book>/notes/story-bible.* || echo "MISSING: <candidate>"
```

Severity: **WARNING (silent canon)** — recommend adding to the bible.

---

## SUMMARY — detection classes

| Class | Trigger grep | Severity |
| --- | --- | --- |
| Physical invariant drift | character + action verb + cross-check `Physical invariants` | BLOCKING |
| Artifact location / pronoun | artifact + location / pronoun proximity | BLOCKING |
| Generic-vs-canonical-name | descriptor ("the redhead", "the friend from …") + search for full names | BLOCKING |
| Bible-prescribed count mismatch | bible says N, text gives M | WARNING |
| Age / temporal drift | character age in bible vs in scene | BLOCKING |
| Silent canon | entity ≥ 2 occurrences, no bible entry | WARNING |
| Canon expansion | new fact about a known entity, no contradiction | INFO |
