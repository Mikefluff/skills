# Input для release-notes — mock commit list for v3.4.0

## Version

v3.4.0 — minor release, 2026-05-20, SaaS web app.

## Mock commits

- feat(ui): added dark mode (Settings → Appearance)
- feat(search): added Cmd+K quick-search across workspaces
- feat(api): POST /v2/exports endpoint, returns 202 Accepted with job ID
- fix(search): no results when query has leading space
- fix(mobile): "Save draft" flashed twice when typing quickly
- fix(safari): dark mode broken on Safari 17.0-17.2
- perf: reduced project-list load from 2.1s to 380ms (caching layer)
- security: patched session-fixation in OAuth callback (CVE-2026-1234)
- chore: bumped lodash to 4.17.21 (transitive)
- docs: README update
- test: added coverage for export endpoint

## Audience

Primary: end-users + developers (mixed). Use Pattern B (audience-tagged bullets).
