"""OAuth 2.0 authorization-code flow with a one-shot loopback listener.

Six of the seven platforms want the same dance with different nouns, so the
dance lives here and each publisher supplies an OAuthApp describing its
endpoints, scopes and quirks.

Two things this module refuses to hide:

  · The redirect URI must match what you registered with the platform, exactly.
    Some platforms (Meta, TikTok) reject plain http://localhost, which is why
    `cli.auth --paste-token` exists as a first-class path rather than a
    workaround — for those, pasting a token from the platform's own token tool
    is the supported route, not a lesser one.

  · State is verified, and PKCE is used wherever the platform supports it.
    A loopback listener is a local open port; treating the callback as trusted
    input would be careless.
"""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import requests

from .errors import RunnerError

DEFAULT_PORT = int(os.environ.get("SKILLS_OAUTH_PORT", "8723"))
DEFAULT_REDIRECT = os.environ.get("SKILLS_OAUTH_REDIRECT", f"http://localhost:{DEFAULT_PORT}/callback")
FLOW_TIMEOUT = 300.0

_APPS: dict[str, "OAuthApp"] = {}


@dataclass
class OAuthApp:
    platform: str
    authorize_url: str
    token_url: str
    scopes: tuple[str, ...]
    client_id_env: str
    client_secret_env: str
    use_pkce: bool = False
    scope_sep: str = " "
    extra_authorize_params: dict[str, str] = field(default_factory=dict)
    extra_token_params: dict[str, str] = field(default_factory=dict)
    # TikTok names its client credentials client_key/client_secret rather than
    # client_id/client_secret, and rejects the standard names outright.
    client_id_param: str = "client_id"
    client_secret_param: str = "client_secret"
    setup_url: str = ""

    def client_id(self) -> str | None:
        return os.environ.get(self.client_id_env)

    def client_secret(self) -> str | None:
        return os.environ.get(self.client_secret_env)

    def configured(self) -> bool:
        return bool(self.client_id() and self.client_secret())


def register_app(app: OAuthApp) -> None:
    _APPS[app.platform] = app


def get_app(platform: str) -> OAuthApp | None:
    return _APPS.get(platform)


# ── loopback listener ───────────────────────────────────────────────────────


class _CallbackHandler(BaseHTTPRequestHandler):
    result: dict[str, str] = {}

    def do_GET(self):  # noqa: N802 — BaseHTTPRequestHandler's naming
        parsed = urllib.parse.urlparse(self.path)
        if not parsed.path.startswith("/callback"):
            self.send_response(404)
            self.end_headers()
            return

        params = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}
        _CallbackHandler.result = params

        ok = "code" in params
        body = (
            "<h2>Authorised.</h2><p>You can close this tab and return to the terminal.</p>"
            if ok
            else f"<h2>Authorisation failed.</h2><pre>{params.get('error_description', params)}</pre>"
        )
        payload = f"<html><body style='font-family:system-ui;padding:3rem'>{body}</body></html>"
        self.send_response(200 if ok else 400)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(payload.encode("utf-8"))

    def log_message(self, *args):  # silence the default stderr access log
        pass


def _listen_once(port: int) -> dict[str, str]:
    """Serve until the callback arrives or FLOW_TIMEOUT elapses."""
    _CallbackHandler.result = {}
    try:
        server = HTTPServer(("localhost", port), _CallbackHandler)
    except OSError as exc:
        raise RunnerError(
            f"cannot listen on localhost:{port} ({exc}). "
            f"Something else is using it — set SKILLS_OAUTH_PORT to a free port "
            f"and register the matching redirect URI with the platform."
        ) from exc

    # Loop rather than a single handle_request(): browsers routinely fetch
    # /favicon.ico against the loopback origin, and a one-shot listener would
    # spend its only request on that and then miss the callback entirely.
    # Non-/callback paths get a 404 and the loop keeps waiting.
    server.timeout = 1.0
    deadline = time.monotonic() + FLOW_TIMEOUT
    try:
        while not _CallbackHandler.result and time.monotonic() < deadline:
            server.handle_request()
    finally:
        server.server_close()

    if not _CallbackHandler.result:
        raise RunnerError(f"no callback received within {FLOW_TIMEOUT:.0f}s — authorisation abandoned")
    return dict(_CallbackHandler.result)


# ── the flow ────────────────────────────────────────────────────────────────


def _pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode().rstrip("=")
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    )
    return verifier, challenge


def run_flow(app: OAuthApp, *, redirect_uri: str = DEFAULT_REDIRECT, port: int = DEFAULT_PORT) -> dict[str, Any]:
    """Open the browser, catch the callback, exchange the code. Returns the raw
    token response so each publisher can read its own non-standard fields."""
    if not app.configured():
        missing = [
            e for e in (app.client_id_env, app.client_secret_env) if not os.environ.get(e)
        ]
        hint = f" See {app.setup_url}" if app.setup_url else ""
        raise RunnerError(
            f"{app.platform}: missing app credentials {', '.join(missing)} in ~/.skills.env.{hint}"
        )

    state = secrets.token_urlsafe(24)
    verifier = challenge = None

    auth_params = {
        app.client_id_param: app.client_id(),
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": app.scope_sep.join(app.scopes),
        "state": state,
        **app.extra_authorize_params,
    }
    if app.use_pkce:
        verifier, challenge = _pkce_pair()
        auth_params["code_challenge"] = challenge
        auth_params["code_challenge_method"] = "S256"

    url = f"{app.authorize_url}?{urllib.parse.urlencode(auth_params)}"
    print(f"Opening the browser to authorise {app.platform}.")
    print(f"If nothing opens, visit:\n  {url}\n")
    webbrowser.open(url)

    params = _listen_once(port)

    if params.get("state") != state:
        # Either a stale tab from an earlier attempt or something forged. Both
        # deserve a hard stop rather than a token exchange.
        raise RunnerError(f"{app.platform}: state mismatch on callback — authorisation rejected")

    if "code" not in params:
        detail = params.get("error_description") or params.get("error") or str(params)
        raise RunnerError(f"{app.platform}: authorisation denied — {detail}")

    token_params = {
        app.client_id_param: app.client_id(),
        app.client_secret_param: app.client_secret(),
        "code": params["code"],
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        **app.extra_token_params,
    }
    if verifier:
        token_params["code_verifier"] = verifier

    try:
        resp = requests.post(
            app.token_url,
            data=token_params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=60,
        )
    except requests.RequestException as exc:
        raise RunnerError(f"{app.platform}: token exchange failed: {exc}") from exc

    try:
        payload = resp.json()
    except ValueError:
        raise RunnerError(f"{app.platform}: token endpoint returned non-JSON: {resp.text[:300]}") from None

    if resp.status_code >= 400 or "error" in payload:
        detail = payload.get("error_description") or payload.get("error") or resp.text[:300]
        raise RunnerError(f"{app.platform}: token exchange rejected: {detail}")

    return payload
