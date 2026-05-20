# awesome-claude-code PR

Target list: <https://github.com/hesreallyhim/awesome-claude-code> (or the active awesome-claude-code fork at the time of submission).

Likely section: "Skills" or "Prose / Writing" — check the active README first.

## Short entry (one-line)

```markdown
- [Mikefluff/skills](https://github.com/Mikefluff/skills) — 17 prose / marketing / tech-docs / outreach / visual-prompt skills layered on a Python regex linter that catches 28 categories of LLM-prose tells (EN + RU). MIT.
```

## Long entry (if format expects a paragraph)

```markdown
### Mikefluff/skills

**[github.com/Mikefluff/skills](https://github.com/Mikefluff/skills)** — 17 Claude Code skills for editing prose, marketing copy, release notes, RFCs, cold outreach, and AI image/video prompts without LLM-tells. Built around an offline Python regex linter that catches 28 categories of AI-prose patterns (EN + RU) with severity tags and code-fence-aware scanning. Wrappers: viral-text, prose-edit, essay-write, tone-shifter, pelevin-digression, cold-email, landing-copy, release-notes, rfc-writer, microcopy, image-prompt, video-prompt. Read-only linters: style-check (pre-commit gate), translation-sync (RU↔EN↔PT-BR parity), canon-check (story-bible consistency). MIT. Install via curl, Docker (`ghcr.io/mikefluff/skills`), npm (`@mikefluff/skills`), or Homebrew (`mikefluff/tap/skills`).
```

## PR opening message

```markdown
Adds Mikefluff/skills to the [section name] section.

This is a collection of 17 Claude Code skills that I open-sourced after using them for a year of long-form writing + marketing copy. The base is an offline Python regex linter (`writer/scripts/lint.py`) that catches 28 categories of LLM-prose tells in EN + RU. Twelve wrappers compose on top for different domains (fiction, non-fiction, viral social, cold email, landing copy, release notes, RFCs, microcopy, AI image/video prompts). Three read-only linters handle pre-commit gating, multilingual translation parity, and story-bible consistency for fiction.

MIT-licensed. Available via curl/Docker/npm/Homebrew. CI/CD with conventional-commits → semver auto-release.

Happy to adjust the entry placement or description if a different section makes more sense.
```

## Submission checklist

- [ ] Fork the awesome-claude-code repo
- [ ] Add the entry in alphabetical order within its section
- [ ] Verify all links in the entry resolve
- [ ] Open the PR with the message above
- [ ] After merge, share the link in [LAUNCH-POST tracking](../LAUNCH-POST.md)
