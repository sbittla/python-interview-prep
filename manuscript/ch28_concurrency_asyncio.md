# Chapter 28. Concurrency and asyncio

◆ Extended · Tracks S L (M optional) · Study time ≈ 6 h · Prerequisites: §27.5–§27.7, Chapter 26

**Learning objectives**

- Choose threads, processes or asyncio for a workload, and say why in one sentence.
- Find read-modify-write and check-then-act races, and fix them with the smallest lock.
- Build bounded producer–consumer pipelines with `queue.Queue`, `Condition` and `asyncio.Queue`.
- Fan out async work with `gather`, `TaskGroup` and `Semaphore`, under timeouts and clean
  cancellation.

> **Recognise it**
>
> | You hear / see | Reach for |
> |---|---|
> | "many slow network calls", "fan out" | asyncio `gather`, or `ThreadPoolExecutor` for blocking libraries |
> | "CPU-heavy", "use all cores" | `ProcessPoolExecutor` |
> | "shared counter", "balance", "two threads update" | `Lock` around the whole read-modify-write |
> | "producer/consumer", "bounded buffer", "at most k at a time" | bounded queue, `Semaphore(k)` |
> | "deadline"; "print in order" | `wait_for`; `Event` hand-offs |

## 28.1 Concurrency vs parallelism

**Concurrency** means tasks are in progress at the same time, taking turns. **Parallelism**
means they run at the same instant on different cores. In the default CPython build the GIL
lets only one thread run Python bytecode at a time (→ §27.5). Threads therefore give you
concurrency, and parallelism only while they wait on I/O or run C code that releases the GIL.
The free-threaded build is opt-in (→ §27.6); choosing a model is §27.7.

| Model | Switches when | Best for | Cost |
|---|---|---|---|
| `threading` | the OS preempts it; the GIL hands off | blocking I/O libraries | memory per thread; races |
| `multiprocessing` | the OS schedules it | CPU-bound Python | start-up, pickling, no shared memory |
| `asyncio` | only at `await` | thousands of sockets | one blocking call stalls all tasks |

## 28.2 `threading`: threads, locks, race conditions

`count += 1` is three steps: read, add, write. If two threads both read before either one
writes, an update is lost. A demo that prints a count produced by luck proves nothing, so this
one forces the bad interleaving with a barrier:

```python
import threading

state = {"count": 0}
barrier = threading.Barrier(4)
lock = threading.Lock()


def unsafe() -> None:
    seen = state["count"]        # read
    barrier.wait()               # force: all 4 reads happen before any write
    state["count"] = seen + 1    # write: clobbers the other three


def safe() -> None:
    for _ in range(10_000):
        with lock:               # read-modify-write is now indivisible
            state["count"] += 1


for target in (unsafe, safe):
    state["count"] = 0
    threads = [threading.Thread(target=target) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"{target.__name__}: {state['count']}")
```

```text
unsafe: 1
safe: 40000
```

An unlocked counter often *looks* correct on the default build. That proves nothing.
**Check-then-act** (`if balance >= x: balance -= x`) has the same flaw:
one lock must cover both the check and the act. Ex01 forces an overdraft to −50. Its top rung
is sharding: each thread counts privately and the totals are summed after `join()`, so the
threads never contend.

Pitfalls: two locks taken in opposite orders deadlock (use one global order); `Lock` is not
reentrant (use `RLock`).

## 28.3 Thread-safe queues and producer–consumer

`queue.Queue(maxsize)` does its own locking. `put` blocks while the queue is full; `get` blocks
while it is empty. With k worker threads, this gives **backpressure**: a fast producer stalls
instead of filling memory. Stop the workers with one sentinel each. `q.join()` waits for every
`task_done()`, but it does not stop the threads.

Ex02's ladder: sequential, O(n·t) → one thread per item (unbounded threads) → k workers and
a bounded queue, ≈ n·t/k for I/O in O(k + maxsize) memory.

Write results to `results[index]`. Catch exceptions inside the worker loop: one that escapes
kills the thread silently.

## 28.4 `multiprocessing` and `concurrent.futures` (`ThreadPoolExecutor`, `ProcessPoolExecutor`)

Thread and process pools share one interface. `submit` returns a `Future`, and
`future.result()` re-raises the worker's exception. `map` yields results in **input** order.
`as_completed` yields futures in **completion** order, so store each result by key before you
print it.

```python
from concurrent.futures import ProcessPoolExecutor


def count_primes(lo: int, hi: int) -> int:          # top level: picklable by name
    return sum(all(n % d for d in range(2, int(n ** 0.5) + 1)) for n in range(max(lo, 2), hi))


if __name__ == "__main__":                           # spawned children re-import this file
    los, his = [0, 25_000, 50_000], [25_000, 50_000, 75_000]
    with ProcessPoolExecutor(max_workers=3) as pool:
        print("map (input order):", list(pool.map(count_primes, los, his)))
```

```text
map (input order): [2762, 2371, 2260]
```

Windows and macOS start workers with **spawn**. Linux used fork before 3.14 and uses
forkserver from 3.14. Under spawn, every child imports your module. The worker function must
therefore live at top level so it can be pickled by name, and the pool must be created under
the `__main__` guard. A `ThreadPoolExecutor` returns the same answer but no speed-up, because
of the GIL. Ex05 proves a pool is k-wide with a `Barrier(k)`, not
with timings.

## 28.5 asyncio fundamentals: event loop, coroutines, `await`

Calling an `async def` function returns a **coroutine object**. It does nothing until it is
awaited or wrapped in a Task. The **event loop** runs one task until it awaits something that
is not ready (a timer, a socket, a lock), then switches to another ready task. Switches happen
only at `await`, so code between two awaits is never interleaved, and a single-threaded
asyncio counter needs no lock. A blocking call freezes every task (§28.9).

`asyncio.run(main())` creates a **new** loop and runs `main` to completion. It then cancels
the leftover tasks, finalises async generators, shuts down the default executor (3.9+) and
closes the loop. It raises `RuntimeError` inside an already-running loop, so in Jupyter write
`await main()` instead. Wrong-but-tempting: `fetch()` without `await` only builds a
coroutine object.

## 28.6 Tasks, `gather`, `TaskGroup`, `as_completed`

```python
import asyncio


async def fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)                 # suspends; the loop runs other tasks
    if name == "bad":
        raise ConnectionError(name)
    return name


async def main() -> None:
    jobs = [("users", 0.03), ("orders", 0.01), ("prices", 0.02)]
    print("gather:", await asyncio.gather(*(fetch(n, d) for n, d in jobs)))
    print("as_completed:", [await c for c in asyncio.as_completed(
        [fetch(n, d) for n, d in jobs])])
    print("return_exceptions:", await asyncio.gather(
        fetch("users", 0.01), fetch("bad", 0.01), return_exceptions=True))


asyncio.run(main())
```

```text
gather: ['users', 'orders', 'prices']
as_completed: ['orders', 'prices', 'users']
return_exceptions: ['users', ConnectionError('bad')]
```

The `as_completed` order is fixed. The loop pops expired timers from a heap in deadline order,
so the order holds even when the loop runs late. Sequential awaits cost the *sum* of the
delays; `gather` costs the *max*. On ex06's virtual clock that is 0.6 s against 0.3 s.

| Tool | Result order | When one task fails |
|---|---|---|
| `gather(*aws)` | input | the exception propagates; the **siblings keep running** |
| `gather(..., return_exceptions=True)` | input | the exception becomes a value in its slot |
| `as_completed(aws)` | completion | it surfaces when you await that task |
| `asyncio.TaskGroup()` (**3.11+**) | read `task.result()` | **siblings are cancelled**, then an `ExceptionGroup` is raised |

On 3.10, emulate TaskGroup's fail-fast behaviour:

1. Create the tasks.
2. Call `asyncio.wait(tasks, return_when=FIRST_EXCEPTION)`.
3. Cancel the pending tasks and await them.
4. Re-raise the first exception.

Ex07 checks this against TaskGroup. `except*` is a SyntaxError on 3.10. Keep
a reference to every task: the loop holds only weak references.

## 28.7 Timeouts and cancellation

`asyncio.wait_for(aw, s)` cancels `aw` when time runs out. On 3.11+, `async with
asyncio.timeout(s)` puts one deadline over a whole block; on 3.10 use `wait_for`. Before 3.11,
`asyncio.TimeoutError` was not the builtin `TimeoutError`, so portable code catches
`asyncio.TimeoutError`.

`task.cancel()` only *requests* cancellation: `CancelledError` is raised at the task's next
`await`. It is a `BaseException` (since 3.8), so `except Exception` does not catch it. Clean up
in `finally` and **re-raise**; swallowing it breaks TaskGroup, timeouts and shutdown.
`asyncio.shield(aw)` keeps an inner operation running when the outer task is cancelled. Ex07's
output (excerpt):

```text
TaskGroup raised ExceptionGroup: ['broken failed'] | log: ['quick finished', 'slow cancelled']
plain gather log: ['quick finished', 'caller saw: broken failed', 'slow finished']
```

Ex11 adds retries. Each attempt gets its own `wait_for`, and the waits between attempts use
capped exponential backoff with full jitter, `uniform(0, min(cap, base·2^(k−1)))`, drawn from
an injected `random.Random`. Only `ConnectionError` and timeouts are retried.

## 28.8 Limiting concurrency with `asyncio.Semaphore`

**Worked problem (ex08): fetch n URLs, at most k in flight, results in input order.**

- *Rung 1, sequential:* O(Σd) wall time.
- *Rung 2, `gather` all n:* max(d) wall time, but n requests at once. The server throttles you,
  and sockets and memory grow with n.
- *Rung 3, a semaphore inside each task:* at most k in flight. For equal durations d the wall
  time is ⌈n/k⌉·d, using O(n) task objects. A variant with k workers pulling from a queue keeps
  only O(k) tasks alive, which matters for huge n.

```python
import asyncio


async def fake_fetch(url: str) -> str:
    await asyncio.sleep(0.01)
    if "bad" in url:
        raise ConnectionError(url)
    return url.upper()


async def fetch_bounded(urls: list[str], limit: int) -> tuple[list[str], int]:
    sem = asyncio.Semaphore(limit)             # create inside the running loop
    in_flight = peak = 0

    async def one(url: str) -> str:
        nonlocal in_flight, peak
        async with sem:                        # at most `limit` coroutines past here
            in_flight += 1
            peak = max(peak, in_flight)
            try:
                return await fake_fetch(url)
            except ConnectionError as exc:
                return f"error: {type(exc).__name__}"
            finally:
                in_flight -= 1

    results = await asyncio.gather(*(one(u) for u in urls))   # input order
    return list(results), peak


urls = ["a", "bad-host", "c", "d", "e"]
for limit in (1, 2, 10):
    print(limit, asyncio.run(fetch_bounded(urls, limit)))
```

```text
1 (['A', 'error: ConnectionError', 'C', 'D', 'E'], 1)
2 (['A', 'error: ConnectionError', 'C', 'D', 'E'], 2)
10 (['A', 'error: ConnectionError', 'C', 'D', 'E'], 5)
```

→ repo: `chapters/ch28_concurrency_asyncio/solutions/ex08_semaphore_limit.py`. On the virtual
clock, six 0.5 s requests take 3.0, 1.5, 1.0 and 0.5 s at k = 1, 2, 3 and 6.

**Edge cases:** n = 0; k ≥ n (peak n); failures release their slot; input order.
**Wrong-but-tempting:** one `async with sem` around the whole `gather` limits nothing; a
module-level semaphore shared across `asyncio.run` calls binds to the first loop it waits on.
**Follow-ups:** Requests per second calls for a token bucket (→ §29.5). Per-host limits need a
dict of semaphores. LLM fan-out uses the same pattern (→ §42.2).

## 28.9 Blocking calls in async code and `to_thread`

A synchronous call inside `async def` freezes the loop: every task and timeout waits. Ex09
proves it without timing. A heartbeat task ticks three times, then sets the `threading.Event`
that blocking `legacy_read` waits on. Called directly, the read never sees it (the heartbeat
cannot run); via `to_thread` it does:

```text
direct blocking call (saw event, ticks during): (False, 0)
asyncio.to_thread                              : (True, 3)
loop.run_in_executor(None, ...)                : (True, 3)
CPU work in a process pool: True
```

→ repo: `chapters/ch28_concurrency_asyncio/solutions/ex09_blocking_to_thread.py`.
`asyncio.to_thread` (3.9+) runs the call in the default thread pool, which holds
`min(32, os.cpu_count() + 4)` threads. Before 3.9, use `loop.run_in_executor(None, f, *args)`.
CPU-bound Python still contends for the GIL, so pass a `ProcessPoolExecutor` to
`run_in_executor` instead (ex09). Better still, use an async-native library. In code review,
`time.sleep` inside a coroutine is a red flag.

## 28.10 Async producer–consumer with `asyncio.Queue`

**Worked problem (ex10): a stream of jobs, k async workers, bounded memory.**

- *Rung 1, one loop:* n·(arrival + work).
- *Rung 2, one task per job:* fast, but with an endless stream the pending tasks grow without
  limit.
- *Rung 3, `asyncio.Queue(maxsize)` and k workers:* elapsed ≈ max(n·arrival, n·work/k) plus a
  tail, in O(maxsize + k) memory. `await q.put` blocks while the queue is full.

```python
import asyncio


async def pipeline(n_items: int, n_workers: int, maxsize: int) -> tuple[list, int]:
    q: asyncio.Queue[int] = asyncio.Queue(maxsize=maxsize)
    results: list = []
    peak = 0

    async def worker() -> None:
        while True:
            i = await q.get()
            try:
                await asyncio.sleep(0.01)          # the slow stage
                results.append((i, i * i))
            finally:
                q.task_done()                      # always, or q.join() hangs

    workers = [asyncio.create_task(worker()) for _ in range(n_workers)]
    for i in range(n_items):
        await q.put(i)                             # waits while full: backpressure
        peak = max(peak, q.qsize())
    await q.join()                                 # all jobs done...
    for w in workers:
        w.cancel()                                 # ...so stop the idle workers
    await asyncio.gather(*workers, return_exceptions=True)
    return sorted(results), peak


print(asyncio.run(pipeline(6, n_workers=2, maxsize=2)))
print(asyncio.run(pipeline(0, n_workers=2, maxsize=2)))
```

```text
([(0, 0), (1, 1), (2, 4), (3, 9), (4, 16), (5, 25)], 2)
([], 0)
```

→ repo: `chapters/ch28_concurrency_asyncio/solutions/ex10_async_queue_pipeline.py` (adds
arrivals and poison jobs). Eight jobs arriving every 0.1 s with 0.4 s of work take 3.3, 1.8
and 1.2 virtual seconds with 1, 2 and 4 workers; at four, arrivals are the limit.

**Edge cases:** zero jobs; a job that raises (record it, keep the worker alive);
`maxsize=0` means *unbounded*; sort, since completion order varies.
**Wrong-but-tempting:** awaiting workers with no stop signal, or skipping `task_done()`, hangs.
**Follow-ups:** multi-stage pipelines; re-sequencing with a min-heap.

## 28.11 Common concurrency interview problems (print in order, bounded buffer)

**Print in order (ex03).** Three threads start in any order but must print first, second,
third. Use one `Event` per hand-off: `second` waits on `done_first`, then sets `done_second`.
Repeated turns (ping-pong, zero-even-odd) use one `Semaphore(0)` per thread; whoever moves
first starts at 1. Each step is O(1). Sleeping only makes the race rarer.

**Worked problem (ex04): a bounded blocking buffer without `queue.Queue`.**

- *Rung 1, lock plus polling sleep:* burns CPU and adds up to one sleep of latency per item.
- *Rung 2, one `Condition` with `notify_all`:* correct, but a put also wakes the waiting
  producers (a thundering herd).
- *Rung 3, two conditions sharing one lock:* `put` notifies only `not_empty`, `get` only
  `not_full`. Each operation is O(1) and wakes exactly one thread.

```python
import threading
from collections import deque


class BoundedBuffer:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._items: deque = deque()
        lock = threading.Lock()
        self._not_full = threading.Condition(lock)     # two conditions, one lock
        self._not_empty = threading.Condition(lock)
        self.max_seen = 0

    def put(self, item, timeout: float | None = None) -> None:
        with self._not_full:
            if not self._not_full.wait_for(lambda: len(self._items) < self.capacity, timeout):
                raise TimeoutError("buffer full")
            self._items.append(item)
            self.max_seen = max(self.max_seen, len(self._items))
            self._not_empty.notify()                    # wake one consumer

    def get(self, timeout: float | None = None):
        with self._not_empty:
            if not self._not_empty.wait_for(lambda: len(self._items) > 0, timeout):
                raise TimeoutError("buffer empty")
            item = self._items.popleft()
            self._not_full.notify()                     # wake one producer
            return item
```

The repo driver feeds 3 producers × 200 items into 2 consumers at capacity 4, and prints
booleans rather than racy counts (excerpt):

```text
all 600 items consumed exactly once: True
size never above capacity 4: True
```

→ repo: `chapters/ch28_concurrency_asyncio/solutions/ex04_bounded_buffer.py`

**Edge cases:** capacity 1; more consumers than items; timeouts when full or empty; one
`None` per consumer after the producers join; FIFO order.
**Wrong-but-tempting:** `if` instead of `while` around `wait()` (the slot may be taken, and
spurious wake-ups happen; `wait_for` loops for you); `notify` without the lock raises
`RuntimeError`. **Follow-ups:** `close()`; `queue.Queue` is this design.

## Interviewer's view

- **Rewarded:** naming the workload (I/O or CPU) first; bounded queues and semaphores;
  timeouts; clean shutdown; tests that force interleavings.
- **Penalised:** "threads make Python faster"; `time.sleep` for ordering or in a coroutine;
  unbounded `gather`; swallowing `CancelledError`; unflagged 3.11+ APIs.

## Exercises

| # | Title | Tier | Pattern |
|---|---|---|---|
| 01 | Lost updates and the lock that fixes them | ★ | `Lock`, check-then-act |
| 02 | Producer–consumer worker pool | ★ | `queue.Queue`, sentinels |
| 03 | Print in order, ping-pong, zero-even-odd | ★ | `Event`/`Semaphore` hand-off |
| 04 | Bounded blocking buffer | ★ | two `Condition`s |
| 05 | Thread and process pools | ◆ | `map`, `as_completed`, spawn |
| 06 | Coroutines, gather and as_completed | ★ | overlapping waits |
| 07 | Timeouts, cancellation, fail-fast groups | ◆ | `wait_for`, `TaskGroup` |
| 08 | Bounded concurrency | ★ | `Semaphore`, k workers |
| 09 | A blocking call freezes the loop | ◆ | `to_thread` |
| 10 | Async producer–consumer pipeline | ★ | `asyncio.Queue` |
| 11 | Retry with timeout and backoff | ◆ | full jitter |

Index: `chapters/ch28_concurrency_asyncio/README.md`. The async exercises use a
virtual-clock loop.

## Checkpoint quiz

1. Eight threads each run a pure-Python prime count on the default build. What speed-up do you
   get, and what should you use instead?
2. One task in a `gather` raises. What happens to the others, and what does `TaskGroup` do
   differently?
3. A coroutine calls `requests.get(url)`. What breaks, and how do you fix it?
4. Why must `Condition.wait()` sit inside a `while` loop?
5. A shutdown that awaits `q.join()` and then the workers hangs. Name two causes.

<details><summary>Answers</summary>

1. About none, because of the GIL. Use a `ProcessPoolExecutor`.
2. The others keep running. `TaskGroup` (3.11+) cancels them, waits for them, then raises an
   `ExceptionGroup`.
3. The whole loop freezes. Fix it with `await asyncio.to_thread(requests.get, url)` or an async
   HTTP client.
4. The slot may be taken before you wake, and spurious wake-ups happen.
5. A path that skips `task_done()`, or workers parked in `get()` that were never cancelled or
   sent a sentinel.
</details>

## Summary card

- I/O with blocking libraries → threads; many sockets → asyncio; CPU-bound → processes
  (GIL, → §27.5).
- Lock the whole invariant, take locks in one global order, and shard hot counters.
- Use bounded queues for backpressure. Stop workers with a sentinel each, or `join()` then
  cancel. Put `task_done()` in `finally`.
- `map` gives input order and `as_completed` gives completion order, so re-key the results.
  Under spawn, use top-level functions and a `__main__` guard.
- Tasks switch only at `await`; `asyncio.run` makes and closes a fresh loop.
- `TaskGroup` and `asyncio.timeout` are 3.11+. On 3.10, use `wait_for` and
  `wait(FIRST_EXCEPTION)` plus cancel.
- Re-raise `CancelledError`. Cap fan-out with `Semaphore(k)`. Move blocking calls to
  `to_thread`.
- Tests: force interleavings (`Barrier`, `Event`) and use a virtual clock.
