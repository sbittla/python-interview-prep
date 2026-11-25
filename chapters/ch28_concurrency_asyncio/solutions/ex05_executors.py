"""
Exercise 05 — Thread and Process Pools with concurrent.futures   [Tier: ◆ Extended]
Chapter 28 · Pattern: ThreadPoolExecutor / ProcessPoolExecutor, map vs as_completed · Target time: 25 min

Problem
-------
1. `count_primes(lo, hi)` counts primes in [lo, hi) (CPU-bound, top-level so it pickles).
2. `split_range(n, parts)` cuts [0, n) into `parts` contiguous half-open ranges whose sizes
   differ by at most 1 (empty ranges allowed when parts > n).
3. `parallel_count(n, parts, executor_cls, max_workers)` counts primes below n by sending each
   range to an executor with `executor.map` and summing. Must equal `count_primes(0, n)`.
4. `fetch_all(keys, fetch, max_workers)` runs `fetch(key)` in a ThreadPoolExecutor using
   `submit` + `as_completed`, and returns `{key: result or "error: <ExcType>"}` in **key order**
   (so the output does not depend on completion order).
5. `peak_threads(max_workers, rounds)` proves the pool really runs `max_workers` tasks at once:
   each task waits on a shared `threading.Barrier(max_workers)`, which only opens when that many
   tasks are inside it together. Return the peak number of tasks seen in flight.

Examples
--------
>>> split_range(10, 3)
[(0, 4), (4, 7), (7, 10)]
>>> parallel_count(100, 4, ThreadPoolExecutor, 2)
25
>>> fetch_all(["a", "bb"], len, 2)
{'a': 1, 'bb': 2}

Constraints
-----------
- n <= 10**6; parts >= 1. On Windows/macOS, process pools *spawn* a fresh interpreter: the
  worker function must be importable at module top level and the pool must be created under
  `if __name__ == "__main__":` (or from code it calls), or the children re-run the script.

Approach ladder
---------------
1. Brute force — `count_primes(0, n)` in one thread: O(n·√n) trial division, one core.
2. Improved   — ThreadPoolExecutor: same answer, but in the default build the GIL lets only one
   thread run Python bytecode at a time (→ §27.5), so CPU-bound work does not speed up.
   Threads *do* help I/O-bound work (`fetch_all`): blocking calls release the GIL.
3. Optimal    — ProcessPoolExecutor: one interpreter per core, true parallelism for CPU work;
   costs process start-up plus pickling arguments/results, so send few large chunks
   (`parts` ≈ a small multiple of cores) rather than one task per number.

Hints
-----
- `executor.map` yields results in *input* order; `as_completed` yields futures in completion
  order. Store by key to make completion order irrelevant.
- `future.result()` re-raises the worker's exception in the caller.
- `with Executor(...) as ex:` waits for all tasks (`shutdown(wait=True)`) on exit.

Follow-ups
----------
- `map(..., chunksize=k)` batches many tiny tasks for process pools.
- Exceptions inside `map` surface when you iterate to that item; the rest are lost unless you
  catch per item.
- Free-threaded 3.13t/3.14t builds let threads run CPU work in parallel (→ §27.6).
"""
from __future__ import annotations

import threading
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Any, Callable


def count_primes(lo: int, hi: int) -> int:
    count = 0
    for n in range(max(lo, 2), hi):
        if all(n % d for d in range(2, int(n ** 0.5) + 1)):
            count += 1
    return count


def split_range(n: int, parts: int) -> list[tuple[int, int]]:
    base, extra = divmod(n, parts)
    out, lo = [], 0
    for i in range(parts):
        hi = lo + base + (1 if i < extra else 0)
        out.append((lo, hi))
        lo = hi
    return out


def parallel_count(n: int, parts: int, executor_cls: type[Executor] = ProcessPoolExecutor,
                   max_workers: int = 4) -> int:
    ranges = split_range(n, parts)
    with executor_cls(max_workers=max_workers) as ex:
        los, his = zip(*ranges)
        return sum(ex.map(count_primes, los, his))      # results arrive in input order


def fetch_all(keys: list[str], fetch: Callable[[str], Any], max_workers: int) -> dict[str, Any]:
    results: dict[str, Any] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(fetch, k): k for k in keys}
        for fut in as_completed(futures):               # completion order: varies run to run
            key = futures[fut]
            try:
                results[key] = fut.result()
            except Exception as exc:
                results[key] = f"error: {type(exc).__name__}"
    return {k: results[k] for k in keys}                # report in key order


def peak_threads(max_workers: int, rounds: int) -> int:
    barrier = threading.Barrier(max_workers)
    lock = threading.Lock()
    state = {"now": 0, "peak": 0}

    def task() -> None:
        with lock:
            state["now"] += 1
            state["peak"] = max(state["peak"], state["now"])
        barrier.wait(timeout=10)                        # opens only with max_workers inside
        with lock:
            state["now"] -= 1

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        for fut in [ex.submit(task) for _ in range(max_workers * rounds)]:
            fut.result()
    return state["peak"]


def fake_fetch(key: str) -> int:  # given
    threading.Event().wait(0.01 * (len(key) % 3))       # stand-in for network latency
    if key.startswith("bad"):
        raise ConnectionError(key)
    return len(key)


def main() -> None:
    n = 60_000
    print("split_range(10, 3):", split_range(10, 3))
    print("split_range(2, 4):", split_range(2, 4))
    serial = count_primes(0, n)
    print(f"primes below {n}: serial = {serial}")
    print("process pool agrees:", parallel_count(n, 8, ProcessPoolExecutor, 4) == serial)
    print("thread pool agrees:", parallel_count(n, 8, ThreadPoolExecutor, 4) == serial)
    keys = ["alpha", "bad-host", "io", "kappa", "z"]
    print("fetch_all:", fetch_all(keys, fake_fetch, max_workers=3))
    print("peak tasks in flight with 4 workers:", peak_threads(4, rounds=3))


if __name__ == "__main__":          # required: spawned children import this file
    main()
