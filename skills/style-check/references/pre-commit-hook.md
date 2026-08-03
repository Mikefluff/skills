# INTEGRATION — как поставить как pre-commit hook

Скилл сам не ставит хук. Если автор попросит — выдать инструкцию:

```bash
# .git/hooks/pre-commit
#!/usr/bin/env bash
# Вызывает Claude Code с /style-check staged
# (через подходящий враппер CLI)
```

Скилл не редактирует `.git/hooks/` сам — это решает автор.
