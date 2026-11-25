"""
Exercise 05 — Retry with Exponential Backoff (injectable sleep)        [Tier: ★ Core]
Chapter 25 · Pattern: decorator factory + dependency injection · Target time: 25 min

Problem
-------
Write `retry(times=3, *, exceptions=(Exception,), base_delay=0.1, factor=2.0,
max_delay=None, sleep=time.sleep)`, a decorator factory.

- Call the function at most `times` attempts in total (times >= 1, else
  ValueError at decoration time).
- If an attempt raises one of `exceptions`, wait and try again. The wait before
  retry k (k = 1, 2, ...) is base_delay * factor**(k-1), capped at max_delay.
- Any other exception propagates immediately, with no retry and no sleep.
- When the last attempt fails, re-raise THAT exception unchanged.
- All waiting goes through the injected `sleep`, so tests run instantly and can
  assert the exact delays. Keep the original name/doc (functools.wraps).

Examples
--------
>>> waits = []
>>> flaky = Flaky(fail_times=2)
>>> retry(3, sleep=waits.append)(flaky)()
'ok after 3 attempts'
>>> waits
[0.1, 0.2]

Constraints
-----------
- 1 <= times <= 20; delays are floats >= 0.

Hints
-----
- Three levels: retry(config) -> decorator(func) -> wrapper(*args, **kwargs).
- `except exceptions:` accepts a tuple of exception classes.
- A bare `raise` inside the except block re-raises the current exception.
- Default arguments are evaluated once: `sleep=time.sleep` binds the real
  function when `retry` is defined, so patching `time.sleep` later does not
  reach it. Inject instead.

Follow-ups
----------
- Add jitter (random fraction of the delay) and a total-time budget; jitter and
  idempotency are §42.3.
- Retry only on specific results (e.g. HTTP 503) instead of exceptions.
- Make an async version (`await asyncio.sleep(delay)`), Chapter 28.
- Log each failure: combine with ex06's log_calls.
"""
from __future__ import annotations

import time
from functools import wraps
from typing import Callable


def retry(times: int = 3, *, exceptions: tuple[type[BaseException], ...] = (Exception,),
          base_delay: float = 0.1, factor: float = 2.0, max_delay: float | None = None,
          sleep: Callable[[float], object] = time.sleep):
    raise NotImplementedError("TODO")


class Flaky:
    """Test double: raises `error` for the first `fail_times` calls, then succeeds."""

    def __init__(self, fail_times: int, error: type[Exception] = ConnectionError) -> None:
        self.fail_times, self.error, self.attempts = fail_times, error, 0
        self.__name__ = "flaky"

    def __call__(self) -> str:
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise self.error(f"attempt {self.attempts} failed")
        return f"ok after {self.attempts} attempts"


def main() -> None:
    cases = [
        ("succeeds on 3rd", dict(times=3), Flaky(2)),
        ("gives up", dict(times=3), Flaky(5)),
        ("capped delays", dict(times=5, base_delay=1.0, max_delay=3.0), Flaky(4)),
        ("not retryable", dict(times=3, exceptions=(ConnectionError,)), Flaky(1, KeyError)),
    ]
    for label, config, flaky in cases:
        waits: list[float] = []
        call = retry(**config, sleep=waits.append)(flaky)
        try:
            result = call()
        except Exception as exc:
            result = f"raised {type(exc).__name__}({exc})"
        print(f"{label:15} attempts={flaky.attempts} waits={waits!s:22} -> {result}")
    try:
        retry(0)
    except ValueError as exc:
        print("retry(0):", exc)


if __name__ == "__main__":
    main()
