"""Provider key verification — lightweight HTTP ping per env var.

Returns one of: 'valid' / 'invalid' / 'unknown' / 'unsupported' / 'unset'.
We avoid using vendor SDKs to keep this dependency-free at import time and
to surface raw HTTP statuses (401 = invalid, 200 = valid, anything else = unknown).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import urllib.error
import urllib.request


@dataclass
class VerifyResult:
    env_var: str
    status: str            # valid | invalid | unknown | unsupported | unset
    detail: str = ""       # short human note (model count, error code, etc.)


_TIMEOUT = 8  # seconds


def _http(url: str, headers: dict[str, str], *, timeout: int = _TIMEOUT) -> tuple[int, str]:
    """Tiny urllib wrapper. Returns (status, body[:200])."""
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(200).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read(200).decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            body = ""
        return exc.code, body
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, ""


# ----- per-provider probes -------------------------------------------------


def _probe_openai(key: str) -> VerifyResult:
    code, body = _http(
        "https://api.openai.com/v1/models",
        {"Authorization": f"Bearer {key}", "User-Agent": "skills-keys/1.0"},
    )
    if code == 200:
        return VerifyResult("OPENAI_API_KEY", "valid", "models endpoint OK")
    if code == 401:
        return VerifyResult("OPENAI_API_KEY", "invalid", "401 unauthorized")
    if code == 0:
        return VerifyResult("OPENAI_API_KEY", "unknown", "network error / timeout")
    return VerifyResult("OPENAI_API_KEY", "unknown", f"HTTP {code}")


def _probe_gemini(key: str) -> VerifyResult:
    code, body = _http(
        f"https://generativelanguage.googleapis.com/v1/models?key={key}",
        {"User-Agent": "skills-keys/1.0"},
    )
    if code == 200:
        return VerifyResult("GEMINI_API_KEY", "valid", "models endpoint OK")
    if code in {400, 401, 403}:
        return VerifyResult("GEMINI_API_KEY", "invalid", f"HTTP {code}")
    if code == 0:
        return VerifyResult("GEMINI_API_KEY", "unknown", "network error / timeout")
    return VerifyResult("GEMINI_API_KEY", "unknown", f"HTTP {code}")


def _probe_anthropic(key: str) -> VerifyResult:
    code, body = _http(
        "https://api.anthropic.com/v1/models",
        {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "User-Agent": "skills-keys/1.0",
        },
    )
    if code == 200:
        return VerifyResult("ANTHROPIC_API_KEY", "valid", "models endpoint OK")
    if code in {401, 403}:
        return VerifyResult("ANTHROPIC_API_KEY", "invalid", f"HTTP {code}")
    if code == 0:
        return VerifyResult("ANTHROPIC_API_KEY", "unknown", "network error / timeout")
    return VerifyResult("ANTHROPIC_API_KEY", "unknown", f"HTTP {code}")


def _probe_bfl(key: str) -> VerifyResult:
    code, body = _http(
        "https://api.bfl.ai/v1/get_result?id=test",
        {"x-key": key, "User-Agent": "skills-keys/1.0"},
    )
    # Invalid id but valid key → 200 with "not_found" OR 400. 401 = bad key.
    if code in {200, 400, 404, 422}:
        return VerifyResult("BFL_API_KEY", "valid", f"HTTP {code} (key authenticated)")
    if code in {401, 403}:
        return VerifyResult("BFL_API_KEY", "invalid", f"HTTP {code}")
    if code == 0:
        return VerifyResult("BFL_API_KEY", "unknown", "network error / timeout")
    return VerifyResult("BFL_API_KEY", "unknown", f"HTTP {code}")


def _probe_ideogram(key: str) -> VerifyResult:
    # No public list endpoint — try a minimal generate which will 400 on missing
    # body but 401 on bad key.
    code, body = _http(
        "https://api.ideogram.ai/api/v1/styles",
        {"Api-Key": key, "User-Agent": "skills-keys/1.0"},
    )
    if code == 200:
        return VerifyResult("IDEOGRAM_API_KEY", "valid", "styles endpoint OK")
    if code in {401, 403}:
        return VerifyResult("IDEOGRAM_API_KEY", "invalid", f"HTTP {code}")
    if code == 404:
        # Endpoint may not exist; try alternate
        return VerifyResult("IDEOGRAM_API_KEY", "unknown", "alt endpoint required")
    if code == 0:
        return VerifyResult("IDEOGRAM_API_KEY", "unknown", "network error / timeout")
    return VerifyResult("IDEOGRAM_API_KEY", "unknown", f"HTTP {code}")


def _probe_replicate(key: str) -> VerifyResult:
    code, body = _http(
        "https://api.replicate.com/v1/account",
        {"Authorization": f"Token {key}", "User-Agent": "skills-keys/1.0"},
    )
    if code == 200:
        return VerifyResult("REPLICATE_API_TOKEN", "valid", "account endpoint OK")
    if code in {401, 403}:
        return VerifyResult("REPLICATE_API_TOKEN", "invalid", f"HTTP {code}")
    if code == 0:
        return VerifyResult("REPLICATE_API_TOKEN", "unknown", "network error / timeout")
    return VerifyResult("REPLICATE_API_TOKEN", "unknown", f"HTTP {code}")


def _probe_fal(key: str) -> VerifyResult:
    # fal exposes /api/keys/whoami but it requires the new auth header style.
    code, body = _http(
        "https://fal.run/health",
        {"Authorization": f"Key {key}", "User-Agent": "skills-keys/1.0"},
    )
    if code == 200:
        return VerifyResult("FAL_KEY", "valid", "health endpoint OK")
    if code in {401, 403}:
        return VerifyResult("FAL_KEY", "invalid", f"HTTP {code}")
    if code == 0:
        return VerifyResult("FAL_KEY", "unknown", "network error / timeout")
    return VerifyResult("FAL_KEY", "unknown", f"HTTP {code}")


def _probe_runway(key: str) -> VerifyResult:
    code, body = _http(
        "https://api.dev.runwayml.com/v1/tasks?limit=1",
        {
            "Authorization": f"Bearer {key}",
            "X-Runway-Version": "2024-11-06",
            "User-Agent": "skills-keys/1.0",
        },
    )
    if code == 200:
        return VerifyResult("RUNWAY_API_KEY", "valid", "tasks endpoint OK")
    if code in {401, 403}:
        return VerifyResult("RUNWAY_API_KEY", "invalid", f"HTTP {code}")
    if code == 0:
        return VerifyResult("RUNWAY_API_KEY", "unknown", "network error / timeout")
    return VerifyResult("RUNWAY_API_KEY", "unknown", f"HTTP {code}")


def _probe_elevenlabs(key: str) -> VerifyResult:
    code, body = _http(
        "https://api.elevenlabs.io/v1/user",
        {"xi-api-key": key, "User-Agent": "skills-keys/1.0"},
    )
    if code == 200:
        return VerifyResult("ELEVENLABS_API_KEY", "valid", "user endpoint OK")
    if code in {401, 403}:
        return VerifyResult("ELEVENLABS_API_KEY", "invalid", f"HTTP {code}")
    if code == 0:
        return VerifyResult("ELEVENLABS_API_KEY", "unknown", "network error / timeout")
    return VerifyResult("ELEVENLABS_API_KEY", "unknown", f"HTTP {code}")


# Suno doesn't have a standard public verify endpoint; we skip
# (return unsupported) so users know to test by generating.
# Kling uses a key-pair signature scheme — verify requires building a JWT;
# skip in v1.


_PROBES: dict[str, Callable[[str], VerifyResult]] = {
    "OPENAI_API_KEY": _probe_openai,
    "GEMINI_API_KEY": _probe_gemini,
    "ANTHROPIC_API_KEY": _probe_anthropic,
    "BFL_API_KEY": _probe_bfl,
    "IDEOGRAM_API_KEY": _probe_ideogram,
    "REPLICATE_API_TOKEN": _probe_replicate,
    "FAL_KEY": _probe_fal,
    "RUNWAY_API_KEY": _probe_runway,
    "ELEVENLABS_API_KEY": _probe_elevenlabs,
}


def supported_envs() -> list[str]:
    return sorted(_PROBES)


def verify_key(env_var: str, value: str | None) -> VerifyResult:
    if env_var not in _PROBES:
        return VerifyResult(env_var, "unsupported", "no verify endpoint configured")
    if not value:
        return VerifyResult(env_var, "unset", "no value")
    try:
        return _PROBES[env_var](value)
    except Exception as exc:  # noqa: BLE001
        return VerifyResult(env_var, "unknown", f"{type(exc).__name__}: {exc}")
