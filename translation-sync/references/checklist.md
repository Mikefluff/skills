# 15-Point Pre-Commit Translation Parity Checklist

> How to apply: run through these 15 in order before committing a translated chapter. Each item maps to a specific check in the parity pipeline. If an item is missing, the canonical source is the section in parentheses.

This list is the operational summary of the full translation guide. Each point is a one-line gate; a failure on items 1–11 is **blocking**, on 12–14 is **warning**, on 15 is **author-discretion**.

---

1. **Canon reconciled.** Names, numbers, dates match the RU source AND the story-bible for that book.
   - Books: `god-academy`, `era-arkhitektorov`, `heavenly-code`. Each has its own canon registry under `books/<book>/notes/story-bible.tex`.
   - Cross-check against [terminology.md](terminology.md) for shared terms across the three books.

2. **Anchor quotes translated literally.** Nothing has been "improved", word order preserved where it carries meaning.
   - Full list in [anchor-quotes.md](anchor-quotes.md). Any deviation = BLOCKING.
   - The canonical examples: `"I know."` is exactly two words, period. `"One. Whole. Draft."` is three words through periods. No `"Yes, I knew that"`, no `"A whole, complete draft"`.

3. **Concrete details preserved.** Every number, duration, dimension, distance — literal.
   - `900 milliseconds` not `under a second`. `17 days` not `a couple of weeks`. `11 cracks` not `several cracks`. `R² = 0.41` stays as-is.
   - Full list in [what-not-to-smooth.md](what-not-to-smooth.md).

4. **Metaphors consistent.** `stack` ≠ `layer` ≠ `render`. `signature` ≠ `anchor`. The translator does not swap them.
   - Stack-of-reality terminology in [terminology.md](terminology.md) §Reality stack.

5. **Real names in Latin script.** Sam Battle, Vazza, Vanchurin, Tononi, Hoffman, Friston, Levin, etc. — never transcribed.
   - Russian historical figures (Иван Елагин, Стругацкие братья, Николай Фёдоров) take standard transliteration in EN/PT-BR. Never the reverse.
   - Full rules in [names-and-realia.md](names-and-realia.md) §Real people.

6. **Italics on the same words.** If RU italicizes _способ_, EN italicizes _the way_ — not _the manner_ (even if the latter sounds better).
   - Italics carry semantic emphasis; they are not stylistic decoration. Preserved position-by-position.

7. **Bracketed digressions stay in brackets.** Do not promote them to separate sentences. Bracketed digressions are voice, not "additional information".

8. **No extenders.** Wei Lin / Artyom speak short. No added `"my friend"`, `"you see"`, `"como assim"`, `"young man"`.
   - Wei Lin is a quiet character. If the RU has two phrases, the EN has two phrases.

9. **No smoothed specifics.** Numbers not rounded; durations not turned into "a few"; cracks not turned into "several".
   - This is item 3 restated as a separate gate because it is the single most common drift.

10. **No neuro-slop metaphors.** `frame`, `noise` (as background, non-acoustic), `lens` (as way of seeing), `register` (as tone), `contour` — all banned in EN. In PT-BR: `enquadramento`, `ruído` (metaphoric), `lente`, `registro`, `contorno` — same.
    - These were cleaned out of RU during the May 2026 depth-pass. Their translated equivalents are equally forbidden.

11. **No additions.** The father hangs up the phone without saying goodbye — do not add `"goodbye"` / `"tchau"`. It is an engineer's gesture. The father's reply lands without `"yes, son"`. The quote lands without `"as I said"`.

12. **Quotes and dashes correct.** TeX-style quotes `` ``...'' `` and `` `...' ``. Em-dash `---` (three minuses in LaTeX), never `--`, never `-`.
    - Full per-language typography rules in [typography.md](typography.md).

13. **Footnotes for realia.** Лубянка, Шуховская башня, Phenazepam, Gastroshield — explanatory footnote on first mention, none after.
    - Footnote pattern and the full realia inventory in [names-and-realia.md](names-and-realia.md) §Cultural realia.

14. **Diminutive names standardized.** Dan, Seryozha, Danya — standardized per [names-and-realia.md](names-and-realia.md). No `Sergei` for Серёжа. No `Danny` for Даня. No `Elena` for Лена.

15. **If a RU depth-pass landed after the last EN sync:** cross-check against the current RU, not an old version. Pull the latest from `books/<book>/ru/chapters/` and diff against the translated file's known sync point.

---

## State map — when is sync due

| Book | Last RU depth-pass | Last EN sync | Last PT-BR sync | What to catch up |
|-------|--------------------|---------------|------------------|-----------------|
| AB    | 16 May (Pelevin-Dostoyevsky hybrid, ch01-25) | 11 May | 11 May | depth-pass + new integrator scene in ch11 + ch03/04 egg rework + five theological translations expanded in ch15 |
| HC (НК) | 13 May (ch01/04 "unit with N zeros" fix, ch11 architecture) | 12 May | 12 May | ch01/04 final nuances + ch11 final pass |
| EA (ЭА) | 17 May (ch01/04/05/14 long-period expansion) | 11 May | 11 May | ch01/04/05/14 + ch08 Wei Lin line rework |

**Rule:** after a RU depth-pass, do not mark a chapter "done" until EN and PT-BR are synced. If the edit is purely stylistic (a tic, a repeat, a cliché), check it is even relevant in the target language — some Russian tics simply don't exist in EN/PT-BR.
