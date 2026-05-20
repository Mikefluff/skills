# ROUTING — какой набор правил применить

По пути проверяемого файла:

```
books/god-academy/{ru,en,pt-br}/chapters/*.tex        → writer + prose-edit
books/era-arkhitektorov/{ru,en,pt-br}/chapters/*.tex  → writer + prose-edit
books/heavenly-code/{ru,en,pt-br}/chapters/*.tex      → writer + essay-write
preprints/**/*.tex                                    → writer (+ essay-write для нарративных секций)
*.md (root, books/*/notes/, etc.)                     → writer
*.tex (root, arcs/, lore/, inserts/, dialogs/)        → writer + prose-edit (это inserts в книги)
любой другой текстовый файл                           → writer
```

Если файл — код (`.py`, `.js`, `.ts`, etc.) — пропустить, это не задача скилла.
