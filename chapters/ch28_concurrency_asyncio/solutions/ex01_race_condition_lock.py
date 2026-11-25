"""
Exercise 01 — Lost Updates and the Lock That Fixes Them      [Tier: ★ Core]
Chapter 28 · Pattern: threading.Lock, read-modify-write and check-then-act races · Target time: 20 min

Problem
-------
`count += 1` is three steps: read, add, write. If two threads both read before either writes,
one update is lost. `if balance >= x: balance -= x` (check-then-act) has the same flaw.

1. `lost_update_demo(n_threads)` — make the bad interleaving happen on purpose: each thread
   reads the shared value, waits at a `threading.Barrier(n_threads)` (so every read happens
   before any write), then writes value + 1. Return the final value.
2. `LockedCounter(pause)` — `increment()` and `value`; increments never get lost. `increment`
   reads the value, calls `pause()` (a test hook that widens the race window), then writes.
3. `run_counter(counter, n_threads, per_thread)` — each thread calls `counter.increment()`
   `per_thread` times; join all threads and return `counter.value`.
4. `run_sharded(n_threads, per_thread)` — same total with no shared lock: each thread counts
   into its own slot of a list; sum after `join`.
5. `Account(balance, pause)` — subclass of the given `UnsafeAccount` whose `withdraw` is atomic.
   `concurrent_withdrawals(account, n_threads, amount)` starts one thread per withdrawal and
   returns `(successes, final_balance)`.

Examples
--------
>>> lost_update_demo(4)
1
>>> run_counter(LockedCounter(), 4, 1000)
4000
>>> concurrent_withdrawals(Account(100), 10, 30)
(3, 10)

Constraints
-----------
- Standard library only; every thread is joined before returning.
- Output must be identical on every run, so never print a count produced by an unforced race.

Approach ladder
---------------
1. Brute force — no lock. Wrong: lost updates are possible. In the default (GIL) build the
   interpreter switches threads only at some bytecode boundaries, so an unlocked counter often
   *looks* right; that proves nothing, and on the free-threaded build (→ §27.6) it fails fast.
2. Improved   — one `Lock` around each read-modify-write: correct; O(1) per increment, but all
   n·k increments serialise on one lock (contention).
3. Optimal    — shard: each thread updates private state and the results are combined once
   after `join()` (O(n·k) work, O(n) memory, one synchronisation point per thread). Move up
   when the shared update is hot; keep the lock when threads must see each other's updates.

Hints
-----
- `with self._lock:` releases the lock even if the body raises.
- The lock must cover the *check and the act* together, not each separately.
- `Thread.join()` is what makes the workers' writes visible to the summing thread.

Follow-ups
----------
- Why is `threading.Lock` not reentrant, and when do you need `RLock`?
- Two locks taken in opposite orders by two threads: deadlock. Fix: one global lock order.
- Is `list.append` thread-safe? In CPython a single append is atomic, but "append if absent"
  is check-then-act and still needs a lock.
"""
from __future__ import annotations

import threading
from typing import Callable


def lost_update_demo(n_threads: int) -> int:
    state = {"count": 0}
    barrier = threading.Barrier(n_threads)

    def worker() -> None:
        seen = state["count"]          # read
        barrier.wait()                 # every thread has read 0 before anyone writes
        state["count"] = seen + 1      # write: overwrites the others' updates

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return state["count"]


class LockedCounter:
    def __init__(self, pause: Callable[[], None] = lambda: None) -> None:
        self._value = 0
        self._lock = threading.Lock()
        self._pause = pause

    def increment(self) -> None:
        with self._lock:               # read-modify-write is now indivisible
            seen = self._value
            self._pause()              # without the lock, another thread could write here
            self._value = seen + 1

    @property
    def value(self) -> int:
        with self._lock:
            return self._value


def run_counter(counter: LockedCounter, n_threads: int, per_thread: int) -> int:
    def worker() -> None:
        for _ in range(per_thread):
            counter.increment()

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return counter.value


def run_sharded(n_threads: int, per_thread: int) -> int:
    slots = [0] * n_threads            # one private slot per thread: nothing shared to race on

    def worker(i: int) -> None:
        local = 0
        for _ in range(per_thread):
            local += 1
        slots[i] = local

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return sum(slots)


class UnsafeAccount:  # given
    def __init__(self, balance: int, pause: Callable[[], None] = lambda: None) -> None:
        self.balance = balance
        self._pause = pause            # hook to widen the race window in demos and tests

    def withdraw(self, amount: int) -> bool:
        if self.balance >= amount:     # check
            self._pause()
            self.balance -= amount     # act
            return True
        return False


class Account(UnsafeAccount):
    def __init__(self, balance: int, pause: Callable[[], None] = lambda: None) -> None:
        super().__init__(balance, pause)
        self._lock = threading.Lock()

    def withdraw(self, amount: int) -> bool:
        with self._lock:               # check and act under one lock
            return super().withdraw(amount)


def concurrent_withdrawals(account: UnsafeAccount, n_threads: int, amount: int) -> tuple[int, int]:
    results = [False] * n_threads

    def worker(i: int) -> None:
        results[i] = account.withdraw(amount)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return sum(results), account.balance


def main() -> None:
    print("forced lost update, 4 threads -> final count:", lost_update_demo(4))
    print("locked counter 8 x 20000:", run_counter(LockedCounter(), 8, 20_000))
    print("sharded counter 8 x 20000:", run_sharded(8, 20_000))
    barrier = threading.Barrier(2)
    unsafe = UnsafeAccount(50, pause=barrier.wait)   # both threads pass the check first
    print("unsafe: 2 x withdraw(50) from 50 ->", concurrent_withdrawals(unsafe, 2, 50))
    print("locked: 10 x withdraw(30) from 100 ->", concurrent_withdrawals(Account(100), 10, 30))
    print("locked never overdraws:",
          all(concurrent_withdrawals(Account(100), 10, 30) == (3, 10) for _ in range(20)))


if __name__ == "__main__":
    main()
