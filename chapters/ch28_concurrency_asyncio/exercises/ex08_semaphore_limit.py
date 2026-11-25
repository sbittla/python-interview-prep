"""
Exercise 08 — Bounded Concurrency with asyncio.Semaphore        [Tier: ★ Core]
Chapter 28 · Pattern: cap in-flight work at k; results in input order · Target time: 25 min

Problem
-------
You must call `fake_fetch(url)` for n URLs, but the server allows at most `limit` requests in
flight. Write `fetch_bounded(urls, limit, probe)` returning results in **input order**, where a
failed fetch yields `"error: <ExcType>"`. `probe` is a given `Probe` object: call
`probe.enter()` just before each request and `probe.leave()` just after (success or not); it
records the peak number of requests in flight.

Also write `fetch_worker_pool(urls, limit, probe)`: the same contract using exactly `limit`
worker tasks that pull indices from an `asyncio.Queue` instead of one task per URL.

Each request takes `len(url) / 10` seconds on the virtual clock (`vclock.run_virtual`), so the
elapsed time is exact: e.g. 6 equal requests of 0.4 s with limit 2 take 3 rounds = 1.2 s.

Examples
--------
>>> p = Probe(); run_virtual(fetch_bounded(["a", "bb", "ccc"], 2, p)), p.peak
(['A', 'BB', 'CCC'], 2)

Constraints
-----------
- 0 <= n <= 10**4, 1 <= limit. The semaphore is created inside the coroutine (per run).


Hints
-----
- Put `async with sem:` *inside* the per-URL coroutine, around only the request.
- `gather` keeps input order even though completion order differs.
- `probe.leave()` belongs in a `finally` so failed requests release their slot in the count.

Follow-ups
----------
- Rate limit (requests per second) instead of concurrency limit: token bucket (→ §29.5).
- Per-host limits: a dict of semaphores keyed by host.
- LLM API fan-out with the same pattern plus `return_exceptions=True` (→ §42.2).
"""
from __future__ import annotations

import asyncio

from vclock import run_virtual


class Probe:  # given
    """Counts requests in flight. Single-threaded event loop, so no lock is needed."""

    def __init__(self) -> None:
        self.now = 0
        self.peak = 0

    def enter(self) -> None:
        self.now += 1
        self.peak = max(self.peak, self.now)

    def leave(self) -> None:
        self.now -= 1


async def fake_fetch(url: str) -> str:  # given
    await asyncio.sleep(len(url) / 10)
    if "bad" in url:
        raise ConnectionError(url)
    return url.upper()


async def _guarded(url: str, probe: Probe) -> str:
    raise NotImplementedError("TODO")


async def fetch_bounded(urls: list[str], limit: int, probe: Probe) -> list[str]:
    raise NotImplementedError("TODO")


async def fetch_worker_pool(urls: list[str], limit: int, probe: Probe) -> list[str]:
    raise NotImplementedError("TODO")


async def timed(coro_fn, *args) -> tuple[list[str], float]:  # given
    loop = asyncio.get_running_loop()
    start = loop.time()
    out = await coro_fn(*args)
    return out, round(loop.time() - start, 3)


def main() -> None:
    urls = ["api/a", "api/b", "api/c", "api/d", "api/e", "api/f"]     # 0.5 s each
    for limit in (1, 2, 3, 6):
        p = Probe()
        res, secs = run_virtual(timed(fetch_bounded, urls, limit, p))
        print(f"limit={limit}: elapsed {secs} s, peak in flight {p.peak}")
    print("results:", res)
    mixed = ["x", "bad-host", "yyyy", "zz", "bad"]
    p = Probe()
    print("semaphore, errors:", run_virtual(fetch_bounded(mixed, 2, p)), "peak", p.peak)
    p = Probe()
    print("worker pool:      ", run_virtual(fetch_worker_pool(mixed, 2, p)), "peak", p.peak)
    print("empty input:", run_virtual(fetch_bounded([], 3, Probe())))


if __name__ == "__main__":
    main()
