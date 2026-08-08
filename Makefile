.DEFAULT_GOAL := help
.PHONY: help install install-local update list uninstall check validate smoke lint lint-all test coverage check-docs check-prices check-descriptions freeze-descriptions gen gen-readme gen-index gen-coverage gen-pricing install-hook install-precommit-hook new-skill bump-patch bump-minor bump-major release clean-test

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

coverage: ## Show which neuroslop categories lint.py detects via regex
	python3 scripts/coverage.py

check-docs: ## Verify skills.json ↔ README ↔ USER-GUIDE ↔ walkthroughs ↔ CHANGELOG ↔ prices
	bash scripts/check-docs-consistency.sh

check-prices: ## Verify every price quoted in a skill doc against cost.PRICE_TABLE
	python3 scripts/check-prices.py

check-descriptions: ## Verify each skills.json blurb was written against the current SKILL.md
	python3 scripts/check-skill-descriptions.py

freeze-descriptions: ## Accept the current SKILL.md descriptions (after re-reading the blurbs)
	python3 scripts/check-skill-descriptions.py --freeze

gen-readme: ## Regenerate the README skills table from skills.json (write in place)
	python3 scripts/gen-skills-table.py --write

gen-launch-baseline: ## Re-freeze the reviewed launch-copy lint baseline
	python3 scripts/check-launch-copy.py --update

gen-coverage: ## Regenerate docs/LINTER-COVERAGE.md from the catalogue + lint.py
	python3 scripts/coverage.py --write

gen-pricing: ## Regenerate common/references/model-pricing.md from cost.PRICE_TABLE
	python3 scripts/gen-pricing.py --write

test-unit: ## Run runner unit tests (stdlib unittest, no deps)
	python3 -m unittest discover -s tests/unit -t . -v

gen-index: ## Regenerate docs/SKILL-INDEX.md from skills.json (write in place)
	python3 scripts/gen-skill-index.py --write

gen: gen-readme gen-index gen-coverage gen-pricing ## Regenerate every derived file at once
	@printf '\ngen: README table, SKILL-INDEX, LINTER-COVERAGE, model-pricing\n'
	@printf 'Now run: make check-docs && make smoke\n\n'

lint: ## Run writer offline linter on every skill's examples/
	@for skill in $$(find skills -mindepth 1 -maxdepth 1 -type d); do \
	  if [ -d $$skill/examples ]; then \
	    for f in $$skill/examples/*.md; do \
	      [ -f "$$f" ] || continue; \
	      echo "── $$f ──"; \
	      python3 skills/writer/scripts/lint.py "$$f" || true; \
	      echo; \
	    done; \
	  fi; \
	done

lint-all: ## Run writer linter across every reference, example, and doc file (quiet)
	@echo "Linting references…"
	@find . -path './node_modules' -prune -o -path './.git' -prune -o -type f -name '*.md' -path '*/references/*' -print 2>/dev/null | xargs -n1 python3 skills/writer/scripts/lint.py --quiet || true
	@echo "Linting examples…"
	@find . -path './node_modules' -prune -o -path './.git' -prune -o -type f -name '*.md' -path '*/examples/*' -print 2>/dev/null | xargs -n1 python3 skills/writer/scripts/lint.py --quiet || true
	@echo "Linting docs…"
	@find docs -type f -name '*.md' 2>/dev/null | xargs -n1 python3 skills/writer/scripts/lint.py --quiet || true
	@echo "lint-all: done (advisory; non-clean reports printed above)"

install-precommit-hook: ## Install local .git/hooks/pre-commit (writer linter on staged .md files)
	bash scripts/install-precommit-hook.sh

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
	if ! grep -q "^## \[$$v\]" CHANGELOG.md; then \
	  echo "CHANGELOG.md has no [$$v] section — run 'make bump-*' first"; exit 1; \
	fi; \
	bash scripts/smoke.sh >/dev/null || { echo "smoke failed — not tagging"; exit 1; }; \
	git tag -a "v$$v" -m "release: v$$v" && \
	git push origin "v$$v" && \
	echo "tagged + pushed v$$v"; \
	$(MAKE) --no-print-directory publish-npm; \
	echo "NOTE: install.sh --version latest resolves the newest GitHub *release*."; \
	echo "      Publish the release for v$$v on GitHub, or curl installs stay on the previous tag."

publish-npm: ## Publish the current VERSION to npm (idempotent; skips if already up there)
	@v=$$(cat VERSION); \
	if npm view "@mikefluff/skills@$$v" version >/dev/null 2>&1; then \
	  echo "npm: @mikefluff/skills@$$v is already published"; exit 0; \
	fi; \
	if ! npm whoami >/dev/null 2>&1; then \
	  echo "npm: not logged in — run 'npm login', then 'make publish-npm'"; \
	  echo "     (the git tag is already pushed; this step is safe to re-run alone)"; \
	  exit 0; \
	fi; \
	npm publish --access public && echo "npm: published $$v"

# ── housekeeping ─────────────────────────────────────────────────────────

clean-test: ## Remove any /tmp/skills-* test installations
	rm -rf /tmp/skills-test /tmp/skills-test2
