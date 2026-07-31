#!/usr/bin/env python3
"""
writer-lint — offline regex linter for the writer skill.

Catches a high-recall subset of the neuroslop categories defined in
writer/SKILL.md, plus two things regex alone cannot see: chatbot copy-paste
artifacts (class A — a single hit is proof) and structural rhythm metrics
(uniform sentence length, bold density, verb echo across adjacent sentences).
Does NOT replace the full 4-layer cleaning pass — it is meant as a fast
pre-check ("does this draft already look like LLM output?") before asking
Claude to apply writer in clean/apply mode.

Two orthogonal outputs:
  * verdict  — how dense the slop is (clean / borderline / neuroslop suspected)
  * gate     — whether any HARD BAN fired (em-dash in RU prose, math signs in
               prose, negative parallelism, chopped drama, copy-paste artifact)

A text can be "clean" by density and still fail the gate on one pasted
`turn0search3`. That is the point: density is a judgement call, the gate is not.

Usage:
    python3 lint.py path/to/text.md
    python3 lint.py path/to/text.md --json
    cat text.md | python3 lint.py -

Exit codes:
    0 — clean (0-1 hits)
    1 — borderline (2-4 hits)
    2 — neuroslop suspected (5+ hits OR any category 3+ times)
    3 — hard ban present (gate failed; overrides the density verdict)

Class A artifact regexes are ported from smixs/humanizer-ru (MIT), which in
turn credits Vladimir-Human/humanizer-ru and petergyang/no-ai-slop (both MIT).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Iterable

# Each pattern is (category, regex, optional human label).
# Regex is matched case-insensitively unless inline (?-i) is used.
PATTERNS: list[tuple[str, str]] = [
    # --- 1. AI_QA ---
    ("AI_QA", r"\b(знакомо|звучит\s+знакомо|sound\s+familiar|sounds\s+familiar)\?"),
    ("AI_QA", r"\b(а\s+теперь\s+представь(те)?|now\s+imagine)\b"),
    ("AI_QA", r"\b(давай(те)?\s+честно|let'?s\s+be\s+honest)\b"),
    ("AI_QA", r"\b(шаг\s+за\s+шагом|step\s+by\s+step)\b"),
    ("AI_QA", r"\b(секрет\s+в\s+том|the\s+secret\s+is)\b"),
    ("AI_QA", r"\b(суть\s+в\s+том|the\s+essence\s+is)\b"),
    ("AI_QA", r"\bне\s+правда\s+ли\?"),
    # --- 2. NE_X_A_Y ---
    ("NE_X_A_Y", r"(?m)^\s*[—-]?\s*ты\s+не\s+\S+.{1,40}\s[—-]\s+ты\s+\S+"),
    ("NE_X_A_Y", r"(?m)^\s*это\s+не\s+про\s+\S+.{1,40}\s[—-]\s+это\s+про\s+\S+"),
    ("NE_X_A_Y", r"(?m)^\s*не\s+\S+,\s+а\s+\S+"),
    ("NE_X_A_Y", r"(?i)you'?re\s+not\s+\S+\s+[—-]\s+you'?re\s+\S+"),
    ("NE_X_A_Y", r"(?i)this\s+isn'?t\s+about\s+\S+\s+[—-]\s+it'?s\s+about\s+\S+"),
    # --- 3. PSEUDO_SMART ---
    ("PSEUDO_SMART", r"\bпо\s+сути\s+(дела|своей)\b"),
    ("PSEUDO_SMART", r"\bв\s+конечном\s+(итоге|счёте|счете)\b"),
    ("PSEUDO_SMART", r"\bв\s+действительности\b"),
    ("PSEUDO_SMART", r"\bкак\s+таков(ой|ая|ые|ого)\b"),
    ("PSEUDO_SMART", r"\bможно\s+с\s+уверенностью\s+сказать\b"),
    ("PSEUDO_SMART", r"\bнельзя\s+не\s+отметить\b"),
    ("PSEUDO_SMART", r"\b(трудно|сложно)\s+переоценить\b"),
    ("PSEUDO_SMART", r"\bесли\s+вдуматься\b"),
    ("PSEUDO_SMART", r"\bстоит\s+задуматься\b"),
    ("PSEUDO_SMART", r"\bоно\s+того\s+стоит\b"),
    # --- 4. AI_INTENSIFIER ---
    ("AI_INTENSIFIER", r"\bбеспрецедентн\w*"),
    ("AI_INTENSIFIER", r"\bреволюционн\w+\s+(подход|изменени|метод|открыти)\w*"),
    ("AI_INTENSIFIER", r"\bтрансформирующ\w*"),
    ("AI_INTENSIFIER", r"\bинновационн\w*"),
    ("AI_INTENSIFIER", r"\bпоразительн\w*"),
    ("AI_INTENSIFIER", r"\bневероятн\w+\s+(результат|открыти|потенциал|сил|важност)\w*"),
    ("AI_INTENSIFIER", r"\bпотрясающ\w+\s+результат\w*"),
    ("AI_INTENSIFIER", r"\bудивительн\w+\s+(открыти|свойств|результат)\w*"),
    ("AI_INTENSIFIER", r"\bфундаментальн\w+\s+(изменени|свойств)\w*"),
    ("AI_INTENSIFIER", r"\bисключительн\w+\s+(важност|значени)\w*"),
    ("AI_INTENSIFIER", r"\bглубочайш\w*"),
    ("AI_INTENSIFIER", r"\bистинн\w+\s+(сущност|природ|смысл)\w*"),
    ("AI_INTENSIFIER", r"\bсовершенно\s+(друг|разн|конкретн|нов)\w+"),
    ("AI_INTENSIFIER", r"\bабсолютно\s+(друг|нов|уникальн)\w+"),
    ("AI_INTENSIFIER", r"\bполностью\s+(нов|друг|уникальн)\w+"),
    # --- 5. BUREAU_INV ---
    ("BUREAU_INV", r"\bпредставляет\s+собой\b"),
    ("BUREAU_INV", r"\bвыступает\s+в\s+качестве\b"),
    ("BUREAU_INV", r"\bиграет\s+(ключев|важн|существенн|центральн|особ)\w+\s+роль"),
    ("BUREAU_INV", r"\bносит\s+характер\b"),
    ("BUREAU_INV", r"\bимеет\s+место(\s+быть)?\b"),
    ("BUREAU_INV", r"\bобладает\s+(способност|возможност|свойств|потенциал)\w+"),
    ("BUREAU_INV", r"\bосуществляется\b"),
    ("BUREAU_INV", r"\bв\s+рамках\b"),
    ("BUREAU_INV", r"\bвышеуказанн\w+|нижеследующ\w+"),
    # --- 6. CORPORATE ---
    ("CORPORATE", r"\bцелев\w+\s+аудитор\w+"),
    ("CORPORATE", r"\bболев\w+\s+точк\w+"),
    ("CORPORATE", r"\bзон\w+\s+комфорт\w+"),
    ("CORPORATE", r"\bценностн\w+\s+предложени\w+"),
    ("CORPORATE", r"\bключев\w+\s+метрик\w+"),
    ("CORPORATE", r"\bточк\w+\s+рост\w+"),
    ("CORPORATE", r"\bдрайвер\w*\s+рост\w+"),
    ("CORPORATE", r"\bсинерги\w+|синергетическ\w+"),
    ("CORPORATE", r"\bстратегическ\w+\s+(инициатив|приоритет|видени)\w+"),
    ("CORPORATE", r"\bоперационн\w+\s+эффективност\w+"),
    ("CORPORATE", r"\bcustomer\s+journey\b"),
    ("CORPORATE", r"\buser\s+experience\b"),
    # --- 7. GPT_FILLER ---
    ("GPT_FILLER", r"\bстоит\s+(отметить|подчеркнуть|обратить\s+внимание)\b"),
    ("GPT_FILLER", r"\bважно\s+(понимать|отметить|подчеркнуть)\b"),
    ("GPT_FILLER", r"\bследует\s+(учитывать|отметить|признать)\b"),
    ("GPT_FILLER", r"\bнужно\s+(подчеркнуть|отметить)\b"),
    ("GPT_FILLER", r"\bкак\s+уже\s+было\s+сказано\b"),
    ("GPT_FILLER", r"\bкак\s+мы\s+(видим|видели|можем\s+заметить)\b"),
    ("GPT_FILLER", r"\bв\s+этой\s+связи\b"),
    ("GPT_FILLER", r"\bв\s+этом\s+контексте\b"),
    ("GPT_FILLER", r"\bв\s+свете\s+(этого|сказанного|вышеизложенного)\b"),
    ("GPT_FILLER", r"\bдавайте\s+(углубимся|разберёмся|погрузимся)"),
    ("GPT_FILLER", r"\bпогружаясь\s+в\s+детали\b"),
    ("GPT_FILLER", r"\bкопнём\s+глубже\b"),
    ("GPT_FILLER", r"\bперейдём\s+к\b"),
    # --- 8. AI_BRIDGE (sentence-initial) ---
    ("AI_BRIDGE", r"(?m)^(\s|[«„\"\'])*таким\s+образом\b"),
    ("AI_BRIDGE", r"(?m)^(\s|[«„\"\'])*следовательно\b"),
    ("AI_BRIDGE", r"(?m)^(\s|[«„\"\'])*подводя\s+итог\b"),
    ("AI_BRIDGE", r"(?m)^(\s|[«„\"\'])*в\s+заключение\b"),
    ("AI_BRIDGE", r"(?m)^(\s|[«„\"\'])*резюмируя\b"),
    ("AI_BRIDGE", r"(?m)^(\s|[«„\"\'])*суммируя\s+вышесказанное\b"),
    ("AI_BRIDGE", r"(?m)^(\s|[«„\"\'])*из\s+вышесказанного\s+следует\b"),
    # --- 9. STOCK_METAPHOR ---
    ("STOCK_METAPHOR", r"\bработает\s+как\s+часы\b"),
    ("STOCK_METAPHOR", r"\bкак\s+по\s+маслу\b"),
    ("STOCK_METAPHOR", r"\bзолот\w+\s+середин\w+"),
    ("STOCK_METAPHOR", r"\bсвет\s+в\s+конце\s+туннел\w+"),
    ("STOCK_METAPHOR", r"\bвершин\w+\s+айсберг\w+"),
    ("STOCK_METAPHOR", r"\bкапл\w+\s+в\s+море\b"),
    ("STOCK_METAPHOR", r"\bпо\s+образу\s+и\s+подоби\w+"),
    ("STOCK_METAPHOR", r"\bразделяй\s+и\s+властвуй\b"),
    ("STOCK_METAPHOR", r"\bвремя\s+покажет\b"),
    ("STOCK_METAPHOR", r"\bпищ\w+\s+для\s+размышлени\w+"),
    ("STOCK_METAPHOR", r"\bключ\s+к\s+(пониманию|успеху|разгадке|сердцу)\b"),
    ("STOCK_METAPHOR", r"\bкрасн\w+\s+флаг\w+|зелён\w+\s+флаг\w+"),
    # --- 10. AI_HEDGE ---
    ("AI_HEDGE", r"\bв\s+(некотором|определённом|каком-то)\s+смысле\b"),
    ("AI_HEDGE", r"\bпо\s+большому\s+счёт\w+"),
    ("AI_HEDGE", r"\bможно\s+(сказать|утверждать)\b"),
    ("AI_HEDGE", r"\bследует\s+признать\b"),
    # --- 11. SELF_REF ---
    ("SELF_REF", r"\bдорог\w+\s+(читатель|друг)"),
    ("SELF_REF", r"\bкак\s+мы\s+увидим\s+(далее|позже|ниже)"),
    ("SELF_REF", r"\bвернёмся\s+к\s+(нашей\s+теме|основной\s+мысли)"),
    # --- 12. PSEUDO_CAUSAL ---
    ("PSEUDO_CAUSAL", r"\bдело\s+в\s+том,\s+что\b"),
    ("PSEUDO_CAUSAL", r"\bсуть\s+в\s+следующем\b"),
    ("PSEUDO_CAUSAL", r"\bпонимаете\s+ли\b"),
    ("PSEUDO_CAUSAL", r"\bвидите\s+ли\b"),
    ("PSEUDO_CAUSAL", r"\bпо\s+причине\s+того,\s+что\b"),
    ("PSEUDO_CAUSAL", r"\bв\s+силу\s+того,\s+что\b"),
    ("PSEUDO_CAUSAL", r"\bименно\s+(поэтому|потому\s+что)\b"),
    # --- 13. SELFHELP ---
    ("SELFHELP", r"\bповерь\s+в\s+себя\b"),
    ("SELFHELP", r"\bвыйди\s+из\s+зоны\s+комфорта\b"),
    ("SELFHELP", r"\bистинн\w+\s+сущност\w+"),
    ("SELFHELP", r"\bраскро\w+\s+свой\s+потенциал\b"),
    ("SELFHELP", r"\bнастоящ\w+\s+маги\w+"),
    ("SELFHELP", r"\bсекретн\w+\s+соус\w+"),
    ("SELFHELP", r"\bзолот\w+\s+стандарт\w+"),
    ("SELFHELP", r"\bискренност\w+\s+и\s+уязвимост\w+"),
    # --- 14. PSEUDO_SCI ---
    ("PSEUDO_SCI", r"\bнейробиологически\b"),
    ("PSEUDO_SCI", r"\bэволюционно\s+сложилось\b"),
    ("PSEUDO_SCI", r"\bгенетически\s+запрограммирован\w+"),
    ("PSEUDO_SCI", r"\bучёные\s+установили\b"),
    ("PSEUDO_SCI", r"\bисследования\s+показывают,\s+что\b"),
    ("PSEUDO_SCI", r"\bнаучно\s+доказано\b"),
    # --- 15. WIDE_NET ---
    ("WIDE_NET", r"\bнет\s+ничего,\s+что\s+бы\b"),
    ("WIDE_NET", r"\bневозможно\s+передать\b"),
    ("WIDE_NET", r"\bсложно\s+(передать|описать)\b"),
    # --- 17. NOMINALIZATION ---
    ("NOMINALIZATION", r"\bв\s+процессе\s+(познани|исследовани|изучени|осмыслени|становлени|трансформаци|переосмыслени)\w+"),
    ("NOMINALIZATION", r"\bосуществлени\w+\s+процесс\w+"),
    # --- 18. FILLER_INTRO ---
    ("FILLER_INTRO", r"(?m)^(\s|[«„\"\'])*в\s+современн\w+\s+(мире|реальности)"),
    ("FILLER_INTRO", r"(?m)^(\s|[«„\"\'])*как\s+известно\b"),
    ("FILLER_INTRO", r"(?m)^(\s|[«„\"\'])*общеизвестно,\s+что\b"),
    ("FILLER_INTRO", r"(?m)^(\s|[«„\"\'])*в\s+наш\w*\s+(дни|время)"),
    ("FILLER_INTRO", r"(?m)^(\s|[«„\"\'])*все\s+знают,?\s+что\b"),
    # --- 19. VAGUE_PERSON ---
    ("VAGUE_PERSON", r"\bодин\s+(человек|мужчина|женщина)\s+сказал\w*"),
    ("VAGUE_PERSON", r"\bнек\w+\s+эксперт\w*"),
    ("VAGUE_PERSON", r"\bнекоторые\s+люди\s+(говорят|считают)\b"),
    ("VAGUE_PERSON", r"\bмногие\s+утверждают\b"),
    ("VAGUE_PERSON", r"\bчасто\s+можно\s+услышать\b"),
    # --- 20. SUPERLATIVE_OVERLOAD ---
    ("SUPERLATIVE_OVERLOAD", r"\bсамый\s+(важн|главн|существенн|основн|значительн)\w+\s+момент\b"),
    ("SUPERLATIVE_OVERLOAD", r"\bсамый\s+поразительн\w+\s+(вопрос|тезис|вывод|урок)\b"),
    # --- 22. NEURAL_METAPHOR (selective) ---
    ("NEURAL_METAPHOR", r"\bтрещит\s+по\s+швам\b"),
    ("NEURAL_METAPHOR", r"\bдержит\s+линию\b"),
    ("NEURAL_METAPHOR", r"\bнерв\w*\s+(разговора|дисциплины|темы)"),
    ("NEURAL_METAPHOR", r"\bнарратив\w*"),
    ("NEURAL_METAPHOR", r"\bоптик\w+\s+(проблемы|взгляда|вопроса)"),
    ("NEURAL_METAPHOR", r"\bв\s+рамках\s+(модели|подхода|логики)"),
    ("NEURAL_METAPHOR", r"\b(шёпот|шепот)\w*|прошептал\w*"),
    # Extra "держать" abstract-metaphor variants flagged by the author in own drafts
    # (feedback_no_synthetic_words.md / feedback_prose_cleanness.md)
    ("NEURAL_METAPHOR", r"\bдержит\s+(веер|линию|роль|компас|тревог)"),
    ("NEURAL_METAPHOR", r"\bсвязка\s+\w+\s+держит"),
    ("NEURAL_METAPHOR", r"\bкомпас\s+держит"),
    # Literal шёпот also banned (see neuroslop-categories.md cat 22)
    ("NEURAL_METAPHOR", r"\b(шёпотом?|прошептал\w*)\b"),
    # --- DOUBLE_NEG_REGEX (feedback_no_double_negation.md) ---
    # Run these before commit; rewrite each match into an affirmative/contrast form.
    ("DOUBLE_NEG_REGEX", r"\bне\s+[а-яё]+,?\s+не\s+[а-яё]+"),
    ("DOUBLE_NEG_REGEX", r"\bбез\s+[а-яё]+,?\s+без\s+[а-яё]+"),
    ("DOUBLE_NEG_REGEX", r"\bни\s+[а-яё]+,?\s+ни\s+[а-яё]+,?\s+ни\b"),
    # --- 23. TYPOGRAPHY ---
    ("TYPOGRAPHY", r'"[^"\n]{1,80}"'),  # straight quotes (rough — flags any "X")
    ("TYPOGRAPHY", r"“[^”\n]{1,80}”"),  # curly "X"
    # ─── EN AI-style signatures (mirrors writer/references/neuroslop-categories.md) ───
    # FILLER_INTRO (EN)
    ("FILLER_INTRO", r"(?m)^(\s|[\"'])*in\s+today'?s\s+(\w+(-\w+)?,?\s+){1,5}world\b"),
    ("FILLER_INTRO", r"(?m)^(\s|[\"'])*in\s+a\s+world\s+where"),
    ("FILLER_INTRO", r"(?m)^(\s|[\"'])*as\s+(we\s+all\s+know|everyone\s+knows)"),
    ("FILLER_INTRO", r"(?m)^(\s|[\"'])*in\s+(this|today'?s)\s+ever[- ]?(changing|evolving)\s+landscape"),
    # GPT_FILLER (EN)
    ("GPT_FILLER", r"\bit'?s\s+(important|worth|crucial)\s+to\s+(note|mention|remember)\b"),
    ("GPT_FILLER", r"\blet'?s\s+(delve|dive)\s+(in|into)\b"),
    ("GPT_FILLER", r"\bdelv(e|ing)\s+(deeper|into)\b"),
    ("GPT_FILLER", r"\bin\s+this\s+context\b"),
    ("GPT_FILLER", r"\bin\s+light\s+of\s+(this|the\s+above)\b"),
    ("GPT_FILLER", r"\bas\s+(we\s+can\s+see|previously\s+mentioned|stated\s+earlier)\b"),
    ("GPT_FILLER", r"\bbear\s+in\s+mind\b"),
    # AI_BRIDGE (EN — sentence-initial)
    ("AI_BRIDGE", r"(?m)^(\s|[\"'])*furthermore\b"),
    ("AI_BRIDGE", r"(?m)^(\s|[\"'])*moreover\b"),
    ("AI_BRIDGE", r"(?m)^(\s|[\"'])*additionally\b"),
    ("AI_BRIDGE", r"(?m)^(\s|[\"'])*in\s+conclusion\b"),
    ("AI_BRIDGE", r"(?m)^(\s|[\"'])*ultimately,?\s+"),
    ("AI_BRIDGE", r"(?m)^(\s|[\"'])*to\s+sum\s+up\b"),
    # STOCK_METAPHOR (EN)
    ("STOCK_METAPHOR", r"\b(rich\s+)?tapestry\s+of\b"),
    ("STOCK_METAPHOR", r"\bnavigat(e|ing)\s+the\s+complexities\b"),
    ("STOCK_METAPHOR", r"\bembark\s+on\s+a\s+journey\b"),
    ("STOCK_METAPHOR", r"\b(a\s+)?journey\s+of\s+(continuous|self-?)\w+"),
    ("STOCK_METAPHOR", r"\bcornerstone\s+of\b"),
    ("STOCK_METAPHOR", r"\bplay(s|ing|ed)?\s+a\s+(pivotal|crucial|key)\s+role\b"),
    ("STOCK_METAPHOR", r"\b(very\s+)?fabric\s+of\b"),
    ("STOCK_METAPHOR", r"\bshap(e|ing|es)\s+the\s+future\b"),
    # AI_INTENSIFIER (EN)
    ("AI_INTENSIFIER", r"\btruly\s+(remarkable|amazing|inspiring|unique)\b"),
    ("AI_INTENSIFIER", r"\babsolutely\s+(critical|essential|fundamental)\b"),
    ("AI_INTENSIFIER", r"\bdeeply\s+(important|meaningful|profound)\b"),
    ("AI_INTENSIFIER", r"\bincredibly\s+(important|powerful|valuable)\b"),
    ("AI_INTENSIFIER", r"\bunderscor(es|ing|ed)\s+the\s+importance\b"),
    ("AI_INTENSIFIER", r"\bmulti[- ]?faceted\b"),
    ("AI_INTENSIFIER", r"\bintricate\b"),
    ("AI_INTENSIFIER", r"\bfar[- ]?reaching\b"),
    ("AI_INTENSIFIER", r"\bcannot\s+be\s+overstated\b"),
    # AI_HEDGE (EN)
    ("AI_HEDGE", r"\bit\s+(could|can)\s+be\s+argued\s+that\b"),
    ("AI_HEDGE", r"\bsome\s+would\s+say\b"),
    ("AI_HEDGE", r"\bone\s+might\s+argue\b"),
    ("AI_HEDGE", r"\bon\s+one\s+hand\b.*\bon\s+the\s+other\s+hand\b"),
    ("AI_HEDGE", r"\bwhile\s+there\s+are\s+valid\b"),
    ("AI_HEDGE", r"\bboth\s+perspectives?\s+have\s+merit\b"),
    # SELFHELP (EN)
    ("SELFHELP", r"\bwhether\s+you'?re\s+\w+\s+or\s+\w+,"),
    ("SELFHELP", r"\bunleash\s+(your|the)\s+(potential|power)\b"),
    ("SELFHELP", r"\bunlock\s+(your|the)\s+(potential|true)\b"),
    ("SELFHELP", r"\bsecret\s+sauce\b"),
    ("SELFHELP", r"\bgold\s+standard\b"),
    # PSEUDO_CAUSAL (EN)
    ("PSEUDO_CAUSAL", r"\bthe\s+thing\s+is,?\b"),
    ("PSEUDO_CAUSAL", r"\bwhat\s+this\s+means\s+is\b"),
    ("PSEUDO_CAUSAL", r"\byou\s+see,?\b"),
    # AI_TRIPLETS — three synonyms (smart, capable, and intelligent)
    ("AI_TRIPLETS", r"\b\w+,\s+\w+,\s+and\s+\w+\s+technology\b"),
    ("AI_TRIPLETS", r"\bsmart,?\s+capable,?\s+and\s+intelligent\b"),
    # PSEUDO_SMART (EN)
    ("PSEUDO_SMART", r"\bessentially\b"),
    ("PSEUDO_SMART", r"\bfundamentally,?\s"),
    ("PSEUDO_SMART", r"\bat\s+the\s+end\s+of\s+the\s+day\b"),
    ("PSEUDO_SMART", r"\bin\s+essence\b"),
    ("PSEUDO_SMART", r"\bin\s+reality\b"),
    # BUREAU_INV (EN)
    ("BUREAU_INV", r"\bplays?\s+the\s+role\s+of\b"),
    ("BUREAU_INV", r"\bserves?\s+as\s+a\b"),
    ("BUREAU_INV", r"\brepresents?\s+a\s+(form|kind|type)\s+of\b"),
    ("BUREAU_INV", r"\bin\s+the\s+(framework|context)\s+of\b"),
    ("BUREAU_INV", r"\bin\s+terms\s+of\b"),
    ("BUREAU_INV", r"\bwith\s+respect\s+to\b"),
    ("BUREAU_INV", r"\bvia\s+the\s+(implementation|application|introduction|use)\s+of\b"),
    # CORPORATE (EN)
    ("CORPORATE", r"\bvalue\s+proposition\b"),
    ("CORPORATE", r"\bgrowth\s+drivers?\b"),
    ("CORPORATE", r"\bgo-?to-?market\b"),
    ("CORPORATE", r"\bkey\s+(metrics?|takeaways?|learnings?|insights?)\b"),
    ("CORPORATE", r"\bpain\s+points?\b"),
    ("CORPORATE", r"\btarget\s+audience\b"),
    ("CORPORATE", r"\bsynerg(y|ies|istic)\b"),
    ("CORPORATE", r"\bstrategic\s+(initiative|vision|priorities|roadmap)s?\b"),
    ("CORPORATE", r"\boperational\s+efficienc(y|ies)\b"),
    ("CORPORATE", r"\bleverag(e|ing|ed)\s+\w+"),
    # NE_X_A_Y (EN — "this isn't X. It's Y." / "you're not X. You're Y." structures)
    ("NE_X_A_Y", r"(?i)this\s+is(n'?t|\s+not)\s+(just\s+)?[\w\s]{1,40}[.;]\s+It'?s\s+\w+"),
    ("NE_X_A_Y", r"(?i)you'?re\s+not\s+[\w\s]{1,40}[.;]\s+You'?re\s+\w+"),
    ("NE_X_A_Y", r"(?i)it'?s\s+not\s+about\s+[\w\s]{1,40}[.;]\s+It'?s\s+about\s+\w+"),
    # SELF_REF (EN)
    ("SELF_REF", r"\bdear\s+reader\b"),
    ("SELF_REF", r"\bas\s+we'?ll\s+see\s+(later|below|further\s+on)\b"),
    ("SELF_REF", r"\bas\s+I\s+(mentioned|noted|wrote)\s+(earlier|above)\b"),
    ("SELF_REF", r"\blet'?s\s+return\s+to\s+our\b"),
    # PSEUDO_SCI (EN)
    ("PSEUDO_SCI", r"\bresearch\s+shows\s+that\b"),
    ("PSEUDO_SCI", r"\bstudies\s+(show|suggest|indicate)\s+that\b"),
    ("PSEUDO_SCI", r"\bscientists?\s+(have\s+)?(found|established|discovered)\s+that\b"),
    ("PSEUDO_SCI", r"\b(neurologically|neuroscientifically)\b"),
    ("PSEUDO_SCI", r"\bevolutionarily\s+(programmed|wired)\b"),
    ("PSEUDO_SCI", r"\bscientifically\s+proven\b"),
    # VAGUE_PERSON (EN)
    ("VAGUE_PERSON", r"\bsome\s+(experts?|researchers?|scholars?|people)\s+(say|believe|claim|argue|suggest)\b"),
    ("VAGUE_PERSON", r"\bmany\s+(claim|believe|argue|assert)\b"),
    ("VAGUE_PERSON", r"\b(people|folks)\s+(often|usually|sometimes)\s+(say|think|believe)\b"),
    ("VAGUE_PERSON", r"\bone\s+(expert|study|researcher)\s+(said|noted|wrote|argued)\b"),
    # NOMINALIZATION (EN)
    ("NOMINALIZATION", r"\bthe\s+(implementation|consideration|application|exploration|investigation|examination|optimization|enhancement)\s+of\b"),
    ("NOMINALIZATION", r"\bin\s+the\s+process\s+of\s+(implementing|considering|exploring|investigating|examining|optimizing|enhancing|understanding|learning|transforming)\b"),
    # SUPERLATIVE_OVERLOAD (EN)
    ("SUPERLATIVE_OVERLOAD", r"\bthe\s+(most|single\s+most)\s+(important|critical|significant|essential|fundamental)\s+(thing|point|moment|aspect|factor)\b"),
    ("SUPERLATIVE_OVERLOAD", r"\bone\s+of\s+the\s+(most|biggest|greatest)\s+\w+\s+(of|in)\s+our\s+(time|era|generation)\b"),
    ("SUPERLATIVE_OVERLOAD", r"\bnever\s+before\s+(has|have)\s+\w+\s+been\s+\w+\b"),
    # AI_QA (EN — already has some; add more)
    ("AI_QA", r"\bsounds?\s+familiar\?"),
    ("AI_QA", r"\bnow\s+imagine\b"),
    ("AI_QA", r"\blet'?s\s+be\s+honest\b"),
    ("AI_QA", r"\bhere'?s\s+the\s+thing\b"),
    ("AI_QA", r"\bsounds?\s+counter[-\s]?intuitive\?"),
    # ─── SYNTHETIC — fake AI authenticity (see references/synthetic-constructions.md) ───
    # Name-dropping templates (RU): noun-of-profession + из + city + transfer verb
    ("SYNTHETIC", r"\b(терапевт|тренер|наставник|психолог|коуч|хирург|предприниматель|инвестор|консультант|эксперт)\s+из\s+[А-ЯЁ]\w+\s+(сказал\w?|рассказал\w?|нарисовал\w?|показал\w?|объяснил\w?|написал\w?)"),
    ("SYNTHETIC", r"\bнаставник\s+(из|с)\s+\d+\s+(года|лет)\s+стаж\w*"),
    ("SYNTHETIC", r"\bодин\s+(предприниматель|инвестор|стартапер|основатель)\s+(сказал|садился|пришёл|рассказал)"),
    ("SYNTHETIC", r"\bна\s+коворкинге\s+в\s+[А-ЯЁ]\w+"),
    # Name-dropping templates (EN)
    ("SYNTHETIC", r"\ba\s+(therapist|coach|trainer|surgeon|entrepreneur|investor|consultant|founder)\s+from\s+[A-Z]\w+\s+(told|said|showed|explained)"),
    ("SYNTHETIC", r"\ba\s+(coach|trainer|expert)\s+with\s+\d+\s+years?\s+(of\s+)?experience\s+(said|told)"),
    # CTA stamps
    ("SYNTHETIC", r"\bесли\s+это\s+про\s+(вас|тебя),?\s+пишите\s+(ДА|да)\b"),
    ("SYNTHETIC", r"\bнапишите\s+в\s+комментах\b"),
    ("SYNTHETIC", r"\bif\s+this\s+resonates,?\s+(drop|leave)\s+a\s+comment\b"),
    ("SYNTHETIC", r"\btag\s+someone\s+who\s+needs\s+this\b"),
    ("SYNTHETIC", r"\bsave\s+this\s+for\s+later\b"),
    # Formula metaphors
    ("SYNTHETIC", r"\bработает\s+как\s+радар\b"),
    ("SYNTHETIC", r"\bкак\s+маяк\s+в\s+тумане\b"),
    ("SYNTHETIC", r"\bworks\s+like\s+a\s+radar\b"),
    ("SYNTHETIC", r"\bacts\s+as\s+a\s+compass\b"),
    ("SYNTHETIC", r"\bserves?\s+as\s+a\s+beacon\b"),
    # Red flags / Green flags list templates
    ("SYNTHETIC", r"\b\d+\s+(красн\w+|зелён\w+)\s+флаг\w+"),
    ("SYNTHETIC", r"\b\d+\s+(red|green)\s+flags?\s+(of|in|to)"),
    # Coaching jargon
    ("SYNTHETIC", r"\bосознанн(о|ое|ой|ого|ость)\b"),
    # Pseudo-vulnerability / faux-confession templates
    ("SYNTHETIC", r"\bя\s+тоже\s+через\s+это\s+прошёл\b"),
    ("SYNTHETIC", r"\bи\s+тогда\s+я\s+понял\b"),
    ("SYNTHETIC", r"\bперелом\s+случился\b"),
    ("SYNTHETIC", r"\bI\s+made\s+every\s+mistake\s+in\s+the\s+book\b"),
    ("SYNTHETIC", r"\bI\s+was\s+that\s+person\s+who\b"),
    ("SYNTHETIC", r"\bit\s+took\s+me\s+\d+\s+years?\s+to\s+(figure|realize|understand)"),
    # Synthetic constructions (templates that signal AI "depth")
    ("SYNTHETIC", r"\bза\s+этим\s+стоит\b"),
    ("SYNTHETIC", r"\bкоторую\s+стоит\s+разобрать\b"),
    ("SYNTHETIC", r"\bэто\s+не\s+хорошо\s+и\s+не\s+плохо\b"),
    ("SYNTHETIC", r"\bпросто\s+так\s+работает\b"),
    # ─── MARKETING_HYPE (EN + RU) ───
    # Superlatives that signal marketing rather than substance. Common in landing
    # pages and release notes; explicitly banned in landing-copy/release-notes
    # banned-patterns.md but absent from the base linter until now.
    ("MARKETING_HYPE", r"\brevolutionary\b"),
    ("MARKETING_HYPE", r"\bgame[- ]chang(ing|er)\b"),
    ("MARKETING_HYPE", r"\bworld[- ]class\b"),
    ("MARKETING_HYPE", r"\bindustry[- ]leading\b"),
    ("MARKETING_HYPE", r"\bcutting[- ]edge\b"),
    ("MARKETING_HYPE", r"\bbest[- ]in[- ]class\b"),
    ("MARKETING_HYPE", r"\bgroundbreaking\b"),
    ("MARKETING_HYPE", r"\bnext[- ]generation\b"),
    ("MARKETING_HYPE", r"\bstate[- ]of[- ]the[- ]art\b"),
    ("MARKETING_HYPE", r"\bunparalleled\b"),
    ("MARKETING_HYPE", r"\bunmatched\b"),
    # RU (standalone — AI_INTENSIFIER catches революционн+noun, this catches bare adjective)
    ("MARKETING_HYPE", r"\bмирового\s+класса\b"),
    ("MARKETING_HYPE", r"\bлидер(а|ом)?\s+отрасли\b"),
    ("MARKETING_HYPE", r"\bпрорывн(ой|ая|ое|ые)\b"),
    # ─── EMPTY_CTA ───
    # CTAs without verb context — common in landing copy and microcopy. Forces
    # the author to commit to a specific action (verb + object).
    ("EMPTY_CTA", r"\b(click|tap)\s+(here|us|now)\b"),
    ("EMPTY_CTA", r"\b(learn|read|find\s+out)\s+more\b(?!\s+about)"),
    ("EMPTY_CTA", r"\bget\s+started\b(?!\s+with\s+)"),
    # RU
    ("EMPTY_CTA", r"\bнажмите\s+(здесь|сюда|тут)\b"),
    ("EMPTY_CTA", r"\bузнайте\s+(больше|подробнее)\b(?!\s+о)"),
    # ─── WEAK_OPENER ───
    # Sentence-initial excitement preambles ("We're excited to announce") that
    # add no information. Strip them and lead with the actual change.
    ("WEAK_OPENER", r"(?m)^\s*we['’]re\s+(excited|thrilled|proud|delighted|pleased|happy)\s+to"),
    ("WEAK_OPENER", r"(?m)^\s*we\s+are\s+(excited|thrilled|proud|delighted|pleased)\s+to"),
    # RU
    ("WEAK_OPENER", r"(?m)^\s*мы\s+(рады|счастлив\w*|горды|с\s+гордостью)"),
    ("WEAK_OPENER", r"(?m)^\s*(с\s+радостью|с\s+удовольствием)\s+(объявля|сообщ|представля)"),
    # ─── VAGUE_BENEFIT ───
    # Generic productivity claims without numbers. Replace with specific metric
    # ("60% review-time reduction") or remove.
    ("VAGUE_BENEFIT", r"\bsave\s+(you\s+)?time\b"),
    ("VAGUE_BENEFIT", r"\bboost\s+productivity\b"),
    ("VAGUE_BENEFIT", r"\bget\s+more\s+done\b"),
    ("VAGUE_BENEFIT", r"\bstreamline\s+your\s+workflow\b"),
    ("VAGUE_BENEFIT", r"\bsupercharge\s+your\b"),
    ("VAGUE_BENEFIT", r"\blevel\s+up\s+your\b"),
    # RU
    ("VAGUE_BENEFIT", r"\bэконом(ит|ьте|им|ия)\s+врем(я|ени|енем)\b"),
    ("VAGUE_BENEFIT", r"\bповыша(ет|йте)\s+продуктивност\w*"),
    # ─── WRONG_TENSE_RELEASE ───
    # Future tense for already-shipped work (release-notes anti-pattern).
    # "will support" → "supports". Advisory severity (some legitimate uses exist
    # for upcoming/deprecated callouts).
    ("WRONG_TENSE_RELEASE", r"\bwill\s+(support|enable|provide|introduce|allow|enhance)\b"),
    # ─── THERAPEUTIC — pseudo-therapeutic register ───
    # The model imitates empathy with self-help support formulas. In a text that
    # is not about psychology they read as a borrowed voice. Distinct from
    # SELFHELP (motivational imperatives) — this is fake *care*, not fake drive.
    ("THERAPEUTIC", r"\bи\s+это\s+(нормально|окей|ок)\b"),
    ("THERAPEUTIC", r"\bвы\s+не\s+одинок(и|а)\b"),
    ("THERAPEUTIC", r"\bты\s+не\s+один\s+такой\b"),
    ("THERAPEUTIC", r"\bдавайте\s+признаем\b"),
    ("THERAPEUTIC", r"\bпозвольте\s+себе\b"),
    ("THERAPEUTIC", r"\bэто\s+абсолютно\s+естественно\b"),
    ("THERAPEUTIC", r"\bбудьте\s+к\s+себе\s+добрее\b"),
    ("THERAPEUTIC", r"\band\s+that'?s\s+(okay|ok|fine)\b"),
    ("THERAPEUTIC", r"\byou'?re\s+not\s+alone\b"),
    ("THERAPEUTIC", r"\bgive\s+yourself\s+permission\b"),
    ("THERAPEUTIC", r"\bbe\s+gentle\s+with\s+yourself\b"),
    # ─── CALQUE_COLLOCATION — calqued word pairing ───
    # Every word is Russian, the pairing is English. The model picks the word via
    # the nearest English semantic field instead of Russian collocation. Distinct
    # from ru-calques.md word swaps, which list direct borrowings
    # ("имплементировать"); here the borrowing is the *combination*.
    ("CALQUE_COLLOCATION", r"\bадресова(ть|л|ла|ли|н\w*)\s+(проблем|вопрос|задач|риск)\w*"),
    ("CALQUE_COLLOCATION", r"\bдостав(ить|ил\w*|ляет|ляем)\s+(ценност|результат|качеств)\w*"),
    ("CALQUE_COLLOCATION", r"\bвстрет(ить|ил\w*)\s+(дедлайн|срок|ожидани)\w*"),
    ("CALQUE_COLLOCATION", r"\bуточн(ить|ил\w*)\s+\w+\s+усили\w+"),
    ("CALQUE_COLLOCATION", r"\bоснование\s+(науки|дисциплины|индустрии)\b"),
    ("CALQUE_COLLOCATION", r"\bсильн(ое|ые)\s+мнени(е|я)\b"),
    ("CALQUE_COLLOCATION", r"\bделать\s+смысл\b"),
    # ─── DANGLING_GERUND — gerund clause that lost its subject ───
    # "Используя метод, результаты улучшаются" — results cannot use a method.
    # Two deliberate narrowings keep this at zero false positives:
    #   1. a closed list of gerunds, not a suffix guess. "-ая/-яя" would also
    #      match ordinary adjectives ("Красивая работа, можно гордиться").
    #   2. a required impersonal / inanimate head after the comma. A sound gerund
    #      sharing its subject with the main verb ("Уйдя со службы, он стал
    #      писать") therefore cannot match.
    ("DANGLING_GERUND",
     r"(?:^|(?<=[.!?]\s))\s*(?:используя|применяя|сравнив|анализируя|рассматривая|"
     r"учитывая|принимая|изучая|оценивая|внедряя|разрабатывая|обобщая|суммируя|"
     r"основываясь|опираясь|исходя|проанализировав|рассмотрев|оценив|изучив)"
     r"[^,.\n]{0,60},\s*"
     r"(?:становится|стало|можно|нельзя|следует|стоит|видно|ясно|получается|"
     r"наблюдается|отмечается|результат\w*|эффективност\w*|качеств\w*|"
     r"показател\w*|вывод\w*)\b"),
]

# Severity per category. Default "caution" for any category not listed.
# blocker — flag prominently (count toward neuroslop threshold)
# caution — standard flag (count toward borderline threshold)
# nit     — advisory only (does NOT trigger borderline alone)
SEVERITY: dict[str, str] = {
    "MARKETING_HYPE": "caution",
    "EMPTY_CTA": "caution",
    "WEAK_OPENER": "caution",
    "VAGUE_BENEFIT": "caution",
    "WRONG_TENSE_RELEASE": "nit",
    "TYPOGRAPHY": "nit",
    # Hard bans and copy-paste artifacts — see HARD_BANS / ARTIFACTS below.
    "COPYPASTE_ARTIFACT": "blocker",
    "EM_DASH_RU": "blocker",
    "MATH_SIGN_PROSE": "blocker",
    "NEG_PARALLEL": "blocker",
    "CHOPPED_DRAMA": "blocker",
}

COMPILED = [(cat, re.compile(p, re.IGNORECASE)) for cat, p in PATTERNS]

# ---------------------------------------------------------------------------
# Class A — chatbot copy-paste artifacts
# ---------------------------------------------------------------------------
# Service markers that reach a text only by copying out of a chat UI. No editor
# and no autocorrect produces them, so a single hit is proof of paste — it does
# not need corroborating soft signals. Scanned against the raw text (URLs must
# survive, that is where utm_source lives) but NOT inside backticks: quoting an
# artifact in documentation is not the same as pasting one.
#
# Ported from smixs/humanizer-ru (MIT), which credits Vladimir-Human/humanizer-ru
# and petergyang/no-ai-slop (both MIT).
ARTIFACTS: list[tuple[str, str]] = [
    ("oaicite footnote", r":contentReference\[oaicite:\d+\]|oai_citation:\d+‡|\boaicite:\d+"),
    ("turn marker", r"\bturn\d+(?:search|file|fetch|image|news|video|ref)\d+|citeturn"),
    ("chatbot utm/referrer", r"utm_source=(?:chatgpt|copilot)\.com|referrer=grok\.com"),
    ("grok card", r"grok_card://|grok_render_citation_card_json|<grok-card\b"),
    ("gemini citation",
     r"vertexaisearch\S*grounding-api-redirect|\[cite_start\]|\[cite:\s*\d+|\[span_\d+\]"),
    ("internal footnote", r"【\d+†[^】]*】|\]\(sandbox:/mnt/data/"),
    ("reasoning leftover", r"</?think>"),
    ("perplexity upload", r"ppl-ai-file-upload"),
    ("unfilled placeholder",
     r"INSERT_SOURCE_URL|PASTE_\w+_URL_HERE|\bURL_HERE\b|\b20\d\d-XX-XX\b"),
    ("PUA marker", r"[-]"),
]
ARTIFACTS_COMPILED = [(label, re.compile(p)) for label, p in ARTIFACTS]

# Zero-width characters are class B, not A: newsletters and CMSs inject them too,
# so they warrant a look at the source rather than an automatic verdict. ZWJ
# (U+200D) inside an emoji sequence is legitimate — matched only outside emoji.
EMOJI_CH = "[\U0001F000-\U0001FAFF☀-➿️\U0001F3FB-\U0001F3FF]"
ZERO_WIDTH = re.compile(
    r"[​‌⁠﻿]|(?<!%s)‍|‍(?!%s)" % (EMOJI_CH, EMOJI_CH)
)

# ---------------------------------------------------------------------------
# Hard bans — the gate
# ---------------------------------------------------------------------------
# These are not density signals, they are pass/fail. `ru_only` bans apply only to
# lines containing Cyrillic: an em-dash is banned in Russian prose (see
# references/typography.md) and perfectly legitimate in English.
HARD_BANS: list[tuple[str, str, bool]] = [
    # (category, pattern, ru_only)
    ("EM_DASH_RU", r"[—–]", True),
    ("MATH_SIGN_PROSE", r"(?:[≈≥≤≠±⇒←→]|\s[=><&+]\s|\bvs\.?\b)", True),
    # Negative parallelism. Only the *completed* contrast is a blocker — a bare
    # "не только" without its "но и" stays a caution under NE_X_A_Y, because
    # ordinary Russian speech uses it without the AI cadence.
    ("NEG_PARALLEL", r"[Нн]е\s+только\b[^.!?\n]{0,80}?\bно\s+и\b", True),
    ("NEG_PARALLEL", r"[Ээ]то\s+не\s+просто\b", True),
    ("NEG_PARALLEL", r"[Нн]е\s+просто\b[^.!?\n]{0,60}?,\s*а\s+\w", True),
    ("NEG_PARALLEL", r"[Рр]ечь\s+идёт\s+не\s+только", True),
    ("NEG_PARALLEL", r"[Нн]ет\s+[^,.!?\n]{1,40},\s*нет\s+", True),
    # "Без кода. Без настроек. Только результат." — manufactured drama.
    ("CHOPPED_DRAMA", r"(?:Без|Ноль)\s+[^.!?\n]{1,35}[.!]\s+(?:Без|Ноль)\s+", True),
]
HARD_BANS_COMPILED = [(cat, re.compile(p), ru_only) for cat, p, ru_only in HARD_BANS]

CYRILLIC = re.compile(r"[а-яёА-ЯЁ]")
# Markdown bullets and blockquote markers are not prose punctuation: strip the
# leading marker before scanning, or "> цитата" trips MATH_SIGN_PROSE.
MD_MARKER = re.compile(r"^\s*[>+*]\s")
INLINE_CODE = re.compile(r"`[^`\n]+`")
URL = re.compile(r"https?://\S+")
BOLD_SPAN = re.compile(r"\*\*[^*\n]+\*\*")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")
NON_PROSE_LINE = re.compile(r"^\s*(#|\||[-*+]\s|\d+\.\s|>)")

# Hedging cascade: three or more softeners inside one sentence. One or two are
# ordinary careful speech and must not fire.
SOFTENERS_RU = (
    "возможно", "вероятно", "по-видимому", "как правило", "в некоторых случаях",
    "скорее всего", "при определённых условиях", "обычно", "в зависимости от",
    "в большинстве случаев", "потенциально", "в целом", "как бы",
)
SOFTENERS_EN = (
    "perhaps", "possibly", "arguably", "generally", "in some cases", "typically",
    "more or less", "to some extent", "in most cases", "potentially", "somewhat",
)

# Colon reveal: "подводка: драматичное раскрытие". Only explicit setups, so plain
# lists and labels ("Список покупок: хлеб, молоко") do not fire.
COLON_REVEAL = re.compile(
    r"(?:[Сс]амое\s+(?:интересное|главное|важное)|[Лл]учшая\s+часть|[Гг]лавная\s+деталь|"
    r"[Фф]ишка\s+в\s+том|[Дд]еталь,\s+которая\s+[^:\n]{0,35}|"
    r"[Hh]ere'?s\s+the\s+(?:best|kicker|catch)|[Tt]he\s+best\s+part)\s*:"
)

# Verb echo (RU): stem heuristic over verb suffixes — no morphology library is
# pulled in for one check. Known limitation: nouns ending in the same letters
# ("результат" → "результ") can produce a false pair. That is acceptable for a
# caution-level signal meant to be judged in clusters, and is why this is not a
# blocker. Upgrade to pymorphy if the false-positive rate becomes a nuisance.
VERB_SUFFIX = re.compile(r"(ует|яет|ает|еет|ит|ат|ят|ют|ал|ял|ил|ел|ся|сь|ть)$")


@dataclass
class Hit:
    line: int
    col: int
    category: str
    match: str
    severity: str = "caution"

    def to_dict(self) -> dict:
        return {
            "line": self.line,
            "col": self.col,
            "category": self.category,
            "severity": self.severity,
            "match": self.match,
        }


@dataclass
class Report:
    hits: list[Hit] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.hits)

    @property
    def by_category(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for h in self.hits:
            out[h.category] = out.get(h.category, 0) + 1
        return out

    @property
    def by_severity(self) -> dict[str, int]:
        out: dict[str, int] = {"blocker": 0, "caution": 0, "nit": 0}
        for h in self.hits:
            out[h.severity] = out.get(h.severity, 0) + 1
        return out

    @property
    def hard_bans(self) -> int:
        return sum(1 for h in self.hits if h.severity == "blocker")

    def gate(self) -> str:
        """Pass/fail on hard bans, orthogonal to the density verdict."""
        return "fail" if self.hard_bans else "pass"

    def verdict(self) -> tuple[int, str]:
        # Nit-only hits don't escalate verdict.
        non_nit_total = sum(1 for h in self.hits if h.severity != "nit")
        cats = {}
        for h in self.hits:
            if h.severity == "nit":
                continue
            cats[h.category] = cats.get(h.category, 0) + 1
        max_per_cat = max(cats.values(), default=0)
        if non_nit_total >= 5 or max_per_cat >= 3:
            return 2, "neuroslop suspected"
        if non_nit_total >= 2:
            return 1, "borderline"
        return 0, "clean"


def _mask_code_blocks(text: str) -> str:
    """Replace lines inside fenced code blocks with empty strings.

    Why: linter scans line-by-line and would otherwise flag "revolutionary" or
    "click here" inside code examples and command output. Markdown fences open
    with ``` or ~~~ at line start (after optional indent); the same delimiter
    closes the block.
    """
    out: list[str] = []
    fence: str | None = None  # active fence marker, or None
    for line in text.splitlines():
        stripped = line.lstrip()
        if fence is None:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence = stripped[:3]
                out.append("")
                continue
            out.append(line)
        else:
            out.append("")
            if stripped.startswith(fence):
                fence = None
    return "\n".join(out)


def _strip_inline_code(text: str) -> str:
    """Blank out `inline code` spans, preserving line and column positions.

    Why: an artifact quoted in documentation (``the `turn0search0` marker``) is a
    citation, not a paste. Replacing with spaces keeps reported columns honest.
    """
    return INLINE_CODE.sub(lambda m: " " * len(m.group(0)), text)


def _prose_sentences(lines: list[str]) -> list[str]:
    """Sentences from prose lines only — no headings, tables, lists, quotes."""
    prose = " ".join(l for l in lines if l.strip() and not NON_PROSE_LINE.match(l))
    prose = URL.sub(" ", prose)
    prose = re.sub(r"\*\*|«|»", "", prose)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", prose) if s.strip()]


def _verb_stems(sentence: str) -> set[str]:
    stems = set()
    for w in re.findall(r"[а-яё]{5,}", sentence.lower()):
        if VERB_SUFFIX.search(w):
            stems.add(VERB_SUFFIX.sub("", w)[:6])
    return {s for s in stems if len(s) >= 4}


def _content_stems(text: str) -> set[str]:
    """Crude prefix stems, so «производительность» matches «производительности».

    Six characters is enough to separate distinct roots without pulling in a
    morphology library; inflection lives past that boundary in both RU and EN.
    """
    return {w[:6] for w in re.findall(r"[^\W\d_]{4,}", text.lower())}


def _structural_hits(text: str, lines: list[str]) -> list[Hit]:
    """Document-level checks that regex-per-line cannot express.

    These carry line=0: they describe the text as a whole, not one location.
    """
    hits: list[Hit] = []

    def add(category: str, message: str, line: int = 0) -> None:
        hits.append(
            Hit(line=line, col=0, category=category,
                severity=SEVERITY.get(category, "caution"), match=message)
        )

    sentences = _prose_sentences(lines)
    lengths = [len(s.split()) for s in sentences]

    # Rhythm (burstiness). Human prose varies sentence length sharply; an LLM
    # holds a near-constant width. This is the one AI tell regex cannot see.
    if len(lengths) >= 8:
        diffs = [abs(a - b) for a, b in zip(lengths, lengths[1:])]
        mean_diff = sum(diffs) / len(diffs)
        if mean_diff < 4:
            add("RHYTHM_MONOTONE",
                f"adjacent sentence lengths differ by {mean_diff:.1f} words on "
                f"average (live prose: 6+)")
        if len(lengths) >= 10 and not any(l <= 8 for l in lengths):
            add("RHYTHM_NO_SHORT",
                f"no sentence under 9 words across {len(lengths)} sentences — "
                f"no pauses, no accents")

    # Hedging cascade — three or more softeners inside a single sentence.
    for s in sentences:
        low = s.lower()
        n = sum(low.count(w) for w in SOFTENERS_RU) + sum(low.count(w) for w in SOFTENERS_EN)
        if n >= 3:
            add("HEDGE_CASCADE", f"{n} softeners in one sentence: {s[:60]}")

    # Colon reveal — a drum roll before an ordinary statement. Write the payoff
    # as a plain sentence instead.
    for line_idx, line in enumerate(lines, start=1):
        for m in COLON_REVEAL.finditer(line):
            hits.append(
                Hit(line=line_idx, col=m.start() + 1, category="COLON_REVEAL",
                    severity="caution", match=m.group(0)[:60])
            )

    # Verb echo across adjacent sentences (RU). The repetition penalty makes the
    # model vary nouns (hence synonym cycling) while it *duplicates* verbs into
    # parallel constructions — "X предлагает… Y предлагает…". A human reaches for
    # a different verb without thinking about it.
    for a, b in zip(sentences, sentences[1:]):
        shared = _verb_stems(a) & _verb_stems(b)
        if shared:
            add("VERB_ECHO",
                f"«{sorted(shared)[0]}…» repeats in adjacent sentences: {b[:50]}")

    # Bold density — roughly one bold span per 200 words. Above that, formatting
    # is standing in for content.
    words_total = sum(lengths)
    bold = len(BOLD_SPAN.findall(text))
    if words_total >= 200 and bold > words_total / 200 + 1:
        add("BOLD_DENSITY",
            f"{bold} bold spans across {words_total} words "
            f"(budget ~{max(1, words_total // 200)})")

    # Heading echo — the line after a heading restates it, a warm-up lap before
    # the actual content. Delete the line; the heading already said it.
    #
    # Only the literal-repeat variant is detectable here. The semantic variant
    # («## Производительность» → «Скорость имеет значение.») shares no stems and
    # stays LLM territory — see references/structural-prose.md.
    #
    # The discriminator is *restates vs. adds*, not overlap. A section's opening
    # sentence naturally reuses the section's topic word and is not an echo:
    # "## Where the canon may live" / "Non-fiction projects split canon across
    # two sources:" shares stems but introduces five new ones. An echo introduces
    # almost nothing. Counting shared stems alone flagged ordinary documentation.
    for idx, line in enumerate(lines):
        m = HEADING.match(line)
        if not m:
            continue
        # Backticked spans are identifiers, not prose. "In `Physical invariants`:"
        # under a "Physical invariant" heading is a cross-reference, not an echo.
        title_stems = _content_stems(INLINE_CODE.sub(" ", m.group(1)))
        if not title_stems:
            continue
        for offset, nxt in enumerate(lines[idx + 1: idx + 4]):
            if not nxt.strip():
                continue
            if NON_PROSE_LINE.match(nxt):
                break
            # A real paragraph reusing the term is normal prose. The tell is a
            # short standalone line that carries nothing but the heading again.
            if len(nxt.split()) > 12:
                break
            body_stems = _content_stems(INLINE_CODE.sub(" ", nxt))
            if not body_stems:
                break
            shared = title_stems & body_stems
            introduced = body_stems - title_stems
            if shared and len(introduced) <= 2:
                add("HEADING_ECHO",
                    f"line restates the heading «{m.group(1)[:40]}»",
                    line=idx + offset + 2)
            break

    return hits


def scan(text: str, skip_code_blocks: bool = True, fiction: bool = False) -> Report:
    """Scan text. `fiction` demotes the em-dash ban from blocker to nit.

    Why the exception: references/typography.md bans the em-dash in Russian prose
    and viral posts, but explicitly leaves it alone in book typesetting. In
    fiction the em-dash also opens dialogue lines, so a blanket blocker would
    flag every line of speech.
    """
    report = Report()
    scanned = _mask_code_blocks(text) if skip_code_blocks else text
    lines = scanned.splitlines()

    # Pass 1 — class A artifacts. Run against the raw (code-masked) text so URLs
    # survive; backticked spans are blanked so quoting an artifact is not a hit.
    artifact_source = _strip_inline_code(_mask_code_blocks(text)).splitlines()
    for line_idx, line in enumerate(artifact_source, start=1):
        for label, regex in ARTIFACTS_COMPILED:
            for m in regex.finditer(line):
                report.hits.append(
                    Hit(line=line_idx, col=m.start() + 1, category="COPYPASTE_ARTIFACT",
                        severity="blocker", match=f"{label}: {m.group(0)[:60]}")
                )
        for m in ZERO_WIDTH.finditer(line):
            report.hits.append(
                Hit(line=line_idx, col=m.start() + 1, category="ZERO_WIDTH",
                    severity="caution",
                    match="invisible character (CMSs and newsletters inject these "
                          "too — check the source)")
            )

    # Pass 2 — hard bans and the phrase catalogue, line by line.
    for line_idx, line in enumerate(lines, start=1):
        probe = MD_MARKER.sub("  ", line)
        is_ru = bool(CYRILLIC.search(probe))
        for cat, regex, ru_only in HARD_BANS_COMPILED:
            if ru_only and not is_ru:
                continue
            sev = "nit" if (fiction and cat == "EM_DASH_RU") else "blocker"
            for m in regex.finditer(probe):
                report.hits.append(
                    Hit(line=line_idx, col=m.start() + 1, category=cat,
                        severity=sev, match=m.group(0)[:80])
                )
        for cat, regex in COMPILED:
            for m in regex.finditer(line):
                report.hits.append(
                    Hit(
                        line=line_idx,
                        col=m.start() + 1,
                        category=cat,
                        severity=SEVERITY.get(cat, "caution"),
                        match=m.group(0)[:80],
                    )
                )

    # Pass 3 — document-level structure and rhythm.
    report.hits.extend(_structural_hits(scanned, lines))
    report.hits.sort(key=lambda h: (h.line, h.col, h.category))
    return report


def format_human(report: Report) -> str:
    if not report.hits:
        return "writer-lint: clean (0 hits), gate passed\n"
    out: list[str] = []
    code, label = report.verdict()
    out.append(f"writer-lint: {label} ({report.total} hits)")
    if report.hard_bans:
        out.append(
            f"GATE FAILED — {report.hard_bans} hard ban(s). Fix these first, "
            f"then re-run; the density verdict is secondary."
        )
    else:
        out.append("gate passed: no hard bans.")
    out.append("")
    out.append("By category:")
    for cat, n in sorted(report.by_category.items(), key=lambda kv: -kv[1]):
        out.append(f"  {cat:<22} {n}")
    out.append("")
    out.append("Hits:")
    for h in report.hits[:200]:
        out.append(f"  L{h.line}:{h.col}  [{h.severity:<7}] {h.category:<22}  {h.match!r}")
    if len(report.hits) > 200:
        out.append(f"  ... and {len(report.hits) - 200} more")
    return "\n".join(out) + "\n"


def read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline regex linter for the writer skill.")
    parser.add_argument("path", help="Path to text file, or '-' for stdin")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--scan-code-blocks",
        action="store_true",
        help="Also scan inside fenced code blocks (default: skipped).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only emit when verdict is not clean.",
    )
    parser.add_argument(
        "--fiction",
        action="store_true",
        help=("Fiction / book-typesetting mode: demote the RU em-dash ban to an "
              "advisory nit (dialogue dashes are legitimate there)."),
    )
    args = parser.parse_args(argv)

    text = read_input(args.path)
    report = scan(text, skip_code_blocks=not args.scan_code_blocks, fiction=args.fiction)
    code, label = report.verdict()

    if args.json:
        print(
            json.dumps(
                {
                    "verdict": label,
                    "gate": report.gate(),
                    "total": report.total,
                    "hard_bans": report.hard_bans,
                    "by_category": report.by_category,
                    "by_severity": report.by_severity,
                    "hits": [h.to_dict() for h in report.hits],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif not (args.quiet and code == 0 and not report.hard_bans):
        sys.stdout.write(format_human(report))

    # A hard ban outranks the density verdict: a text can be sparse in slop and
    # still carry one pasted `turn0search3`.
    return 3 if report.hard_bans else code


if __name__ == "__main__":
    sys.exit(main())
