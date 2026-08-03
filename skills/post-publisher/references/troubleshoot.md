# Troubleshooting

Platform errors, translated. Ordered by how often they actually happen.

## Nothing is sent, and no error appears

You are in dry-run, which is the default. Add `--yes`. The summary line says so:

```
Dry run complete — 1 of 1 platform(s) would proceed (0 skipped, 0 blocked). Add --yes to publish.
```

## `— platform: skipped, no draft support`

You passed `--draft` to a platform that has no drafts (Telegram, X, LinkedIn).
Skipping is deliberate: publishing live when a draft was asked for would be the
worst possible reading of the flag. Drop `--draft`, or target only platforms
that support it.

## `— platform: skipped, identical content already published`

`posted.json` in the source directory records this exact content going to this
exact platform. Change the caption and it counts as new; pass `--force` to post
it again anyway.

## `not authorised. Run: cli.auth --platform X`

No usable token. Either it was never obtained, or it expired past the point of
refresh. `--status` shows which.

## Telegram

| Message | Meaning |
|---|---|
| `not enough rights` | The bot is in the channel but not an administrator, or lacks the post-messages permission. |
| `chat not found` | Wrong `TELEGRAM_CHAT_ID`. Public channels use `@name`; private ones the numeric `-100…` id. |
| `Request Entity Too Large` | Over 50 MB. The public Bot API cannot take it; a self-hosted Bot API server can. |
| `message caption is too long` | Over 1024 chars with media attached. Preflight normally catches this first. |

## Instagram / Threads

| Message | Meaning |
|---|---|
| `The user is not an Instagram Business` | Personal account. Convert to Business/Creator, or use the browser fallback. |
| `Media upload has failed` / container `ERROR` | Meta could not fetch the URL. Presigned link expired, bucket unreachable, or the file is not really the type its extension claims. |
| container stuck `IN_PROGRESS` | Normal for video; Reels take 30–60s. Failing after 300s means Meta is struggling with the file — re-encode it. |
| `Application request limit reached` | Rate limited. For Instagram, `--check` reports the 24h posting allowance. |
| `Invalid OAuth access token` | Expired past refresh (60 days unused), or issued for a different account. Re-run `cli.auth`. |
| `media_type REELS is required` | A plain video container was attempted. This is handled automatically, so encountering it means the API changed — check `platform-limits.md`. |

## TikTok

| Symptom | Meaning |
|---|---|
| Post succeeds, nobody can see it | The app is not audited. Every direct post is forced to SELF_ONLY. Use `--draft`, or apply for audit. This is the one failure the API reports as success. |
| `spam_risk_too_many_posts` | Per-account posting cap. Wait. |
| `url_ownership_unverified` | Photo posts pull from a URL whose domain must be verified in the developer portal. |
| `privacy_level_option_mismatch` | The account does not offer the requested privacy level — a private account has no public option. Normally resolved from `creator_info`; override with `TIKTOK_PRIVACY_LEVEL`. |
| `access_token_invalid` | TikTok access tokens live 24h. Refresh is automatic; if it fails, the year-long refresh token also expired. |

## X

| Message | Meaning |
|---|---|
| `PARTIAL: 3/6 posts published` | A thread failed part way. The earlier posts are live. Delete them by hand, or continue the thread manually — re-running would duplicate the root. |
| 429 | Documented ceilings are 10,000/24h per app and 100/15min per user; your plan may cap it lower. |
| `Unsupported Authentication` | The endpoint wants OAuth 1.0a rather than the OAuth 2.0 user token. Check `X_UPLOAD_URL` against current docs. |
| `duplicate content` | X refuses identical text posted twice in quick succession. |

## YouTube

| Message | Meaning |
|---|---|
| `quotaExceeded` | 100 uploads/day by default, private ones included, on an allocation separate from the 10,000-unit pool. Resets at midnight Pacific. Request more in the Cloud console. |
| `no refresh_token` | Google issues one only on first consent. Revoke at myaccount.google.com/permissions and authorise again. |
| `youtubeSignupRequired` | The Google account has no YouTube channel. |
| `uploadLimitExceeded` | Per-account daily upload cap, separate from API quota. |
| upload ends with no video id | The resumable session died. Re-run; nothing was published. |

## LinkedIn

| Message | Meaning |
|---|---|
| 403 on `/rest/posts` | Missing `w_member_social`, or posting as an organisation without Community Management approval. |
| `Invalid version` | `LINKEDIN_API_VERSION` has aged out — LinkedIn rejects versions older than about a year. Set it to the current `YYYYMM`. |
| `no member id stored` | The token was obtained without `openid`/`profile`, so the member id was never fetched. Re-run `cli.auth`. |
| Refresh fails | Refresh tokens are only granted to approved apps. Re-run the flow for a fresh 60-day token. |

## S3 staging

| Message | Meaning |
|---|---|
| `fetches media by URL and cannot accept raw bytes` | Instagram/Threads with media and no bucket configured. Set `S3_BUCKET` / `S3_ACCESS_KEY` / `S3_SECRET_KEY`. |
| `boto3 is not installed` | `pip install -r common/runners/requirements.txt`, or re-run `install.sh`. |
| Meta cannot fetch the staged file | Check `S3_ENDPOINT` is reachable from the public internet. A MinIO instance on `127.0.0.1` is visible to you and not to Meta. |

## Diagnostics

```bash
python3 -m common.runners.cli.publish --list-platforms      # configured / authorised / neither
python3 -m common.runners.cli.publish --check --platform instagram
python3 -m common.runners.cli.auth --status                 # tokens and expiry, masked
python3 -m common.runners.cli.auth --platform x --verify    # ask the platform, not the file
```

When reporting a problem, include the `--list-platforms` output. It never
contains a token.
