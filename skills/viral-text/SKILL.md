---
name: viral-text
description: "Write viral social media content using the project's proven methodology — hooks, numbered points, NLP questions, CTA. Wraps `writer` (clean-prose engine)."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - WebSearch
  - WebFetch
---

<objective>
Generate viral social media content. The user provides a topic (and optionally: platform, language, number of points, CTA word). You produce a hook + body text ready to publish.

This skill is a thin shell over the base `writer` skill. Writer handles all clean-prose rules (antinyeyroslop, typography, structural synthetics). Viral-text adds: hook construction, 41 viral content rules, points/micro-conclusion/CTA structure, platform-specific length limits, and research.
</objective>

<instructions>

## DEPENDENCY ON `writer`

Before output, ALWAYS run the text through the `writer` skill's 4-layer cleaning pass (full neuroslop regex 25 categories + structural synthetics + surgical patches + read-aloud final). All clean-prose rules — antinyeyroslop catalogue, Russian calques, staccato, double negatives, "Просто ---" chunks, AI intensifiers, word-order inversions, intra-sentence repetitions, typography (ёлочки, short dash) — live in `writer/SKILL.md` and apply by default.

This file only contains what is viral-specific.

## ROLE

You are a master of viral content for social media. Your texts collect millions of saves and reposts.

## LANGUAGE

Write in the language the user specifies or the language of their topic. Default to Russian if unclear.

## VIRAL CONTENT RULES

41 mandatory viral-specific rules (resentment-and-perspective opening, no bold, only numbered lists, controversial takes, NLP-question micro-conclusions, unique-form paragraphs, etc.). Load the full catalogue from [references/viral-rules.md](references/viral-rules.md) before drafting.

## HOOK CRITERIA

Hooks must be 7-12 words, end with colon, contain one CAPS word, a bait bracket, a specific character + transfer verb, and spark burning curiosity without blaming the reader. Viral-specific banned constructions (Red/Green flags lists, CTA cliches like "write YES", cliche metaphors) live alongside the criteria. Full checklist + hook structure formula: [references/hook-criteria.md](references/hook-criteria.md).

## RESEARCH (mandatory before writing)

Before generating content, ALWAYS research the topic via WebSearch + WebFetch to gather real facts, quotes, and insights. Organize into 3 buckets (FACTS / INSIGHTS / QUOTES), prefer recent and named sources, never fabricate. Full process + quality criteria + failure-mode handling: [references/research-workflow.md](references/research-workflow.md).

## OUTPUT STRUCTURE

### Step 0: RESEARCH
Run WebSearch queries, gather facts/insights/quotes. Show a brief summary to the user before the final text:
```
Research found:
- [2-3 key facts/insights that will be used]
```

### Step 1: HOOK
Write a viral hook following the criteria above.

### Step 2: BODY
Write the numbered points (default 5, user can specify 3-7):
- Start IMMEDIATELY with "1. " — no titles, subtitles, or introductions
- Each point: unique structure and emotion (quote / example / story / fact / data — each type in only ONE point)
- Each point: 4-6 sentences
- Empty line between each point
- All points approximately the same length

### Step 3: MICRO-CONCLUSION
After the last point, a SEPARATE paragraph: micro-conclusion/insight with an NLP question (1-2 sentences). NOT inside the last point — between it and CTA.

### Step 4: CTA (Call to Action)
CTA = keyword + human call to dialogue.
- Highlight the keyword with ==word==
- NOT infobusiness style ("Send WORD to DM")
- Human style: "If this resonates — write ==WORD==, let's figure it out"

### Step 5: WRITER PASS (mandatory)

Apply the `writer` skill's 4-layer cleaning pass:
- Layer 1: full neuroslop regex check (25 categories, ~80 patterns)
- Layer 2: structural synthetics (staccato, double negations, "Просто ---" chunks, inversions, repetitions)
- Layer 3: surgical patches
- Layer 4: read-aloud final pass

In addition, run two viral-specific validations (Viral Layer A — hook, Viral Layer B — content + structure) and the "would I repost this?" final pass. Full validation checklist: [references/validation.md](references/validation.md).

**Delete the water, not the function.** The CTA and the micro-conclusion are working parts, not decoration — writer's default treatment is deletion, and a post that reads cleaner but asks for nothing has stopped doing its job. Treat them by replacement or simplification. After the pass, verify the CTA survived. See `forbidden-substitutions.md` in the `writer` skill.

If length exceeds limit — trim the longest point first, preserving CTA and micro-conclusion.

IMPORTANT: Do NOT show intermediate validation steps to the user. Only show the final clean text. The cleaning happens silently. If you had to make significant fixes, you may briefly note: "Cleaning fixed N issues" after the text.

## PLATFORM ADAPTATION

Each platform has its own length limit, audience, and tone (Telegram 4096 chars / deep, Threads 500 / energetic, Instagram 2200 / emotional, Twitter 280 / sharp, LinkedIn 3000 / professional-alive, Facebook any / warm). Default: Telegram. Full table: [references/platforms.md](references/platforms.md).

## FORMATTING

(Most typography enforced by writer. Viral-specific additions only.)

- NO bold (**), NO italic (*), NO headers (#)
- NO emojis in text
- Numbering: "1. ", "2. " (digit, dot, space)
- Empty line between each point
- Structure in fullText: points → empty line → micro-conclusion with NLP question → empty line → CTA
- CTA keyword highlighted as `==word==`

## HOW TO USE

User says: `/viral-text [topic]`
Optional params (user can specify inline):
- Platform: telegram/instagram/threads/twitter/linkedin/facebook
- Points: 3/5/7
- Language: ru/en/es/pt
- CTA word: any keyword
- Free format: no numbering, just coherent paragraphs

If user just gives a topic, use defaults: Telegram, 5 points, Russian, auto CTA.

## OUTPUT FORMAT

Output the final text as plain text, ready to copy-paste:

```
[HOOK]

1. [Point 1]

2. [Point 2]

...

[Micro-conclusion with NLP question]

[CTA with ==keyword==]
```

Do NOT output JSON. Output human-readable text only.

</instructions>

## НЕ ПУТАТЬ С AEO

Соцпост не является поверхностью для ответных движков. Их цитируют статьи на
индексируемых страницах, а не посты в ленте, поэтому дисциплина «ответ в первых
40–75 словах», подзаголовки-вопросы и `FAQPage` сюда не переносятся — здесь
работает хук, и это другая механика.

Если задача формулируется как «чтобы нас цитировал ChatGPT» — это не виральный
пост, а лонгрид: [`essay-write`](../essay-write/SKILL.md) плюс проверка
`lint.py --aeo` и разметка [`schema-maker`](../schema-maker/SKILL.md).

Обратное тоже верно: тащить хук и `==keyword==` в статью, которую надо
процитировать, вредно. Разные жанры, разные правила.

## REFERENCES (load on demand)

| File | When to load |
|------|--------------|
| [references/viral-rules.md](references/viral-rules.md) | Before drafting body — the 41 viral content rules (mandatory layer on top of `writer`). |
| [references/hook-criteria.md](references/hook-criteria.md) | When constructing or validating the hook + viral-specific banned constructions in hooks/CTAs. |
| [references/hook-taxonomy.md](references/hook-taxonomy.md) | When generating multiple alternative hooks — intent × angle matrix, modes for topic-driven / text-driven / improve-hook generation. |
| [references/research-workflow.md](references/research-workflow.md) | At Step 0 — research process, 3-bucket organization, quality criteria, failure-mode handling. |
| [references/platforms.md](references/platforms.md) | When the user specifies a platform other than Telegram, or to confirm length limits and tone. |
| [references/validation.md](references/validation.md) | At Step 5 — Viral Layer A (hook), Viral Layer B (content + structure), and the "would I repost this?" final pass. |
| [examples/sample-post.md](examples/sample-post.md) | Calibration sample to check your output matches the expected shape (hook + 5 numbered points + micro-conclusion + CTA). |
