---
name: release-notes
description: "Write user-facing release notes + changelogs. Keep-a-Changelog format, sections Added/Changed/Fixed/Deprecated/Removed/Security. Per-audience tone (user/dev/ops). Anti-marketing-fluff bans. Use when the user says 'release notes for vX.Y.Z', 'changelog entry', 'what's new', 'product update'."
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

<objective>
Write release notes that users actually read. Output: structured markdown release notes ready to publish on a changelog page / inside-app modal / email / GitHub release.

Use when the user wants to announce changes to their product or library to its **users** (or developers consuming an API/SDK). Not for internal engineering decisions — that's `rfc-writer`. Not for marketing landing pages — that's `landing-copy`.

This skill does NOT:
- write RFCs / design docs / ADRs (use `rfc-writer`)
- write landing-page marketing copy (use `landing-copy`)
- write commit messages or PR descriptions (those are for engineers; release notes are downstream)
- write blog posts about a release (different shape — use `essay-write` or `viral-text`)
</objective>

## ROLE

Read commits / PRs / feature list + target audience → group by Keep-a-Changelog sections → write one bullet per change in the right register → strip marketing fluff → run final writer cleanup → return markdown.

## PIPELINE

1. **Identify audience.** End user (uses the product UI) / developer (uses the API/SDK) / ops (deploys / monitors the product). Tone differs significantly — see `references/audience-tone.md`.

2. **Identify scope.** Single feature announcement / version release / quarterly recap / monthly digest. Each has different length and structure.

3. **Gather changes.** From git log / PR list / user-provided list. Group into:
   - **Added** — new features, new APIs, new options
   - **Changed** — behavior changes (non-breaking)
   - **Fixed** — bug fixes
   - **Deprecated** — still works, will be removed in vX
   - **Removed** — gone in this version
   - **Security** — vulnerabilities patched
   - **Breaking** — only for major versions (semver)

   See `references/sections.md`.

4. **Write one bullet per change.**
   - Lead with the verb in past tense for "Added/Changed/Fixed/Removed"
   - Lead with the noun being deprecated for "Deprecated"
   - One line per bullet (allow continuation only if context matters)
   - User-facing benefit first, technical detail second

5. **Apply anti-fluff rules.** Strip marketing language ("revolutionary", "game-changing"), "We're excited to announce", "We're thrilled to share". See `references/banned-patterns.md`.

6. **Order within sections.** Most-impactful items first. Don't bury big features under a 12-bullet "Fixed" list.

7. **Add a header / lead** (1-2 lines) for context: what version, what date, what theme if there is one. See `references/structure.md`.

8. **Final pass.** Run through `writer` for anti-neuroslop + typography + structural-prose layers.

## MODES

- `release-notes <version> <changes-list>` — write release notes for vX.Y.Z
- `release-notes --from-git <since-tag>` — read git log since a tag, summarize
- `release-notes --from-prs <PR-list>` — write notes from a list of PR titles/descriptions
- `release-notes --recap quarterly|monthly|annual` — longer recap covering multiple releases
- `release-notes --audience user|dev|ops` — explicit audience selection
- `release-notes --format changelog-md|github-release|email|in-app` — output format
- `release-notes --improve <existing>` — rewrite weak release notes

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/sections.md](references/sections.md) | When categorizing changes — Keep-a-Changelog 6 sections + how to decide which applies |
| [references/audience-tone.md](references/audience-tone.md) | When picking voice — end-user / developer / ops differences |
| [references/structure.md](references/structure.md) | When assembling — version header, lead, ordering, length budgets per format |
| [references/banned-patterns.md](references/banned-patterns.md) | After draft — strip marketing fluff, hype, vague "we improved X" |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — 5 calibration pairs: weak release notes vs strong, across SaaS / API / library / mobile-app contexts.

## CONSTRAINTS

- **No marketing hype.** "Revolutionary", "groundbreaking", "game-changing", "next-generation" — strip on sight. The work speaks for itself.
- **No "We're excited / thrilled / proud to announce".** State what shipped. The user doesn't care about your feelings.
- **No "Improved X" without specifics.** Replace with: "Reduced X latency from 2.1s to 380ms" / "Now supports Y format" / "Fixed Z bug that affected users of W".
- **Past tense for shipped work.** "Added dark mode" not "Adding dark mode" not "We are adding dark mode".
- **One bullet per change.** Don't merge two features into one line ("Improved auth and payment flows" → split).
- **Specific over abstract.** "Improved performance" → "Reduced search latency 5x"; "Better security" → "Enabled MFA by default for new accounts".
- **Link to longer docs when relevant.** Release note is the headline; help-article / RFC / docs page is the body.
- **Date in ISO format.** `2026-05-20`, not "May 20, 2026" or "20/05/2026".
- **Version follows semver.** Major (breaking) / minor (features) / patch (fixes).
- **No emoji in dev/ops audience.** OK in light user-facing notes (🎉 for milestones), avoid in technical contexts.

## INVOCATION HINTS

When the user says any of:
- "release notes for vX.Y.Z"
- "changelog entry / update"
- "what's new in version..."
- "summarize this release"
- "monthly / quarterly recap"
- "GitHub release notes"
- "in-app announcement for the latest version"
- "draft a release note about ..."

Use this skill. For internal design docs / RFCs → `rfc-writer`. For marketing landing announcements → `landing-copy`. For viral social posts about the release → `viral-text`.
