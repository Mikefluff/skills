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
]

COMPILED = [(cat, re.compile(p, re.IGNORECASE)) for cat, p in PATTERNS]


@dataclass
class Hit:
    line: int
    col: int
    category: str
    match: str

    def to_dict(self) -> dict:
        return {
            "line": self.line,
            "col": self.col,
            "category": self.category,
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

    def verdict(self) -> tuple[int, str]:
        cats = self.by_category
        max_per_cat = max(cats.values(), default=0)
        if self.total >= 5 or max_per_cat >= 3:
            return 2, "neuroslop suspected"
        if self.total >= 2:
            return 1, "borderline"
        return 0, "clean"


def scan(text: str) -> Report:
    report = Report()
    lines = text.splitlines()
    for line_idx, line in enumerate(lines, start=1):
        for cat, regex in COMPILED:
            for m in regex.finditer(line):
                report.hits.append(
                    Hit(
                        line=line_idx,
                        col=m.start() + 1,
                        category=cat,
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
        out.append(f"  L{h.line}:{h.col}  {h.category:<22}  {h.match!r}")
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
    args = parser.parse_args(argv)

    text = read_input(args.path)
    report = scan(text)

    if args.json:
        code, label = report.verdict()
        print(
            json.dumps(
                {
                    "verdict": label,
                    "total": report.total,
                    "by_category": report.by_category,
                    "hits": [h.to_dict() for h in report.hits],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        sys.stdout.write(format_human(report))

    return report.verdict()[0]


if __name__ == "__main__":
    sys.exit(main())
