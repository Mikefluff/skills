# Banned patterns

Strip these on sight. Each one signals "marketing fluff" or "engineer-talking-to-engineer" — neither serves the actual reader.

> **See also (shared across cold-email / landing-copy / release-notes):**
> [`common/references/banned-patterns-hype.md`](../../common/references/banned-patterns-hype.md) ·
> [`common/references/banned-patterns-preambles.md`](../../common/references/banned-patterns-preambles.md)
>
> The base linter (`writer/scripts/lint.py`) catches the regex-detectable subset under `MARKETING_HYPE` / `WEAK_OPENER` / `WRONG_TENSE_RELEASE`.

---

## 1. Marketing hype

Pure hype superlatives (`revolutionary`, `game-changing`, `world-class`, `industry-leading`,
`cutting-edge`, `best-in-class`, `groundbreaking`, `next-generation`) live in
[`common/references/banned-patterns-hype.md`](../../common/references/banned-patterns-hype.md).
The base linter catches them under `MARKETING_HYPE`.

Release-notes-specific hype patterns — usually adjective+noun forms:

| ❌ Banned | ✅ Replace with |
|---|---|
| `Award-winning` (without specific award) | (delete) |
| `Powerful new X` | `New X` |
| `Robust X` | `X` (or describe what makes it robust) |
| `Enterprise-grade X` | (delete; or describe the enterprise-specific feature) |
| `Lightning-fast X` | `X — N% faster` (with number) |
| `Seamless X` | `X` (or describe the seamlessness with concrete behavior) |

Rule: any adjective that's pure praise without specifics is banned.

---

## 2. Vague "improved" without specifics

| ❌ Banned | ✅ Replace with |
|---|---|
| `Improved performance` | `Reduced search latency from 2.1s to 380ms` |
| `Better security` | `Enabled MFA by default for new accounts` |
| `Enhanced UX` | `Search results now group by project` |
| `Optimized X` | `X: dropped from 800MB to 240MB memory use` (specific number) |
| `Streamlined X` | (describe the actual change) |
| `Polished X` | (describe the actual change) |
| `Refined X` | (describe the actual change) |

Rule: "improved X" without a before/after measurement is not a release note — it's a marketing slogan.

---

## 3. Excitement / feelings

The user doesn't care about your feelings. State the work.

Standard "We're excited / thrilled / proud / delighted to announce" preambles live in
[`common/references/banned-patterns-preambles.md`](../../common/references/banned-patterns-preambles.md).
The base linter catches them under `WEAK_OPENER`.

Release-notes-specific feeling preambles — strip these too:

| ❌ Banned | ✅ Replace with |
|---|---|
| `We've been working hard on X` | `X` (followed by description) |
| `After months of development...` | (delete; users don't care) |
| `We can't wait for you to try X` | `X` |
| `We hope you love X` | `X` |

Rule: any "we feel" preamble is filler. Past tense + the thing.

---

## 4. Empty preambles

| ❌ Banned | ✅ Replace with |
|---|---|
| `In this release, we have added X` | `Added X` (or just under "Added" section: "- X") |
| `This release brings X` | `Added X` |
| `As of this version, X is now available` | `Added X` |
| `We are now offering X` | `Added X` |
| `Going forward, X will...` | `X now...` |

Rule: never write a sentence whose purpose is to introduce the next sentence. Just write the next sentence.

---

## 5. Future-tense for shipped work

| ❌ Banned | ✅ Replace with |
|---|---|
| `Adding dark mode` | `Added dark mode` |
| `We are adding X` | `Added X` |
| `X will now be available` | `X is now available` (or `Added X`) |
| `This release introduces X` | `Added X` |
| `Going forward...` | (state the new behavior in present tense) |

Rule: if it shipped, it's past tense (Added/Changed/Fixed) or present tense (the new behavior). No "we are adding".

---

## 6. Engineer-talking-to-engineer (when audience is end-user)

| ❌ Banned (for end-user notes) | ✅ Replace with |
|---|---|
| `Idempotent retries on the auth endpoint` | (drop — internal) |
| `Race condition in the bulk-export worker fixed` | `Bulk exports for large workspaces no longer fail intermittently` |
| `Refactored the state machine in X` | (drop — internal) |
| `Migrated from React 17 to 18` | (drop — internal, unless visible perf benefit) |
| `Database migrations now run with advisory locks` | (drop for end-user; KEEP for ops) |
| `Bumped lodash to 4.17.21` | (drop, OR move to Security with the specific CVE) |

Rule: implementation detail without user impact = skip. If the change had user impact, describe the impact, not the implementation.

---

## 7. Vague impact statements

| ❌ Banned | ✅ Replace with |
|---|---|
| `Many users will benefit from this` | (delete — describe what users can now do) |
| `Most users won't notice` | (delete — if no one notices, don't put it in notes) |
| `This is a small fix` | (delete — just state it) |
| `Minor improvements` | (delete — describe specific minor improvements) |
| `Various bug fixes` | (delete — list the specific fixes) |

Rule: NEVER use phrases that diminish or hedge the impact. Either describe it, or omit it.

---

## 8. Apologies

| ❌ Banned (overuse) | ✅ Reserved use |
|---|---|
| `Sorry for the inconvenience` (routine bug fix) | Keep ONLY for: data loss risks, prolonged outages, security breaches |
| `Apologies for the late release` | (delete unless you're explaining a genuine delay) |
| `Our bad on the X bug` | (delete; "Fixed X" is enough) |

Rule: routine bug fixes don't require apologies. The fix IS the apology.

---

## 9. Self-promotion within release notes

| ❌ Banned | Where it might belong |
|---|---|
| `Sign up at example.com` (in a release note) | Marketing page, not release notes |
| `Upgrade to Pro for more features` | Email to free users, not changelog |
| `Follow us on Twitter` | Footer of website, not release notes |
| `Check out our amazing new launch on Product Hunt` | Social post, not release notes |

Rule: release notes are reference documents, not marketing channels. Don't bundle.

---

## 10. Specific dev-jargon (when audience is end-user)

If you're writing for end-users and find yourself using these terms — translate:

| Dev term | End-user translation |
|---|---|
| API | (often drop entirely; or "connection" / "integration") |
| Endpoint | (drop) |
| Webhook | (drop, OR "notification to your other tools") |
| Idempotent | "safe to retry" |
| Race condition | (drop, or describe the symptom) |
| Memory leak | "performance issue that built up over time" |
| Migration | "data move" or "upgrade" |
| Schema | "data structure" (often drop) |
| Cache | (often drop, OR "saved copy") |
| Authentication | "sign-in" |
| Authorization | "permissions" |
| Latency | "response time" / "loading time" |
| Throughput | (translate to user-visible: "more X at the same time") |
| Concurrency | (translate: "multiple things at once") |

---

## Quick strip-test

Before submitting any release note, scan for these patterns and strip:

1. `revolutionary` / `game-changing` / `groundbreaking` / `next-gen` → delete
2. `we're excited to / thrilled to / proud to` → delete
3. `we've been working hard on` → delete
4. `improved` without a number → either add a number or rewrite
5. `seamless` / `streamlined` / `enhanced` → either rewrite specifically or delete
6. `In this release, we...` / `This release brings...` → delete
7. `Going forward...` → rewrite in present tense
8. Apologies for routine fixes → delete
9. Marketing CTAs (sign up, upgrade) → delete
10. Engineer-jargon when audience is end-user → translate

Average release note loses 20-30% length after this scan, gains 0% clarity loss.

---

## What to add (positive direction)

After stripping, the release note may need:

- **A specific number** for any "improved" claim
- **A link** for any non-trivial migration / new feature
- **A specific user-visible behavior** for any internal change you decided to keep
- **The audience tag** if mixed-audience release (Pattern B from `audience-tone.md`)
- **A migration guide link** for any deprecation

Add these. Don't add filler.
