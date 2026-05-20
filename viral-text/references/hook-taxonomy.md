# Hook taxonomy — intent × angle matrix

Controllable hook generation. Use these axes when (a) generating multiple alternative hooks for a topic, (b) generating hooks for an existing text, or (c) iterating on a weak hook.

Companion to [`hook-criteria.md`](hook-criteria.md): hook-criteria.md tells you what a good hook LOOKS like; this file tells you how to generate a DIVERSE set of good hooks (different angles + different emotional intents).

---

## Intent (5 options)

The emotional state the hook is engineered to evoke in the reader. Pick exactly one per hook.

| Intent | What it does | When to use |
|---|---|---|
| `anger` | Frames something as outrageous, unfair, or wrong. Reader engagement via indignation. | Polarizing topics, exposing patterns the audience already half-resents |
| `surprise` | Counter-intuitive claim or unexpected mechanism. Reader engagement via "wait, what?" | Inverted-conventional-wisdom takes, paradox |
| `ground` | Concrete relatable scenario the reader recognizes. Engagement via "yes, that's me" | Pain points, common dilemmas |
| `give_action` | Specific actionable lever or technique. Engagement via "I can use this now" | How-to, technique reveals |
| `sell_idea` | Bold thesis the post will defend. Engagement via "tell me why" | Manifesto-style, position statements |

For a 5-hook generation: ONE of each intent. No duplicates.

---

## Angle (5 options)

The structural shape of the hook content. Pick exactly one per hook.

| Angle | Shape | Example hook |
|---|---|---|
| `numbers` | Data, statistics, specific quantities | «73% врачей в Москве делают X — никто не спрашивает почему:» |
| `conflict` | Named opposition or controversy | «Стартап-инвесторы говорят X. Скаут Y2-фонда говорит обратное:» |
| `new_standard` | "Old way is dead. New way is X" | «Сторителлинг как маркетинг умер ещё в 2022. Вот что работает сейчас:» |
| `threat_to_professions` | Professional displacement or risk | «Эта одна привычка отбирает работу у джунов быстрее AI:» |
| `instruction_what_to_do` | Direct prescription | «Никогда не отвечайте на «Сколько это стоит?» сразу — три причины:» |

For a 5-hook set: ONE of each angle. No duplicates.

---

## The 5 × 5 = 25 cell matrix

Each cell is a viable hook style. When generating multiple hooks, traverse the diagonal (cells where intent ≠ angle-default) so that no two hooks share intent OR angle:

|                   | numbers | conflict | new_standard | threat | instruction |
|---|---|---|---|---|---|
| **anger**         | "X% теряют" | "Y делает X — а Z делает наоборот" | "Y умер — новый стандарт Z" | "Эта одна привычка отбирает работу у Z" | "Никогда не делай X — три причины" |
| **surprise**      | "1 из 5 не знал" | "Считалось X — оказалось Y" | "Старый X закончился в Y году" | "AI заберёт работу у X — но не у Y" | "Сделай X наоборот — будет лучше" |
| **ground**        | "9 из 10 делают X" | "Все спорят про X — а проблема в Y" | "X было нормой — теперь это Y" | "В X профессиях это уже норма" | "Если делаешь X — стой и сделай Y" |
| **give_action**   | "За 5 минут X" | "Когда команда говорит X — отвечай Y" | "Старый алгоритм X. Новый — Y" | "Чтобы не потерять работу в Y — делай X" | "Делай X. Не делай Y. Вот алгоритм:" |
| **sell_idea**     | "Все цифры X говорят одно" | "Большинство ошибается про X — вот почему" | "X закончился — Y начинается" | "Профессия X доживает последние Y лет" | "Перестаньте делать X. Делайте Y. Вот мой манифест:" |

---

## Modes

### Mode 1 — generate hooks for a TOPIC (no existing text)

User: «Сгенерируй 5 хуков на тему: офис open space»

Output: 5 hooks, one per intent, one per angle (no repeats), each following all 26 hook-criteria from `hook-criteria.md`.

### Mode 2 — generate hooks for AN EXISTING TEXT

User has a draft text and wants 5 alternative hooks that fit it (after reading the text, capture insights, then generate).

Pipeline:
1. Extract 3-5 key insights from the text (the "what did the reader learn?" elements)
2. For each, pick an intent + angle that maps to that insight (e.g. a statistic in the text → `numbers + surprise`)
3. Generate the hook applying hook-criteria.md
4. Verify: hook MUST cite something concrete from the actual text (no generic hooks)

### Mode 3 — improve a weak hook

User: «Этот хук слабый: «Открытый офис — это плохо». Переделай»

Pipeline:
1. Identify what's wrong (cf. hook-criteria.md — usually fails on: not 7-12 words, no specific subject, no time marker, no bait bracket, generic verb)
2. Pick a stronger intent + angle (likely `anger + conflict` or `surprise + new_standard`)
3. Generate improved hook keeping the underlying claim

---

## Forbidden hook constructions (banned absolutely)

These are in addition to the bans in [`viral-rules.md`](viral-rules.md):

❌ Never:
- «Ты не X — ты Y» (infobusiness construction, see `writer/references/synthetic-constructions.md`)
- «Это не про X — это про Y»
- «Один человек», «некий эксперт», «некий учёный»
- «Мало кто знает», «секрет в том», «удивительный факт»
- Any directly-addressing manipulation: «Знакомо?», «А теперь представь»
- Hooks WITHOUT specific subject (no "everyone says..." without naming)
- Hooks where the bait bracket has commas inside (it must be ≤4-5 words)
- Hooks WITHOUT colon at the end

---

## Hook generation prompt template

For Mode 1 (topic-based):

```
TASK: Write 5 viral hooks on the topic «{topic}»

LANGUAGE: {ru / en — explicit}

CONTEXT (audience, niche): {context_string}

REQUIREMENTS:
1. Each hook MUST use a DIFFERENT angle — one each: numbers, conflict,
   new_standard, threat_to_professions, instruction_what_to_do.
   Set "angle" field in JSON.
2. Each hook MUST use a DIFFERENT intent — one each: anger, surprise,
   ground, give_action, sell_idea. Set "intent" field in JSON.
3. Compliance with ALL 26 criteria from hook-criteria.md
4. 7-12 words, no fluff
5. Specific character (profession + place) where possible
6. Different transfer verbs across the 5 hooks
7. Bait bracket at the end
8. Colon at the end
9. One word in CAPS in each hook

⛔ FORBIDDEN (any of these → reject and regenerate):
- "Ты не X — ты Y" (infobiz)
- "Один эксперт", "некий специалист"
- "Мало кто знает", "удивительный факт"
- Generic hooks not tied to a specific subject

Output JSON: [{ "hook": "...", "intent": "...", "angle": "...", "subject": "...", "transfer_verb": "..." }, ...]
```

For Mode 2 (text-driven):

Add to the above:
- The actual text (truncated to ~1500 chars if long)
- Key insights list (3-5)
- Requirement: each hook must reference something specific FROM the text (a number, character, scenario, claim)

For Mode 3 (improve):

```
ORIGINAL HOOK: {hook}
ISSUES: {feedback}

TASK: Rewrite preserving the underlying claim. Apply all 26 criteria from hook-criteria.md. Pick a stronger intent + angle from the matrix.

⛔ REMOVE all neuro-constructions:
- "Ты не X — ты Y"
- "Один человек", "некий эксперт"
- "Мало кто знает", "секрет в том"

Return: { "hook": "...", "intent": "...", "angle": "...", "changes_made": [...] }
```

---

## Calibration examples

### Topic: «AI и работа джунов»

Generated 5 hooks (one per intent + angle):

1. `numbers + ground`: «9 из 10 джунов в IT всё ещё пишут промпты как в 2023:»
2. `conflict + anger`: «CTO большой компании учит так — наставник Yandex отвечает наоборот:»
3. `new_standard + surprise`: «„AI заменит джунов" — устарело за 8 месяцев. Что заменяет сейчас:»
4. `threat_to_professions + sell_idea`: «Профессия „джуна по копипасте" уже мертва. Что приходит на её место:»
5. `instruction_what_to_do + give_action`: «Перестаньте делать X в первую неделю джуна. Делайте Y. Алгоритм:»

Each is 7-12 words, has CAPS-word (visible), bait bracket, colon, specific subject. No two share intent or angle.

---

## Cross-references

- Hook criteria checklist: [`hook-criteria.md`](hook-criteria.md)
- Viral content rules: [`viral-rules.md`](viral-rules.md)
- Forbidden synthetic constructions (broader): [`../../writer/references/synthetic-constructions.md`](../../writer/references/synthetic-constructions.md)
