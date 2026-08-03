"""~/.skills-tokens.json — OAuth token store for the publishing layer.

Deliberately separate from ~/.skills.env. The two hold different things with
different lifetimes and different ways of arriving:

  ~/.skills.env          app credentials    long-lived   pasted by the user
  ~/.skills-tokens.json  user access tokens hours/days   produced by an OAuth flow

Cramming expiring JSON blobs into a flat KEY=VALUE file that sixteen providers
read at startup would have been the cheap move and the wrong one — every
runner would then carry expired social tokens in os.environ for no reason.
So tokens are never loaded into the environment; they are read on demand.

Refresh is platform-specific, so each publisher registers its own refresher:

    tokens.register_refresher("instagram", _refresh_long_lived)

get_valid() then transparently refreshes anything inside the skew window and
persists the result before returning.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

from . import atomicfile
from .errors import TokenError

TOKENS_FILE = Path(os.environ.get("SKILLS_TOKENS_FILE", str(Path.home() / ".skills-tokens.json")))

SCHEMA_VERSION = 1

# Refresh this many seconds before nominal expiry. Covers clock drift plus the
# round-trip of the request we are about to make.
REFRESH_SKEW = 300.0

_REFRESHERS: dict[str, Callable[["TokenEntry"], "TokenEntry"]] = {}


@dataclass
class TokenEntry:
    platform: str
    access_token: str
    refresh_token: str | None = None
    expires_at: float | None = None  # epoch seconds; None = does not expire
    scopes: list[str] = field(default_factory=list)
    account_id: str = ""
    account_label: str = ""  # "@handle" / channel name — for the confirmation prompt
    obtained_at: float = 0.0

    def expired(self, *, skew: float = REFRESH_SKEW) -> bool:
        if self.expires_at is None:
            return False
        return time.time() >= (self.expires_at - skew)

    def expires_in_human(self) -> str:
        if self.expires_at is None:
            return "no expiry"
        remaining = self.expires_at - time.time()
        if remaining <= 0:
            return "expired"
        if remaining < 3600:
            return f"{remaining / 60:.0f} min"
        if remaining < 86400:
            return f"{remaining / 3600:.1f} h"
        return f"{remaining / 86400:.1f} days"

    def masked(self) -> str:
        from .keysfile import mask

        return mask(self.access_token)


def register_refresher(platform: str, fn: Callable[[TokenEntry], TokenEntry]) -> None:
    """Publishers call this at import time to teach the store how to refresh."""
    _REFRESHERS[platform] = fn


# ── file I/O ────────────────────────────────────────────────────────────────


def _read_raw() -> dict:
    if not TOKENS_FILE.is_file():
        return {"version": SCHEMA_VERSION, "platforms": {}}
    try:
        data = json.loads(TOKENS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # A corrupt token file must not brick every publisher. Treat as empty;
        # re-running the auth flow rewrites it.
        return {"version": SCHEMA_VERSION, "platforms": {}}
    if not isinstance(data, dict) or "platforms" not in data:
        return {"version": SCHEMA_VERSION, "platforms": {}}
    return data


def _write_raw(data: dict) -> None:
    atomicfile.write_secret_text(TOKENS_FILE, json.dumps(data, indent=2, sort_keys=True) + "\n")


def read(platform: str) -> TokenEntry | None:
    raw = _read_raw()["platforms"].get(platform)
    if not raw:
        return None
    known = {f for f in TokenEntry.__dataclass_fields__}
    return TokenEntry(**{k: v for k, v in raw.items() if k in known})


def save(entry: TokenEntry) -> None:
    if not entry.obtained_at:
        entry.obtained_at = time.time()
    data = _read_raw()
    data["version"] = SCHEMA_VERSION
    data["platforms"][entry.platform] = asdict(entry)
    _write_raw(data)


def remove(platform: str) -> bool:
    data = _read_raw()
    if platform not in data["platforms"]:
        return False
    del data["platforms"][platform]
    _write_raw(data)
    return True


def all_entries() -> list[TokenEntry]:
    known = {f for f in TokenEntry.__dataclass_fields__}
    out = []
    for raw in _read_raw()["platforms"].values():
        out.append(TokenEntry(**{k: v for k, v in raw.items() if k in known}))
    return sorted(out, key=lambda e: e.platform)


# ── the part publishers actually call ───────────────────────────────────────


def has_usable(platform: str) -> bool:
    """Cheap, offline check for --list-platforms. No refresh attempted."""
    entry = read(platform)
    if entry is None or not entry.access_token:
        return False
    if not entry.expired():
        return True
    # Expired but refreshable counts as usable — get_valid() will renew it.
    return bool(entry.refresh_token and platform in _REFRESHERS)


def get_valid(platform: str) -> str:
    """Return a live access token, refreshing first if it is close to expiry."""
    entry = read(platform)
    if entry is None or not entry.access_token:
        raise TokenError(platform, "no token stored")

    if not entry.expired():
        return entry.access_token

    refresher = _REFRESHERS.get(platform)
    if refresher is None:
        raise TokenError(
            platform, f"token expired {entry.expires_in_human()} ago and this platform has no refresh flow"
        )

    # Deliberately no "is there a refresh token?" check here. Whether one is
    # needed is a property of the platform's flow, and this module has no
    # business knowing it: Meta's long-lived tokens renew using the access
    # token itself and never store a refresh token, so a guard here silently
    # made Threads unrefreshable. Each refresher validates its own inputs.
    try:
        refreshed = refresher(entry)
    except TokenError:
        raise
    except Exception as exc:  # noqa: BLE001 — surface as a typed, actionable error
        raise TokenError(platform, f"refresh failed: {exc}") from exc

    save(refreshed)
    return refreshed.access_token


def status_lines() -> list[str]:
    """Human-readable summary for `skills-keys --oauth-status`. Never prints a token."""
    entries = all_entries()
    if not entries:
        return ["No social accounts connected. Run: python3 -m common.runners.cli.auth --platform <name>"]
    lines = []
    for e in entries:
        label = e.account_label or e.account_id or "(unknown account)"
        lines.append(f"  {e.platform:12s} {label:24s} {e.masked():14s} expires in {e.expires_in_human()}")
    return lines
