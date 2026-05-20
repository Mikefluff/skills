# Synthetic constructions — fake AI authenticity

These are patterns LLMs produce when **trying too hard to sound real**. They look concrete on the surface but on second glance are formulaic. This file covers what regex CAN catch — see also `neuroslop-categories.md` for the broader 23-category catalogue.

A text full of these patterns reads as "typical AI viral post" even when each individual phrase passes basic checks.

---

## 1. Name-dropping templates (fake authority)

The "city + profession + transfer verb" formula. LLMs reach for this when asked for "real-sounding examples":

❌ Bad — formulaic:
- «терапевт из Казани нарисовал»
- «наставник из Лондона с 20 лет стажа сказал»
- «один предприниматель садился за стол»
- «на коворкинге в Тбилиси встретил»
- «хирург из Киото показал»
- "a therapist from Boston told me"
- "a coach with 20 years of experience said"
- "an entrepreneur I met at a conference"

✅ Replace with one of:
- Real specific story without the city-profession scaffolding
- Verifiable named source: «Подкаст Никитина», «Виноградов в книге „X"»
- First-person observation: «у меня было», «я видел»
- Just drop it — the example was load-bearing only as fake authority

**Detection heuristic**: noun denoting profession + "из/from" + place + transfer verb ("сказал/нарисовал/показал/told/showed"). If the same paragraph contains another such template, definitely synthetic.

---

## 2. CTA stamps (fake call-to-action)

LLM viral posts default to the same 5-6 CTAs. They feel canned because they are.

❌ Banned CTAs:
- «Если это про вас, пишите ДА в комментариях»
- «напишите в комментах»
- «разберём»
- «пишите ДА»
- «If this resonates, drop a comment»
- «Tag someone who needs this»
- «Save this for later»
- «Let's discuss in the comments»

✅ Replacements (any one):
- Live, non-templated ask: «Какой из 5 пунктов у вас уже работает?»
- Specific action with consequence: «Попробуй на одной встрече — заметишь разницу через час»
- No CTA at all (some viral posts work better with a strong micro-conclusion than a forced CTA)

---

## 3. Formula metaphors

LLM-generated metaphors often follow the same shape: "X works like Y" or "X calls Y" where Y is a stock concept.

❌ Banned:
- «работает как радар»
- «сигнал как радар»
- «X зовёт X»
- «как маяк в тумане»
- "works like a radar"
- "acts as a compass"
- "serves as a beacon"

These read as filler — the metaphor doesn't actually clarify anything; it's just there to sound profound.

✅ Either:
- Cut the metaphor entirely
- Replace with concrete operational detail: «срабатывает на голос матери, но не на голос отца» — that's specific, not metaphoric

---

## 4. List-as-template (red flags / green flags)

❌ Avoid as default structure:
- «5 красных флагов в отношениях»
- «10 зелёных флагов хорошего работодателя»
- «3 признака того, что ты выгораешь»

This template is so worn that it signals AI generation by itself. If you genuinely have a list to write, use a more specific frame:
- "Three patterns that broke my last relationship" (specific, owned)
- "What I'd check before signing the offer" (specific perspective)

Lists ARE OK; the X-flags / N-signs template is what's banned.

---

## 5. Uniform paragraph rhythm

LLM viral posts tend to have every paragraph in the same shape: medium length, somewhat profound, ends with a takeaway. Reading the whole post is like listening to the same melody five times.

❌ Bad rhythm signature:
- Paragraph 1: insight + example + takeaway
- Paragraph 2: insight + example + takeaway
- Paragraph 3: insight + example + takeaway
- All paragraphs ~40-60 words
- All end on a generalization

✅ Healthy rhythm:
- Paragraph 1: insight + 3 examples (long)
- Paragraph 2: counter-example (short, 1-2 sentences)
- Paragraph 3: quote + reaction
- Paragraph 4: live numbers
- Paragraph 5: micro-conclusion

The form variation IS the dopamine — the reader's brain hits novelty between paragraphs, not just inside them.

**Detection heuristic**: if 4+ consecutive paragraphs are 35-65 words AND all end on generalization, suspect synthetic rhythm. (This is hard to detect via regex; the wrapper LLM pass handles it.)

---

## 6. Synthetic construction templates (formula-AI signatures)

These are not the same as the 23 neuroslop categories — they're a meta-pattern: phrases that AI uses when asked to "sound profound" or "be insightful":

❌ Banned constructions:
- "Это не про X. Это про Y" — infobusiness template
- "Это не X и не Y" — template negation
- "За этим стоит..." — pseudo-depth
- "...которую стоит разобрать" — sales-tone insertion
- "Это не хорошо и не плохо" — hedging dodge
- "просто так работает" — pseudo-explanation
- "осознанное" / "осознанно" — coaching jargon
- "Знакомо?" — manipulative question
- "Давай честно" / "Если честно" — fake intimacy
- Nominative-sentence slogans: "X — тоже Y" as headlines
- Each sentence sounds like "live speech of a real person" — if EVERY sentence sounds like a polished epigram, it's synthetic

✅ The rule:
- If you can extract any sentence from your post and put it in an Instagram quote graphic and it would work — that's exactly what's wrong. Real-person writing has dependencies; every sentence is a sentence in the same conversation, not a self-contained aphorism.

---

## 7. Pseudo-vulnerability and faux-confession

LLMs love to fake humility in viral content:

❌ Banned:
- «Я тоже через это прошёл»
- «Я ошибался много лет»
- «И я тогда понял»
- «Перелом случился»
- «Это был самый сложный момент моей жизни»
- «Я делал X 5 лет и ничего не работало»
- "I made every mistake in the book"
- "I was that person who..."
- "It took me 10 years to figure this out"

These are templates because they're load-bearing for "authenticity" without specific content. If you genuinely have a specific moment of failure with concrete details (place, time, what was on the table, what you smelled, who said what), keep it. If the "confession" is generic, cut it.

---

## Cross-references

- General AI-prose tells: [`neuroslop-categories.md`](neuroslop-categories.md) (23 categories)
- Structural / sentence-level patterns: [`structural-prose.md`](structural-prose.md)
- Viral content specifically: [`../../viral-text/references/viral-rules.md`](../../viral-text/references/viral-rules.md)

---

## Note on detection

Most of these patterns are hard to express as regex (they require semantic context — is this name-drop fake or real? is this metaphor formulaic or fresh?). The regex linter (`lint.py`) catches the **most-common literal phrases** in SYNTHETIC category. The full audit happens in the LLM wrapper pass.
