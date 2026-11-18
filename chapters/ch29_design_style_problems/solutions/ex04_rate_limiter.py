"""
Exercise 04 — Rate Limiters with an Injectable Clock [Tier: ★ Core]
Chapter 29 · Pattern: time windows, queues, token bucket · Target time: 40 min

Problem
-------
Implement four per-client rate limiters that share one API:

    limiter.allow(client_id) -> bool     # True = serve the request, False = reject (HTTP 429)

1. `FixedWindowLimiter(limit, window, clock)`   — at most `limit` requests per aligned
   window [k*window, (k+1)*window).
2. `SlidingLogLimiter(limit, window, clock)`    — at most `limit` requests in any
   half-open interval (now - window, now]; keeps a timestamp log per client.
3. `SlidingWindowCounterLimiter(limit, window, clock)` — approximates the sliding window
   with two fixed-window counters: estimate = prev_count * overlap_fraction + curr_count.
4. `TokenBucketLimiter(capacity, refill_rate, clock)` — a bucket of up to `capacity`
   tokens refilled continuously at `refill_rate` tokens/second; a request costs 1 token.

Time comes from an injected `clock` (a zero-argument callable returning seconds). Tests
and demos use `FakeClock`, so results never depend on the wall clock.

Examples
--------
>>> clock = FakeClock()
>>> rl = FixedWindowLimiter(limit=2, window=10, clock=clock)
>>> [rl.allow("u1") for _ in range(3)]
[True, True, False]
>>> clock.advance(10); rl.allow("u1")
True

Constraints
-----------
- Timestamps are non-decreasing. limit >= 1, window > 0, capacity >= 1, refill_rate > 0.
- Memory: fixed window/counter/bucket O(1) per client; sliding log O(limit) per client.

Approach ladder
---------------
1. Fixed window — one counter per (client, window index). O(1) time/space, but allows a
   burst of 2*limit across a window boundary (limit at 9.9s + limit at 10.0s).
2. Sliding log — deque of timestamps; pop those older than now-window, then compare the
   length with the limit. Exact, but O(limit) memory per client.
3. Sliding window counter — two counters per client, O(1) memory, approximation error is
   small in practice (assumes requests in the previous window were evenly spread).
4. Token bucket — two numbers per client (tokens, last_refill); allows controlled bursts
   up to `capacity` while enforcing a long-run average rate. Lazy refill on each call
   means no background timer is needed.

Hints
-----
- Never call `time.time()` inside the limiter; call `self.clock()`.
- Sliding log: should a rejected request be logged? (No — otherwise a client that keeps
  retrying can lock itself out forever.)
- Token bucket refill: tokens = min(capacity, tokens + elapsed * rate).

Follow-ups
----------
- Distributed limiter: store counters in Redis with INCR + EXPIRE (fixed window) or a Lua
  script (token bucket) so the check-and-update is atomic.
- Return `Retry-After`: how long until the next request would be allowed?
- Memory cleanup for idle clients (TTL eviction, or an LRU of client states).
"""
from __future__ import annotations

from collections import deque
from typing import Callable

Clock = Callable[[], float]


# provided
class FakeClock:
    """A controllable clock: call it to read the time, `advance` / `set` to move it."""

    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds

    def set(self, t: float) -> None:
        self.now = t


class FixedWindowLimiter:
    def __init__(self, limit: int, window: float, clock: Clock) -> None:
        self.limit, self.window, self.clock = limit, window, clock
        self.state: dict[str, tuple[int, int]] = {}      # client -> (window_index, count)

    def allow(self, client: str) -> bool:
        idx = int(self.clock() // self.window)
        w, count = self.state.get(client, (idx, 0))
        if w != idx:                                       # new window: reset
            w, count = idx, 0
        if count < self.limit:
            self.state[client] = (w, count + 1)
            return True
        self.state[client] = (w, count)
        return False


class SlidingLogLimiter:
    def __init__(self, limit: int, window: float, clock: Clock) -> None:
        self.limit, self.window, self.clock = limit, window, clock
        self.logs: dict[str, deque[float]] = {}

    def allow(self, client: str) -> bool:
        now = self.clock()
        log = self.logs.setdefault(client, deque())
        while log and log[0] <= now - self.window:         # expire old timestamps
            log.popleft()
        if len(log) < self.limit:
            log.append(now)
            return True
        return False

    def retry_after(self, client: str) -> float:
        """Seconds until the next request would be allowed (0 if allowed now)."""
        now = self.clock()
        log = self.logs.get(client, deque())
        live = [t for t in log if t > now - self.window]
        if len(live) < self.limit:
            return 0.0
        return live[len(live) - self.limit] + self.window - now


class SlidingWindowCounterLimiter:
    def __init__(self, limit: int, window: float, clock: Clock) -> None:
        self.limit, self.window, self.clock = limit, window, clock
        self.state: dict[str, list] = {}                   # client -> [idx, prev, curr]

    def allow(self, client: str) -> bool:
        now = self.clock()
        idx = int(now // self.window)
        st = self.state.setdefault(client, [idx, 0, 0])
        if idx == st[0] + 1:                               # moved into the next window
            st[:] = [idx, st[2], 0]
        elif idx > st[0] + 1:                              # skipped windows: all quiet
            st[:] = [idx, 0, 0]
        elapsed_fraction = (now - idx * self.window) / self.window
        estimate = st[1] * (1 - elapsed_fraction) + st[2]
        if estimate < self.limit:
            st[2] += 1
            return True
        return False


class TokenBucketLimiter:
    def __init__(self, capacity: int, refill_rate: float, clock: Clock) -> None:
        self.capacity, self.rate, self.clock = capacity, refill_rate, clock
        self.buckets: dict[str, tuple[float, float]] = {}  # client -> (tokens, last_time)

    def allow(self, client: str, cost: float = 1.0) -> bool:
        now = self.clock()
        tokens, last = self.buckets.get(client, (float(self.capacity), now))
        tokens = min(self.capacity, tokens + (now - last) * self.rate)   # lazy refill
        if tokens >= cost:
            self.buckets[client] = (tokens - cost, now)
            return True
        self.buckets[client] = (tokens, now)
        return False


def simulate(limiter_factory, times: list[float], client: str = "u") -> str:
    """Run requests at the given times; return a string like '11011' (1 = allowed)."""
    clock = FakeClock()
    limiter = limiter_factory(clock)
    out = []
    for t in times:
        clock.set(t)
        out.append("1" if limiter.allow(client) else "0")
    return "".join(out)


def main() -> None:
    # The classic boundary burst: 3 requests at t=9.5 and 3 at t=10.0, limit 3 per 10s.
    times = [9.5, 9.6, 9.7, 10.0, 10.1, 10.2, 19.6, 25.0]
    factories = {
        "fixed window": lambda c: FixedWindowLimiter(3, 10, c),
        "sliding log": lambda c: SlidingLogLimiter(3, 10, c),
        "sliding counter": lambda c: SlidingWindowCounterLimiter(3, 10, c),
        "token bucket (cap 3, 0.3/s)": lambda c: TokenBucketLimiter(3, 0.3, c),
    }
    print("request times:", times)
    for name, factory in factories.items():
        print(f"{name:<28} {simulate(factory, times)}")

    # Clients are independent.
    clock = FakeClock()
    rl = SlidingLogLimiter(2, 60, clock)
    print("alice x3:", [rl.allow("alice") for _ in range(3)], " bob:", rl.allow("bob"))
    clock.advance(30)
    print("retry_after(alice) at t=30:", rl.retry_after("alice"))
    clock.advance(30)
    print("alice at t=60:", rl.allow("alice"))

    # Token bucket: burst then steady rate.
    clock = FakeClock()
    tb = TokenBucketLimiter(capacity=5, refill_rate=1.0, clock=clock)
    burst = sum(tb.allow("x") for _ in range(10))
    print("token bucket burst of 10 at t=0 -> allowed", burst)
    allowed = 0
    for _ in range(10):
        clock.advance(0.5)
        allowed += tb.allow("x")
    print("then 10 requests every 0.5s -> allowed", allowed, "(rate 1/s)")


if __name__ == "__main__":
    main()
