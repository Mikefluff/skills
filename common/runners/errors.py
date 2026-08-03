"""Typed errors for the runners layer."""

from __future__ import annotations


class RunnerError(Exception):
    """Base class for all runner errors."""


class KeyMissingError(RunnerError):
    """Required env var is missing or empty."""

    def __init__(self, provider: str, env_vars: list[str], kind: str = "provider"):
        self.provider = provider
        self.env_vars = env_vars
        joined = " / ".join(env_vars)
        super().__init__(
            f"{kind} '{provider}' requires env var(s): {joined}. "
            f"Set them in your shell (.zshrc/.bashrc) or source a .env file."
        )


class ProviderError(RunnerError):
    """Vendor API returned an error status."""

    def __init__(self, provider: str, status: int | None, message: str):
        self.provider = provider
        self.status = status
        self.message = message
        prefix = f"[{provider}]"
        if status is not None:
            prefix = f"[{provider} {status}]"
        super().__init__(f"{prefix} {message}")


class QuotaError(ProviderError):
    """Vendor returned 429 / quota / billing error."""


class TimeoutError(RunnerError):
    """Polling exceeded max wait time."""

    def __init__(self, provider: str, elapsed: float):
        self.provider = provider
        self.elapsed = elapsed
        super().__init__(
            f"provider '{provider}' did not finish within {elapsed:.0f}s. "
            f"Job may still complete server-side; check vendor dashboard."
        )


class CostConfirmationDeclined(RunnerError):
    """User answered 'n' to the cost confirmation prompt."""

    def __init__(self, estimated_usd: float):
        super().__init__(f"user declined cost confirmation (estimated ${estimated_usd:.4f})")


# ───────────────────────────────────────────────────────────────────────────
# Publishing layer (common/runners/publishers/)
# ───────────────────────────────────────────────────────────────────────────


class PublishError(RunnerError):
    """Platform API refused the post."""

    def __init__(self, platform: str, status: int | None, message: str):
        self.platform = platform
        self.status = status
        self.message = message
        prefix = f"[{platform}]" if status is None else f"[{platform} {status}]"
        super().__init__(f"{prefix} {message}")


class RateLimitError(PublishError):
    """Platform returned 429 or a documented posting-cap error."""


class TokenError(RunnerError):
    """OAuth token is missing, expired, or could not be refreshed."""

    def __init__(self, platform: str, reason: str):
        self.platform = platform
        super().__init__(
            f"no usable token for '{platform}': {reason}. "
            f"Run: python3 -m common.runners.cli.auth --platform {platform}"
        )


class PreflightFailed(RunnerError):
    """One or more blocking violations — nothing was sent."""

    def __init__(self, platform: str, violations: list[str]):
        self.platform = platform
        self.violations = violations
        joined = "\n  - ".join(violations)
        super().__init__(f"preflight failed for '{platform}':\n  - {joined}")


class UnsupportedPost(RunnerError):
    """Platform cannot carry this post kind (e.g. carousel on YouTube)."""

    def __init__(self, platform: str, kind: str, supported: list[str]):
        self.platform = platform
        self.kind = kind
        super().__init__(
            f"'{platform}' does not support {kind} posts. Supported: {', '.join(sorted(supported))}"
        )


class AlreadyPublished(RunnerError):
    """A receipt records this exact content already going to this platform."""

    def __init__(self, platform: str, permalink: str | None, when: str):
        self.platform = platform
        self.permalink = permalink
        where = permalink or "(no permalink recorded)"
        super().__init__(
            f"identical content already published to '{platform}' at {when}: {where}. "
            f"Pass --force to post it again."
        )
