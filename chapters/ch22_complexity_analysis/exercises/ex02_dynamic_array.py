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

Hints
-----
- Resize only when size == capacity; copy element by element so the copy
  cost is visible, and return how many elements moved.
- Sum the copies for doubling: 1 + 2 + 4 + ... — compare with 2n.
- Accounting: bank += charge - 1 - moved after every append; track the minimum.
- Reject a growth function that does not increase capacity (ValueError).

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
        raise NotImplementedError("TODO")


def total_copies(n: int, growth: Growth) -> int:
    raise NotImplementedError("TODO")


def accounting_min_balance(n: int, charge: int) -> int:
    raise NotImplementedError("TODO")


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
