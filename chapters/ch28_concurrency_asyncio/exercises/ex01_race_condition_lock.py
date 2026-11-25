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
    raise NotImplementedError("TODO")


class LockedCounter:
    def __init__(self, pause: Callable[[], None] = lambda: None) -> None:
        raise NotImplementedError("TODO")

    def increment(self) -> None:
        raise NotImplementedError("TODO")

    @property
    def value(self) -> int:
        raise NotImplementedError("TODO")


def run_counter(counter: LockedCounter, n_threads: int, per_thread: int) -> int:
    raise NotImplementedError("TODO")


def run_sharded(n_threads: int, per_thread: int) -> int:
    raise NotImplementedError("TODO")


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
        raise NotImplementedError("TODO")

    def withdraw(self, amount: int) -> bool:
        raise NotImplementedError("TODO")


def concurrent_withdrawals(account: UnsafeAccount, n_threads: int, amount: int) -> tuple[int, int]:
    raise NotImplementedError("TODO")


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
