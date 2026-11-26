"""
Exercise 11 — The "Know These" Sorts: Bubble, Selection, Insertion [Tier: ○ Reference]
Chapter 11 · Pattern: quadratic sorts · Target time: 15 min

Problem
-------
Implement bubble sort (with early exit), selection sort and insertion sort.
Each function returns (sorted_list, number_of_swaps_or_shifts) so you can
compare how much work each does on sorted, reversed and random input. Then
show which of the three are stable.

Examples
--------
>>> solve([5, 2, 4, 6, 1, 3])
[1, 2, 3, 4, 5, 6]

Constraints
-----------
- Only for small n. These are O(n^2).

Approach ladder
---------------
These ARE the brute-force rung of sorting. Know their properties:
- Bubble     O(n^2), best O(n) with early exit, stable, in place.
- Selection  O(n^2) always, at most n-1 swaps (good when writes are costly), NOT stable.
- Insertion  O(n^2), best O(n) on nearly sorted input, stable, in place, online.
  Timsort extends short runs with BINARY insertion sort, and the number of shifts
  equals the number of inversions (Exercise 06).

Follow-ups
----------
- Which would you use for 10 elements? Insertion sort (low overhead).
- Which minimises writes? Selection sort.
- Which works on a stream as items arrive? Insertion sort.
"""
from __future__ import annotations


def bubble_sort(nums: list) -> tuple[list, int]:
    a, swaps = list(nums), 0
    for end in range(len(a) - 1, 0, -1):
        swapped = False
        for i in range(end):
            if a[i] > a[i + 1]:              # strict '>' keeps equal keys in order: stable
                a[i], a[i + 1] = a[i + 1], a[i]
                swaps += 1
                swapped = True
        if not swapped:                      # early exit: already sorted
            break
    return a, swaps


def selection_sort(nums: list) -> tuple[list, int]:
    a, swaps = list(nums), 0
    for i in range(len(a) - 1):
        m = i
        for j in range(i + 1, len(a)):
            if a[j] < a[m]:
                m = j
        if m != i:                           # long-distance swap breaks stability
            a[i], a[m] = a[m], a[i]
            swaps += 1
    return a, swaps


def insertion_sort(nums: list) -> tuple[list, int]:
    a, shifts = list(nums), 0
    for i in range(1, len(a)):
        x = a[i]
        j = i - 1
        while j >= 0 and a[j] > x:           # shift bigger items right
            a[j + 1] = a[j]
            shifts += 1
            j -= 1
        a[j + 1] = x
    return a, shifts


def solve(nums: list) -> list:
    return insertion_sort(nums)[0]


class Card:
    """Compares by rank only, so we can watch what happens to equal ranks."""

    def __init__(self, rank: int, suit: str) -> None:
        self.rank, self.suit = rank, suit

    def __lt__(self, other: "Card") -> bool:
        return self.rank < other.rank

    def __gt__(self, other: "Card") -> bool:
        return self.rank > other.rank

    def __repr__(self) -> str:
        return f"{self.rank}{self.suit}"


def main() -> None:
    inputs = {"sorted": [1, 2, 3, 4, 5, 6], "reversed": [6, 5, 4, 3, 2, 1],
              "random": [5, 2, 4, 6, 1, 3]}
    print(f"{'input':<9} {'bubble swaps':>12} {'selection swaps':>15} {'insertion shifts':>16}")
    for name, arr in inputs.items():
        print(f"{name:<9} {bubble_sort(arr)[1]:>12} {selection_sort(arr)[1]:>15} "
              f"{insertion_sort(arr)[1]:>16}")
    arr = [5, 2, 4, 6, 1, 3]
    print("all agree:", bubble_sort(arr)[0] == selection_sort(arr)[0] == solve(arr) == sorted(arr))
    cards = [Card(2, "a"), Card(2, "b"), Card(1, "c")]
    print("input cards :", cards)
    print("bubble      :", bubble_sort(cards)[0])
    print("selection   :", selection_sort(cards)[0], "<- 2a and 2b swapped: not stable")
    print("insertion   :", insertion_sort(cards)[0])
    print("edge cases:", solve([]), solve([1]), solve([2, 2, 1]))


if __name__ == "__main__":
    main()
