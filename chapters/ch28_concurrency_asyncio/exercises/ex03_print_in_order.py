"""
Exercise 03 — Print in Order, Ping-Pong, Zero-Even-Odd         [Tier: ★ Core]
Chapter 28 · Pattern: Event / Semaphore hand-off between threads · Target time: 25 min

Problem
-------
Threads start in an arbitrary order; force the order in which they act.

1. `run_in_order(start_order)` — three threads call `first()`, `second()`, `third()`; they are
   *started* in `start_order` (a permutation of [0, 1, 2]). Return the log, which must always
   be `["first", "second", "third"]`.
2. `ping_pong(n)` — thread A appends "ping" n times, thread B appends "pong" n times; return the
   log, strictly alternating and starting with "ping".
3. `zero_even_odd(n)` — three threads: Z appends 0 before every number, E appends the even
   numbers, O the odd ones; return the joined string, e.g. n=5 -> "0102030405".

Examples
--------
>>> run_in_order([2, 0, 1])
['first', 'second', 'third']
>>> ping_pong(2)
['ping', 'pong', 'ping', 'pong']
>>> zero_even_odd(3)
'010203'

Constraints
-----------
- 0 <= n <= 1000. No `time.sleep` for ordering: sleeps make races rarer, never impossible.


Hints
-----
- `Event` is a latch: once set, every later `wait()` returns at once. Good for one-shot order.
- For repeated turns, `Semaphore(0).release()` means "your turn"; whoever moves first starts
  with a semaphore at 1.
- In zero-even-odd, Z decides who goes next by the parity of the number about to be printed.

Follow-ups
----------
- The same hand-off in asyncio: `asyncio.Event` / `asyncio.Semaphore`, no threads needed.
- Generalise ping-pong to k threads in a ring: k semaphores, thread i releases i+1 mod k.
"""
from __future__ import annotations

import threading


def run_in_order(start_order: list[int]) -> list[str]:
    raise NotImplementedError("TODO")


def ping_pong(n: int) -> list[str]:
    raise NotImplementedError("TODO")


def zero_even_odd(n: int) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    for order in ([0, 1, 2], [2, 1, 0], [1, 2, 0]):
        print(f"start order {order} ->", run_in_order(order))
    print("ping_pong(3):", ping_pong(3))
    print("ping_pong(0):", ping_pong(0))
    print("zero_even_odd(5):", zero_even_odd(5))
    print("zero_even_odd(1):", zero_even_odd(1))
    print("1000 rounds alternate:", ping_pong(1000) == ["ping", "pong"] * 1000)


if __name__ == "__main__":
    main()
