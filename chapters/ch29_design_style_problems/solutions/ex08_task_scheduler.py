"""
Exercise 08 — Task Scheduler and Job Queue         [Tier: ★ Core]
Chapter 29 · Pattern: heap keyed by (time, priority, seq) · Target time: 35 min

Problem
-------
Part A — cooldown scheduling. Given task labels (e.g. "AAABBC") and a cooldown n, the
same label cannot run twice within n time units. Each time unit runs one task or idles.
Return the minimum number of time units, `least_interval(tasks, n)`.

Part B — a timer-driven job queue (the core of cron, Celery beat, `sched`):

    js = JobScheduler()
    job_id = js.schedule(name, run_at, priority=0, every=None)   # every = repeat period
    js.cancel(job_id)                -> bool
    js.run_until(t)                  -> list of (time, name) executed with time <= t,
                                        ordered by time, then priority (lower first),
                                        then submission order
    js.pending()                     -> number of live scheduled jobs

Examples
--------
>>> least_interval("AAABBC", 2)      # A B C A B _ A
7
>>> js = JobScheduler()
>>> _ = js.schedule("backup", 10); _ = js.schedule("email", 5)
>>> js.run_until(10)
[(5, 'email'), (10, 'backup')]

Constraints
-----------
- Part A: up to 10**4 tasks, 26 labels, 0 <= n <= 100.
- Part B: up to 10**5 jobs; cancellation must not be O(n).

Approach ladder
---------------
Part A
1. Simulation with a max-heap of remaining counts and a cooldown queue: O(T log 26).
2. Counting formula: let f = max count, k = number of labels with count f.
   answer = max(len(tasks), (f - 1) * (n + 1) + k). O(T). Why: the most frequent label
   forms f-1 full "frames" of length n+1 plus a final partial frame of k tasks; if there
   are enough other tasks to fill every gap, no idling is needed at all.
Part B
1. Sorted list, re-sorted after each insert: O(n log n) per schedule.
2. Heap of (run_at, priority, seq, id): O(log n) schedule and pop. Cancellation by
   *lazy deletion* — mark the id cancelled and skip it when it surfaces: O(1) cancel.
   Recurring jobs are re-pushed with run_at + every when they run.

Hints
-----
- The `seq` counter in the heap tuple makes ordering total and stable, and stops Python
  from ever comparing two payload objects.
- Keep `pending()` correct under lazy deletion by tracking a live set.

Follow-ups
----------
- Job dependencies (run B only after A): topological order (Kahn) feeding the heap.
- Workers and retries with exponential backoff: re-schedule failed jobs at now + 2**k.
- Persisting the queue so a crash does not lose jobs.
"""
from __future__ import annotations

import heapq
from collections import Counter, deque


def least_interval_sim(tasks: str, n: int) -> int:
    """Rung 1: simulate time with a max-heap and a cooldown queue."""
    heap = [-c for c in Counter(tasks).values()]
    heapq.heapify(heap)
    cooling: deque[tuple[int, int]] = deque()     # (time available again, -remaining)
    time = 0
    while heap or cooling:
        time += 1
        if heap:
            remaining = heapq.heappop(heap) + 1    # run one instance (counts are negative)
            if remaining:
                cooling.append((time + n, remaining))
        if cooling and cooling[0][0] == time:
            heapq.heappush(heap, cooling.popleft()[1])
    return time


def least_interval(tasks: str, n: int) -> int:
    """Rung 2: closed-form count."""
    if not tasks:
        return 0
    counts = Counter(tasks)
    f = max(counts.values())
    k = sum(1 for c in counts.values() if c == f)
    return max(len(tasks), (f - 1) * (n + 1) + k)


def schedule_order(tasks: str, n: int) -> str:
    """One optimal schedule as a string, '_' = idle (used for the demo)."""
    counts = Counter(tasks)
    ready_at = {t: 0 for t in counts}
    out = []
    time = 0
    while counts:
        ready = [t for t in counts if ready_at[t] <= time]
        if ready:
            # most remaining first; ties alphabetical for determinism
            t = min(ready, key=lambda x: (-counts[x], x))
            out.append(t)
            counts[t] -= 1
            if not counts[t]:
                del counts[t]
            ready_at[t] = time + n + 1
        else:
            out.append("_")
        time += 1
    return "".join(out)


class JobScheduler:
    def __init__(self) -> None:
        self.heap: list[tuple[float, int, int, int]] = []
        self.jobs: dict[int, tuple[str, float | None, int]] = {}   # id -> (name, every, prio)
        self.next_id = 0
        self.seq = 0
        self.now = 0.0

    def schedule(self, name: str, run_at: float, priority: int = 0,
                 every: float | None = None) -> int:
        if every is not None and every <= 0:
            raise ValueError("every must be positive")
        job_id = self.next_id
        self.next_id += 1
        self.jobs[job_id] = (name, every, priority)
        self._push(run_at, priority, job_id)
        return job_id

    def _push(self, run_at: float, priority: int, job_id: int) -> None:
        heapq.heappush(self.heap, (run_at, priority, self.seq, job_id))
        self.seq += 1

    def cancel(self, job_id: int) -> bool:
        return self.jobs.pop(job_id, None) is not None   # heap entry is skipped later

    def pending(self) -> int:
        return len(self.jobs)

    def run_until(self, t: float) -> list[tuple[float, str]]:
        ran = []
        while self.heap and self.heap[0][0] <= t:
            run_at, prio, _, job_id = heapq.heappop(self.heap)
            job = self.jobs.get(job_id)
            if job is None:                      # cancelled: lazy deletion
                continue
            name, every, _ = job
            self.now = run_at
            ran.append((run_at, name))
            if every is None:
                del self.jobs[job_id]
            else:
                self._push(run_at + every, prio, job_id)
        self.now = max(self.now, t)
        return ran


def main() -> None:
    cases = [("AAABBC", 2), ("AAABBB", 2), ("AAABBB", 0), ("ABCDEF", 2), ("AAAA", 3), ("", 5)]
    print(f"{'tasks':<8} {'n':>2}  sim  formula  schedule")
    for tasks, n in cases:
        print(f"{tasks!r:<8} {n:>2}  {least_interval_sim(tasks, n):>3}  {least_interval(tasks, n):>7}"
              f"  {schedule_order(tasks, n)}")

    js = JobScheduler()
    js.schedule("backup", 10)
    js.schedule("email", 5)
    js.schedule("report", 10, priority=-1)          # same time as backup, higher priority
    hb = js.schedule("heartbeat", 0, every=4)
    tmp = js.schedule("temp-cleanup", 7)
    print("cancel temp-cleanup:", js.cancel(tmp), " cancel again:", js.cancel(tmp))
    print("run_until(10):", js.run_until(10))
    js.cancel(hb)
    js.schedule("late", 11)
    print("after cancelling heartbeat, run_until(20):", js.run_until(20))
    print("pending:", js.pending())


if __name__ == "__main__":
    main()
