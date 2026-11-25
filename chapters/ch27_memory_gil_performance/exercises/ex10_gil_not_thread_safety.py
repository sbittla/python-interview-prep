"""
Exercise 10 — The GIL Is Not Thread Safety: Lost Updates     [Tier: ★ Core]
Chapter 27 · Pattern: deterministic interleaving model + lock · Target time: 25 min

Problem
-------
`counter += 1` is a read-modify-write: load the value, add, store. The
language does not promise that this is atomic. Older CPythons, other
implementations and the free-threaded build do lose updates when another
thread stores between the load and the store; current GIL builds (3.10+)
switch threads only at certain instructions and rarely show it — which is
exactly why an unlocked test that "passes" proves nothing.

1. `bytecode_steps(fn)` returns how many instructions of `fn` belong to the
   read-modify-write of a global (all instructions except RESUME, the final
   return and its constant load). For `def bump(): global c; c += 1` this is
   more than 1 on every CPython (LOAD_GLOBAL, LOAD_CONST, BINARY_OP,
   STORE_GLOBAL from 3.11; INPLACE_ADD instead of BINARY_OP in 3.10).
2. `run_schedule(schedule)` models threads that each do ONE `+= 1` as three
   steps: "L" load into the thread's register, "A" add 1 to the register,
   "S" store the register. `schedule` is a string of thread letters, e.g.
   "AABBAB": each letter runs that thread's next step. Return the final
   counter (starting at 0). Raise ValueError if a thread runs more than 3
   steps or stops before finishing.
3. `locked_total(threads, per_thread)` runs real threads that increment a
   shared counter under a `threading.Lock` and returns the total, which must
   equal threads * per_thread. Create the lock with the module-level name
   `Lock` (`from threading import Lock`) so the tests can count acquisitions.

Examples
--------
>>> run_schedule("AAABBB")      # serial: no lost update
2
>>> run_schedule("ABABAB")      # both load 0 before either stores
1

Constraints
-----------
- Never assert on an UNLOCKED real-thread run: whether updates are lost
  depends on timing and version, so such a test could pass by luck.


Hints
-----
- Keep one register per thread and a pointer to its next step.
- `with lock: counter += 1` makes the three steps one critical section.

Follow-ups
----------
- Does the free-threaded build (3.13+, PEP 703) make this worse? (The race
  is the same; with true parallelism it simply shows up more often.)
- Which operations are atomic in practice? (Single C-level calls such as
  `list.append` or `dict[k] = v` on built-ins in the GIL build — an
  implementation detail; use locks or `queue.Queue` rather than rely on it.)
"""
from __future__ import annotations

import dis
import threading
from threading import Lock          # module-level name: tests swap in a counting lock

c = 0


def bump() -> None:
    global c
    c += 1


def bytecode_steps(fn) -> int:
    raise NotImplementedError("TODO")


def run_schedule(schedule: str) -> int:
    raise NotImplementedError("TODO")


def locked_total(threads: int, per_thread: int) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    print("c += 1 spans more than one instruction:", bytecode_steps(bump) > 1)
    for schedule in ["AAABBB", "ABABAB", "AABBAB", "ABBBAA", "ABCABCABC"]:
        n = len(set(schedule))
        print(f"{schedule:10} final={run_schedule(schedule)}  expected={n}")
    for bad in ["AAAA", "AAB"]:
        try:
            run_schedule(bad)
        except ValueError as exc:
            print(f"{bad:10} ValueError: {exc}")
    print("locked 4 x 50,000 =", locked_total(4, 50_000))


if __name__ == "__main__":
    main()
