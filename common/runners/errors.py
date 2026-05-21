"""Typed errors for the runners layer."""

from __future__ import annotations


class RunnerError(Exception):
    """Base class for all runner errors."""


class KeyMissingError(RunnerError):
    """Required env var is missing or empty."""

    def __init__(self, provider: str, env_vars: list[str]):
        self.provider = provider
        self.env_vars = env_vars
        joined = " / ".join(env_vars)
        super().__init__(
            f"provider '{provider}' requires env var(s): {joined}. "
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
