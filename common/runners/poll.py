"""poll-with-timeout helper for async vendors (video, music).

Pattern mirrored from the author's earlier production polling layer —
simple poll loop with exponential-ish backoff and a max wait time.
"""

from __future__ import annotations

import sys
import time
from collections.abc import Callable
from typing import TypeVar

from .errors import TimeoutError as RunnerTimeoutError

T = TypeVar("T")


def poll_until(
    check: Callable[[], T | None],
    *,
    provider: str,
    timeout: float = 600.0,
    initial_interval: float = 3.0,
    max_interval: float = 12.0,
    progress: bool = True,
) -> T:
    """Call check() in a loop until it returns non-None or timeout fires.

    Backs off from initial_interval to max_interval. Prints a dot per attempt to stderr
    when progress=True. Raises RunnerTimeoutError if max wait exceeded.
    """
    started = time.monotonic()
    interval = initial_interval
    attempt = 0

    while True:
        result = check()
        if result is not None:
            if progress:
                sys.stderr.write(f" done ({time.monotonic() - started:.1f}s)\n")
                sys.stderr.flush()
            return result

        elapsed = time.monotonic() - started
        if elapsed >= timeout:
            if progress:
                sys.stderr.write(" timeout\n")
                sys.stderr.flush()
            raise RunnerTimeoutError(provider, elapsed)

        if progress:
            sys.stderr.write(".")
            sys.stderr.flush()

        time.sleep(min(interval, timeout - elapsed))
        attempt += 1
        # gentle backoff: x1.5 capped at max_interval, but only every 3 attempts
        if attempt % 3 == 0:
            interval = min(interval * 1.5, max_interval)
