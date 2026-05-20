# OUTPUT FORMAT

Структурированный отчёт, по файлу — по группам нарушений.

```
=== style-check ===
Mode: staged | last | range <a>..<b> | file <path>
Routing: writer + prose-edit | writer + essay-write | writer only

[FILE 1] books/era-arkhitektorov/ru/chapters/ch07.tex
  Routing: writer + prose-edit
  ----
  L142 STACCATO  «А.Б. так делал. Он шёл. Он молчал.»
                 → 3+ односоставных подряд (writer L2)

  L156 NEURAL_METAPHOR  «теория трещит по швам»
                        → нейрослоп (writer L1 cat 22). Заменить: «теория не выдерживает»

  L201 TAVTOLOGY  «открытое открытие»
                  → корень-в-корне (prose-edit cleanness #5)

  L256 CANON_DRIFT  упоминание хвата Ирэн — сверить со story-bible §3.2
                    (prose-edit canon check)

  L289 META_REF  «как в гл. 4 АБ»
                 → запрещены ссылки на свои же книги в голосе рассказчика

  L312 ANGLICISM  «post-door»
                  → латиница в авторском голосе

[FILE 2] books/heavenly-code/ru/chapters/ch03.tex
  Routing: writer + essay-write
  ----
  L42 UNCITED_CLAIM  «исследования показывают, что»
                     → нет конкретного источника (essay-write sourcing)

  L88 ACADEMIC_PATHOS  «рассмотрим следующий аспект»
                       → лекторский тон (essay-write bans)

  L115 METAPHOR_OVERLOAD  7 сравнений на главу (рекомендация 3-5)

  L142 VIRAL_FORMAT  numbered list «1. / 2. / 3.»
                     → виральный приём в нон-фикшн

=== SUMMARY ===
Files checked: 2
Total violations:
  - writer L1 (regex 20 cats): 1
  - writer L2 (structural): 2
  - prose-edit художественный слой: 3
  - essay-write нон-фикшн слой: 4

Severity:
  - BLOCKING (нужно поправить до коммита): canon drift, uncited claim
  - WARNING (стоит посмотреть): staccato, neural metaphor, tavtology, meta-ref, anglicism, academic pathos, viral format
  - INFO (на усмотрение автора): metaphor overload
```
