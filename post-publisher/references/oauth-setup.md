# Connecting accounts

Two stores, two lifetimes. App credentials go in `~/.skills.env` by hand and last
until you rotate them. User tokens go in `~/.skills-tokens.json` and are written
only by the auth flow — never edit that file.

```bash
python3 -m common.runners.cli.auth --platform threads      # browser flow
python3 -m common.runners.cli.auth --platform instagram --paste-token
python3 -m common.runners.cli.auth --status                # what is connected
python3 -m common.runners.cli.auth --platform x --verify   # is it still good
python3 -m common.runners.cli.auth --revoke tiktok         # forget it locally
```

The loopback listener defaults to `http://localhost:8723/callback`. Register
exactly that string with the platform. Change it with `SKILLS_OAUTH_PORT` /
`SKILLS_OAUTH_REDIRECT` if 8723 is taken — and update the platform to match.

**`--paste-token` is not a lesser path.** Several platforms reject plain-http
loopback redirects, and their own token tools are the supported way to get a
token. Pasting is verified against the platform before anything is stored, so a
bad paste fails immediately rather than mid-publish.

---

## Recommended order

1. **Telegram** — no OAuth at all, works in five minutes, and it is the only
   platform you can test the whole pipeline against without an approval queue.
2. **Threads** — simplest real OAuth, and a text post needs no S3 bucket.
3. Everything else, once you know the shape works.

Starting with Instagram is the common mistake: it needs a Business account, an
app, *and* an S3 bucket before the first post can go out.

---

## Telegram

No app review, no OAuth, no expiry.

1. Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token.
2. Add the bot to your channel **as an administrator** with "Post messages" on.
3. Channel id: `@your_channel` for a public channel, or the numeric `-100…` id
   for a private one.

```bash
skills-keys add TELEGRAM_BOT_TOKEN 123456:AA...
skills-keys add TELEGRAM_CHAT_ID @your_channel
```

A bot that is a member but not an admin fails with "not enough rights" — that is
the single most common setup error here.

---

## Threads

1. [developers.facebook.com](https://developers.facebook.com) → create an app →
   add the **Threads API** use case.
2. Permissions: `threads_basic`, `threads_content_publish`.
3. Add the redirect URI under the Threads settings.

```bash
skills-keys add THREADS_APP_ID <app-id>
skills-keys add THREADS_APP_SECRET <app-secret>
python3 -m common.runners.cli.auth --platform threads
```

The flow exchanges the short-lived token for a ~60-day one automatically and
refreshes it on use. A token untouched for 60 days cannot be refreshed —
re-run the flow.

---

## Instagram

Requires **a Business or Creator account**. There is no API path to a personal
account; if that is a blocker, see `browser-fallback.md`.

This skill uses the *Instagram API with Instagram Login* (`graph.instagram.com`),
which does **not** need a linked Facebook Page. The older Graph API route does.

1. Create an app → add **Instagram** → *API setup with Instagram login*.
2. Permissions: `instagram_business_basic`, `instagram_business_content_publish`.
3. Add the redirect URI.

```bash
skills-keys add INSTAGRAM_APP_ID <app-id>
skills-keys add INSTAGRAM_APP_SECRET <app-secret>
python3 -m common.runners.cli.auth --platform instagram
```

**S3 is mandatory for Instagram**, and for Threads with media. Instagram fetches
media from a URL you supply; it never accepts uploaded bytes. Set `S3_BUCKET`,
`S3_ACCESS_KEY`, `S3_SECRET_KEY` (plus `S3_ENDPOINT` / `S3_REGION` for R2, Spaces
or MinIO). The bucket stays private — files are staged and handed over as
presigned links that expire in an hour.

---

## TikTok

1. [developers.tiktok.com](https://developers.tiktok.com) → create an app → add
   the **Content Posting API** product.
2. Scopes: `video.upload` (inbox/draft) and `video.publish` (direct).
3. Redirect URI must be **https**. If yours is http, use `--paste-token`.

```bash
skills-keys add TIKTOK_CLIENT_KEY <client-key>
skills-keys add TIKTOK_CLIENT_SECRET <client-secret>
python3 -m common.runners.cli.auth --platform tiktok
```

**Direct publishing requires passing TikTok's app audit.** Until then every
direct post is forced to SELF_ONLY — the API says success and nobody can see
the post. Use `--draft`, which routes to the inbox and needs no audit.

Access tokens last 24h; the refresh token lasts a year and is used automatically.

---

## X

1. [developer.x.com](https://developer.x.com/en/portal/dashboard) → project → app.
2. User authentication: **OAuth 2.0**, type *Web App / Automated App*, with
   `tweet.read`, `tweet.write`, `users.read`, `offline.access`.
3. `offline.access` is what yields a refresh token — without it the connection
   dies in two hours.

```bash
skills-keys add X_CLIENT_ID <client-id>
skills-keys add X_CLIENT_SECRET <client-secret>
python3 -m common.runners.cli.auth --platform x
```

Documented ceilings are 10,000 posts per 24h per app and 100 per 15 minutes per
user. What your account may actually spend on top of that depends on the plan,
and X has moved to pay-per-usage pricing — check current pricing before
budgeting a cadence around this.

---

## YouTube

1. [console.cloud.google.com](https://console.cloud.google.com) → project →
   enable **YouTube Data API v3**.
2. OAuth consent screen → add scope `.../auth/youtube.upload` → add yourself as
   a test user (an unpublished app only works for test users).
3. Credentials → OAuth client ID → **Desktop app** or Web with the loopback URI.

```bash
skills-keys add YOUTUBE_CLIENT_ID <client-id>
skills-keys add YOUTUBE_CLIENT_SECRET <client-secret>
python3 -m common.runners.cli.auth --platform youtube
```

Google issues a refresh token **only on first consent**. The flow requests
`access_type=offline&prompt=consent` to force it; if you still see "no
refresh_token", revoke the app at
[myaccount.google.com/permissions](https://myaccount.google.com/permissions)
and authorise again.

Uploads have their own allocation: 100 videos.insert calls per day by default,
private ones included, separate from the 10,000-unit pool everything else
shares.

---

## LinkedIn

1. [linkedin.com/developers/apps](https://www.linkedin.com/developers/apps) →
   create an app, associated with a company page you administer (the page is
   only for app ownership, not for posting).
2. Products: **Share on LinkedIn** and **Sign In with LinkedIn using OpenID
   Connect**.
3. Scopes: `w_member_social`, `openid`, `profile`.

```bash
skills-keys add LINKEDIN_CLIENT_ID <client-id>
skills-keys add LINKEDIN_CLIENT_SECRET <client-secret>
python3 -m common.runners.cli.auth --platform linkedin
```

This posts as **you**. Posting as a company page needs the Community Management
API, which is partner-gated and usually declined for individual developers.

Tokens last ~60 days. Refresh tokens are only granted to approved apps, so
expect to re-run the flow rather than rely on refresh.

---

## Troubleshooting the flow

| Symptom | Cause |
|---|---|
| `cannot listen on localhost:8723` | Port in use. Set `SKILLS_OAUTH_PORT` and update the platform's redirect URI. |
| `state mismatch on callback` | A stale browser tab from an earlier attempt. Close it, re-run. |
| `redirect_uri_mismatch` | The registered URI differs from `SKILLS_OAUTH_REDIRECT`, character for character. |
| `no callback received within 300s` | The browser never reached the listener — check that the URL printed in the terminal opens. |
| Token stored but publishing 401s | Scopes were granted for a different account, or the app is unpublished and you are not a test user. Run `--verify`. |
