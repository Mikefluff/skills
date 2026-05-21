# Output format

Exact structure of the saved `./generated/research/<slug>.md` file.

---

## File header

```markdown
# <Topic Title Case>

_Brief generated: <YYYY-MM-DD>. Sources used: <N>. Depth: <quick|standard|deep>. Language: <en|ru|mixed>._
```

Title Case the topic. Keep the topic phrase short — if the request was a long sentence, distill to 3-7 words.

The italic metadata line MUST include all four: date, N sources, depth, language. Downstream skills parse this.

---

## Sections (in order)

1. **TL;DR** — exactly 3 sentences. Sentence 1: what the thing is. Sentence 2: why it matters now. Sentence 3: one tension / contrarian frame.

2. **Key facts** — bulleted list. Each bullet:
   - One fact per bullet
   - Citation marker at end: `[#N]` (N = source index in Sources section)
   - `[single-source]` annotation if applicable
   - `<dated>` annotation if source is >12 months old on a fast-moving topic
   - 5-15 bullets total (depth-dependent: 5/10/15 for quick/standard/deep)

3. **Notable quotes** — block quotes from named people. Each:
   ```
   > "<exact quote>"
   > — <Name>, <Title/Role>, <Publication> (<date>) [#N]
   ```
   2-5 quotes total. Skip the section if no real attributable quotes found — don't fabricate.

4. **Suggested angles** — numbered list. Each angle:
   - Headline (4-10 words) — what the angle is
   - Format target — `for carousel` / `for reel` / `for essay` / `for landing-hero` / `for cold-email`
   - One-sentence why
   - Optional: which 1-2 facts from above support it (`builds on [#3] [#7]`)

   3-5 angles total (`--angles N` controls). Each angle must be ACTUALLY different — not "X impacts business" then "X impacts marketing". Distinct narrative shapes.

5. **Open questions** — bulleted list. Things you couldn't verify, contradictions, unresolved tensions. 3-8 items. Mandatory for `--depth standard` and `--depth deep`. Skip for `--depth quick` if there are none.

6. **Out of reach / requires expertise** — list of:
   - Paywalled sources you couldn't access
   - NDA / private-info gaps
   - Topics where the brief writer can't reliably evaluate (real-time data, vendor enterprise pricing, domain claims requiring expert judgment)
   Skip if there are none — don't pad.

7. **Sources** — numbered list. Each:
   ```
   1. [<exact page title>](<full URL>) — <publication>, <date or 'undated'> — accessed <YYYY-MM-DD>
   ```
   Numbered consistently with `[#N]` markers throughout. URL must be the canonical landing page, not a search-result snippet. Strip tracking params (utm_*).

---

## Slug rules

`<topic-slug>-<YYYYMMDD>.md`

- Slug = kebab-case of the topic
- Strip stop words (the, a, an, of, in, on, for, to) unless dropping them breaks meaning
- Max 40 chars before the date suffix
- Lowercase only
- ASCII only — transliterate non-Latin: "ии в России" → "ai-in-russia"

Examples:
- "AI productivity tools for marketers in 2026" → `ai-productivity-tools-marketers-20260521.md`
- "Veo 3.1 vs Sora 2 deep comparison" → `veo-3-1-vs-sora-2-20260521.md`
- "Тренд на slow living в 2026" → `slow-living-trend-20260521.md`

If the same slug + date file exists, append `-N` (`-2`, `-3`).

---

## Word budgets by `--format`

| --format | TL;DR | Key facts | Quotes | Angles | Open Qs | Total body |
|---|---|---|---|---|---|---|
| `brief` (default) | 3 sentences | 5-10 bullets | 2-3 | 3 | 3-5 | 200-500 words |
| `outline` | 3 sentences | 10-15 bullets, expanded | 3-5 | 3-5 | 5-8 | 500-800 words |
| `article-ready` | 3 sentences + 2-para context | 12-20 bullets with sub-bullets | 4-6 | 3-5 with paragraph rationale | 5-10 | 800-1500 words |

Stay within budget. A 2000-word brief is signal that depth was wrong — escalate to `--depth deep` next time instead.

---

## Citation style

- Inline: `[#1]`, `[#2]`, etc. Always square-bracketed, always with a hash, no space.
- For two sources on one fact: `[#1][#3]` (no comma, no space).
- For quoted material, citation comes AFTER the attribution line, not inside the quote.
- Sources list uses Markdown link syntax. URLs are not shortened — full URLs only.

Don't use academic-style citations (Smith 2023). Don't use footnote refs. The `[#N]` system is the only one supported.

---

## Multilingual handling

If `--lang ru` or `--lang mixed`:

- Section headings stay in English (TL;DR, Key facts, etc.) — these are structural markers that downstream skills parse.
- Body content (facts, quotes, angles) follows `--lang`.
- Quotes from non-target-language sources: include original + translation:
  ```
  > "<original>" — <translated>
  > — <Name>, <Pub> (<date>) [#N]
  ```
- Suggested angles can mix languages if appropriate (e.g. RU brief for a RU audience but EN angle for a global landing).

If `--lang mixed`: TL;DR + structure stay EN; facts/quotes/angles can switch by source.

---

## stdout output

Last line printed on stdout MUST be the file path:
```
Brief written to ./generated/research/ai-productivity-tools-marketers-20260521.md (12 sources, TL;DR: <30-char snippet>...)
```

Downstream skills regex-extract the path from this line. Don't print anything after it.
