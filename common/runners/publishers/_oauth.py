"""Shared base for publishers that authenticate through an OAuth flow.

Five of the seven platforms repeated the same forty lines: look up the
registered OAuthApp, turn a token response into a TokenEntry, and POST a form
to a refresh endpoint. Only the endpoint and a couple of field names differed,
and the duplication was already drifting — the "is there a refresh token?"
guard existed in three of them and not the other two.

Subclasses now declare the differences and inherit the shape:

    class FooPublisher(OAuthPublisher):
        oauth_scopes = ("foo.write",)
        default_token_ttl = 7200.0
        refresh_url = "https://api.foo/oauth/token"

        def verify_token(self, access_token) -> tuple[str, str]: ...
        def _refresh_payload(self, entry) -> dict: ...

Meta's two platforms override `finalize_auth` and `refresh` outright, because
their long-lived tokens renew using the access token itself rather than a
refresh token. That is a real difference in the protocol, not a wrinkle worth
parameterising.
"""

from __future__ import annotations

import time
from typing import Any

import requests

from .. import oauth, tokens
from ..errors import RunnerError
from .base import Publisher


class OAuthPublisher(Publisher):
    """Publisher whose credentials come from an authorisation-code flow."""

    requires_oauth = True

    oauth_scopes: tuple[str, ...] = ()
    scope_delimiter: str = " "

    # Used when the token response omits expires_in. Erring short is safe: an
    # early refresh costs one request, a late one costs a failed publish.
    default_token_ttl: float = 3600.0

    refresh_url: str = ""
    refresh_requires_token: bool = True
    refresh_missing_message: str = ""

    # ── the app ─────────────────────────────────────────────────────────────

    def oauth_app(self) -> oauth.OAuthApp | None:
        return oauth.get_app(self.name)

    # ── first authorisation ─────────────────────────────────────────────────

    def identify(self, access_token: str) -> tuple[str, str]:
        """verify_token() that never raises.

        Used while storing a token: a platform being briefly unreachable should
        not throw away a credential the user just authorised. `--verify` exists
        to check it properly afterwards.
        """
        try:
            return self.verify_token(access_token)
        except (RunnerError, NotImplementedError):
            return "", ""

    def parse_scopes(self, raw: dict[str, Any]) -> list[str]:
        granted = raw.get("scope")
        if not granted:
            return list(self.oauth_scopes)
        if isinstance(granted, list):
            return [str(s) for s in granted]
        return [s for s in str(granted).replace(",", " ").split() if s]

    def finalize_auth(self, raw: dict[str, Any]) -> tokens.TokenEntry:
        access = raw.get("access_token")
        if not access:
            raise RunnerError(f"{self.name}: token response had no access_token: {raw}")
        account_id, label = self.identify(access)
        return tokens.TokenEntry(
            platform=self.name,
            access_token=access,
            refresh_token=raw.get("refresh_token"),
            expires_at=time.time() + float(raw.get("expires_in", self.default_token_ttl)),
            scopes=self.parse_scopes(raw),
            account_id=account_id,
            account_label=label,
        )

    # ── renewal ─────────────────────────────────────────────────────────────

    def _refresh_payload(self, entry: tokens.TokenEntry) -> dict[str, Any]:
        """Form body for the refresh request. Subclasses supply this."""
        raise NotImplementedError(f"{self.name} does not implement _refresh_payload()")

    def refresh(self, entry: tokens.TokenEntry) -> tokens.TokenEntry:
        if self.refresh_requires_token and not entry.refresh_token:
            raise RunnerError(
                self.refresh_missing_message
                or f"{self.name}: no refresh token stored — re-run cli.auth"
            )
        data = self._post_form(self.refresh_url, self._refresh_payload(entry))
        entry.access_token = data["access_token"]
        entry.refresh_token = data.get("refresh_token", entry.refresh_token)
        entry.expires_at = time.time() + float(data.get("expires_in", self.default_token_ttl))
        return entry

    def _post_form(self, url: str, payload: dict[str, Any], **kwargs) -> dict[str, Any]:
        try:
            resp = requests.post(url, data=payload, timeout=60, **kwargs)
        except requests.RequestException as exc:
            raise RunnerError(f"{self.name}: refresh request failed: {exc}") from exc
        try:
            data = resp.json() if resp.content else {}
        except ValueError:
            data = {}
        if resp.status_code >= 400 or "access_token" not in data:
            raise RunnerError(f"{self.name}: refresh rejected: {resp.text[:200]}")
        return data
