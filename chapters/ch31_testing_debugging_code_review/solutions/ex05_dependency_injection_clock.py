"""
Exercise 05 — Testable Time and Randomness via Injection   [Tier: ★ Core]
Chapter 31 · Pattern: dependency injection, fakes vs patch · Target time: 25 min

Problem
-------
Implement a token-bucket ``RateLimiter(capacity, refill_per_sec, clock=time.monotonic)``:
the bucket starts full; ``allow()`` spends one token and returns True, or returns False when
empty; tokens refill continuously at ``refill_per_sec`` up to ``capacity``.

Also implement ``backoff_delays(attempts, base, cap, rng)`` returning "full jitter"
exponential back-off delays: attempt k waits ``rng.uniform(0, min(cap, base * 2**k))``.

Both depend on things tests cannot control — the wall clock and randomness — so take them as
parameters. Write tests with a ``FakeClock`` and a seeded ``random.Random``: no ``sleep``, no
flakiness, and every test finishes instantly.

Examples
--------
>>> clock = FakeClock()
>>> rl = RateLimiter(capacity=2, refill_per_sec=1.0, clock=clock)
>>> [rl.allow(), rl.allow(), rl.allow()]
[True, True, False]
>>> clock.advance(1.0); rl.allow()
True

Constraints
-----------
- capacity >= 1, refill_per_sec > 0 (ValueError otherwise).

Approach ladder
---------------
1. Brute force — call ``time.sleep(1)`` in tests and hope; slow and flaky on busy CI.
2. Improved   — ``mock.patch("time.monotonic")``; works, but patches every user of the
   module-level function and breaks if the code switches to ``time.perf_counter``.
3. Optimal    — constructor injection with a production default: tests pass a fake, callers
   change nothing. O(1) per ``allow()``.

Follow-ups
----------
- Why ``time.monotonic`` and not ``time.time``? Wall-clock time can jump (NTP, DST).
- Thread safety: wrap ``allow`` in a ``threading.Lock`` if called from several threads.
"""
from __future__ import annotations

import random
import time
from collections.abc import Callable

import pytest


class FakeClock:
    """A controllable clock: call it to read the time, ``advance`` to move it forward."""

    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class RateLimiter:
    def __init__(self, capacity: int, refill_per_sec: float,
                 clock: Callable[[], float] = time.monotonic) -> None:
        if capacity < 1 or refill_per_sec <= 0:
            raise ValueError("capacity must be >= 1 and refill_per_sec > 0")
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self._clock = clock
        self._tokens = float(capacity)
        self._last = clock()

    def _refill(self) -> None:
        now = self._clock()
        self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.refill_per_sec)
        self._last = now

    def allow(self) -> bool:
        self._refill()
        if self._tokens >= 1:
            self._tokens -= 1
            return True
        return False


def backoff_delays(attempts: int, base: float, cap: float, rng: random.Random) -> list[float]:
    return [rng.uniform(0, min(cap, base * 2 ** k)) for k in range(attempts)]


def solve(events: list[tuple[float, str]], capacity: int, refill: float) -> list[bool]:
    """Replay (time, 'req') events against a limiter; return the allow() results."""
    clock = FakeClock()
    limiter = RateLimiter(capacity, refill, clock)
    out = []
    for t, _ in events:
        clock.advance(t - clock.now)
        out.append(limiter.allow())
    return out


# ------------------------------------------------------------------ embedded pytest suite
@pytest.fixture
def clock():
    return FakeClock(start=1000.0)


def test_burst_up_to_capacity_then_reject(clock):
    rl = RateLimiter(3, 1.0, clock)
    assert [rl.allow() for _ in range(4)] == [True, True, True, False]


def test_refills_over_time(clock):
    rl = RateLimiter(2, 2.0, clock)
    rl.allow(), rl.allow()
    clock.advance(0.25)            # half a token
    assert rl.allow() is False
    clock.advance(0.25)            # now one full token
    assert rl.allow() is True


def test_never_exceeds_capacity(clock):
    rl = RateLimiter(2, 10.0, clock)
    clock.advance(3600)            # an hour idle must not bank 36,000 tokens
    assert [rl.allow() for _ in range(3)] == [True, True, False]


@pytest.mark.parametrize("capacity, refill", [(0, 1.0), (1, 0.0), (1, -2.0)])
def test_rejects_bad_config(capacity, refill):
    with pytest.raises(ValueError):
        RateLimiter(capacity, refill, FakeClock())


def test_backoff_is_reproducible_and_bounded():
    a = backoff_delays(6, 0.5, 4.0, random.Random(7))
    b = backoff_delays(6, 0.5, 4.0, random.Random(7))
    assert a == b                                   # same seed, same delays
    assert all(0 <= d <= min(4.0, 0.5 * 2 ** k) for k, d in enumerate(a))


def test_patching_is_the_fallback(monkeypatch):
    fake = FakeClock(50.0)
    monkeypatch.setattr(time, "monotonic", fake)    # undone automatically after the test
    rl = RateLimiter(1, 1.0, clock=time.monotonic)  # default arg was bound at import time!
    assert rl._clock is not fake                    # ...so the patch did NOT reach it


def main() -> None:
    clock = FakeClock()
    rl = RateLimiter(capacity=3, refill_per_sec=1.0, clock=clock)
    timeline = []
    for step in range(8):
        timeline.append(f"t={clock():.1f}s {'allow' if rl.allow() else 'deny '}")
        clock.advance(0.4)
    print("token bucket (capacity 3, 1 token/s), one request every 0.4 s:")
    for line in timeline:
        print("  " + line)
    print("replayed events:", solve([(0, "req"), (0, "req"), (0.5, "req"), (1.0, "req")], 2, 1.0))
    delays = backoff_delays(5, base=0.5, cap=4.0, rng=random.Random(7))
    print("backoff delays (seed 7):", [round(d, 3) for d in delays])
    print()
    from ch31_testkit import print_results, run_embedded_tests

    print_results(run_embedded_tests(__file__))


if __name__ == "__main__":
    main()
