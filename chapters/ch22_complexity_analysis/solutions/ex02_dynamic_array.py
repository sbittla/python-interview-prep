"""
Exercise 02 — Amortised Dynamic Array with Cost Accounting   [Tier: ★ Core]
Chapter 22 · Pattern: amortised analysis (aggregate + accounting) · Target time: 20 min

Problem
-------
Build ``DynamicArray(growth)`` backed by a fixed-capacity Python list that you
manage yourself (start with capacity 1). ``append(x)`` writes into a free slot;
when the array is full it allocates a bigger buffer and copies every element.
``growth`` maps the old capacity to the new one, e.g. ``double`` (2 * cap) or
``add_k(k)`` (cap + k). Track ``copies`` (element moves caused by resizing)
and ``resizes``.

Then:

- ``total_copies(n, growth)`` — copies after n appends (aggregate method).
- ``accounting_min_balance(n, charge)`` — charge every append ``charge``
  credits under doubling; a write costs 1 credit and each copied element 1
  credit. Return the lowest bank balance seen. Show that charge = 3 never goes
  negative (so every append is amortised O(1)) while charge = 2 eventually does.

Examples
--------
>>> total_copies(8, double)
7
>>> total_copies(8, add_k(2))
16
>>> accounting_min_balance(1000, 3) >= 0
True

Constraints
-----------
- 0 <= n <= 10**6 for doubling; keep n <= 10**4 for add_k (it is quadratic).

Approach ladder
---------------
1. Grow by one slot every time — n appends copy 0 + 1 + ... + (n-1)
   = n(n-1)/2 elements: O(n^2) total, O(n) per append.
2. Grow by a constant k — copies about n^2 / (2k): still O(n^2), just k times
   smaller. A bigger constant never fixes it.
3. Grow by a constant factor (doubling) — copies 1 + 2 + 4 + ... < 2n, so
   n appends cost O(n) total: amortised O(1) each, worst single append O(n).
   Any factor > 1 works (CPython lists over-allocate by roughly 1/8).

Follow-ups
----------
- Shrinking: halve when the array is 1/4 full, not 1/2, or alternating
  push/pop at the boundary costs O(n) each time (thrashing).
- Amortised is not average-case: it is a worst-case guarantee on the total
  over any sequence, with no probability involved.
"""
from __future__ import annotations

from typing import Callable

Growth = Callable[[int], int]


def double(cap: int) -> int:
    return 2 * cap


def add_k(k: int) -> Growth:
    def grow(cap: int) -> int:
        return cap + k
    grow.__name__ = f"add_{k}"
    return grow


class DynamicArray:
    def __init__(self, growth: Growth = double) -> None:
        self._growth = growth
        self._buf: list = [None]
        self._size = 0
        self.copies = 0
        self.resizes = 0

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return len(self._buf)

    def __getitem__(self, i: int):
        if not 0 <= i < self._size:
            raise IndexError(i)
        return self._buf[i]

    def append(self, x) -> int:
        """Append x; return the number of elements copied by this call."""
        moved = 0
        if self._size == len(self._buf):
            new_cap = self._growth(len(self._buf))
            if new_cap <= len(self._buf):
                raise ValueError("growth must increase capacity")
            new_buf = [None] * new_cap
            for i in range(self._size):
                new_buf[i] = self._buf[i]
            moved = self._size
            self._buf = new_buf
            self.copies += moved
            self.resizes += 1
        self._buf[self._size] = x
        self._size += 1
        return moved


def total_copies(n: int, growth: Growth) -> int:
    arr = DynamicArray(growth)
    for i in range(n):
        arr.append(i)
    return arr.copies


def accounting_min_balance(n: int, charge: int) -> int:
    arr, bank, lowest = DynamicArray(double), 0, 0
    for i in range(n):
        moved = arr.append(i)
        bank += charge - 1 - moved          # 1 credit for the write, 1 per copy
        lowest = min(lowest, bank)
    return lowest


def main() -> None:
    print("copies after n appends (start capacity 1)")
    print(f"{'n':>6} {'double':>8} {'add_10':>8} {'add_100':>8}  copies/n (double)")
    for n in (10, 100, 1_000, 10_000):
        d = total_copies(n, double)
        print(f"{n:>6} {d:>8} {total_copies(n, add_k(10)):>8} "
              f"{total_copies(n, add_k(100)):>8}  {d / n:.2f}")
    print(f"doubling copies < 2n for n=1..2000: "
          f"{all(total_copies(n, double) < 2 * n for n in range(1, 2001))}")
    ratio = total_copies(10_000, add_k(10)) / total_copies(5_000, add_k(10))
    print(f"add_10: doubling n multiplies copies by {ratio:.2f} (quadratic -> ~4)")
    arr = DynamicArray(double)
    worst = max(arr.append(i) for i in range(1025))
    print(f"worst single append at n=1025 copies {worst} elements; resizes={arr.resizes}")
    for charge in (2, 3):
        print(f"accounting, charge {charge}/append: min balance over 10^5 appends = "
              f"{accounting_min_balance(100_000, charge)}")


if __name__ == "__main__":
    main()
