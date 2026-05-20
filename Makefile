.DEFAULT_GOAL := help
.PHONY: help install install-local update list uninstall check validate smoke lint test coverage check-docs gen-readme install-hook new-skill bump-patch bump-minor bump-major release clean-test

PREFIX ?= $(HOME)/.claude/skills
VERSION := $(shell cat VERSION 2>/dev/null || echo "?")

# ── help ─────────────────────────────────────────────────────────────────

help: ## Show this help
	@printf '\nMikefluff/skills — v$(VERSION)\n\n'
	@printf 'Targets:\n'
	@awk 'BEGIN{FS=":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf '\nVariables (override with VAR=value):\n'
	@printf '  PREFIX     install destination       (default: %s)\n' "$(PREFIX)"
	@printf '\n'

# ── install / update ─────────────────────────────────────────────────────

install: ## Install all skills from this checkout into $(PREFIX)
	bash install.sh --copy-from . --prefix $(PREFIX)

install-local: install ## Alias for install

update: ## Re-install from this checkout, overwriting existing skills
	bash install.sh --copy-from . --prefix $(PREFIX) --update

list: ## List installed skills under $(PREFIX)
	@ls -1 $(PREFIX) 2>/dev/null || echo "(nothing installed)"

uninstall: ## Remove all installed skills + marker (interactive)
	bash install.sh --uninstall --prefix $(PREFIX)

check: ## Compare installed version to latest release
	bash install.sh --check --prefix $(PREFIX)

install-hook: ## Install the status-line update banner (idempotent)
	bash scripts/install-hook.sh

# ── quality gates ────────────────────────────────────────────────────────

validate: ## Validate frontmatter + cross-links of all skills
	bash scripts/validate.sh

smoke: ## Validate + writer linter regression + fixture snapshots
	bash scripts/smoke.sh

test: ## Run snapshot tests on fixtures (writer linter)
	bash tests/run.sh

coverage: ## Show which of the 23 neuroslop categories lint.py detects via regex
	python3 scripts/coverage.py

check-docs: ## Verify skills.json ↔ README ↔ USER-GUIDE ↔ walkthroughs ↔ CHANGELOG
	bash scripts/check-docs-consistency.sh

gen-readme: ## Regenerate the README skills table from skills.json (write in place)
	python3 scripts/gen-skills-table.py --write

lint: ## Run writer offline linter on every skill's examples/
	@for skill in $$(find . -mindepth 1 -maxdepth 1 -type d ! -name '.*' ! -name 'scripts' ! -name 'docs' ! -name 'hooks' ! -name 'tests'); do \
	  if [ -d $$skill/examples ]; then \
	    for f in $$skill/examples/*.md; do \
	      [ -f "$$f" ] || continue; \
	      echo "── $$f ──"; \
	      python3 writer/scripts/lint.py "$$f" || true; \
	      echo; \
	    done; \
	  fi; \
	done

# ── scaffolding ──────────────────────────────────────────────────────────

new-skill: ## Bootstrap a new skill: make new-skill NAME=foo DESC="..." [LAYER=wrapper] [DEPS=writer]
	@[ -n "$(NAME)" ] || (echo "usage: make new-skill NAME=foo-bar DESC=\"...\" [LAYER=wrapper] [DEPS=writer]"; exit 2)
	bash scripts/new-skill.sh $(NAME) $(if $(DESC),--description "$(DESC)") $(if $(LAYER),--layer $(LAYER)) $(if $(DEPS),--deps $(DEPS))

# ── releasing ────────────────────────────────────────────────────────────

bump-patch: ## Bump VERSION (x.y.Z+1) and open a new CHANGELOG section
	bash scripts/bump.sh patch

bump-minor: ## Bump VERSION (x.Y+1.0)
	bash scripts/bump.sh minor

bump-major: ## Bump VERSION (X+1.0.0)
	bash scripts/bump.sh major

release: ## Tag current VERSION and push (assumes VERSION already bumped + committed)
	@v=$$(cat VERSION); \
	if git rev-parse "v$$v" >/dev/null 2>&1; then \
	  echo "tag v$$v already exists"; exit 1; \
	fi; \
	git tag -a "v$$v" -m "release: v$$v" && \
	git push origin "v$$v" && \
	echo "tagged + pushed v$$v — release workflow will fire"

# ── housekeeping ─────────────────────────────────────────────────────────

clean-test: ## Remove any /tmp/skills-* test installations
	rm -rf /tmp/skills-test /tmp/skills-test2
