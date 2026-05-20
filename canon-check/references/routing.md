# ROUTING — which canon source to apply

The skill picks the bible to apply based on the file path. The patterns below are **illustrative defaults**; adapt them to your project layout.

## Default routing (illustrative)

```
<book>/<lang>/chapters/*.{md,tex,txt,rst}
    → <book>/notes/story-bible.{md,tex,txt}

sequel-book/<lang>/chapters/*
    → sequel-book/notes/story-bible.*
    + parent-book/notes/story-bible.*
      (read the parent's `Inherited canon` / `Canon overview` section
       so the sequel respects the parent's locked details)

non-fiction-book/<lang>/chapters/*
    → non-fiction-book/notes/story-bible.*
    + (optional) any external biographical-canon files
      the user configures explicitly

*/notes/*.{md,tex,txt}
    → SKIP (these ARE the bibles, not chapters)

any other path
    → SKIP silently
```

---

## Why a sequel reads both bibles

If your project has multi-book continuity (a sequel inheriting characters and rules from a prior book), the sequel's bible typically has an `Inherited canon` section describing what cannot be retro-projected back. That section is the skeleton the sequel must respect: physical invariants of returning characters, anchor quotes, names/ages of key figures, locked locations.

Concretely — details a sequel typically **inherits** from its parent book:

- Established physical invariants of returning characters
- Established temporal anchors (a character's age in book A → reference point for book B's chronology)
- Anchor quotes locked in the parent book
- Locations with documented in-world history

Details that **change** in the sequel and become new canon:

- New names introduced for previously-unnamed objects
- Relocations explicitly written into the sequel's text
- New artifacts, new locations, new characters

When canon-checking a sequel chapter — both bibles open, both read. When canon-checking a parent-book chapter — only the parent's bible.

---

## Why non-fiction may read multiple sources

A biographical non-fiction project (memoir, autobiography, biographical essay collection) typically has its canon spread across:

1. The book's own `notes/story-bible.*` — structured canon (timeline, named people, weighted locations).
2. Optional external memory / notes documents the user maintains — extended biographical detail, per-character side documents.

Between them there may be discrepancies. **Rule:** when bible and external memory disagree — ask the user; do not guess. External memory may be outdated; the bible may be incomplete.

The location of any external biographical-canon source is project-specific. To wire it in, list the paths explicitly here (the skill doesn't auto-discover them).

---

## Configuring your own routing

The defaults above assume a `<book>/<lang>/chapters/` and `<book>/notes/story-bible.*` layout. If your project uses something different:

1. **Single-book project** — point the skill at your single bible: `<your-prose-dir>/* → <your-bible-path>`.
2. **Multi-book series** — list each book's chapter pattern alongside its bible. If books inherit canon, list the parent bible too.
3. **Non-fiction** — point at the structured bible and any external memory files the user maintains, with paths spelled out.
4. **Mixed-content repo (prose + code)** — make sure code paths are explicitly skipped (`SKIP`), and prose paths are explicit.

The routing can also be overridden per-invocation by the user (e.g. `canon-check chapter your-book ch07 --bible custom/path/bible.md`).

---

## Edge cases

- **Files in `arcs/` / `lore/` / `inserts/` / `dialogs/`** — these are prose inserts. If the context makes the target book clear — apply that book's bible. If not — SKIP with a warning.
- **Files in `preprints/`** — scientific texts, canon-check usually not needed. SKIP.
- **Chapters outside the source language directory** (translations: `en/`, `pt-br/`, …) — the canon is the same as for the source-language original. Canon-check applies, and **physical invariants + anchor quotes** are checked more strictly here: a translator must not smooth concrete specifics.
- **Code (`.py`, `.js`, `.ts`, etc.)** — SKIP silently.

---

## Short summary table

| Path pattern | Bible | Additional sources |
| --- | --- | --- |
| `<book>/<lang>/chapters/*` | `<book>/notes/story-bible.*` | — |
| `<sequel-book>/<lang>/chapters/*` | `<sequel-book>/notes/story-bible.*` | + parent-book bible (inherited canon) |
| `<non-fiction-book>/<lang>/chapters/*` | `<non-fiction-book>/notes/story-bible.*` | + (optional) external biographical canon files |
| `*/notes/*` | — (this IS the bible) | SKIP |
| `preprints/**`, code files, `.gitignore`, … | — | SKIP silently |
