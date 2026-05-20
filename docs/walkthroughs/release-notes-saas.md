---
title: "Write release notes for a SaaS minor version"
persona: "Engineer publishing v3.4.0 release notes"
time: "10-15 minutes"
skills:
  - release-notes
  - writer
---

# Release notes for v3.4.0 — from PRs to GitHub release in 15 minutes

Сценарий: спринт закрыт, 23 PR'а смерджены в `main`, через час релиз. Тебе нужны user-facing release notes — в формате Keep-a-Changelog, без маркетингового fluff'а, organized по правильным секциям, готовые для копипасты в GitHub Release.

Это работа для `release-notes`. Скилл берёт commits/PRs, классифицирует, режет marketing language, собирает по 6 фиксированным секциям Keep-a-Changelog.

## Intent — Keep-a-Changelog шесть секций

Секции в строгом порядке (см. `release-notes/references/keep-a-changelog.md`):

1. **Security** — first, всегда. Если есть security fix, он наверху.
2. **Added** — новые features.
3. **Changed** — изменения в existing functionality.
4. **Deprecated** — soon-to-be-removed.
5. **Removed** — gone in this release.
6. **Fixed** — bug fixes.

Не «New / Improved / Bug fixes / Misc». Не «What's new + What's better». Keep-a-Changelog format. End-of-debate.

## Intent — anti-marketing-fluff bans

Release notes ≠ marketing email. Скилл режет (см. `release-notes/references/banned.md`):

- «We're excited to announce...» / «We're thrilled...»
- «Game-changing» / «revolutionary» / «next-generation»
- «Significantly improved» (without a number) → «20% faster» (with a number) OR cut
- «Best-in-class» / «industry-leading»
- «Powerful» / «robust» / «scalable» — adjective-pile
- «Under the hood...» — corporate-tech-blog patois
- «Enhanced» — vague verb. Use «added», «improved by X%», «replaced with Y».
- «New and improved» — pick one

## Setup

Скилл установлен. Reads PR / commit list. Audience tuning: `--audience user` (default) / `dev` / `ops`.

## Step 1. Feed the source

Скилл принимает три формата input:

```
/release-notes from-git v3.3.0..main
/release-notes from-prs https://github.com/yourorg/repo/milestone/12
/release-notes from-file CHANGES.txt
```

Берём первый — commits + merged PRs since the previous tag.

```
/release-notes from-git v3.3.0..main --version 3.4.0 --audience user
```

Скилл шурудит git log + PR titles + PR bodies, классифицирует каждый item.

## Step 2. The classification pass

Скилл показывает draft classification, before writing:

```
=== v3.4.0 — classified 23 items ===

Security (1):
  - #847 — bump openssl 3.0.10 → 3.0.13 (CVE-2024-2511)

Added (4):
  - #832 — bulk-edit support for tasks
  - #841 — SAML SSO for Enterprise
  - #844 — public API endpoint /v1/exports
  - #851 — keyboard shortcut for "command palette" (Cmd+K)

Changed (3):
  - #830 — dashboard default sort: created → updated
  - #837 — invoice PDF layout (legal review)
  - #849 — email digest moved from daily to weekly default

Deprecated (1):
  - #838 — /v0/legacy-export endpoint (sunset 2026-09-01)

Removed (1):
  - #840 — legacy "tags v1" syntax (deprecated since v3.0)

Fixed (10):
  - #828 — task sidebar collapses on resize ↳
  - #831 — Stripe webhook double-firing on retry
  - #833 — calendar export wrong timezone for DST
  ... (7 more)

Skipped (3 — internal-only, not user-facing):
  - #835 — refactor billing service
  - #842 — bump test dependencies
  - #846 — add CI cache for Docker builds
```

Скилл сам решает skip internal-only items (refactors, dependency bumps, CI). Если ты не согласна — `include #842`, скилл его добавит обратно.

## Step 3. The first draft

После classification скилл пишет финал по audience-specific tone. Default `--audience user`:

```markdown
## [3.4.0] — 2026-05-20

### Security
- Updated OpenSSL to 3.0.13 to address CVE-2024-2511 (uncontrolled
  memory growth in SSL_SESSION handling). No action required from users.

### Added
- **Bulk-edit for tasks.** Select multiple tasks in the list view and
  edit status, assignee, or due date in one action.
- **SAML SSO** (Enterprise plan). Configure your identity provider in
  Settings → Security → SSO. Supports Okta, Azure AD, Google Workspace.
- **Public API export endpoint** `/v1/exports`. Generate task exports
  programmatically. See [API docs](#) for the schema.
- **Command palette.** Press Cmd+K (or Ctrl+K on Windows) to search
  tasks, jump to projects, or trigger actions.

### Changed
- Dashboard default sort is now **last updated** (was: created date).
  You can change this back in Settings → Display.
- Invoice PDF layout updated for clarity. Existing invoices regenerate
  automatically the next time you download them.
- Email digest default frequency moved from **daily** to **weekly**.
  Adjust in Settings → Notifications if you prefer the old cadence.

### Deprecated
- `/v0/legacy-export` API endpoint. Migrate to `/v1/exports` (Added,
  this release). Sunset date: **2026-09-01**.

### Removed
- Legacy `tags v1` syntax (deprecated since v3.0). All tags now follow
  the `#name` format.

### Fixed
- Task sidebar no longer collapses when the window is resized below 1024px.
- Stripe webhooks no longer double-fire on retries (caused duplicate
  invoice records in some accounts).
- Calendar export now uses the correct timezone during DST transitions.
- ... (7 more fixes)
```

## Step 4. The before / after

Before — what an engineer typically writes from raw commit messages:

```
v3.4.0

🚀 We're thrilled to announce v3.4.0! This release is a game-changer
with a ton of awesome new features and significant improvements under
the hood.

✨ What's new:
- Bulk edit (so awesome!)
- SAML SSO (Enterprise only — ping sales)
- New API endpoint
- Command palette (Cmd+K, you'll love it)

🔧 Improvements:
- Dashboard sort is now smarter
- Invoices look way better
- Less email spam (weekly digest)

🐛 Bug fixes:
- Fixed a bunch of stuff

⚠️ Heads up: /v0/legacy-export is going away on Sept 1, 2026.

Plus: bumped OpenSSL for security 🔒

Happy shipping!
```

After — what `release-notes` produces (see Step 3 above): same content, but Keep-a-Changelog format, specific lengths, no emoji-as-section-headers, no «game-changer», no «you'll love it», no «happy shipping». Engineers reading this in a notification respect it. Marketing version trains them to skip.

## Step 5. Per-audience deltas

If `--audience dev`:

- Less «Settings → X» nav prose, more «set `digest.frequency=weekly` in config»
- Include CLI / API changes inline with code samples
- Less anxiety-snap framing («no action required») — engineers can read the diff themselves

If `--audience ops`:

- Lead with breaking-changes / deployment-relevant items
- Include migration commands inline
- Add infrastructure-impact section (DB migrations, env vars, restart requirements)

Same content, three different tones.

## Step 6. Format for GitHub release

GitHub Release UI renders markdown but trims some patterns. Скилл выдаёт GitHub-safe variant:

- Section headers as `### Added` not `## Added` (одна # уже занята versioned heading)
- No `[link]` references — inline links
- Code blocks ≤ 80 char width (GitHub Releases narrow column)
- Linked PRs as `(#832)` not `(GH #832)`

Скопируй output, paste в GitHub Release body, publish.

## Когда НЕ использовать release-notes

- **Marketing launch announcement** — это не changelog. Используй `landing-copy launch-announcement` или viral-text для post-кампании.
- **Internal-only changelog (engineers reading own commits)** — overkill. Просто `git log --oneline` достаточно.
- **Major version с breaking changes** — release-notes пишет per-version section, но для big release (v3 → v4) нужен дополнительно migration guide. Скилл предложит сгенерировать его отдельно.
- **Hotfix patch (one bug fix, 1 minute)** — write the one line and ship. Skill overhead не окупается.

## Troubleshooting

### Скилл классифицировал PR неправильно

`reclassify #841 from Added to Changed` — скилл переразмещает. Если не уверен — Keep-a-Changelog reference (`release-notes/references/keep-a-changelog.md`) даёт правила: Added = new public functionality, Changed = different behaviour for existing functionality, Fixed = bug fix without new behaviour.

### PRs не имеют user-facing descriptions

`/release-notes from-prs ... --strict` потребует proper PR descriptions. Без них скилл вернётся с «PR #835 has no user-facing description — add one or mark as internal». Это force discipline на PR review level.

### Output слишком длинный (50+ bullets)

Group similar fixes: «10 fixes related to calendar timezone handling» как one entry с linked PRs. Скилл сам предложит group если видит ≥ 3 fixes в одной area.

### Marketing хочет «more excitement»

Push back. Release notes ≠ launch announcement. Если marketing хочет hype — пусть пишут отдельный launch post (use `landing-copy` или `viral-post`). Mixing трэнирует пользователей skip'ать changelog.

## Related

- [landing-launch.md](landing-launch.md) — где сидит launch-announcement (другой жанр)
- [rfc-architecture.md](rfc-architecture.md) — где decisions documented before they ship
- [microcopy-error-states.md](microcopy-error-states.md) — родственная задача с per-audience tone
- [release-notes/references/keep-a-changelog.md](../../release-notes/references/keep-a-changelog.md) — полная schema
