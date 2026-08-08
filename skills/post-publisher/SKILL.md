---
name: post-publisher
description: "Publish assets to Instagram, Threads, TikTok, X, YouTube, Telegram or LinkedIn, and syndicate articles to dev.to, Telegraph or Hashnode with a canonical URL. Dry-run by default. Use when: 'опубликуй это', 'выложи карусель в треды', 'post this to Instagram', 'кросс-постинг статьи', 'syndicate this article'."

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
The last mile. Every other skill in this collection stops at `./generated/...`; this one sends what is there to the platform and records that it did.

Input: an output directory from `carousel-builder` / `reel-builder` (or a single file, or just text). Output: a live post or a platform-side draft, plus a `posted.json` receipt.

This skill does NOT:
- Write the content — that is `viral-text` / `essay-write` / `carousel-builder` / `reel-builder`.
- Schedule anything. There is no queue and no cron. It publishes now, or it stages a draft you finish by hand.
- Post to a platform you have not connected. Credentials are yours; nothing is bundled.
- Guarantee reach, or touch analytics.
</objective>

## ROLE

Resolve a source directory → build one platform-neutral `Post` → preflight it against each target platform's real limits → show the user exactly what would go where → ask → publish → write a receipt.

**Publication is irreversible. Dry-run is the default and `--yes` is what leaves it.** Even with `--yes`, each platform is confirmed separately: approving an Instagram post is not approval to also post to X.

## PIPELINE

1. **Resolve the source.** A directory is inspected in this order: `final.mp4` → video; several images → carousel (sorted numerically, so `slide-2` precedes `slide-10`); one image → image; nothing → text post. Override with `--kind`.

2. **Resolve the caption.** From `--text`, else `--text-file`, else `captions.md` in the source directory. The parser looks for a `## Main post` / `## Основной пост` heading and takes everything up to the next heading; with no such heading it takes the whole file minus headings. **Always check the extracted text in the dry-run preview** — `captions.md` is written by an agent, so its shape is a convention, not a contract.

3. **Preflight, per platform.** Character limits including hashtags, media count, file size, extension, missing alt text, and each platform's own rules (Telegram's 1024-char caption ceiling that does not apply to text posts; Instagram's 24h posting cap; TikTok's audit caveat). A `block` finding means nothing is sent; a `warn` means it goes but you should know.

4. **Preview + confirm.** Full text, character count, every file with its size and alt text, and whether it is going out live or as a draft.

5. **Publish, then record.** The receipt (`posted.json`) is written immediately after each platform succeeds — a crash mid-fan-out cannot cause a re-post of the platforms already done. A later run with identical content is refused unless `--force`.

## PLATFORMS

| Platform | Post kinds | Draft | The thing that will bite you |
|---|---|---|---|
| `telegram` | text, image, carousel, video | — | Caption on media caps at 1024 chars (text-only gets 4096). Video ≤50 MB. **The only one testable end-to-end without OAuth — start here.** |
| `threads` | text, image, carousel, video | container | 500 chars. Text-only posts need no S3 — the easiest real connection. |
| `instagram` | image, carousel, video | container | Business/Creator account required. Media is fetched by URL, so **S3 is mandatory**. Video publishes as a Reel (≤300 MB, ≤15 min). 100 posts/24h. |
| `tiktok` | video, image, carousel | **inbox** | Direct publishing needs an audited app; without one, posts are silently forced to SELF_ONLY. **Use `--draft`.** |
| `x` | text, image, carousel, video | — | 280 chars. 10,000/24h per app, 100/15min per user; what you may spend depends on the plan. Threads publish incrementally — a failure mid-chain leaves earlier posts live. |
| `youtube` | video | `private` | 100 uploads/day on their own allocation, drafts included. Cleanest draft of the seven. |
| `linkedin` | text, image, carousel, video | — | 3000 chars. Member posts work with `w_member_social`; company pages need the partner-gated Community Management API. |

## MODES

### Source
- `post-publisher <dir>` — a `carousel-builder` / `reel-builder` output directory
- `post-publisher <file>` — a single image or video
- `post-publisher --kind text --text "..."` — no source at all

### Targeting
- `--platform a,b,c` — comma-separated; each is confirmed separately
- `--draft` — stage instead of publish. A platform without drafts is **skipped**, not published live
- `--kind text|image|carousel|video|article` — override auto-detection

### Content
- `--text` / `--text-file` — caption (overrides `captions.md`)
- `--title` — YouTube title / LinkedIn article title
- `--hashtags "a,b,c"` — kept separate from the body so preflight can count them
- `--alt "..."` — repeat once per media file, in order
- `--link` — attached where the platform supports it

### Article syndication (`--kind article`)

- `--canonical <url>` — **the important one.** The URL of the original on your own domain
- `--description` — SEO excerpt / subtitle
- `--series` — dev.to series name, Hashnode series id
- `--cover-url` — cover image, already hosted
- `--packets <dir>` — write submission packets for the platforms with no API

### Execution
- *(nothing)* — dry-run. Prints what would happen and stops
- `--yes` — leave dry-run. Still asks before each platform
- `--force` — publish despite a matching receipt in `posted.json`
- `--publish-container <id>` — publish a Meta container left by an earlier `--draft`
- `--check --platform X` — readiness: credentials present, token usable
- `--list-platforms` — everything, with what each is missing

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Everything asked for happened, or was already done |
| `1` | At least one platform failed — blocked by preflight, missing credentials, or a platform error |
| `2` | Usage error: no `--platform`, unreadable source |

A *skip* is not a failure. A platform skipped because it has no drafts, or
because `posted.json` says this content already went out, leaves the code at
`0` — in a mixed run (`--platform telegram,instagram --draft`) Instagram
drafting successfully should not be reported as an error because Telegram was
skipped. The summary line always states how many proceeded, were skipped and
were blocked.

### Accounts
- `python3 -m common.runners.cli.auth --platform <name>` — OAuth in a browser
- `... --paste-token` — paste a token from the platform's own token tool (the supported route wherever loopback redirects are rejected)
- `... --status` / `--verify` / `--revoke <name>`
- `skills-keys accounts` — the same list, from the credentials skill

## REFERENCES (load on demand)

| File | When to load |
|---|---|
| [references/syndication.md](references/syndication.md) | `--kind article` — why canonical decides whether syndication helps or hurts, which platforms have an API, and the order to publish in |
| [references/oauth-setup.md](references/oauth-setup.md) | **First** — per-platform app registration, scopes, account type, which env vars go in `~/.skills.env` |
| [references/platform-limits.md](references/platform-limits.md) | Step 3 — the limit matrix `preflight` enforces, with what to verify against live docs |
| [references/browser-fallback.md](references/browser-fallback.md) | When the API path is closed: unaudited TikTok, personal Instagram, org LinkedIn pages |
| [references/troubleshoot.md](references/troubleshoot.md) | A platform returned an error and the message is not self-explanatory |
| [viral-text platform budgets](../viral-text/references/platforms.md) | Writing to fit a platform *before* generating — character budgets and tone per network |

## EXAMPLES

See [examples/before-after.md](examples/before-after.md) — three calibration runs: an 8-slide carousel to Instagram as a draft, a reel to TikTok's inbox, and a text post fanned out to Threads + Telegram + X.

## CONSTRAINTS

- **Dry-run is the default and must stay that way.** Every other runner here is safely re-runnable because a wasted generation costs cents. A wasted publish costs an audience. `--yes` is the deliberate act.

- **Confirm per platform, never in bulk.** A single "yes" must not fan out to seven networks.

- **`--draft` is a promise.** If a platform cannot draft, skip it. Publishing live because the user asked for a draft is the worst possible reading of the flag.

- **Never print a token.** Masked in `--status`, absent from errors, absent from logs. `~/.skills-tokens.json` is `chmod 600` and gitignored.

- **Preflight before bytes.** Every check that can happen locally happens before the first network call. Staging a 200 MB reel to S3 and waiting a minute for ingestion, only to be refused on a caption length, is a bug.

- **Receipts are per (platform, content).** Editing the caption makes it a new post and it goes through; re-running the identical command does not.

- **Report partial failure as partial.** An X thread that publishes 3 of 6 posts is not a failed publish and must not be reported as one — the receipt records what actually went out.

- **Verify endpoints before first use.** All seven APIs move. Versions are env-overridable (`INSTAGRAM_API_VERSION`, `LINKEDIN_API_VERSION`, `THREADS_API_VERSION`, `X_UPLOAD_URL`) precisely so a vendor change does not need a code change. `references/platform-limits.md` carries the last-verified date.

- **The browser path is a fallback, not a peer.** It is best-effort, it is a grey area under some platforms' terms, and it requires explicit consent every single time. Never drive it silently.

- **No engagement automation.** This skill posts what the user wrote. It does not follow, like, comment, DM, or run multiple accounts in concert.

## INVOCATION HINTS

Triggers:
- "опубликуй / выложи / запость это", "залей в инсту", "выложи карусель в треды", "кинь рил в тикток"
- "post this to X", "publish the carousel", "upload the reel to YouTube", "send it to the channel"
- Immediately after `carousel-builder` or `reel-builder` finishes, when the user says "и выложи" / "and post it"

Defaults: dry-run, no `--draft`, caption from `captions.md`. If the user names no platform, ask once — do not guess a destination.

If nothing is connected yet, route to `references/oauth-setup.md` and suggest starting with Telegram (no OAuth) or Threads (simplest OAuth), not Instagram.

Upstream: `carousel-builder`, `reel-builder`, `viral-text`, `quote-card-maker`, `meme-card-maker` — anything that lands assets in `./generated/`.
