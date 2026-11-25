"""
Exercise 11 — Async Retry with Per-Attempt Timeout and Backoff   [Tier: ◆ Extended]
Chapter 28 · Pattern: wait_for per attempt, exponential backoff + full jitter · Target time: 25 min

Problem
-------
Write `retry(op, attempts, base, cap, timeout, rng)`:

- call `await op()` up to `attempts` times; each attempt is limited to `timeout` seconds;
- retry only on `ConnectionError` or a timeout; any other exception propagates at once;
- before retry k (k = 1, 2, …) sleep `rng.uniform(0, min(cap, base * 2**(k-1)))` seconds
  ("full jitter"); `rng` is an injected `random.Random`, so tests are reproducible;
- return `(result, log)` where `log` lists `"t=<time> attempt <n>: <outcome>"` lines using
  `loop.time()` rounded to 3 decimals; after the last failure raise `RetryError` (given) whose
  `.log` holds the log.

`FlakyService(script)` is a given fake: each call consumes the next script entry: "ok"
returns "payload", "fail" raises ConnectionError, "hang" sleeps 60 s, "bug" raises KeyError.
Everything runs on the virtual clock (`vclock.run_virtual`).

Examples
--------
>>> r, log = run_virtual(retry(FlakyService(["fail", "ok"]).call, 3, 0.1, 1.0, 1.0,
...                            random.Random(0)))
>>> r, len(log)
('payload', 2)

Constraints
-----------
- attempts >= 1, 0 < base <= cap, timeout > 0.


Hints
-----
- Catch `asyncio.TimeoutError` (aliases builtin `TimeoutError` on 3.11+) around `wait_for`.
- Do not sleep after the final attempt.
- Never retry on `CancelledError` (the caller wants you to stop) or on programming errors.

Follow-ups
----------
- Respect a server's `Retry-After` hint instead of the computed backoff.
- Retrying non-idempotent operations (payments) needs an idempotency key.
- Circuit breaker: stop calling after many consecutive failures, probe again later.
"""
from __future__ import annotations

import asyncio
import random
from typing import Awaitable, Callable

from vclock import run_virtual


class RetryError(Exception):  # given
    def __init__(self, log: list[str]) -> None:
        super().__init__(f"gave up after {len(log)} attempts")
        self.log = log


class FlakyService:  # given
    def __init__(self, script: list[str]) -> None:
        self.script = list(script)
        self.calls = 0

    async def call(self) -> str:
        step = self.script[self.calls]
        self.calls += 1
        await asyncio.sleep(0.05)                   # every call costs 50 ms of "network"
        if step == "fail":
            raise ConnectionError("connection reset")
        if step == "hang":
            await asyncio.sleep(60)
        if step == "bug":
            raise KeyError("missing field")
        return "payload"


async def retry(op: Callable[[], Awaitable[str]], attempts: int, base: float, cap: float,
                timeout: float, rng: random.Random) -> tuple[str, list[str]]:
    raise NotImplementedError("TODO")


def main() -> None:
    svc = FlakyService(["fail", "hang", "fail", "ok"])
    result, log = run_virtual(retry(svc.call, 5, base=0.2, cap=1.0, timeout=0.5,
                                    rng=random.Random(7)))
    print("result:", result, "after", svc.calls, "calls")
    print("\n".join(log))
    try:
        run_virtual(retry(FlakyService(["fail"] * 3).call, 3, 0.2, 1.0, 0.5, random.Random(7)))
    except RetryError as exc:
        print("exhausted:", exc, "| last:", exc.log[-1])
    try:
        run_virtual(retry(FlakyService(["bug", "ok"]).call, 3, 0.2, 1.0, 0.5, random.Random(7)))
    except KeyError as exc:
        print("not retried:", type(exc).__name__, exc)


if __name__ == "__main__":
    main()
