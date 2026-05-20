# Voice references + Style drift checklist

Этот файл описывает целевой голос художественной прозы и набор сигналов, по которым ловится съезд от него.

## VOICE REFERENCES

Ориентир — Пелевин (философия через юмор, дерзкий голос, без пафоса). Приёмы Мэнсона — провокация, скепсис, абсурд, «ну и что?». Не подражание, а вектор.

### Style drift checklist (10 пунктов)

Сверять при правке: не съезжает ли текст в сторону, противоположную голосу.

1. **Штампы**: «золотая середина», «вершина айсберга», «на острие бритвы» — выкидывать (большая часть уже в writer Layer 1 категория 9, но в художке проверять отдельно — часто проходят как «авторская стилизация»)
2. **Пафос**: «истинная природа», «глубокий смысл», «бесконечная мудрость» — снимать, заменять конкретикой
3. **Проповеди**: «нужно понять», «помни», «никогда не забывай» — переписывать через действие или сцену
4. **Netflix-моменты**: телевизионная сцена-картинка («он медленно повернулся, и в его глазах…») — заменять на нелинейный ход
5. **Резонёрство**: длинный авторский комментарий вместо сцены — превращать в действие
6. **Морализаторство**: оценка персонажа от рассказчика — снимать, оставлять читателю
7. **Гладкость**: текст «читается легко» = вычистили шероховатости, которые держали голос — вернуть
8. **Самоповтор**: автор уже использовал эту фигуру в предыдущей главе/книге — заменить на новую (вести список повторяющихся фигур по корпусу)
9. **Объяснительность**: «потому что» там, где должно быть умолчание — выкинуть связку
10. **Псевдоумность**: «как известно», «как мы знаем», «очевидно» — выкинуть (writer ловит, но в художке смотреть отдельно)

---

## EN voice patterns

EN-language layer for fiction prose. Applies on top of writer EN AI-style signatures (neuroslop-categories.md EN-1..EN-18) and writer EN structural patterns (structural-prose.md "EN ..."). The rules below catch fiction-specific voice issues that the universal layer misses.

### Adverb crutches — `-ly` modifiers on weak verbs

"Said quietly", "walked slowly", "thought sadly", "smiled brightly", "looked nervously". The adverb is patching a verb that didn't do its job. Either pick a verb that already carries the manner, or replace with a beat (a body action) that shows it.

- BEFORE: "She walked slowly into the room."
- AFTER: "She drifted into the room." (verb does the work)
- OR: "She paused at the threshold, then crossed to the window." (beat shows the pace)

Hint regex: `\b(said|walked|smiled|looked|moved|spoke|thought|sat|stood) [a-z]+ly\b` → flag. Allow when the adverb is genuinely the only word that fits.

### Show-don't-tell trigger verbs

"She felt angry." "He was scared." "She was happy." Internal-state labels with no embodied evidence. Replace with bodily reaction, action, dialogue beat, or environmental detail.

- BEFORE: "He felt afraid."
- AFTER: "His mouth went dry; he tried to swallow and couldn't."

Hint regex: `\b(felt|was|seemed) (angry|afraid|sad|happy|nervous|confused|tired|excited)\b` → flag.

### POV consistency — close-third vs. omniscient slip

In close-third POV, the narrator can only know what the POV character knows. Common slips:

- The narrator describes the POV character's own face ("her green eyes flashed") — impossible from inside her head.
- The narrator dips into another character's thoughts mid-scene ("he didn't know that across town, Sarah was thinking...").
- The narrator surfaces information the POV character couldn't have ("the killer, whom she would not meet for another three days, was already...").

Rule: lock the POV per scene. If the manuscript uses close-third, every sentence inside a scene must be filterable through that character's perception. Slips read as either amateur or AI.

### Sentence-rhythm — short / medium / long variation

EN equivalent of staccato detection. Healthy prose alternates sentence lengths; AI prose drifts toward two failure modes: (a) flat 12-15 word sentences in a row, or (b) all-short staccato (which writer EN structural patterns catches).

Rule of thumb: if 5+ consecutive sentences fall within ±3 words of each other in length, the rhythm has flattened. Vary by adding a short punchy sentence, or a longer subordinate-clause one.

(Cross-link: writer structural-prose.md "EN staccato".)

### Dialogue-tag overload — "he said / she said" in every line

In a back-and-forth between two characters, the reader knows who's speaking after line 2. Cut tags from lines 3+. Use beats (small physical actions) instead of tags when reattribution is needed.

- BEFORE: "I told you," he said. "You didn't listen," she said. "I did listen," he said.
- AFTER: "I told you." / "You didn't listen." / He set down the cup. "I did listen."

Rule: at most one tag per ~4 dialogue lines in a two-person scene. Multi-person scenes need more, but beats still beat tags.

### Saidism — "exclaimed / muttered / chuckled" instead of "said"

The classic fiction sin. "Said" is invisible; saidisms are visible and distracting. Acceptable: occasional "asked" / "whispered" / "called" when literally accurate. Banned at high frequency: "exclaimed", "ejaculated", "chuckled", "gasped", "snarled", "growled", "hissed".

Rule: "said" is the default; switch only when the alternative carries unique information the dialogue itself doesn't convey.

### Filter verbs — "he saw / she heard / he felt"

Inserting a perception verb between the reader and the sensory detail. The filter weakens immediacy. Cut the filter, render the detail directly.

- BEFORE: "She heard the door slam."
- AFTER: "The door slammed." (in close-third, the reader knows she heard it)
- BEFORE: "He saw the truck come around the corner."
- AFTER: "The truck came around the corner."

Hint regex: `\b(saw|heard|felt|smelled|noticed|watched|observed|realized|thought) (that |[a-z]+ed|the |a |an )` → flag for filter-cut review.

### Em-dash overuse in narration

Same Claude tell as in non-fiction, applied to the narrator's voice. 3+ em-dashes in a single narrative paragraph → rewrite. Allow when the narrator's voice is genuinely dash-heavy (e.g. a fast, breathless first-person), but enforce a budget: dashes earn their keep, they don't replace commas.

(Cross-link: writer structural-prose.md "EN em-dash abuse".)

### Stage-direction bloat — choreography without purpose

"She turned. She walked across the room. She picked up the cup. She turned again. She walked back." Every micro-movement narrated. Cut to meaningful beats only.

- BEFORE: "He stood up. He pushed in the chair. He walked to the door. He opened the door. He went out."
- AFTER: "He left." (or: "He left without pushing in his chair." — keep only the detail that carries character)

Rule: keep a beat only if it shows character, advances story, or anchors the scene physically. Cut the rest.

### "Suddenly" and other narrator-pokes

"Suddenly", "all of a sudden", "out of nowhere", "without warning" — these tell the reader to feel surprise instead of staging surprise. Cut. If the event is sudden, write the event itself with sufficient compression and the suddenness will register.

- BEFORE: "Suddenly, the door burst open."
- AFTER: "The door burst open." (the burst already carries the suddenness)
