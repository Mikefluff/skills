# SEVERITY LEVELS

Категории по серьёзности:

**BLOCKING** — нужно поправить до коммита:
- `CANON_DRIFT` (расхождение со story-bible в ЭА/АБ)
- `UNCITED_CLAIM` (научное утверждение без источника в НК)
- `FABRICATED_SOURCE` (если детектор подозревает выдуманный источник: незнакомый журнал + нет на arXiv/Crossref)
- `BROKEN_LATEX` (синтаксическая ошибка в `.tex`, ломающая билд)

**WARNING** — стоит посмотреть:
- Все writer L1 категории (нейрослоп) с >2 совпадениями
- `STACCATO`, `DOUBLE_NEG`, `INVERSION`, `INCOMPLETE_PREDICATE` (writer L2)
- `TAVTOLOGY`, `META_REF`, `ANGLICISM` (prose-edit)
- `ACADEMIC_PATHOS`, `LECTURER_TONE`, `VIRAL_FORMAT` (essay-write)

**INFO** — на усмотрение автора:
- Writer L1 с 1 совпадением (часто организм)
- `METAPHOR_OVERLOAD` (превышение рекомендации, но не критично)
- `STYLE_DRIFT` (мягкие признаки съезжания голоса)
