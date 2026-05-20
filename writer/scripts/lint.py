#!/usr/bin/env python3
"""
writer-lint — offline regex linter for the writer skill.

Catches a high-recall subset of the 23 neuroslop categories defined in
writer/SKILL.md. Does NOT replace the full 4-layer cleaning pass — it is meant
as a fast pre-check ("does this draft already look like LLM output?") before
asking Claude to apply writer in clean/apply mode.

Usage:
    python3 lint.py path/to/text.md
    python3 lint.py path/to/text.md --json
    cat text.md | python3 lint.py -

Exit codes:
    0 — clean (0-1 hits)
    1 — borderline (2-4 hits)
    2 — neuroslop suspected (5+ hits OR any category 3+ times)
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
}

COMPILED = [(cat, re.compile(p, re.IGNORECASE)) for cat, p in PATTERNS]


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


def scan(text: str, skip_code_blocks: bool = True) -> Report:
    report = Report()
    scanned = _mask_code_blocks(text) if skip_code_blocks else text
    lines = scanned.splitlines()
    for line_idx, line in enumerate(lines, start=1):
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
    return report


def format_human(report: Report) -> str:
    if not report.hits:
        return "writer-lint: clean (0 hits)\n"
    out: list[str] = []
    code, label = report.verdict()
    out.append(f"writer-lint: {label} ({report.total} hits)")
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
    args = parser.parse_args(argv)

    text = read_input(args.path)
    report = scan(text, skip_code_blocks=not args.scan_code_blocks)
    code, label = report.verdict()

    if args.json:
        print(
            json.dumps(
                {
                    "verdict": label,
                    "total": report.total,
                    "by_category": report.by_category,
                    "by_severity": report.by_severity,
                    "hits": [h.to_dict() for h in report.hits],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif not (args.quiet and code == 0):
        sys.stdout.write(format_human(report))

    return code


if __name__ == "__main__":
    sys.exit(main())
