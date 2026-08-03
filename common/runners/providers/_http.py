"""Shared HTTP plumbing for the `requests`-based providers.

Every vendor adapter that speaks plain HTTP does the same three things around
each call, and did them in its own copy: turn a transport failure into a
ProviderError, turn 429 into a QuotaError, turn any other 4xx/5xx into a
ProviderError carrying a truncated body. Nine providers × two or three calls
each is a lot of places for one of them to quietly forget the 429 branch.

The Google adapters do not use this — they go through the google-genai SDK,
which raises its own exception types (see google_video._wrap_error).

Response bodies are truncated to 500 characters on the way into an error.
Vendors answer 500s with whole HTML pages, and a stack trace is not improved by
having one pasted into it.
"""

from __future__ import annotations

from typing import Any

import requests

from ..errors import ProviderError, QuotaError

# Vendor defaults: a job submission is quick, a status poll quicker, and an
# asset download can be a 4K video over a hotel connection.
SUBMIT_TIMEOUT = 60
POLL_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 180


def raise_for_status(provider: str, resp: requests.Response) -> None:
    """Map an error status onto the typed errors the CLI knows how to report."""
    if resp.status_code == 429:
        raise QuotaError(provider, 429, resp.text[:500])
    if resp.status_code >= 400:
        raise ProviderError(provider, resp.status_code, resp.text[:500])


def send(provider: str, method: str, url: str, what: str = "network error", **kwargs: Any) -> requests.Response:
    """One request, with transport and status failures already typed."""
    try:
        resp = requests.request(method, url, **kwargs)
    except requests.RequestException as exc:
        raise ProviderError(provider, None, f"{what}: {exc}") from exc
    raise_for_status(provider, resp)
    return resp


def post(provider: str, url: str, **kwargs: Any) -> requests.Response:
    """Submit a generation request."""
    kwargs.setdefault("timeout", SUBMIT_TIMEOUT)
    return send(provider, "POST", url, **kwargs)


def get(provider: str, url: str, **kwargs: Any) -> requests.Response:
    """Read something that is not a job status — a listing, a signed URL."""
    kwargs.setdefault("timeout", SUBMIT_TIMEOUT)
    return send(provider, "GET", url, **kwargs)


def poll_get(provider: str, url: str, **kwargs: Any) -> requests.Response:
    """One GET of a job's status endpoint, inside a poll loop."""
    kwargs.setdefault("timeout", POLL_TIMEOUT)
    return send(provider, "GET", url, what="network error during poll", **kwargs)


def download(provider: str, url: str, **kwargs: Any) -> bytes:
    """Fetch a finished asset and return its bytes.

    Deliberately not routed through raise_for_status: a 429 on a signed asset
    URL means the link is being fetched too fast, not that the account is out
    of quota, and QuotaError reads as the latter.
    """
    kwargs.setdefault("timeout", DOWNLOAD_TIMEOUT)
    try:
        resp = requests.get(url, **kwargs)
    except requests.RequestException as exc:
        raise ProviderError(provider, None, f"download failed: {exc}") from exc
    if resp.status_code >= 400:
        raise ProviderError(provider, resp.status_code, "asset download failed")
    return resp.content
