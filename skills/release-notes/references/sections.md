# Sections — Keep-a-Changelog format

Standard 6 sections for any release notes. From [keepachangelog.com](https://keepachangelog.com/en/1.1.0/). Use them as-is — don't invent new section names.

---

## Added

**New** features, capabilities, APIs, options, integrations.

Use when:
- New endpoint, new flag, new UI panel, new keyboard shortcut
- New supported platform / format / language
- New SDK method / library function

### Format

```markdown
### Added

- Dark mode (Settings → Appearance → Dark)
- `POST /v2/exports` endpoint for bulk data export — see [docs/api/exports](https://docs.example.com/api/exports)
- Support for German and French in the email templates
- Keyboard shortcut `Cmd+Shift+P` opens the command palette
```

---

## Changed

**Non-breaking behavior changes**. The thing still works, but differently than before.

Use when:
- Default value changed
- UI moved / renamed without breaking automation
- API response shape extended (new fields — additive only)
- Performance improvement that doesn't change semantics
- Visual redesign

### Format

```markdown
### Changed

- Reduced project-list load time from 2.1s to 380ms (caching layer added)
- "Archive" button moved from the project menu to the toolbar
- Email subject lines now include the project name first, then the action
- Default timezone for new accounts is now `UTC` (was `America/Los_Angeles`)
```

Note the **specificity**: numbers, before/after, concrete locations. "Improved performance" without specifics is forbidden.

---

## Fixed

**Bug fixes**. Something was broken; it isn't anymore.

Use when:
- Bug that affected users — describe what was broken, who saw it
- Edge case crash / hang / freeze
- Visual misalignment, broken layout
- Wrong calculation, off-by-one, race condition (user-visible effect)

### Format

```markdown
### Fixed

- Search occasionally returned no results when query had a leading space
- Bulk-export failed for organizations with >500 projects (memory leak)
- Dark mode rendering broke on Safari 17.0-17.2
- "Save" button stayed greyed out after editing a draft on mobile
```

Each bullet describes:
1. The user-visible symptom
2. (Optional) the specific condition that triggered it

Don't say "fixed a bug" without specifying. The user wants to know whether their bug is the one that got fixed.

---

## Deprecated

Features that **still work** but will be removed in a future version. Gives users time to migrate.

Use when:
- Replacing an API endpoint with a new one
- Removing a UI element in N versions
- Sunsetting a feature, plan, or integration

### Format

```markdown
### Deprecated

- `POST /v1/exports` — use `POST /v2/exports`. Removal in v3.0 (estimated Q3 2026). See [migration guide](https://docs.example.com/migrations/exports-v1-to-v2).
- `--legacy-format` flag — replaced by `--format <name>`. Will be removed in v4.0.
```

ALWAYS include:
- What's being deprecated
- What to use instead
- When it's removed (estimated)
- Link to migration guide if non-trivial

---

## Removed

Features that **no longer exist** in this version.

Use when:
- A deprecated feature is finally removed
- A feature is sunset
- An integration is shut down

### Format

```markdown
### Removed

- `POST /v0/exports` (deprecated in v1.0; gone now)
- Legacy "Activity Stream" panel
- Support for Internet Explorer
- The "Beta" tag from the API — all v2 endpoints are now stable
```

For breaking removals — also mention in the section's lead that this is a major version with breakage.

---

## Security

**Vulnerabilities patched**. Always its own section, regardless of how minor.

Use when:
- CVE assigned to your software
- Internal-discovered vulnerability fixed
- Third-party library with vulnerability bumped
- Authentication / authorization / session-related fix

### Format

```markdown
### Security

- Patched session-fixation vulnerability in OAuth callback handler ([CVE-2026-1234](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2026-1234))
- Updated `vulnerable-pkg` from 1.2.3 to 1.2.5 (multiple CVEs)
- Token rotation now happens every 24 hours (was 7 days)
```

For zero-days / urgent patches — include severity (low / medium / high / critical) and whether action is needed from users.

---

## Breaking (major versions only)

For semver-major releases. Spell out what breaks and what to do.

### Format

```markdown
### Breaking

- **API**: `POST /v1/exports` removed. Migrate to `POST /v2/exports` — see [migration guide](https://docs.example.com/migrations/exports-v1-to-v2).
- **CLI**: `--legacy-format` flag removed (deprecated since v2.0). Use `--format <name>`.
- **SDK**: `Client.export()` no longer accepts a single string parameter — pass an options object.
- **Behavior**: New accounts default to `UTC` timezone (was `America/Los_Angeles`). Existing accounts unchanged.
```

Format: **{layer}**: {what broke} + {what to do} + {link to migration if non-trivial}.

---

## Section ordering

In a release note, sections appear in this order:

1. **Security** (if any) — first, because security is highest urgency
2. **Breaking** (major versions only) — high priority for users to action
3. **Added** — what's new
4. **Changed** — behavior changes
5. **Deprecated** — what's going away
6. **Removed** — what's gone
7. **Fixed** — what's no longer broken

If a section has no entries, omit it entirely — don't write "Fixed: (none)".

---

## When sections overlap

Sometimes a change could go in two sections. Pick based on the **dominant user impact**:

| Change | Best section |
|---|---|
| New endpoint that replaces an old one | **Added** (the new endpoint) + **Deprecated** (the old endpoint) — both entries |
| Bug fix that's now the default behavior | **Fixed** (don't move to Changed) |
| Performance improvement that's actually a re-architecture | **Changed** (if user-observable) — describe the impact, not the architecture |
| New permission required for an existing feature | **Breaking** (if major) or **Changed** with explicit migration note |
| Removing a deprecated feature | **Removed** (always, regardless of severity) |
| Renaming a UI element | **Changed** (mention old name → new name) |
| Renaming an API endpoint | **Breaking** (major) or **Deprecated** old + **Added** new (minor) |

---

## What does NOT belong in release notes

❌ Internal refactors that have zero user-observable effect — skip; they belong in commit history, not release notes
❌ Test coverage improvements — skip
❌ Code style / lint cleanup — skip
❌ Documentation updates (unless the docs publish AS the release artifact, e.g. an SDK readme) — usually skip
❌ Build / CI improvements — skip (unless it changes how users build their integration)
❌ Dependency bumps that don't affect users — skip; aggregate as "minor maintenance" if you must mention
✅ Dependency bumps that DO affect users (e.g. fixed a vulnerability) — **Security**
✅ Dependency bumps that change behavior — **Changed** with the specific behavior delta

---

## Examples — when entries are dropped vs kept

| Change | Keep? | If yes, which section + how |
|---|---|---|
| Refactored auth middleware (no observable change) | ❌ skip | — |
| Refactored auth middleware → 40% latency improvement | ✅ keep | **Changed**: "Reduced auth response time from X to Y" |
| Bumped lodash from 4.17.20 to 4.17.21 (no observable change) | ❌ skip | — |
| Bumped lodash from 4.17.19 to 4.17.21 (CVE patched) | ✅ keep | **Security**: "Updated lodash to 4.17.21 (CVE-2021-23337)" |
| Added internal logging | ❌ skip | — |
| Added user-visible activity log | ✅ keep | **Added**: "New Activity Log in Settings" |
| Reorganized internal folder structure | ❌ skip | — |
| Reorganized SDK module structure (changed imports) | ✅ keep | **Breaking** or **Changed** with migration note |

---

## Cross-references

- Tone per audience: [`audience-tone.md`](audience-tone.md)
- Length budgets per output format: [`structure.md`](structure.md)
- What NOT to write: [`banned-patterns.md`](banned-patterns.md)
