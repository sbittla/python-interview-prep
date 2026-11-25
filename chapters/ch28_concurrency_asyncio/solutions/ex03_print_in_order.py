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

Approach ladder
---------------
1. Brute force — busy-wait on a shared turn variable (`while turn != me: pass`): burns a CPU
   core per waiting thread and, under the GIL, slows down the very thread it waits for.
2. Improved   — one `Condition` + turn variable + `notify_all()`: correct, but every hand-off
   wakes every waiter (k threads, O(k) wake-ups per step).
3. Optimal    — one `Event` (one-shot) or `Semaphore(0)` (repeatable) per hand-off edge: each
   step wakes exactly the next thread; O(1) per step, O(n) total for n steps.

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
    log: list[str] = []
    done_first, done_second = threading.Event(), threading.Event()

    def first() -> None:
        log.append("first")
        done_first.set()

    def second() -> None:
        done_first.wait()
        log.append("second")
        done_second.set()

    def third() -> None:
        done_second.wait()
        log.append("third")

    funcs = [first, second, third]
    threads = [threading.Thread(target=funcs[i]) for i in start_order]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return log


def ping_pong(n: int) -> list[str]:
    log: list[str] = []
    ping_turn, pong_turn = threading.Semaphore(1), threading.Semaphore(0)

    def player(word: str, mine: threading.Semaphore, other: threading.Semaphore) -> None:
        for _ in range(n):
            mine.acquire()                 # wait for my turn
            log.append(word)
            other.release()                # hand the turn over

    threads = [threading.Thread(target=player, args=("pong", pong_turn, ping_turn)),
               threading.Thread(target=player, args=("ping", ping_turn, pong_turn))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return log


def zero_even_odd(n: int) -> str:
    out: list[str] = []
    zero, even, odd = threading.Semaphore(1), threading.Semaphore(0), threading.Semaphore(0)

    def zeros() -> None:
        for i in range(1, n + 1):
            zero.acquire()
            out.append("0")
            (even if i % 2 == 0 else odd).release()

    def numbers(sem: threading.Semaphore, start: int) -> None:
        for i in range(start, n + 1, 2):
            sem.acquire()
            out.append(str(i))
            zero.release()

    threads = [threading.Thread(target=numbers, args=(even, 2)),
               threading.Thread(target=numbers, args=(odd, 1)),
               threading.Thread(target=zeros)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return "".join(out)


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
