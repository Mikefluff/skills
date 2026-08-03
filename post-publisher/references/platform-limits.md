# Platform limits

What `preflight` enforces, and where each number came from.

**Last verified against live vendor docs: not yet — see "Verifying" below.**
The numbers here were written from the APIs as documented at build time and are
encoded in `common/runners/publishers/*.py`. All seven platforms change theirs.
Treat a mismatch between this table and a live rejection as this table being
stale, and fix both.

Character budgets for *writing* live in
[`viral-text/references/platforms.md`](../../viral-text/references/platforms.md)
— that is the file to consult before generating. This one is about what the
posting API accepts.

---

## Text

| Platform | Limit | Notes |
|---|---|---|
| Telegram | 4096 / **1024** | 4096 for a text message, 1024 once media is attached. Same field, two ceilings — the commonest surprise in this table. |
| Threads | 500 | Hashtags count. |
| Instagram | 2200 | Hashtags count. ~30 tags is the practical ceiling. |
| TikTok | 2200 | Title, hashtags included. |
| X | 280 | 25,000 on Premium. Each post of a thread is measured separately. |
| YouTube | 100 title / 5000 description | Tags additionally capped at ~500 chars total. |
| LinkedIn | 3000 | Beyond ~5 hashtags reach drops. |

`preflight` measures `post.rendered_text()` — body **plus** hashtags — because
that is what the platform receives.

## Media count

| Platform | Images | Video |
|---|---|---|
| Telegram | 2–10 per album | 1, ≤50 MB via the public Bot API |
| Threads | 2–20 carousel | 1 |
| Instagram | 2–10 carousel | 1, publishes as a Reel |
| TikTok | up to 35 photos | 1 |
| X | up to 4 | 1, and never mixed with images |
| YouTube | — | exactly 1 |
| LinkedIn | multi-image | 1, and never mixed with images |

## File size

| Platform | Image | Video |
|---|---|---|
| Telegram | 10 MB | 50 MB (a self-hosted Bot API server lifts this) |
| Threads | 8 MB | 1 GB |
| Instagram | 8 MB | 1 GB |
| TikTok | 20 MB | 4 GB, chunked at 5–64 MB |
| X | 5 MB | 512 MB |
| YouTube | — | 256 GB / 12 h |
| LinkedIn | 10 MB | 500 MB |

## Posting caps

| Platform | Cap | Checkable? |
|---|---|---|
| Instagram | 25 posts / 24 h | **Yes** — queried before publishing, and again in preflight once authorised |
| Threads | 250 posts / 24 h | No |
| X | ~17 / 24 h, 500 / month on the free tier | Only from the response headers, after the fact |
| YouTube | 1600 quota units per upload of 10,000/day ≈ 6 | No endpoint exists |
| TikTok | per-account, undocumented | No |
| Telegram | ~20 messages/min to one chat | No |
| LinkedIn | per-member throttle, undocumented | No |

## Media transport

This is the constraint that decides whether a platform needs an S3 bucket.

| Platform | How media arrives |
|---|---|
| Telegram | multipart upload — bytes from disk |
| X | chunked upload — bytes from disk |
| YouTube | resumable upload — bytes from disk |
| LinkedIn | initialise, then PUT bytes |
| TikTok video | chunked `FILE_UPLOAD` — bytes from disk |
| **TikTok photos** | `PULL_FROM_URL` only — **needs S3 and a domain verified in the TikTok portal** |
| **Instagram** | platform fetches a URL — **needs S3** |
| **Threads with media** | platform fetches a URL — **needs S3** |

Staged files go up as private objects and are handed over as presigned links
with a one-hour life. The bucket is never made public.

---

## Overridable versions

Vendors deprecate on a schedule this repo cannot track, so the moving parts are
environment variables rather than constants:

| Variable | Default | For |
|---|---|---|
| `INSTAGRAM_API_VERSION` | `v21.0` | Graph version in the URL path |
| `THREADS_API_VERSION` | `v1.0` | same |
| `LINKEDIN_API_VERSION` | `202401` | the `LinkedIn-Version` header; rejected once ~a year old |
| `X_UPLOAD_URL` | `https://api.x.com/2/media/upload` | media upload host, which has moved before |
| `TIKTOK_PRIVACY_LEVEL` | `PUBLIC_TO_EVERYONE` | falls back to whatever the account actually allows |
| `YOUTUBE_PRIVACY` | `public` | `--draft` forces `private` regardless |
| `YOUTUBE_CATEGORY_ID` | `22` | People & Blogs |
| `LINKEDIN_VISIBILITY` | `PUBLIC` | |
| `LINKEDIN_AUTHOR_URN` | from the token | set only to post as something other than yourself |
| `INSTAGRAM_USER_ID` / `THREADS_USER_ID` | from the token | override the stored account id |

## Verifying

Before relying on any of this in anger, and after any vendor deprecation notice:

1. Open each platform's content-publishing reference and compare endpoints,
   parameter names, and the limits above.
2. Fix the constants in `common/runners/publishers/<platform>.py` and this table
   together — they must not drift apart.
3. Update the "last verified" line at the top with the date.
4. Run `make test-unit`; the preflight tests assert against these numbers, so a
   changed limit shows up as a failing test rather than a surprise in production.
