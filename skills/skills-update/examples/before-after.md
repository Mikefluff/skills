# skills-update — calibration before/after pairs

2 paired examples showing the user's local install state before and after running `/skills-update`. Each pair captures the `.skills-collection.json` marker file in both states, plus the diff-summary CLI output that explained the changes to the user.

How to read these:

- The **Before** is what the user sees when their install is stale — the marker still records the old version, the skill count is out of date, and the user is confused about what's actually new in the published release.
- The **After** is the post-update state — marker bumped to the new version, skill list updated, plus the CLI's diff-summary output that landed in the terminal during the update.
- The **Deltas** name what the skill did, what files moved, and (in the second pair) what failure mode the skill recovered from.

These pairs document the happy path and the rate-limited fallback. They are calibration fixtures — the version numbers and timestamps match v1.5.0 → v1.7.0, the actual transition this skill recently shipped.

---

## Example 1 — Normal update (v1.5.0 → v1.7.0)

**Context.** User installed the collection three weeks ago at v1.5.0. They see the status-line update banner. They run `/skills-update` to figure out what changed and apply it. Network is healthy; GitHub API responds under the hour rate limit.

### Before

**Local marker** (`~/.claude/skills/.skills-collection.json`):

```json
{
  "collection": "Mikefluff/skills",
  "version": "1.5.0",
  "installed_at": "2026-04-29T11:42:18Z",
  "skills": [
    "writer",
    "viral-text",
    "prose-edit",
    "essay-write",
    "style-check",
    "translation-sync",
    "canon-check",
    "pelevin-digression",
    "skills-update",
    "tone-shifter",
    "cold-email",
    "image-prompt",
    "video-prompt",
    "microcopy"
  ]
}
```

**User's question (paraphrased from session log)**:

> "I see a banner saying v1.7.0 is out. I'm on v1.5.0. The CHANGELOG.md on GitHub is huge and I can't tell what's new for me specifically vs. what was already in v1.6.0 that I never got. Should I just re-run install.sh and hope?"

The confusion is exactly what skills-update exists to remove: the user has skipped a version, the CHANGELOG file is cumulative, and they have no easy way to see only the slice they haven't installed yet.

### After

**Local marker** (`~/.claude/skills/.skills-collection.json`) — after `bash install.sh --update`:

```json
{
  "collection": "Mikefluff/skills",
  "version": "1.7.0",
  "installed_at": "2026-05-20T14:08:31Z",
  "skills": [
    "writer",
    "viral-text",
    "prose-edit",
    "essay-write",
    "style-check",
    "translation-sync",
    "canon-check",
    "pelevin-digression",
    "skills-update",
    "tone-shifter",
    "cold-email",
    "image-prompt",
    "video-prompt",
    "microcopy",
    "release-notes",
    "rfc-writer",
    "landing-copy"
  ]
}
```

**Diff-summary CLI output** (what the user saw in the terminal):

```
$ /skills-update
local: v1.5.0  (installed 2026-04-29)
remote: v1.7.0  (released 2026-05-20)

update available: v1.5.0 → v1.7.0  (skipping v1.6.0)

Changes since v1.5.0:

## [1.7.0] — 2026-05-20
- 9 per-skill snapshot fixtures added (test parity for all 17 skills)
- 8 dedicated walkthroughs (tone-shift, cold-email-pitch, image-prompt-cover,
  video-prompt-reel, microcopy-error-states, release-notes-saas,
  rfc-architecture, landing-launch)
- RU parity for 7 EN-only skills (cold-email, image-prompt, video-prompt,
  microcopy, release-notes, rfc-writer, landing-copy)
- COMPOSING.md rewritten as 14 named workflow recipes
- skills-update gets examples/

## [1.6.0] — 2026-05-08
- 3 new skills: release-notes, rfc-writer, landing-copy
- writer: 4 new neuroslop categories (EN-17..EN-20)
- prose-edit: canon-cross-check now respects {lang}/chapters layout
- style-check: --json output for CI integration

Skill count: 14 → 17  (+3: release-notes, rfc-writer, landing-copy)

Apply v1.7.0?
  [1] Yes, update now  (Recommended)
  [2] Show install command, I'll run it
  [3] Skip for now

> 1

Running: curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash -s -- --update
   downloading tarball ... ok  (1.2 MB)
   extracting skills/ ... ok  (17 directories)
   writing marker ... ok
   v1.7.0 installed

up to date — v1.7.0
```

**Deltas**

- Marker `version` field: `"1.5.0"` → `"1.7.0"`
- Marker `installed_at` field: `"2026-04-29T11:42:18Z"` → `"2026-05-20T14:08:31Z"` (re-stamped by install.sh)
- Marker `skills` array: 14 entries → 17 entries; three new entries appended (`release-notes`, `rfc-writer`, `landing-copy`)
- The CLI surfaced the **CHANGELOG slice the user actually missed** — not the whole file, but only `[1.7.0]` + `[1.6.0]` (everything `> local`, `≤ remote`). This is the «show CHANGELOG diff» step from SKILL.md §Step 4.
- The CLI marked `(skipping v1.6.0)` explicitly so the user understood they were leapfrogging an intermediate version, not missing it.
- Skill-count delta `14 → 17` printed inline — answers «what's new for me» without making the user diff the marker by hand.
- Explicit confirmation via three-option prompt before any state change — SKILL.md §Step 5; the skill never auto-applies.
- Post-install verification: marker re-read, version compared against remote, success line printed (`up to date — v1.7.0`).
- No edits to `~/.claude/settings.json`, no edits to any other skill folder — install.sh owns those; this skill only orchestrates.

---

## Example 2 — Rate-limited update with fallback (v1.5.0 → v1.7.0)

**Context.** User is on a corporate network behind a shared NAT. They've already burned the GitHub anonymous rate limit (60 requests/hour per IP) earlier in the day on other tooling. When they run `/skills-update`, the API call returns HTTP 403 with `X-RateLimit-Remaining: 0`. The skill must not silently retry, must not crash, and must give the user a working fallback.

### Before

**Local marker** (`~/.claude/skills/.skills-collection.json`) — same as Example 1, still v1.5.0.

**First attempt — what the user sees when the API is rate-limited:**

A naively-written update tool would either:

- crash with a stack trace and an unhelpful `KeyError: 'tag_name'` because the JSON body is `{"message": "API rate limit exceeded ..."}` instead of the release payload, or
- silently retry in a loop, wasting the next quota refresh, or
- pretend the install is current because it couldn't read the remote tag.

All three are failure modes the skill explicitly forbids in SKILL.md §Error handling («don't retry in a loop», «don't try to auto-fix», «report what failed and exit»).

### After

**Local marker** — **unchanged** at v1.5.0. The skill made no writes; the user's install is exactly as it was before the call.

**Diff-summary CLI output** (what the user saw in the terminal):

```
$ /skills-update
local: v1.5.0  (installed 2026-04-29)
remote: <unavailable>

GitHub API responded with 403 Rate Limit Exceeded.
  Remaining: 0 / 60   (anonymous, per-IP)
  Resets at: 2026-05-20T15:00:00Z  (in 52 minutes)

No update was attempted. Your install is still at v1.5.0.

Fallback options:
  [1] Wait 52 minutes and re-run /skills-update.
  [2] Run the installer directly — it does its own HTTPS fetch of the
      tarball, which is not subject to the API rate limit:

        bash -c 'curl -fsSL https://raw.githubusercontent.com/Mikefluff/skills/main/install.sh | bash -s -- --update'

      (You will not see the CHANGELOG diff this way — only the install.)

  [3] Use the cached banner-script tag if you have one
      (~/.claude/skills/.cache/latest-tag, max 24h old):

        cat ~/.claude/skills/.cache/latest-tag
        # 1.7.0

No changes have been made to ~/.claude/skills/.
```

**Deltas**

- Marker `version` field: **unchanged at `"1.5.0"`** — the rate-limit failure is recoverable, and the skill leaves the install state pristine. SKILL.md §What not to do: «Do NOT auto-apply updates without explicit user confirmation» extended to «do not write anything on failure paths either».
- Marker `installed_at` field: **unchanged** at `"2026-04-29T11:42:18Z"`.
- Marker `skills` array: **unchanged** — 14 entries.
- The CLI surfaced the **specific failure reason** (HTTP 403, rate limit, remaining 0/60, reset time) instead of a generic «could not reach GitHub». The remaining-quota and reset-time numbers are the actionable data the user needs to choose between waiting and the fallback.
- Three concrete fallback options printed — not «try again later» as the only advice. Each fallback names the exact command the user can copy.
- Fallback (2) explicitly notes the trade-off: the direct installer skips the CHANGELOG diff. The user gets to decide whether they need the diff or just the update.
- Fallback (3) references the 24-hour cached tag from the optional status-line banner (`scripts/install-hook.sh`) — documented in `examples/manifest-example.md` §Cache behavior. This skill itself does not cache; it points at a sibling cache when one exists.
- No retry loop. No silent retry. No `KeyError`. The skill exited cleanly after printing the failure block — SKILL.md §Error handling, literal.
- Exit code from the skill: 0 (graceful abort), not a fail-state — the install itself is still in a valid (just stale) state. The status-line banner will continue to show the update banner on the next session.

---

## Pattern summary

Across both pairs:

1. The marker `.skills-collection.json` is the single source of truth for what's installed locally. The skill reads it; `install.sh` writes it; nothing else touches it.
2. The CLI output is structured to answer the user's actual question: «what's new **for me** vs. what's just new in the CHANGELOG?» — by slicing the CHANGELOG to `(local, remote]` and printing skill-count deltas inline.
3. The skill never writes anything until the user picks option [1] in the confirm prompt. Network failures, rate limits, malformed CHANGELOGs — all leave the install state pristine.
4. Failure paths print the **actionable information** (rate-limit remaining, reset time, fallback command) rather than a generic error string.
5. The skill never edits `~/.claude/settings.json`, never touches other skill folders directly, never installs hooks. It orchestrates; install.sh executes.
