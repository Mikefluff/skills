# Sample Report

> **CALIBRATION SAMPLE** — what the skill's report looks like. Do NOT use as a real audit.

```
=== canon-check ===
Mode: chapter god-academy ch07
Bible: books/god-academy/notes/story-bible.tex
Bible version: v3.2 (Май 2026)
Entities extracted: 14 (8 characters, 4 artifacts, 2 locations)

----------------------------------------------------------------
[BLOCKING] books/god-academy/ru/chapters/ch07.tex:142
  Entity: Ирэн (character)
  Class: physical_invariant_drift

  In this chapter:
    L142: «Ирэн взяла чашку левой рукой, обхватив пальцами снизу»

  Bible §3.2 (Физические инварианты):
    «Хват матери: большой и указательный сверху, остальные три снизу.
     Одинаковый для чашки (гл.~21) и детских тапочек.
     Это инвариант подписи, а не описательная деталь.»

  Other chapters confirm canonical хват:
    ch02.tex:88   — «два пальца сверху, три снизу»
    ch04.tex:201  — «привычным жестом, большой и указательный сверху»
    ch21.tex:55   — оригинальная сцена, бэйслайн для хвата

  Fix (decide):
    A) изменить «левой рукой ... снизу» → канонический хват
    B) если это деliberately new — обновить bible §3.2 и пометить как
       пересмотр инварианта (но это финальный канон АБ, осторожно)

----------------------------------------------------------------
[BLOCKING] books/god-academy/ru/chapters/ch07.tex:201
  Entity: рыжая ведьма (character)
  Class: generic_vs_canonical_name_drift

  In this chapter:
    L201: «появилась рыжая ведьма, серьга поблёскивала»

  Bible: NO entry under «рыжая», «ведьма», «Ginger», «Татьяна»

  Other chapters (canonical name established):
    NK/interlude10.tex:88  — «Татьяна Ларина / Ginger / Рыжая Ведьма»
    NK/interlude10.tex:140 — «рыжая с серьгой, янтарные глаза»
    NK/ch05.tex:201        — «ведьма с янтарными глазами»

  Note: персонаж фигурирует в НК (нон-фикшн биография), не в АБ.
  Если эта запись — заимствование биографического образа в художке,
  ASK AUTHOR: канонизировать как АБ-персонажа или вычистить.

  Fix (decide):
    A) добавить bible entry в АБ для «рыжей ведьмы» с консолидированными
       чертами (серьга, янтарные глаза, биография из НК-interlude10)
    B) убрать упоминание из АБ ch07, если это случайное заимствование

----------------------------------------------------------------
[WARNING] books/god-academy/ru/chapters/ch07.tex:256
  Entity: яйцо (artifact)
  Class: cross_chapter_drift

  Bible §3.2 (Локации):
    «Хамовники. Квартира Вэй Лина в АБ. Чёрное каменное яйцо на полке.»

  This chapter:
    L256: «яйцо на столе» (локация в Хамовниках консистентна,
           но переехало с полки на стол)

  Other chapters:
    ch04.tex:88  — «на полке, чёрное, каменное»
    ch11.tex:34  — «на полке, рядом с лампой»

  Class: micro-drift (полка → стол). Возможно осознанное перемещение
  внутри одной локации, возможно случайное.

  Fix (decide):
    A) если осознанно (Вэй Лин переставил для эпизода) — добавить в bible
       уточнение «на полке (по умолчанию) / на столе (только в ch07)»
    B) если случайно — поправить на «полке»

----------------------------------------------------------------
[INFO] books/god-academy/ru/chapters/ch07.tex:312
  Entity: Шаболовка (location)
  Class: canon_expansion

  Bible §3.2 (Локации):
    «Шаболовка, Москва. Однушка Дана, седьмой этаж ИКТ.
     Шуховская башня с табличкой исторический памятник.
     Троллейбус №15 отменён в 2021.»

  This chapter:
    L312: «лифт пах нагретым кабелем, кнопка седьмого этажа западала»

  This is canon expansion (new detail, not contradiction).

  Fix (optional):
    добавить в bible §3.2: «Лифт: западает кнопка 7-го этажа,
    запах нагретого кабеля» — если деталь будет повторяться.

----------------------------------------------------------------

=== SUMMARY ===
Files checked:     1
Entities checked:  14
  - 8 characters (5 with bible entries, 1 missing — «рыжая ведьма»)
  - 4 artifacts  (3 with bible entries, 1 silent — кубитная лаборатория)
  - 2 locations  (2/2 with bible entries)

Findings:
  - BLOCKING: 2 (physical invariant drift, generic-vs-canonical name)
  - WARNING:  1 (cross-chapter micro-drift)
  - INFO:     1 (canon expansion)

Bible coverage: 13/14 entities have entries (missing: рыжая ведьма)

Exit code (pre-commit): 2  (BLOCKING present → would abort commit)
```
