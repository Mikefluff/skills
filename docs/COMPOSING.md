# Composing skills

The 9 skills aren't independent — they're stacked. `writer` is the foundation; everything else either wraps it, lints what it produces, or operates on the collection itself. Knowing which to invoke (and which leaves the others alone) saves a lot of churn.

## Dependency graph

```
                                   ┌──────────────┐
                                   │    writer    │  base (clean prose engine)
                                   └──────┬───────┘
              ┌──────────────────────────┼──────────────────────────┐
              │                          │                          │
       ┌──────▼──────┐            ┌──────▼──────┐            ┌──────▼──────┐
       │  viral-text │            │ prose-edit  │            │ essay-write │   wrappers
       │  (RU / EN)  │            │  (fiction)  │            │ (non-fic)   │
       └──────┬──────┘            └──────┬──────┘            └──────┬──────┘
              │                          │                          │
              │                          └──────────┬───────────────┘
              │                                     │
              │                          ┌──────────▼──────────┐
              │                          │ pelevin-digression  │   optional voice layer
              │                          │  (one passage at    │   composes with prose-edit
              │                          │   a time, by ask)   │   or essay-write
              │                          └─────────────────────┘
              │
              │      ┌──────────────────────────────────────────────────┐
              │      │                                                  │
       ┌──────▼──────▼──────┐    ┌─────────────────────┐    ┌──────────▼──────────┐
       │    style-check     │    │   translation-sync  │    │     canon-check     │   linters
       │  (any text file)   │    │   (RU↔EN↔PT-BR)    │    │  (story-bible audit)│   (read-only)
       └────────────────────┘    └─────────────────────┘    └─────────────────────┘

                                    ┌─────────────────┐
                                    │  skills-update  │   meta — manages the collection itself
                                    └─────────────────┘
```

**Dependencies declared in `skills.json`:**

| Skill | Depends on |
|---|---|
| `writer` | — |
| `viral-text` | `writer` |
| `prose-edit` | `writer` |
| `essay-write` | `writer` |
| `style-check` | `writer`, `prose-edit`, `essay-write` |
| `translation-sync` | — |
| `canon-check` | — |
| `pelevin-digression` | `writer`, `prose-edit`, `essay-write` |
| `skills-update` | — |

`viral-text`, `prose-edit`, `essay-write`, and `pelevin-digression` always end their pipeline with a `writer` pass — that's a hard rule, not a suggestion. The linters (`style-check`, `translation-sync`, `canon-check`) don't *invoke* their dependencies — they reference the same rule files for routing.

---

## When to invoke which

### "I want to write a viral Telegram post"
→ `/viral-text` directly. It handles hook → 5 points → micro-conclusion → CTA, then runs `writer` cleanup internally.

### "I'm rewriting a chapter of АБ / ЭА"
→ `/prose-edit` on the file or fragment. It applies fiction voice rules, runs canon-check internally if you point at an ЭА chapter, then runs `writer` cleanup.

### "I'm drafting a non-fiction chapter of НК / a longread"
→ `/essay-write`. It enforces long subordinate sentences, source-backed claims, V/H/P hypothesis markers, then runs `writer` cleanup.

### "I want a Pelevin-style digression in the middle of a scene"
→ `/pelevin-digression at <file:line>`. It writes the digression in voice, then chains to `prose-edit` (if you're in a fiction chapter) or `essay-write` (non-fic), which themselves chain to `writer`.

**Don't invoke `pelevin-digression` for a whole chapter.** Voice fatigue kills the effect. It's a single-passage tool by design.

### "I want to lint my draft before I commit"
→ `/style-check staged` (or `style-check chapter <book> <chN>`). It auto-routes by file path:
- `books/god-academy/**/chapters/*.tex` → fiction lint (writer + prose-edit rules)
- `books/era-arkhitektorov/**/chapters/*.tex` → fiction lint + canon-check trigger
- `books/heavenly-code/**/chapters/*.tex` → non-fiction lint (writer + essay-write rules)
- anything else → writer-only lint

### "I'm about to commit a translated chapter"
→ `/translation-sync chapter <book> <chN>`. Read-only — produces a parity report across RU / EN / PT-BR versions. Fix what BLOCKING says before committing.

### "I'm worried I broke canon"
→ `/canon-check chapter <book> <chN>` before editing. Or `/canon-check entity <book> <name>` to see every appearance of a specific character / artifact / location in the corpus.

### "I want a clean editor pass on a draft without all the wrappers"
→ `/writer clean` directly with the text. Bypasses voice-specific rules — useful for non-book prose (chat messages, emails, README files).

### "I want to know if there's a new version"
→ `/skills-update`. Or rely on the status-line banner if you've installed the hook (`bash scripts/install-hook.sh`).

---

## Common composition patterns

### Pattern: draft → wrapper → lint → commit

```
draft.md → /prose-edit rewrite draft.md → /style-check file draft.md → git commit
```

The wrapper does the voice work. `style-check` is a safety net before committing — read-only, doesn't undo what the wrapper did.

### Pattern: scene + digression

```
chapter has a flat exposition paragraph at line 142
  → /pelevin-digression at ch05.tex:142 "брендовая социология двухтысячных"
    → produces voice-shaped passage
    → chains to /prose-edit (canon-check + fiction voice)
    → chains to /writer (final cleanup)
  → diff shown to author
  → author commits
```

### Pattern: parallel translations

```
finish RU chapter
  → /translation-sync chapter god-academy ch07 (parity report)
  → fix terminology drift in en/ch07.tex per report
  → /style-check file en/ch07.tex
  → commit all 3 files together
```

### Pattern: introducing a new entity

```
about to add a new character to ch08 of EA
  → /canon-check entity era-arkhitektorov "новое-имя"  (probably reports "no bible entry")
  → write the chapter
  → /canon-check chapter era-arkhitektorov ch08  (now flags WARNING: new entity)
  → manually add bible entry per the WARNING
  → re-run /canon-check (now INFO: confirmed)
  → commit
```

---

## Anti-patterns (don't do this)

### Skipping writer

You CAN'T invoke `viral-text` / `prose-edit` / `essay-write` and tell them "skip the writer pass". The 4-layer cleaning pass is the contract — output is supposed to be ready-to-ship. If you find yourself wanting to skip it, you probably want `writer clean` instead.

### Chaining linters

`style-check` already incorporates writer / prose-edit / essay-write *rules*. Don't chain `prose-edit lint` and `style-check` and `writer lint` separately — that's just the same work three times. Use `style-check` alone.

### Applying pelevin-digression to a whole chapter

The voice is designed for 1-3 paragraph inserts. Apply chapter-wide and you get a parody of Pelevin. If you want full-chapter Pelevin voice, that's a `prose-edit` job with a voice flag — not currently supported. File an issue if you need it.

### Editing the story-bible from a chapter PR

`canon-check` flags drift; the author decides what's canonical. Don't edit `story-bible.tex` and a chapter in the same commit — the bible should change deliberately, with its own commit, after the chapter is settled.

### Running translation-sync before all three languages exist

It assumes parity. Use it when you've just touched all three. For "I'm only editing RU right now", just use `style-check`.

---

## Quick reference

| You want to … | Invoke | Hard-deps |
|---|---|---|
| Write a viral RU/EN post | `/viral-text` | writer |
| Edit a fiction chapter | `/prose-edit` | writer |
| Write / edit a non-fiction chapter | `/essay-write` | writer |
| Insert a Pelevin-voice digression | `/pelevin-digression at <file:line>` | writer + prose-edit OR essay-write |
| Lint a draft pre-commit | `/style-check` | (reads writer + prose-edit + essay-write rules) |
| Check translation parity | `/translation-sync` | — |
| Verify story-bible consistency | `/canon-check` | — |
| Clean any prose without voice rules | `/writer clean` | — |
| Check for collection updates | `/skills-update` | — |
