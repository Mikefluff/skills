"""Shared JSON-over-HTTP helper for the article publishers.

The three article platforms all speak plain JSON POST, and all three would
otherwise repeat the same twenty lines of "did the network fail, did it return
HTML instead of JSON, was it a 429, was it a 4xx". The social publishers each
have genuinely different wire formats (multipart, resumable upload, form-encoded
Bot API) and are left alone.
"""

from __future__ import annotations

from typing import Any

import requests

from ..errors import PublishError, RateLimitError


def post_json(
    platform: str,
    url: str,
    *,
    json: dict[str, Any],
    headers: dict[str, str],
    timeout: float = 60.0,
) -> dict[str, Any]:
    """POST `json` and return the decoded response.

    Raises RateLimitError on 429 and PublishError on anything else that is not
    a 2xx, including a body that does not parse — an HTML error page from a
    proxy is a failure mode worth naming rather than crashing on.
    """
    try:
        resp = requests.post(url, json=json, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        raise PublishError(platform, None, f"network error: {exc}") from exc

    if resp.status_code == 429:
        retry = resp.headers.get("Retry-After")
        suffix = f" — retry after {retry}s" if retry else ""
        raise RateLimitError(platform, 429, f"rate limited{suffix}")

    try:
        payload = resp.json()
    except ValueError:
        raise PublishError(
            platform, resp.status_code, f"non-JSON response: {resp.text[:300]}"
        ) from None

    if resp.status_code >= 400:
        raise PublishError(platform, resp.status_code, _error_text(payload) or resp.text[:300])

    return payload


def _error_text(payload: Any) -> str:
    """Pull a human message out of whatever error shape the vendor chose."""
    if not isinstance(payload, dict):
        return ""
    for key in ("error", "message", "detail", "description"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    # GraphQL puts them in a list under `errors`.
    errors = payload.get("errors")
    if isinstance(errors, list) and errors:
        messages = [e.get("message", "") for e in errors if isinstance(e, dict)]
        joined = "; ".join(m for m in messages if m)
        if joined:
            return joined
    return ""
