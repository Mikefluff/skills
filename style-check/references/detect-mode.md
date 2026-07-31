# Detect mode — "was this written by AI?"

An audit with a verdict, not an edit. The user is not asking for cleaner text; they are asking whether a text they did not write came out of a model.

AI detectors guess. A named pattern with a quote is something the reader can check themselves — which is the only useful thing this mode produces.

---

## Triggers

- «проверь на ИИ», «палится ли текст», «это нейросеть писала?», «похоже на GPT?»
- "is this AI-written", "check for AI", "did a model write this"

If the request is to *fix* the text, this is the wrong mode — route to `writer` in `clean` mode.

---

## Procedure

1. **Run the linter first.**
   ```bash
   python3 writer/scripts/lint.py suspect.md --json
   ```
   Any `COPYPASTE_ARTIFACT` hit ends the analysis immediately: the text was pasted out of a chat UI. Report it and stop counting soft signals — no cluster is needed, and none of the probabilistic reasoning below applies.

2. **Build the findings table** — quote, category, one-line note. Same shape as a `writer` phase-1 audit.

3. **Score by families, not by hits.** Group each finding into one of three families:
   - **Лексика** — word-level: AI_INTENSIFIER, CORPORATE, MARKETING_HYPE, NEURAL_METAPHOR, THERAPEUTIC
   - **Структура** — shape-level: RHYTHM_MONOTONE, VERB_ECHO, HEADING_ECHO, BALANCE_HEDGE, INFLATED_TRIPLET, PARAGRAPH_STACK
   - **Коммуникация** — stance-level: AI_QA, GPT_FILLER, SELF_REF, VAGUE_PERSON, AI_HEDGE, HEDGE_CASCADE

4. **Verdict scale.**

   | Findings | Verdict |
   |---|---|
   | any class A artifact | copied out of a chatbot — certain, no further counting |
   | 0-2 soft markers | probably human |
   | 3-5 markers spanning **2+ families** | probably AI |
   | 6+ markers spanning 2+ families | almost certainly AI |
   | any number, all from **one** family | the author's style, not AI |

   The family rule carries most of the weight. A text with nine hits all in Лексика is someone with a corporate vocabulary habit. A text with four hits spread across all three families is a model.

5. **Return the table and the verdict. Do not rewrite the text.** Offer the edit as a separate step.

---

## Where to stop

Do not assert authorship on soft signals as though it were a fact. Flawless grammar, dryness, a wide vocabulary, tidy structure — none of these prove anything. Plenty of people write that way, and increasingly many of them write that way *because* they read a lot of model output.

Phrase the finding, not the accusation: "четыре маркера из трёх семей, вот цитаты" rather than "это писала нейросеть".

Better to let a machine-written text pass than to call a living author a liar. The cost is asymmetric: a missed detection annoys, a false accusation lands on a person.

---

## Output shape

```
=== DETECT ===
Вердикт: вероятно ИИ (4 маркера, 3 семьи)

| Цитата | Категория | Семья | Фикс |
|---|---|---|---|
| «является ключевым фактором» | BUREAU_INV + AI_INTENSIFIER | лексика | «решает» |
| «Важно отметить, что…» | GPT_FILLER | коммуникация | удалить |
| ср. длина соседних предложений 2.1 слова | RHYTHM_MONOTONE | структура | разбить ритм |
| «Подводя итог…» | AI_BRIDGE | коммуникация | удалить абзац |

Что это НЕ доказывает: текст грамотный и сухой — само по себе это ничего не значит.
```
