# Platform limits

What `preflight` enforces, and where each number came from.

**Last verified against live vendor docs: 2026-08-03.** Every row is marked
with what backs it. Rows marked ✅ were read off the vendor's current
documentation on that date. A row marked ~ is one nobody has been able to find
in the vendor's own documentation — it is carried from elsewhere and is the
likeliest in the table to be wrong.

Verifying corrected four numbers that had been written from memory, each in the
direction that would have hurt: Instagram's cap was 25 rather than 100,
Instagram Reels take 300 MB rather than 1 GB, YouTube gets 100 uploads a day
rather than the ~6 implied by the old quota model, and LinkedIn's pinned API
version had already aged out.

A second pass on 2026-08-03 went back for the twelve rows still marked ~,
because the vendor's parameter table had defeated the first read. Telegram's was
read by fetching the page and stripping the markup rather than asking a
summariser to hold 800 KB of HTML in its head; X publishes its media limits
under `/x-api/media/quickstart/best-practices`, which the chunked-upload page
links to but does not repeat. Ten rows came back verified. Two survive as ~:
LinkedIn documents neither a commentary length nor an image file size anywhere
in its API reference.

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
| Telegram ✅ | 4096 / **1024** | `sendMessage.text` is "1-4096 characters after entities parsing"; every `caption` field is "0-1024". Same text, two ceilings, depending on whether media rides along — the commonest surprise in this table. |
| Threads ✅ | 500 | Hashtags count; emoji count as UTF-8 bytes. |
| Instagram ✅ | 2200 | "Maximum 2200 characters, 30 hashtags, and 20 @ tags". |
| TikTok ✅ | 2200 | Title, hashtags included; "UTF-16 runes". |
| X ✅ | 280 | 25,000 on Premium. Each post of a thread is measured separately. X counts *weighted* characters: Latin and Cyrillic weigh 1, CJK and most emoji weigh 2. Preflight counts code points, so it under-counts a CJK post — [see below](#what-the-table-documents-but-preflight-does-not-check). |
| YouTube ✅ | 100 title / 5000 **bytes** description | Mixed units in one resource: `snippet.title` is "a maximum length of 100 characters", `snippet.description` "a maximum length of 5000 **bytes**". Cyrillic is 2 bytes a character, so the description budget is 2500 characters in Russian and less in CJK. Tags capped at 500 chars total, commas included. |
| LinkedIn ~ | 3000 | The Posts API documents no length for `commentary` — only a `FIELD_LENGTH_TOO_LONG` error when you exceed it. 3000 is the figure LinkedIn's own composer enforces and is unverified here. Beyond ~5 hashtags reach drops. multiImage `altText` is documented: "Maximum length is 4,086 characters" ✅. |

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
| Telegram | 10 MB ✅ (sendPhoto) | 50 MB ✅ (a self-hosted Bot API server lifts this) |
| Threads | 8 MB ✅ | 1 GB ✅ (now stated outright; also 300 s max) |
| Instagram ✅ | 8 MB | **300 MB**, 3 s – 15 min (Reels) |
| TikTok | 20 MB ✅ | 4 GB ✅, chunked at 5–64 MB ✅, max 1000 chunks ✅ |
| X | 5 MB ✅ | 512 MB ✅, and 0.5 s – 140 s |
| YouTube | — | 256 GB / 12 h ✅ ("256 GB or 12 hours, whichever is less") |
| LinkedIn | 10 MB ~ | 500 MB ✅ (75 kB – 500 MB, 3 s – 30 min) |

Telegram's `sendPhoto` carries two more constraints preflight does not check:
width + height must total ≤ 10000, and the ratio must be at most 20.

LinkedIn's image row stays ~ because the Images API documents a pixel ceiling
(< 36,152,320 px, JPG/GIF/PNG) and no file size at all. Its video row is ✅ but
the same page contradicts itself — the prose says "Between 75kb and 500MB" while
the `initializeUploadRequest.fileSizeBytes` field says "Maximum allowed Videos
size is 5GB". 500 MB is the conservative read and the one preflight enforces.

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

## What the table documents but preflight does not check

Verifying the rows surfaced four vendor constraints that are real, documented,
and unenforced. They are listed rather than silently omitted, so that the next
rejection they cause is recognisable instead of mysterious.

| Constraint | Platform | Why it is not checked |
|---|---|---|
| Video duration 0.5 s – 140 s | X | No rule reads media duration. `ffmpeg.get_duration()` exists but shells out, and preflight rules "must not perform I/O beyond stat()ing the media". |
| Video duration 3 s – 15 min | Instagram | same |
| Video duration 3 s – 30 min | LinkedIn | same |
| Photo width + height ≤ 10000, ratio ≤ 20 | Telegram | Needs to decode the image; Pillow is optional in this repo. |
| `altText` ≤ 4,086 chars | LinkedIn | Documented and unenforced, but the recommended length is under 120 — nothing this repo generates comes close. |

Duration is the one most likely to bite: a 3-minute reel is well inside X's
512 MB and will still be rejected. Adding it means letting a rule shell out to
ffprobe, which is a deliberate change to the rules contract rather than a fix.

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
| Threads | [Posts](https://developers.facebook.com/docs/threads/posts) — endpoints, `media_type`, carousel 2–20, 500 chars, 250/day, 8 MB image, 1 GB / 300 s video |
| Instagram | [Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing) · [IG User Media](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media/) |
| TikTok | [Direct Post](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post) · [Photo Post](https://developers.tiktok.com/doc/content-posting-api-reference-photo-post) — 35 photos, photo title 90 runes, description 4000 · [Media Transfer Guide](https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide) — "Maximum of 20MB for each image", 4 GB video, 5–64 MB chunks, ≤1000 chunks |
| X | [Create a post](https://docs.x.com/x-api/posts/creation-of-a-post) · [Media best practices](https://docs.x.com/x-api/media/quickstart/best-practices) — image ≤ 5 MB, GIF ≤ 15 MB, video ≤ 512 MB and 0.5–140 s · [Media introduction](https://docs.x.com/x-api/media/introduction) · [Counting characters](https://docs.x.com/fundamentals/counting-characters) — 280, weighted · [Rate limits](https://docs.x.com/x-api/fundamentals/rate-limits) |
| YouTube | [Getting started — quota](https://developers.google.com/youtube/v3/getting-started) · [videos resource](https://developers.google.com/youtube/v3/docs/videos) — title 100 chars, description 5000 **bytes**, tags 500 chars · [videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert) — 256 GB · [Upload videos](https://support.google.com/youtube/answer/71673) — "256 GB or 12 hours, whichever is less" |
| LinkedIn | [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api) — no documented `commentary` length · [MultiImage API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/multiimage-post-api) — altText 4,086, 2–20 images · [Images API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api) — pixel ceiling only, no file size · [Videos API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/videos-api) — "Between 75kb and 500MB", 3 s – 30 min |
| Telegram | [Bots FAQ](https://core.telegram.org/bots/faq) — 50 MB upload ceiling · [Bot API](https://core.telegram.org/bots/api) — `sendMessage.text` 1-4096, `caption` 0-1024, `sendPhoto` "at most 10 MB in size", "width and height must not exceed 10000 in total", "ratio must be at most 20". The page is 800 KB of HTML; fetch it and strip the tags rather than asking a summariser to read it, which is what defeated the first attempt. |

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
