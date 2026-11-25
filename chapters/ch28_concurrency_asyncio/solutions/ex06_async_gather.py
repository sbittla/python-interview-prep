"""
Exercise 06 — Coroutines, Tasks, gather and as_completed      [Tier: ★ Core]
Chapter 28 · Pattern: overlap waits on one event loop · Target time: 20 min

Problem
-------
`fetch(name, delay)` is a coroutine that sleeps `delay` seconds (a fake network call) and
returns `f"{name}:{delay}"`; names starting with "bad" raise `ConnectionError(name)`.
Each function below receives `jobs`, a list of `(name, delay)` pairs, and returns
`(results, elapsed)` where elapsed is measured with `loop.time()`:

1. `run_sequential(jobs)` — await one call after another.
2. `run_gather(jobs)` — all at once with `asyncio.gather`; results in **input** order.
3. `run_as_completed(jobs)` — all at once; return the names in **completion** order.
4. `run_gather_safe(jobs)` — like gather, but a failing call yields `"error: <ExcType>"`
   in its slot instead of aborting the batch (`return_exceptions=True`).

The demo runs on a virtual clock (`vclock.run_virtual`), so sleeps cost no real time and
every elapsed value and completion order is the same on every run.

Examples
--------
>>> run_virtual(run_sequential([("a", 0.2), ("b", 0.1)]))
(['a:0.2', 'b:0.1'], 0.3)
>>> run_virtual(run_gather([("a", 0.2), ("b", 0.1)]))
(['a:0.2', 'b:0.1'], 0.2)
>>> run_virtual(run_as_completed([("a", 0.2), ("b", 0.1)]))
(['b', 'a'], 0.2)

Constraints
-----------
- Elapsed values are rounded to 3 decimals. Distinct delays (ties complete in an unspecified
  order, so ties are excluded from the as_completed contract).

Approach ladder
---------------
1. Brute force — sequential awaits: elapsed = sum of delays, O(Σd).
2. Improved   — `create_task` each call, then await each task: elapsed = max(d), but you must
   handle every task's exception yourself or get "Task exception was never retrieved".
3. Optimal    — `gather` (ordered results, first exception propagates) or `as_completed`
   (handle each result as soon as it lands). Elapsed = max(d) for n calls, O(n) tasks.

Hints
-----
- `fetch("a", 1)` without `await` only creates a coroutine object; nothing runs.
- `asyncio.as_completed` yields awaitables; `await` each one to get the next finished result.
- With plain gather the first exception propagates to the caller, but the other tasks keep
  running; TaskGroup (3.11+, ex07) cancels them instead.

Follow-ups
----------
- Need the first result only? `asyncio.wait(tasks, return_when=FIRST_COMPLETED)`, then cancel.
- Hundreds of calls: cap concurrency with a Semaphore (ex08).
"""
from __future__ import annotations

import asyncio

from vclock import run_virtual


async def fetch(name: str, delay: float) -> str:  # given
    await asyncio.sleep(delay)                   # yields to the loop; others run meanwhile
    if name.startswith("bad"):
        raise ConnectionError(name)
    return f"{name}:{delay}"


def _now() -> float:  # given
    return asyncio.get_running_loop().time()


async def run_sequential(jobs: list[tuple[str, float]]) -> tuple[list[str], float]:
    start = _now()
    results = [await fetch(name, d) for name, d in jobs]
    return results, round(_now() - start, 3)


async def run_gather(jobs: list[tuple[str, float]]) -> tuple[list[str], float]:
    start = _now()
    results = await asyncio.gather(*(fetch(name, d) for name, d in jobs))
    return list(results), round(_now() - start, 3)


async def run_as_completed(jobs: list[tuple[str, float]]) -> tuple[list[str], float]:
    async def tagged(name: str, d: float) -> str:
        await fetch(name, d)
        return name

    start = _now()
    order = [await fut for fut in asyncio.as_completed([tagged(n, d) for n, d in jobs])]
    return order, round(_now() - start, 3)


async def run_gather_safe(jobs: list[tuple[str, float]]) -> tuple[list[str], float]:
    start = _now()
    raw = await asyncio.gather(*(fetch(n, d) for n, d in jobs), return_exceptions=True)
    results = [f"error: {type(r).__name__}" if isinstance(r, Exception) else r for r in raw]
    return results, round(_now() - start, 3)


def main() -> None:
    jobs = [("users", 0.3), ("orders", 0.1), ("prices", 0.2)]
    print("sequential:  ", run_virtual(run_sequential(jobs)))
    print("gather:      ", run_virtual(run_gather(jobs)))
    print("as_completed:", run_virtual(run_as_completed(jobs)))
    bad = [("users", 0.3), ("bad-db", 0.1), ("prices", 0.2)]
    print("gather_safe: ", run_virtual(run_gather_safe(bad)))
    try:
        run_virtual(run_gather(bad))
    except ConnectionError as exc:
        print("plain gather raises:", type(exc).__name__, exc)
    print("empty batch: ", run_virtual(run_gather([])))
    coro = fetch("x", 1)
    print("call without await gives:", type(coro).__name__)
    coro.close()                                 # avoid "coroutine was never awaited"


if __name__ == "__main__":
    main()
