# 15-Point Pre-Commit Translation Parity Checklist

> How to apply: run through these 15 in order before committing a translated chapter. Each item maps to a specific check in the parity pipeline. If an item is missing, the canonical source is the section in parentheses.

This list is the operational summary of the full translation guide. Each point is a one-line gate; a failure on items 1–11 is **blocking**, on 12–14 is **warning**, on 15 is **author-discretion**.

---

1. **Canon reconciled.** Names, numbers, dates match the RU source AND the story bible for that book.
   - Each book carries its own canon registry — typically `<book>/notes/story-bible.{md,tex,txt}` or whatever your project uses.
   - Cross-check against [terminology.md](terminology.md) for shared terms across books in a series.

2. **Anchor quotes translated literally.** Nothing has been "improved", word order preserved where it carries meaning.
   - Full list in [anchor-quotes.md](anchor-quotes.md). Any deviation = BLOCKING.
   - The canonical examples: `"I know."` is exactly two words, period. `"One. Whole. Draft."` is three words through periods. No `"Yes, I knew that"`, no `"A whole, complete draft"`.

3. **Concrete details preserved.** Every number, duration, dimension, distance — literal.
   - `900 milliseconds` not `under a second`. `17 days` not `a couple of weeks`. `11 cracks` not `several cracks`. `R² = 0.41` stays as-is.
   - Full list in [what-not-to-smooth.md](what-not-to-smooth.md).

4. **Metaphors consistent.** `stack` ≠ `layer` ≠ `render`. `signature` ≠ `anchor`. The translator does not swap them.
   - Stack-of-reality terminology in [terminology.md](terminology.md) §Reality stack.

5. **Real names in Latin script.** Real-world public figures (scientists, authors, brands) stay in Latin orthography across all three languages, including the Cyrillic source — never transcribed.
   - Russian historical figures take standard transliteration in EN/PT-BR. Never the reverse.
   - Full rules in [names-and-realia.md](names-and-realia.md) §Real people.

6. **Italics on the same words.** If the RU source italicizes a word, the EN target italicizes the **same** word — not a near-synonym (even if the latter sounds better).
   - Italics carry semantic emphasis; they are not stylistic decoration. Preserved position-by-position.

7. **Bracketed digressions stay in brackets.** Do not promote them to separate sentences. Bracketed digressions are voice, not "additional information".

8. **No extenders.** Quiet characters speak short. No added `"my friend"`, `"you see"`, `"como assim"`, `"young man"`.
   - If the RU has two phrases, the EN has two phrases.

9. **No smoothed specifics.** Numbers not rounded; durations not turned into "a few"; cracks not turned into "several".
   - This is item 3 restated as a separate gate because it is the single most common drift.

10. **No neuro-slop metaphors.** `frame`, `noise` (as background, non-acoustic), `lens` (as way of seeing), `register` (as tone), `contour` — all banned in EN. In PT-BR: `enquadramento`, `ruído` (metaphoric), `lente`, `registro`, `contorno` — same.
    - Any neuro-slop metaphors removed from RU during depth-pass remain banned in EN and PT-BR equivalents.

11. **No additions.** If a character hangs up the phone without saying goodbye, do not add `"goodbye"` / `"tchau"`. A reply lands without `"yes, son"`. A quote lands without `"as I said"`.

12. **Quotes and dashes correct.** TeX-style quotes `` ``...'' `` and `` `...' ``. Em-dash `---` (three minuses in LaTeX), never `--`, never `-`.
    - Full per-language typography rules in [typography.md](typography.md).

13. **Footnotes for realia.** Place names, institutions, brand names, drug names from the source culture — explanatory footnote on first mention, none after.
    - Footnote pattern and the full realia inventory in [names-and-realia.md](names-and-realia.md) §Cultural realia.

14. **Diminutive names standardized.** Pick one Latin-script form per character (full / short / affectionate) and keep it consistent. Standardized per [names-and-realia.md](names-and-realia.md).

15. **If a RU depth-pass landed after the last EN sync:** cross-check against the current RU, not an old version. Pull the latest source-language chapter and diff against the translated file's known sync point.

---

## State map — when is sync due (project-specific, fill in for your books)

Track per book: last source-language depth-pass, last EN sync, last PT-BR sync, what to catch up. Example layout:

| Book | Last RU depth-pass | Last EN sync | Last PT-BR sync | What to catch up |
|-------|--------------------|---------------|------------------|-----------------|
| Book A | YYYY-MM-DD (notes) | YYYY-MM-DD | YYYY-MM-DD | open items |
| Book B | YYYY-MM-DD (notes) | YYYY-MM-DD | YYYY-MM-DD | open items |

**Rule:** after a source-language depth-pass, do not mark a chapter "done" until EN and PT-BR are synced. If the edit is purely stylistic (a tic, a repeat, a cliché), check it is even relevant in the target language — some Russian tics simply don't exist in EN/PT-BR.
