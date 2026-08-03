# Browser fallback

For the cases where the official API is closed rather than merely inconvenient.

This is a **fallback, not a peer** of the API path. It is slower, it breaks when
a platform ships a redesign, on some platforms UI automation sits in a grey area
of the terms of service, and it cannot run unattended. Reach for it when the API
genuinely cannot do the job — not to skip a setup step.

## When it is actually justified

| Situation | Why the API cannot do it |
|---|---|
| TikTok, public post, unaudited app | Direct publishing is gated behind app audit. Everything else is forced to SELF_ONLY. |
| Instagram on a personal account | No API publishes to personal accounts. Converting to Creator is free and is the better fix if the user is willing. |
| LinkedIn company page | Needs the partner-gated Community Management API. |
| Instagram or Threads with media, no S3 | Both fetch media by URL. If a bucket is genuinely not an option, hands are the alternative. |
| One-off post, no app registered | Registering an app to post once is disproportionate. |

If none of these apply, fix the API path instead — see `oauth-setup.md`.

## What this is NOT for

- Posting to many accounts, or on a schedule, or at volume. That is exactly the
  behaviour platform anti-automation exists to stop, and this file does not help
  with it.
- Working around an account restriction, a ban, or a rate limit.
- Anything the user has not asked for in this session.

## Protocol

Driven by Claude in Chrome against the user's own logged-in browser. Nothing is
stored: no cookies, no session, no credentials. That is the point — a Playwright
robot holding social-network session cookies would be a worse thing to own than
the problem it solves.

1. **Prepare first.** Run the normal dry run so preflight still applies:

   ```bash
   post-publisher ./generated/carousel/<slug>/ --platform instagram
   ```

   Character limits, file sizes and aspect rules do not stop mattering because
   the transport changed. Fix anything it blocks on before opening a browser.

2. **Show the user what will be posted** — the caption in full, the file list,
   the target account — and get an explicit yes. Every time. Consent for one
   post is not consent for the next.

3. **Open a new tab.** Never reuse a tab id from an earlier session; call
   `tabs_context_mcp` for current ids.

4. **Navigate to the composer**, attach the files in order, paste the caption.

5. **Stop before the final button.** Screenshot the composed post, show it, and
   ask once more. This is the last reversible moment.

6. **Publish**, then confirm the post exists and capture its URL.

7. **Record it.** Append to `posted.json` in the source directory by hand so a
   later API run does not double-post:

   ```json
   {"version": 1, "receipts": [{
     "platform": "instagram", "post_id": "manual",
     "state": "published", "content_hash": "<from the dry run>",
     "published_at": "2026-08-01T12:00:00+00:00",
     "permalink": "https://instagram.com/p/...", "note": "posted via browser"
   }]}
   ```

   The `content_hash` is printed by the dry run. Without this entry the receipt
   check cannot protect you.

## Rules

- **Never trigger a modal.** `alert()` / `confirm()` blocks the extension and
  the session goes unresponsive until the user dismisses it by hand. Avoid
  anything that raises one, and warn the user first if it is unavoidable.
- **Stop after two or three failed attempts.** Report what was tried and what
  happened; do not keep clicking. A composer that will not accept a file is
  usually a real problem, not a timing one.
- **Do not log in on the user's behalf** and never handle their password. If the
  session is logged out, hand the browser back and wait.
- **One post per invocation.** No loops over accounts or queues.

## Cost of the redesign

Every platform in this list reworks its composer periodically. When a step here
stops matching what is on screen, the fix is to re-read the page and adapt —
not to add selectors to this file. It is deliberately written as intent
("navigate to the composer") rather than as a click script, because a click
script is guaranteed to rot and would give a false impression of reliability.
