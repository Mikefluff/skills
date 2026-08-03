# Platform limits

What `preflight` enforces, and where each number came from.

**Last verified against live vendor docs: 2026-08-03.** Every row is marked
with what backs it. Rows marked ✅ were read off the vendor's current
documentation on that date; rows marked ~ could not be machine-read and are
carried from the API's parameter tables — treat those as the ones most likely
to be wrong.

Verifying corrected four numbers that had been written from memory, each in the
direction that would have hurt: Instagram's cap was 25 rather than 100,
Instagram Reels take 300 MB rather than 1 GB, YouTube gets 100 uploads a day
rather than the ~6 implied by the old quota model, and LinkedIn's pinned API
version had already aged out.

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
| Telegram ~ | 4096 / **1024** | 4096 for a text message, 1024 once media is attached. Same field, two ceilings — the commonest surprise in this table. |
| Threads ✅ | 500 | Hashtags count; emoji count as UTF-8 bytes. |
| Instagram ✅ | 2200 | "Maximum 2200 characters, 30 hashtags, and 20 @ tags". |
| TikTok ✅ | 2200 | Title, hashtags included; "UTF-16 runes". |
| X ~ | 280 | 25,000 on Premium. Each post of a thread is measured separately. |
| YouTube ~ | 100 title / 5000 description | Tags additionally capped at ~500 chars total. |
| LinkedIn ~ | 3000 | Beyond ~5 hashtags reach drops. multiImage altText caps at 4086. |

`preflight` measures `post.rendered_text()` — body **plus** hashtags — because
that is what the platform receives.

## Media count

| Platform | Images | Video |
|---|---|---|
| Telegram ✅ | 2–10 per album | 1, ≤50 MB via the public Bot API |
| Threads ✅ | 2–20 carousel | 1 |
| Instagram ✅ | 2–10 carousel | 1, publishes as a Reel |
| TikTok | up to 35 photos | 1 |
| X ✅ | up to 4 (`media_ids` accepts 1–4) | 1, and never mixed with images |
| YouTube | — | exactly 1 |
| LinkedIn ✅ | 2–20 via `content.multiImage.images[]` | 1, and never mixed with images |

## File size

| Platform | Image | Video |
|---|---|---|
| Telegram | 10 MB ~ (sendPhoto) | 50 MB ✅ (a self-hosted Bot API server lifts this) |
| Threads | 8 MB ✅ | 1 GB ~ (not stated in the docs read) |
| Instagram ✅ | 8 MB | **300 MB**, 3 s – 15 min (Reels) |
| TikTok | 20 MB ~ | 4 GB ✅, chunked at 5–64 MB ✅, max 1000 chunks |
| X ~ | 5 MB | 512 MB |
| YouTube ~ | — | 256 GB / 12 h |
| LinkedIn ~ | 10 MB | 500 MB |

## Posting caps

| Platform | Cap | Checkable? |
|---|---|---|
| Instagram | 100 posts / 24 h | **Yes** — queried before publishing, and again in preflight once authorised |
| Threads | 250 posts / 24 h | No |
| X | 10,000 / 24 h per app · 100 / 15 min per user | Only from the response headers, after the fact |
| YouTube | 100 uploads / day, on their own allocation | No endpoint exists |
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
| `INSTAGRAM_API_VERSION` | `v25.0` | Graph version in the URL path |
| `THREADS_API_VERSION` | `v1.0` | same |
| `LINKEDIN_API_VERSION` | `202607` | the `LinkedIn-Version` header; rejected once ~a year old |
| `X_UPLOAD_URL` | `https://api.x.com/2/media/upload` | media upload host, which has moved before |
| `TIKTOK_PRIVACY_LEVEL` | `PUBLIC_TO_EVERYONE` | falls back to whatever the account actually allows |
| `YOUTUBE_PRIVACY` | `public` | `--draft` forces `private` regardless |
| `YOUTUBE_CATEGORY_ID` | `22` | People & Blogs |
| `LINKEDIN_VISIBILITY` | `PUBLIC` | |
| `LINKEDIN_AUTHOR_URN` | from the token | set only to post as something other than yourself |
| `INSTAGRAM_USER_ID` / `THREADS_USER_ID` | from the token | override the stored account id |

## Sources checked on 2026-08-03

| Platform | Document |
|---|---|
| Threads | [Posts](https://developers.facebook.com/docs/threads/posts) — endpoints, `media_type`, carousel 2–20, 500 chars, 250/day |
| Instagram | [Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing) · [IG User Media](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media/) |
| TikTok | [Direct Post](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post) · [Media Transfer Guide](https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide) |
| X | [Create a post](https://docs.x.com/x-api/posts/creation-of-a-post) · [Chunked media upload](https://docs.x.com/x-api/media/quickstart/media-upload-chunked) · [Rate limits](https://docs.x.com/x-api/fundamentals/rate-limits) |
| YouTube | [Getting started — quota](https://developers.google.com/youtube/v3/getting-started) |
| LinkedIn | [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api) · [MultiImage API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/multiimage-post-api) |
| Telegram | [Bots FAQ](https://core.telegram.org/bots/faq) — 50 MB upload ceiling. The method parameter tables on [the API page](https://core.telegram.org/bots/api) are too large to machine-read; the `~` rows come from them. |

## Re-verifying

After any vendor deprecation notice, and before trusting a `~` row:

1. Open the document above and compare endpoints, parameter names and limits.
2. Fix the constants in `common/runners/publishers/<platform>.py` and this table
   together — they must not drift apart. Each corrected constant carries a
   comment naming the source and date; keep that habit.
3. Update the "last verified" line at the top, and move a `~` to `✅` once you
   have actually read it.
4. Run `make test-unit`; the preflight tests assert against these numbers, so a
   changed limit shows up as a failing test rather than a surprise in production.
