"""
Exercise 07 — Timeouts, Cancellation and Fail-Fast Task Groups   [Tier: ◆ Extended]
Chapter 28 · Pattern: wait_for / asyncio.timeout, CancelledError, structured concurrency · Target time: 30 min

Problem
-------
1. `with_timeout(delay, limit)` — run `asyncio.sleep(delay)` then return "done", but give up
   after `limit` seconds and return "timeout". Use `asyncio.wait_for` (works on 3.10).
   `with_timeout_311(delay, limit)` does the same with `async with asyncio.timeout(limit)`
   (3.11+ only).
2. `cancel_with_cleanup(cancel_after)` — start a worker that logs "start", sleeps 10 s, and
   logs "cleanup" in a `finally`; cancel it after `cancel_after` seconds. Return the worker's
   log plus "cancelled" if awaiting it raised `CancelledError`.
3. `fail_fast(specs, log)` — run the given `job(name, delay, fails, log)` for every spec
   concurrently and return the results in input order. As soon as one job fails, cancel the
   others, wait for them to finish cancelling, and re-raise that job's exception. Jobs append
   "<name> finished" / "<name> cancelled" to `log`. Implement it portably (3.10) with
   `asyncio.wait(..., return_when=FIRST_EXCEPTION)`. `fail_fast_taskgroup(specs, log)` does
   the same with `asyncio.TaskGroup` (3.11+), which raises an `ExceptionGroup` instead.
4. `gather_no_cancel(specs, log)` — plain `gather` for contrast: the exception propagates but
   the siblings keep running. Log "caller saw: <msg>", then let the loop run on to t = 1 s.

All demos run on the virtual clock (`vclock.run_virtual`), so timings are exact.

Examples
--------
>>> run_virtual(with_timeout(0.5, 1.0)), run_virtual(with_timeout(5, 1.0))
('done', 'timeout')
>>> run_virtual(cancel_with_cleanup(0.1))
['start', 'cleanup', 'cancelled']
>>> log = []; run_virtual(fail_fast([("a", 0.1, False), ("b", 0.2, False)], log)), log
(['a', 'b'], ['a finished', 'b finished'])

Constraints
-----------
- Never swallow `CancelledError`: clean up in `finally` and let it propagate.

Approach ladder
---------------
1. Brute force — poll `loop.time()` between steps and stop "voluntarily": misses waits that
   never return and spreads timeout logic everywhere.
2. Improved   — `wait_for(aw, limit)`: cancels the inner awaitable and raises `TimeoutError`
   (an alias of `asyncio.TimeoutError` since 3.11; on 3.10 catch `asyncio.TimeoutError`).
   For a group of tasks, plain gather leaks siblings on failure.
3. Optimal    — scoped deadlines (`asyncio.timeout`, 3.11+) and structured concurrency
   (`TaskGroup`, 3.11+): no task outlives its block; on 3.10 emulate with
   `asyncio.wait(FIRST_EXCEPTION)` + cancel the pending set. O(n) tasks, one wake-up per event.

Hints
-----
- `task.cancel()` only *requests* cancellation: `CancelledError` is raised inside the task at
  its next `await`; await the task afterwards to let the cleanup run.
- `except Exception` does not catch `CancelledError` (it derives from `BaseException` since 3.8).
- After `asyncio.wait`, call `.result()` (or `.exception()`) on done tasks to retrieve errors.

Follow-ups
----------
- `asyncio.shield(aw)` protects an inner operation from an outer cancel (it keeps running).
- A per-attempt timeout plus retries with backoff: ex11.
- Why might a timeout fire late? The loop only checks it when the blocking code yields (ex09).
"""
from __future__ import annotations

import asyncio
import sys

from vclock import run_virtual


async def with_timeout(delay: float, limit: float) -> str:
    try:
        await asyncio.wait_for(asyncio.sleep(delay), timeout=limit)
        return "done"
    except asyncio.TimeoutError:          # same class as builtin TimeoutError on 3.11+
        return "timeout"


async def with_timeout_311(delay: float, limit: float) -> str:   # Python 3.11+
    try:
        async with asyncio.timeout(limit):
            await asyncio.sleep(delay)
        return "done"
    except TimeoutError:
        return "timeout"


async def cancel_with_cleanup(cancel_after: float) -> list[str]:
    log: list[str] = []

    async def worker() -> None:
        log.append("start")
        try:
            await asyncio.sleep(10)
        finally:
            log.append("cleanup")        # runs on cancel; CancelledError then propagates

    task = asyncio.create_task(worker())
    await asyncio.sleep(cancel_after)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        log.append("cancelled")
    return log


async def job(name: str, delay: float, fails: bool, log: list[str]) -> str:  # given
    try:
        await asyncio.sleep(delay)
    except asyncio.CancelledError:
        log.append(f"{name} cancelled")
        raise
    if fails:
        raise ValueError(f"{name} failed")
    log.append(f"{name} finished")
    return name


async def fail_fast(specs: list[tuple[str, float, bool]], log: list[str]) -> list[str]:
    tasks = [asyncio.create_task(job(n, d, f, log)) for n, d, f in specs]
    if not tasks:
        return []
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
    for t in pending:
        t.cancel()
    await asyncio.gather(*pending, return_exceptions=True)   # let cancellations finish
    for t in tasks:                                          # first failure in input order
        if t in done and t.exception() is not None:
            raise t.exception()
    return [t.result() for t in tasks]


async def fail_fast_taskgroup(specs: list[tuple[str, float, bool]],
                              log: list[str]) -> list[str]:  # Python 3.11+
    async with asyncio.TaskGroup() as tg:                    # one failure cancels the rest
        tasks = [tg.create_task(job(n, d, f, log)) for n, d, f in specs]
    return [t.result() for t in tasks]


async def gather_no_cancel(specs: list[tuple[str, float, bool]], log: list[str]) -> None:
    try:
        await asyncio.gather(*(job(n, d, f, log) for n, d, f in specs))
    except ValueError as exc:
        log.append(f"caller saw: {exc}")
    await asyncio.sleep(1 - asyncio.get_running_loop().time())  # run on to t = 1 s


def main() -> None:
    print("wait_for:", run_virtual(with_timeout(0.5, 1.0)), run_virtual(with_timeout(5, 1.0)))
    if sys.version_info >= (3, 11):
        print("asyncio.timeout (3.11+):",
              run_virtual(with_timeout_311(0.5, 1.0)), run_virtual(with_timeout_311(5, 1.0)))
    print("cancel with cleanup:", run_virtual(cancel_with_cleanup(0.1)))
    log: list[str] = []
    print("fail_fast all ok:", run_virtual(fail_fast([("a", 0.1, False), ("b", 0.2, False)], log)),
          log)
    specs = [("slow", 0.5, False), ("broken", 0.1, True), ("quick", 0.05, False)]
    log = []
    try:
        run_virtual(fail_fast(specs, log))
    except ValueError as exc:
        print("fail_fast raised:", exc, "| log:", log)
    if sys.version_info >= (3, 11):
        log = []
        try:
            run_virtual(fail_fast_taskgroup(specs, log))
        except Exception as eg:                  # ExceptionGroup; `except*` would not parse on 3.10
            print(f"TaskGroup raised {type(eg).__name__}:",
                  [str(e) for e in eg.exceptions], "| log:", log)
    log = []
    run_virtual(gather_no_cancel(specs, log))
    print("plain gather log:", log)


if __name__ == "__main__":
    main()
