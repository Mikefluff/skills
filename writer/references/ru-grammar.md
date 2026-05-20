# RU grammar — name declension + gender agreement

Grammatical rules that LLMs often violate on Russian text. Not regex-detectable (context-dependent), but wrappers should apply this checklist on every named entity.

This complements `ru-calques.md` (vocabulary level) and `structural-prose.md` (structural level).

---

## 1. Male names ending in -а / -я decline

These ARE male grammatical-feminine-ending names. They decline as feminine BUT the verb/adjective/predicate agrees with masculine gender.

| Nominative | Genitive | Dative | Accusative | Instrumental | Prepositional |
|---|---|---|---|---|---|
| Никита | Никиты | Никите | Никиту | Никитой | (о) Никите |
| Илья | Ильи | Илье | Илью | Ильёй | (об) Илье |
| Лука | Луки | Луке | Луку | Лукой | (о) Луке |
| Гоша | Гоши | Гоше | Гошу | Гошей | (о) Гоше |

✅ «Никита сказал», «спросил у Никиты», «отдал Никите», «вижу Никиту»
❌ «Никита сказала» (Никита — мужское имя), «спросил у Никита» (не склонили)

Same pattern: Илья, Лука, Гоша, Саша (м.), Жора, Сева, Никита, Афанасий → склоняется как feminine, согласуется как masculine.

---

## 2. Female names ending in -а / -я — same pattern but feminine agreement

| Nominative | Verb agreement | Example |
|---|---|---|
| Анна, Мария, Ольга, Наталья | feminine | «Анна сказала», «Мария пришла» |

Trivial — included for symmetry.

---

## 3. Foreign names ending in -о, -е, -и, -у — DO NOT decline

These are foreign borrowings and have no Russian-grammar inflection.

| Name | All cases |
|---|---|
| Пикассо | Пикассо, Пикассо, Пикассо, Пикассо, Пикассо |
| Феллини | Феллини везде |
| Гюго | Гюго везде |
| Дюма | Дюма везде |
| Дидро | Дидро везде |
| Корнеллу (?) | Same — no inflection |

✅ «работа Пикассо», «фильм Феллини», «о Гюго»
❌ «работа Пикасса», «фильм Феллина»

This applies to first names, last names, and place names ending in unstressed -о/-е (Глазго, Чикаго, Осло).

---

## 4. Foreign female names ending in a consonant — DO NOT decline

| Name | Treatment |
|---|---|
| Элизабет | indeclinable |
| Маргарет | indeclinable |
| Кэт (full Catherine) | indeclinable |
| Жаклин | indeclinable |

✅ «у Элизабет», «о Маргарет», «к Жаклин»
❌ «у Элизабеты», «о Маргарете», «к Жаклине»

But Russian female names ending in -а / -я decline normally («у Анны»).

---

## 5. Foreign male names ending in a consonant — DO decline (like Russian masculine)

| Name | Genitive |
|---|---|
| Джон | Джона |
| Майкл | Майкла |
| Эрих | Эриха |
| Дональд | Дональда |
| Стивен | Стивена |

✅ «работа Джона», «у Майкла», «о Стивене»
❌ «работа Джон», «у Майкл»

---

## 6. Patronymics (-ович / -евич / -овна / -евна)

Decline normally as adjectives:

- Иванович → Ивановича → Ивановичу → Ивановича → Ивановичем → (об) Ивановиче
- Ивановна → Ивановны → Ивановне → Ивановну → Ивановной → (об) Ивановне

The full form «Иван Петрович Сидоров» — all three parts decline together.

---

## 7. Diminutives — same rules as full names

- Саша (м.) → склоняется как Никита (мужской с -а ending), глагол masculine
- Саша (ж.) → склоняется так же, глагол feminine
- Серёжа, Лёша, Миша, Гоша, Илья — male, same pattern

Context determines gender — usually clear from surrounding sentence.

---

## 8. Surnames ending in -ин, -ов, -ев, -ский, -цкий, -их, -ых

- Russian masculine surnames in -ин/-ов/-ев decline:
  Пушкин → Пушкина → Пушкину
  Иванов → Иванова → Иванову
- Russian masculine surnames in -ский/-цкий decline as adjectives:
  Достоевский → Достоевского → Достоевскому
- Surnames in -их/-ых (e.g. Долгих, Косых) — indeclinable for BOTH sexes
- Female counterparts — Пушкина → Пушкиной → Пушкиной (declines as adjective)
- Russian female surnames in -о (Шевченко) — indeclinable for both sexes

---

## 9. Gender agreement — the most-missed LLM error

For each named character, find their grammatical gender (from context or by name) and check ALL agreements:

✅ Correct:
- «Никита сказал, что он устал» (мужской)
- «Анна сказала, что она устала» (женский)
- «Саша пришёл и сказал» (in context — male Sasha)
- «Саша пришла и сказала» (in context — female Sasha)

❌ Common LLM error:
- «Никита сказала» — verb feminine for masculine name
- «Дядя Маши приехал и она привезла подарки» — pronoun mismatch

**Wrapper instruction**: when rewriting prose with named characters, for each character, verify gender from context (first appearance usually clarifies) and propagate gender agreement throughout. If ambiguous, ask the user; do NOT guess.

---

## 10. Multi-syllable indeclinable place names

- Осло, Чикаго, Глазго, Сан-Франциско — indeclinable
- Москва, Питер, Казань, Урал — decline normally
- Borrowed -и / -у endings — usually indeclinable (Боку, Перу)

✅ «в Чикаго», «из Осло»
❌ «в Чикаге», «из Осла»

---

## Quick-reference table — does it decline?

| Pattern | Male | Female |
|---|---|---|
| Russian -а / -я (Никита, Анна) | yes, fem-paradigm, masc agreement | yes, fem-paradigm, fem agreement |
| Russian consonant ending (Иван, Петр) | yes, masc-paradigm | n/a (no Russian female names in C) |
| Russian adjective-form surname (-ский) | yes, adj-paradigm | yes, adj-paradigm (Достоевская) |
| Foreign -о / -е / -и / -у (Пикассо, Феллини) | no | no |
| Foreign consonant ending (John, Майкл) | yes, masc-paradigm | no (Элизабет, Маргарет — indecl.) |
| Russian surname -их / -ых (Долгих) | no | no |

---

## When LLM makes a name-agreement error

The wrapper LLM pass should:

1. Identify all named entities in the passage
2. Determine gender for each (first-mention context, name-list lookup, ask user if ambiguous)
3. Check every verb / pronoun / adjective agreeing with each entity
4. Apply corrections — preserve the original word, fix the agreement

If a translation: cross-reference `translation-sync` for canonical name-form per language.
