# Neuroslop Regex Categories — 23 buckets

Полный каталог Layer 1 паттернов. Реальная человеческая проза редко триггерит больше 1-2 категорий; текст с 5+ категориями — почти наверняка LLM.

Сканировать каждую категорию независимо. Не пытаться применить все паттерны разом «по ощущению» — это даёт false positives. Лучше: regex по списку → отметить хиты → решить, фиксить ли.

---

## 1. AI_QA — стоковые виральные вопросы

- "Знакомо?" / "Sound familiar?"
- "Звучит знакомо?" / "Sounds familiar?"
- "А теперь представь(те)" / "Now imagine"
- "Давай(те) честно" / "Let's be honest"
- "Шаг за шагом" / "Step by step"
- "Секрет в том" / "The secret is"
- "Суть в том" / "The essence is"
- "Не правда ли?" / "Isn't it?"

## 2. NE_X_A_Y — калька-инверсия (запрещена в начале фразы)

- "Ты не X — ты Y" / "You're not X — you're Y"
- "Это не про X — это про Y" / "This isn't about X — it's about Y"
- "Не X, а Y" в начале фразы (calque from "not X but Y"; normal Russian is "Y, а не X")
- Внутри фразы "не X, а Y" как разовый контраст — норма.

## 3. PSEUDO_SMART — эпистемическое позирование

- "по сути дела" / "по сути своей"
- "в конечном итоге" / "в конечном счёте"
- "в действительности"
- "как таковой / таковая / таковые"
- "можно с уверенностью сказать"
- "нельзя не отметить"
- "трудно/сложно переоценить"
- "если вдуматься"
- "стоит задуматься"
- "оно того стоит"

## 4. AI_INTENSIFIER — перегруженные эпитеты

- "беспрецедентный"
- "революционный (подход / изменение / метод / открытие)"
- "трансформирующий"
- "инновационный"
- "поразительный"
- "невероятный (результат / открытие / потенциал / сила / важность)"
- "потрясающий результат"
- "удивительное открытие / свойство / результат"
- "фундаментальное изменение / свойство"
- "исключительная важность / значение"
- "глубочайший"
- "истинная сущность / природа / смысл"
- "совершенно (другой / разный / конкретный / новый)" в значении усилителя — выбрасывать или заменять "вполне / полностью / абсолютно", если по смыслу действительно нужно
- "абсолютно (другой / новый / уникальный)" — то же, чаще всего паразит
- "полностью (новый / другой / уникальный)" — паразит, если не противопоставляется "частично"

## 5. BUREAU_INV — бюрократические инверсии

- "является" + Inst. case (не как математическое определение)
- "представляет собой"
- "выступает в качестве"
- "играет (ключевую/важную/существенную/центральную/особую) роль"
- "носит характер"
- "имеет место (быть)"
- "обладает (способностью / возможностью / свойством / потенциалом)"
- "осуществляется"
- "в рамках"
- "вышеуказанный / нижеследующий"
- "данный" в значении "этот"

## 6. CORPORATE — кальки от корпоративного английского

- "целевая аудитория"
- "болевая точка"
- "зона комфорта"
- "ценностное предложение"
- "ключевые метрики"
- "точка роста"
- "драйверы роста"
- "синергия / синергетический"
- "стратегическая инициатива / приоритет / видение"
- "операционная эффективность"
- "customer journey", "user experience" (без перевода)

## 7. GPT_FILLER — формальные эссейные подпорки

- "стоит отметить / подчеркнуть / обратить внимание"
- "важно понимать / отметить / подчеркнуть"
- "следует учитывать / отметить / признать"
- "нужно подчеркнуть / отметить"
- "как уже было сказано"
- "как мы видим / видели / можем заметить"
- "в этой связи"
- "в этом контексте"
- "в свете этого / сказанного / вышеизложенного"
- "давайте углубимся / разберёмся / погрузимся"
- "погружаясь в детали"
- "копнём глубже"
- "перейдём к"

## 8. AI_BRIDGE — формальные коннекторы в начале предложения

- "Таким образом"
- "Следовательно"
- "Подводя итог"
- "В заключение"
- "В конечном счёте / итоге"
- "Резюмируя"
- "Суммируя вышесказанное"
- "Из вышесказанного следует"

## 9. STOCK_METAPHOR — клишированные метафоры

- "работает как часы"
- "как по маслу"
- "золотая середина"
- "свет в конце туннеля"
- "вершина айсберга"
- "капля в море"
- "по образу и подобию"
- "разделяй и властвуй"
- "время покажет"
- "пища для размышлений / ума"
- "хлеб насущный"
- "ключ к (пониманию / успеху / разгадке / сердцу)"
- "на пороге чего-то"
- "на острие бритвы"
- "красные флаги / зелёные флаги"

## 10. AI_HEDGE — переизбыток vague qualifiers

- "в некотором смысле"
- "в определённом смысле"
- "в каком-то смысле"
- "по большому счёту"
- "по сути своей"
- "можно сказать"
- "можно утверждать"
- "следует признать"

## 11. SELF_REF — эссейная самореференция

- "дорогой читатель / друг"
- "как мы увидим далее / позже / ниже"
- "вернёмся к нашей теме / основной мысли"
- "стоит вернуться к"
- "подытожим"

## 12. PSEUDO_CAUSAL — фальшивые причинные мосты

- "дело в том, что"
- "суть в следующем"
- "понимаете ли"
- "видите ли"
- "по причине того, что"
- "в силу того, что"
- "именно поэтому"
- "именно потому что"

## 13. SELFHELP — клише велнес/коучинга

- "прими себя"
- "поверь в себя"
- "выйди из зоны комфорта"
- "твоя истинная сущность"
- "раскрой свой потенциал"
- "обрети свободу"
- "настоящая магия"
- "секретный соус"
- "золотой стандарт"
- "истинная ценность / природа"
- "искренность и уязвимость"

## 14. PSEUDO_SCI — псевдонаучные подпорки

- "нейробиологически"
- "эволюционно сложилось"
- "генетически запрограммировано"
- "учёные установили"
- "исследования показывают, что"
- "научно доказано"

## 15. WIDE_NET — расплывчатая гипербола

- "нет ничего, что бы"
- "нет способа описать / выразить / объяснить"
- "невозможно передать"
- "сложно передать / описать"
- "никто не может описать / объяснить"

## 16. INFLATED_TRIPLET — три абстрактных существительных подряд

Признак: три существительных на -ость / -ение / -ация / -ство / -изм через запятую/«и».

- AI-fingerprint: "ясность, прозрачность и эффективность"
- Filter: легитимные научные термин-ряды (когерентность, туннелирование, запутанность) — это фактические перечисления, не AI-стиль.

## 17. NOMINALIZATION — абстрактные номинализации

- "в процессе познания / исследования / изучения / осмысления"
- "в процессе становления / трансформации / переосмысления"
- "осуществление процесса"

## 18. FILLER_INTRO — запрещённые открыватели

- "в современном мире"
- "в современной реальности"
- "как известно"
- "общеизвестно, что"
- "в наши дни"
- "в наше время"
- "все знают, что"

## 19. VAGUE_PERSON — анонимная атрибуция

- "один человек / мужчина / женщина сказал"
- "некий эксперт"
- "некоторые люди (говорят / считают)"
- "многие утверждают"
- "часто можно услышать"

## 20. SUPERLATIVE_OVERLOAD — накачанные превосходные

- "самый важный / главный / существенный / основной / значительный момент"
- "самый поразительный вопрос / тезис / вывод / урок"

## 21. BALANCE_HEDGE — AI-fingerprint balance paragraph

- "С одной стороны … с другой стороны" в одном абзаце (LLM-балансер)
- Filter: разовое использование в статье — норма; многократное = AI.

## 22. NEURAL_METAPHOR — слова-метафоры из AI-словаря

Эти слова невинно выглядят, но в фигуративной функции мгновенно опознаются как машинная проза. Допустимы только в буквальном физическом смысле.

- "нерв" как метафора ("больной нерв дисциплины", "нерв всего разговора") → "больная мозоль", "точка преткновения", "узкое место". Буквальный нерв (анатомия) — норма.
- "держать" как абстрактная метафора ("держать линию", "держать роль", "связка нас держит", "держит развилку", "теорию держать в подвешенном состоянии") → конкретный глагол по смыслу (вести / нести / связывать / сохранять / оставлять / придерживать). Физическое "держал кружку", "держал за руку" — норма.
    - Examples the author has flagged in their own drafts (verbatim из `feedback_no_synthetic_words.md` / `feedback_prose_cleanness.md`):
        - "держать роль"
        - "связка нас держит"
        - "держала тихую тревогу"
        - "держит веер"
        - "компас держит"
    - Правка: конкретный глагол по смыслу — «вести», «несла», «связывает», «сохраняет», «оставляет открытым». Физические «держала кружку», «держала за руку», «задержался» — нормально.
- "дрожит / дрожь" как абстрактная характеристика ("статистика дрожи", "уравнения дрожат") → "колеблется / колебания". Буквальная дрожь руки — норма.
- "трещит / трещина" как метафора неисправности ("картина трещит", "формализм трещит", "теория трещит по швам") → "не выдерживает / разваливается / не сходится / даёт сбои / не работает". Буквальная трещина в стене — норма.
- "стоит на стороне X" / "стоит на N словах" как штамп → "выбирает X" / "опирается на N слов". Буквальное "стоит на столе" — норма.
- "стоит" как evaluative connector ("стоит остановиться", "стоит заметить", "стоит подумать") → переписывать через активное действие ("здесь имеет смысл остановиться" → "остановитесь" / "посмотрите")
- "нарратив" в любом контексте (если не литературоведение) → "история", "версия", "рассказ"
- "регистр" как метафора уровня/режима/тона ("три регистра одной операции") → "слой", "язык", "масштаб"
- "контур" как метафора ("контур самооценки", "общественный контур") → "фигура", "расклад", "петля"
- "оптика" как метафора ("оптика проблемы", "оптика взгляда") → "угол зрения", "способ смотреть"
- "рамка" / "в рамках X" как метафора (вне юридического "в рамках закона") → "модель", "язык", "логика", "описание"
- "шёпот" / "шёпотом" / "прошептал" — **банится даже в литеральном (буквальном) смысле**, не только как метафора. Буквальные шёпоты тоже маркер машинной прозы (buzz-word). Замены: «вполголоса», «тихо», «беззвучно», «голос упал», «бормотание».
- "оказывается X" в значении "X is" → "X" (выбрасывать "оказывается" целиком и переписывать через прямое утверждение). Допустимо в живом смысле "выясняется".

Filter: технические термины (стек, контур схемы, оптика прибора, регистр процессора, нерв в анатомии, дрожание в физике колебаний, трещина в материале) — это не метафоры, оставлять.

## 23. TYPOGRAPHY (RU)

- WRONG QUOTES: прямые `"X"` или curly `"X"` в RU тексте → use «ёлочки»
- WRONG DASHES: длинные em-dashes (`—`) в виральном/постовом тексте → short dash (`-`) с пробелами (для книжной вёрстки LaTeX — оставлять)
- INNER QUOTES inside `«...»` → use Russian low-9 quotes `„X"` (LaTeX: `,,X''`)

Подробнее — [typography.md](typography.md).

---

## False positives — typical organic cases

- "является" + program tezis ("Х является нейронной сетью") — ok в нон-фикшн
- "не X, а Y" mid-sentence как фактический контраст ("не в зуб, а в перепонку") — ok
- "Следовательно" в матлогической цепочке (Q.E.D.) — ok
- "если вдуматься" один раз на главу как discursive aside — ok
- "Дорогой читатель/блокнот" как in-character анафора — ok in fiction
- Триплет физических терминов (когерентность/туннелирование/запутанность) — ok

---

## Triage rule of thumb

- 0-1 хитов суммарно: чистая человеческая проза, не трогать
- 2-4 хита: review case-by-case, скорее всего органично; проверить, не выглядит ли что-то формульно
- 5+ хитов ИЛИ одна категория сработала 3+ раза: переписать синтетические куски
- BALANCE_HEDGE + AI_BRIDGE + GPT_FILLER одновременно = подпись LLM, полная перепись

---

## EN AI-style signatures

EN-language parallel of the RU regex catalogue above. Apply only when source language is English. Same triage rule of thumb at the bottom — 5+ hits or one bucket firing 3+ times means rewrite.

The phrases below are the most-recognized "ChatGPT/Claude tells" in English-language prose. A single instance can be organic; clusters are dispositive.

### EN-1. AI_FILLER_OPENERS — boilerplate sentence-openers

One-line rule: cut the opener, start with the claim.

- "It's important to note that..."
- "It's worth noting that..."
- "It's worth mentioning that..."
- "Bear in mind that..."
- "Keep in mind that..."
- "It is interesting to note that..."
- "One thing to consider is that..."

Hint regex: `^(It('s| is) (important|worth) (to note|noting|mentioning)|Bear in mind|Keep in mind|One thing to consider)\b`.

### EN-2. AI_DELVE — "delve" and friends

The signature LLM verb of 2023-2025. Even one instance in business prose flags as AI. Replacements: `look at`, `examine`, `dig into`, `unpack`.

- "delve into the complexities"
- "delving into the details"
- "let's delve deeper"

Hint regex: `\bdelv(e|ing|ed)\b`.

### EN-3. AI_TAPESTRY — overwrought metaphor cluster

- "rich tapestry of..."
- "vibrant tapestry of..."
- "intricate tapestry of..."
- "woven into the fabric of..."
- "the fabric of [our society / modern life / our community]..."

One-line rule: ban "tapestry" / "fabric of X" outright in non-fiction. In fiction, allow only if the narrator's voice genuinely uses textile imagery elsewhere.

### EN-4. AI_NAVIGATE — "navigate the complexities of..."

- "navigate the complexities of X"
- "navigate the challenges of X"
- "navigate the intricacies of X"
- "navigate the landscape of X"

Rule: replace with the actual verb — "handle X", "deal with X", "work through X". If "navigate" is literal (a ship, a UI menu, an app), keep.

Hint regex: `\bnavigat(e|ing|ed) the (complexit|challeng|intricac|landscap|nuance)`.

### EN-5. AI_FILLER_INTRO — banned openers (parallel to RU FILLER_INTRO)

- "In today's fast-paced world..."
- "In today's interconnected world..."
- "In today's digital age..."
- "In today's complex landscape..."
- "In an ever-evolving world..."
- "In the modern era..."
- "Whether you're X or Y..."

One-line rule: cut entirely, open with the actual claim.

Hint regex: `^(In today's|In an ever-evolving|In the modern era|Whether you're [a-z]+ or [a-z]+)`.

### EN-6. AI_PIVOTAL — "plays a pivotal/crucial role"

- "plays a pivotal role in..."
- "plays a crucial role in..."
- "plays a key role in..."
- "plays a vital role in..."
- "crucial role in shaping..."
- "vital role in driving..."

Rule: replace with the specific causal claim — "decides X", "drives X", "controls X", "lets X happen". Or drop entirely if it's just emphasis.

Hint regex: `\bplays? a (pivotal|crucial|key|vital|central|significant) role\b`.

### EN-7. AI_CORNERSTONE — "cornerstone of..."

- "cornerstone of modern X"
- "cornerstone of any successful Y"
- "foundational pillar of..."
- "bedrock of..."

Rule: replace with a concrete claim about what X actually does. "The cornerstone of modern engineering" → "what makes modern engineering work".

### EN-8. AI_MULTIFACETED — abstract complexifiers

- "multifaceted"
- "intricate" (especially "intricate interplay", "intricate dance", "intricate web")
- "complex interplay of..."
- "nuanced understanding of..."

Rule: prefer a specific noun list ("speed, cost, and accuracy") over "multifaceted considerations".

### EN-9. AI_UNDERSCORES — "underscores the importance of..."

- "underscores the importance of..."
- "highlights the need for..."
- "emphasizes the significance of..."
- "speaks to the importance of..."

Rule: replace with the actual evidence — "the data shows X" / "the result is X". Otherwise cut.

### EN-10. AI_JOURNEY — "embark on a journey"

- "embark on a journey..."
- "embark on an exploration..."
- "embark on a quest..."
- "journey of discovery"

Rule: ban outright in non-fiction. In fiction, allow only if the narrator's voice genuinely uses travel imagery.

### EN-11. AI_BRIDGE_EN — discourse-marker tic at paragraph openers

- "Furthermore,"
- "Moreover,"
- "Additionally,"
- "In addition,"
- "Of course,"
- "Indeed,"
- "Notably,"
- "Importantly,"

Rule: at most one per piece. If 30%+ of paragraphs open with these, the prose is machine. (Cross-link: structural-prose.md "EN sentence-opener monotony".)

### EN-12. AI_CONCLUSION — "In conclusion" as opener of last paragraph

The single most recognizable Claude tell in essays. A human writer almost never opens their final paragraph with "In conclusion,". Also banned variants:

- "In conclusion,"
- "To summarize,"
- "To conclude,"
- "In summary,"
- "All in all,"
- "Ultimately,"
- "At the end of the day,"

Rule: rewrite the final paragraph to land the claim directly. The reader knows it's the conclusion because it's the last paragraph.

Hint regex: last paragraph opens with `^(In conclusion|To (summarize|conclude)|In summary|All in all|Ultimately|At the end of the day),`.

### EN-13. AI_TRIPLETS — synonym-triplets ("smart, capable, and intelligent")

The model's compulsion to produce three-of-a-kind where one would do, and where the three are near-synonyms rather than distinct properties.

- BEFORE: "a smart, capable, and intelligent leader"
- AFTER: "a sharp leader" (or pick the property that actually carries meaning)

Rule: every "X, Y, and Z" triplet should pass the test — would the meaning survive dropping any one? If yes, drop. If they are genuinely distinct (e.g. "fast, cheap, and accurate"), keep.

### EN-14. AI_HEDGE_EN — vague-qualifier overload (parallel to RU AI_HEDGE)

- "to some extent"
- "in a sense"
- "in some ways"
- "for the most part"
- "more often than not"
- "by and large"
- "arguably"
- "it could be said that"

Rule: one per piece is fine; two or more in one paragraph means the model is dodging commitment.

### EN-15. AI_INTENSIFIER_EN — stacked degree adverbs (parallel to RU AI_INTENSIFIER)

- "absolutely critical"
- "truly remarkable"
- "deeply important"
- "incredibly powerful"
- "extraordinarily significant"
- "remarkably effective"

Rule: cut the adverb or replace the adjective with a stronger noun/verb. (Cross-link: structural-prose.md "EN intensifier ladder".)

### EN-16. AI_BALANCE_EN — balance-paragraph signature (parallel to RU BALANCE_HEDGE)

- "While X is important, Y is also important"
- "On one hand, X. On the other hand, Y."
- "It's both X and Y."
- "There are valid points on both sides."

Rule: any sentence that lists pros and cons without committing flags as machine. (Cross-link: structural-prose.md "EN balance hedges".)

### EN-17. AI_EMDASH — em-dash overuse

Three or more em-dashes in one paragraph used as comma-replacements is the single most reliable Claude tell. (Cross-link: structural-prose.md "EN em-dash abuse".)

### EN-18. AI_DISCLAIMER — model-voice safety hedges

- "As an AI..."
- "As a language model..."
- "I cannot..."
- "It's important to remember that..."
- "Please consult a qualified professional..."

Rule: cut entirely. Even when leaked into ghostwritten prose, this kills credibility instantly.

---

## EN false positives — typical organic cases

- "Indeed" used once as a real emphasis (not as paragraph filler) — ok
- Em-dashes in dialogue interruption ("I told him — wait, where was I?") — ok
- "It's important" in a literal context ("the meeting is important to attendance") — ok
- "Tapestry" in a fiction context where textile imagery is the voice — ok
- "Navigate" used literally (UI, ship, map) — ok
