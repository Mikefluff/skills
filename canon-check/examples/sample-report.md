# Sample Report

> **CALIBRATION SAMPLE** — what the skill's report looks like. Do NOT use as a real audit.

```
=== canon-check ===
Mode: chapter your-book ch07
Bible: your-book/notes/story-bible.md
Bible version: v3.2
Entities extracted: 14 (8 characters, 4 artifacts, 2 locations)

----------------------------------------------------------------
[BLOCKING] your-book/ru/chapters/ch07.md:142
  Entity: Character A (character)
  Class: physical_invariant_drift

  In this chapter:
    L142: «Character A took the cup left-handed, fingers wrapped from below»

  Bible §3.2 (Physical invariants):
    «Grip: thumb and index on top, the remaining three below.
     Identical for the cup (ch.~21) and the child's slippers (Character B's flashback).
     This is a signature invariant, not a descriptive detail.»

  Other chapters confirm the canonical grip:
    ch02.md:88   — «two fingers on top, three below»
    ch04.md:201  — «the habitual gesture, thumb and index on top»
    ch21.md:55   — original scene, baseline for the grip

  Fix (decide):
    A) change «left-handed ... from below» → canonical grip
    B) if this is deliberately new — update bible §3.2 and mark
       as an invariant revision (but this is locked canon, careful)

----------------------------------------------------------------
[BLOCKING] your-book/ru/chapters/ch07.md:201
  Entity: redhead figure (character)
  Class: generic_vs_canonical_name_drift

  In this chapter:
    L201: «a red-haired figure appeared, earring glinting»

  Bible: NO entry under «redhead», «red-haired», «earring figure»

  Other chapters (canonical name established):
    interlude10.md:88  — «Character C / full proper name / nickname»
    interlude10.md:140 — «red-haired, with earring, amber eyes»
    ch05.md:201        — «the woman with amber eyes»

  Note: this descriptor refers to a character already named in
  the project's other chapters. Reusing the generic descriptor here
  breaks continuity.
  ASK USER: canonize the descriptor → full name binding, or
  remove the descriptor from this chapter.

  Fix (decide):
    A) add a bible entry binding the descriptor «red-haired figure» to
       the established full name (with traits: earring, amber eyes, biography)
    B) remove the mention from ch07 if accidental cross-pollination

----------------------------------------------------------------
[WARNING] your-book/ru/chapters/ch07.md:256
  Entity: heirloom object (artifact)
  Class: cross_chapter_drift

  Bible §3.2 (Locations):
    «Character X's flat. Black stone heirloom on the shelf.»

  This chapter:
    L256: «heirloom on the table» (location within the flat is consistent,
           but the object moved from shelf to table)

  Other chapters:
    ch04.md:88  — «on the shelf, black, stone»
    ch11.md:34  — «on the shelf, next to the lamp»

  Class: micro-drift (shelf → table). Possibly deliberate
  movement within the same room, possibly accidental.

  Fix (decide):
    A) if deliberate (Character X moved it for this scene) — add to the bible
       a clarification «on the shelf (default) / on the table (only in ch07)»
    B) if accidental — correct to «on the shelf»

----------------------------------------------------------------
[INFO] your-book/ru/chapters/ch07.md:312
  Entity: Character D's flat (location)
  Class: canon_expansion

  Bible §3.2 (Locations):
    «Character D's flat. One-room, seventh floor. Bell tower with a historical plaque.
     Tram line 15 discontinued in 2021.»

  This chapter:
    L312: «the lift smelled of warm cable, the seventh-floor button stuck»

  This is canon expansion (new detail, not contradiction).

  Fix (optional):
    add to bible §3.2: «Lift: seventh-floor button sticks, smells
    of warm cable» — if the detail will recur.

----------------------------------------------------------------

=== SUMMARY ===
Files checked:     1
Entities checked:  14
  - 8 characters (5 with bible entries, 1 missing — «redhead figure»)
  - 4 artifacts  (3 with bible entries, 1 silent — research lab)
  - 2 locations  (2/2 with bible entries)

Findings:
  - BLOCKING: 2 (physical invariant drift, generic-vs-canonical name)
  - WARNING:  1 (cross-chapter micro-drift)
  - INFO:     1 (canon expansion)

Bible coverage: 13/14 entities have entries (missing: redhead figure)

Exit code (pre-commit): 2  (BLOCKING present → would abort commit)
```
