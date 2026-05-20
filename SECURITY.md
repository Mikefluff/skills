# Security policy

Skills in this collection are pure markdown plus a small amount of bash, Python (the linter), and Node (the status-line banner). None of them autonomously edit files outside their declared scope or contact external systems without the user invoking them. The threat surface is small but not zero — please report responsibly.

## Reporting a vulnerability

Email **mike@inite.ai** with `[skills security]` in the subject. Include:

- Affected component (skill name, script path, or workflow file)
- Steps to reproduce
- Impact (what an attacker could read / change / exfiltrate)
- Suggested mitigation if you have one

Please do **not** open a public GitHub issue for security reports. I'll acknowledge within 7 days and fix within 30 days for high-severity issues. If the timeline slips I'll tell you why.

## What counts as in-scope

- **install.sh** — anything that lets an attacker compromise the user's machine via a crafted tarball, manipulated GitHub release, or argument injection.
- **scripts/*** — bash / Python that runs on the user's machine.
- **hooks/skills-update-banner.js** — runs on every Claude Code session start if the user opts in.
- **skills-update** skill — invokes `install.sh --update` after user confirmation.
- **.github/workflows/*** — anything that lets an attacker push to `main` or publish a release without commit access.

## What is NOT in scope

- A skill telling Claude to do something dumb (write bad prose, ignore voice rules). That's quality, not security.
- A user manually running `install.sh` from a fork they don't trust. Don't pipe `curl` from unknown forks.
- `writer/scripts/lint.py` producing false positives / false negatives — file a bug, not a security report.

## Coordinated disclosure

I'll credit you in the release notes for the fix if you want credit, or stay quiet if you don't. Tell me which when you report.
