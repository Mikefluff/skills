# Sample for skills-update flow

Это network-driven скилл; фикстура — пример manifest и diff-описание сценария update.

## Local marker before update

```json
{
  "collection": "Mikefluff/skills",
  "version": "1.5.0",
  "installed_at": "2026-05-01T10:00:00Z",
  "skills": ["writer", "viral-text", "prose-edit"]
}
```

## Remote release tag

v1.7.0 — три новых скилла + RU паритет.

## Expected diff в CHANGELOG

Пользователь видит секции `## [1.6.0]` и `## [1.7.0]` с краткой сводкой Added/Changed.

## User confirmation flow

Skill спрашивает: «Применить v1.7.0? Установлены: writer, viral-text, prose-edit». На «да» запускает `install.sh --update`.
