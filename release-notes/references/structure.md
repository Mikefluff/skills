# Structure and length budgets

The shape of a release note depends on (a) the version type and (b) the publication format.

---

## Version header

Every release note starts with a version + date header.

### Format

```markdown
## v3.4.0 — 2026-05-20
```

OR (when major):

```markdown
## v3.0.0 — 2026-05-20 (major release — see breaking changes)
```

OR (with theme):

```markdown
## v3.4.0 — 2026-05-20 — "Dark Mode + Search"
```

### Rules

- ISO date (`2026-05-20`) — locale-independent
- `v` prefix on version is convention; some teams drop it (be consistent within the project)
- Major releases get a parenthetical signal so users see at a glance
- Theme is optional; only use if the release genuinely has a unifying narrative

---

## Lead paragraph (optional, 1-3 sentences)

When the release has a unifying narrative or one big thing — write 1-3 sentences of context.

### When to lead

✅ Major release with breakage
✅ Feature launch ("v3 introduces real-time collaboration")
✅ Quarterly recap (more context, less change-by-change)

### When to skip

❌ Routine patch release (just bullets — no lead needed)
❌ Mixed pile of unrelated fixes (no narrative to write)
❌ When the lead would just paraphrase the bullets below

### Format

```markdown
## v3.0.0 — 2026-05-20 (major release)

This release moves the API to v2 by default and removes the v0/v1 endpoints
deprecated since 2025. Existing integrations require updates — see [migration guide](https://docs.example.com/migrations/v3).

### Breaking
- ...
```

Keep it factual. Don't write marketing prose ("We're proud to announce v3, our most ambitious release yet"). State the change, give the migration link, get out of the way.

---

## Section ordering

See [`sections.md`](sections.md) for the canonical 6 sections + order. Quick reference:

1. Security
2. Breaking
3. Added
4. Changed
5. Deprecated
6. Removed
7. Fixed

Omit empty sections entirely (don't write "Fixed: (none)").

---

## Within a section — bullet ordering

Order by **user impact**:

1. **High-impact items first** — features that affect many users / break many integrations / fix serious bugs
2. **Medium-impact** in the middle
3. **Low-impact / edge case** last

If you have 20 bullets, the top 3 should be the most-likely thing the user is looking for.

For long lists (>10 in one section), consider grouping:

```markdown
### Fixed

**Search**
- Occasionally returned no results when query had a leading space
- Crashed on Unicode emoji in the query (Edge browser only)

**Notifications**
- "Mark all read" briefly showed old unread count after refresh
- Mobile push showed wrong project name when account had >50 projects

**Billing**
- Invoice PDF showed the wrong tax rate for EU customers in March 2026
```

Sub-grouping makes long sections scannable. Apply when one section is >10 items AND the items cluster by feature area.

---

## Length budgets per format

| Format | Sections | Bullets per section | Total bullets | Notes |
|---|---|---|---|---|
| **Changelog page (website)** | All 7 | Unlimited | Unlimited | Full record; users come here to look up specifics |
| **GitHub release notes** | All 7 | Unlimited | Unlimited | Mirror of changelog usually |
| **Email to all users** | Highlights only | 3-5 top items | ≤ 10 | Subject + 2-line preview + bullets + link to full changelog |
| **In-app modal / banner** | Top 1-3 items | — | ≤ 3 | One sentence per item + "See all changes" link |
| **Push notification** | One feature | — | 1 | One-liner: "New: dark mode" |
| **Quarterly recap** | All 7 (cross-version) | 5-10 | 30-50 | Themed by feature area, not by version |
| **Annual recap** | Highlights only | 5-10 | 20-30 | "Year in review" style |

---

## Format-specific templates

### Changelog page (full)

```markdown
## v3.4.0 — 2026-05-20

### Added
- ...
- ...

### Changed
- ...

### Fixed
- ...
- ...

### Deprecated
- ...

### Security
- ...
```

### GitHub release notes

Same as changelog. GitHub renders markdown directly. Add a compare link at the top if useful:

```markdown
**Full Changelog**: https://github.com/example/app/compare/v3.3.0...v3.4.0

## v3.4.0 — 2026-05-20

### Added
- ...
```

### Email to users — trimmed

```markdown
## What's new in v3.4

**Dark mode is here** — toggle in Settings → Appearance.
The most-requested feature in 2025, finally shipped.

**Other highlights:**
- Quick search across all workspaces (Cmd+K)
- "Mute thread" option on conversations
- Search bug fix — leading-space queries now work correctly

[See the full release notes →](https://example.com/changelog/v3.4)
```

Note: email goes deeper on the headline feature (2-3 sentences) and bullet-lists the rest. The full changelog link is the escape hatch.

### In-app modal

```markdown
**v3.4 is here** — 2026-05-20

- Dark mode (Settings → Appearance)
- Quick search Cmd+K

[See all changes]   [Got it]
```

Even tighter — 2-3 items max, dismiss-and-move-on.

### Push notification

```
New: Dark mode now in Settings → Appearance
```

One line, ≤60 characters.

### Quarterly recap

```markdown
## Q2 2026 — Three Months in Review

**Theme**: collaboration + search

**Big launches**
- **Real-time collaboration** (v3.2) — multiple cursors, presence
- **Quick search** (v3.4) — Cmd+K across all workspaces
- **API v2** (v3.0) — async exports, pagination, webhook signatures

**Notable improvements**
- Search latency: 2.1s → 380ms (5x faster, v3.1)
- Dark mode (v3.4)
- Mobile redesign (v3.3)

**Fixed**
- 47 reported bugs closed across v3.0-v3.4
- Notable: search Unicode crash, OAuth redirect loop, bulk-export timeout

**By the numbers**
- 3 versions shipped (v3.0, v3.2, v3.4 — patches as v3.1, v3.3)
- 142 commits from 8 contributors
- Zero downtime, zero security incidents

[See per-release changelogs →](https://example.com/changelog)
```

Quarterly recap reads like a story (theme + biggest things + numbers), not like a flat list.

---

## Common version-header variations

| Project type | Header style |
|---|---|
| SaaS web app | `## v3.4.0 — 2026-05-20` |
| Mobile app | `## v3.4 (build 142) — 2026-05-20` (build number useful) |
| Library / SDK | `## v3.4.0 — 2026-05-20 (npm: example@3.4.0)` |
| Self-hosted product | `## v3.4.0 — 2026-05-20 (Docker: example/app:3.4.0)` |
| API | `## API v2.5 — 2026-05-20` (no "v3.4.0" if the product version doesn't equal API version) |

Match the project's existing convention; don't impose a new one with this skill.

---

## Where the release note lives

Help the user pick the right home for the notes:

| Goal | Best home |
|---|---|
| Long-term searchable record | Changelog page on website + GitHub release |
| Notify users of changes | Email digest (digest the top 3-5) + in-app modal |
| Marketing announcement | Blog post (different skill — `essay-write` or landing-copy) + social (different skill — `viral-text`) |
| API consumers | Developer changelog page + email to API key holders |
| Self-hosted ops | Tagged GitHub release + Helm/Docker version notes |

Don't try to make ONE release note serve all these. Different audiences need different artifacts.

---

## Cross-references

- Section breakdown: [`sections.md`](sections.md)
- Audience-tone differences: [`audience-tone.md`](audience-tone.md)
- What NOT to write: [`banned-patterns.md`](banned-patterns.md)
