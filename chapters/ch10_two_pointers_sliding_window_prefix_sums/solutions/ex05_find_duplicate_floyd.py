"""
Exercise 05 — Find the Duplicate (Floyd) and Happy Numbers  [Tier: ◆ Extended]
Chapter 10 · Pattern: fast and slow pointers on a function graph · Target time: 25 min

Problem
-------
(a) find_duplicate: nums has n + 1 integers, each in 1..n, so by pigeonhole at
    least one value repeats; exactly one value repeats (possibly many times).
    Return it without modifying nums and with O(1) extra space.
(b) is_happy: starting from a positive integer, repeatedly replace it by the
    sum of the squares of its digits. Return True if the sequence reaches 1.

Examples
--------
>>> solve([1, 3, 4, 2, 2])
2
>>> solve([3, 1, 3, 4, 2])
3
>>> is_happy(19), is_happy(2)
(True, False)

Constraints
-----------
- (a) 1 <= n <= 10**5. (b) 1 <= x <= 2**31 - 1.

Approach ladder (find_duplicate)
--------------------------------
1. Brute force — compare every pair. O(n^2) time, O(1) space.
2. Improved   — sort a copy and scan neighbours (O(n log n), O(n) space), or
   a seen-set (O(n) time, O(n) space). Both break a constraint.
   Binary search on the value range with counting is O(n log n), O(1) space.
3. Optimal    — view i -> nums[i] as a function on 0..n. Index 0 is never a
   target (values are >= 1), so walking from 0 must eventually enter a cycle,
   and the cycle's entrance is a value with two incoming arrows: the
   duplicate. Floyd: slow moves 1 step, fast 2 steps until they meet; then
   restart one pointer at 0 and move both 1 step; they meet at the entrance.
   O(n) time, O(1) space, nums untouched.

Why phase 2 works: if the tail has length a and the cycle length c, at the
first meeting slow has walked a + b steps and fast 2(a + b), so a + b is a
multiple of c; walking a more steps from the meeting point lands on the
entrance, which is also where a pointer from the start arrives after a steps.

is_happy: the sequence is eventually periodic (values quickly drop below
1000 and stay there). A seen-set is O(k) space; Floyd detects the loop in
O(1) space — the same idea on a number sequence. Linked-list cycle detection
uses identical code on nodes (-> Chapter 13.4).

Wrong-but-tempting
------------------
- sum(nums) - n*(n+1)//2: works only when the duplicate appears exactly twice.
- Returning the meeting point of phase 1: it is *on* the cycle, not
  necessarily its entrance.

Follow-ups
----------
- Why not mark visited by negating nums[abs(x)]? It is O(1) space but
  modifies the input, which the problem forbids.
"""
from __future__ import annotations


def brute_force(nums: list[int]) -> int:
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return nums[i]
    raise ValueError("no duplicate")


def seen_set(nums: list[int]) -> int:
    seen: set[int] = set()
    for x in nums:
        if x in seen:
            return x
        seen.add(x)
    raise ValueError("no duplicate")


def count_binary_search(nums: list[int]) -> int:
    lo, hi = 1, len(nums) - 1             # answer lies in [lo, hi]
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(1 for x in nums if x <= mid) > mid:
            hi = mid                      # too many values <= mid
        else:
            lo = mid + 1
    return lo


def wrong_sum_formula(nums: list[int]) -> int:
    """Wrong-but-tempting: assumes the duplicate appears exactly twice."""
    n = len(nums) - 1
    return sum(nums) - n * (n + 1) // 2


def solve(nums: list[int]) -> int:
    slow = fast = 0
    while True:                           # phase 1: meet inside the cycle
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = 0                              # phase 2: find the entrance
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow


def _digit_square_sum(x: int) -> int:
    total = 0
    while x:
        x, d = divmod(x, 10)
        total += d * d
    return total


def is_happy_set(x: int) -> bool:
    seen: set[int] = set()
    while x != 1 and x not in seen:
        seen.add(x)
        x = _digit_square_sum(x)
    return x == 1


def is_happy(x: int) -> bool:
    slow, fast = x, _digit_square_sum(x)
    while fast != 1 and slow != fast:
        slow = _digit_square_sum(slow)
        fast = _digit_square_sum(_digit_square_sum(fast))
    return fast == 1


def main() -> None:
    for nums in ([1, 3, 4, 2, 2], [3, 1, 3, 4, 2], [1, 1], [2, 2, 2, 2, 2], [4, 3, 1, 4, 2, 4]):
        print(f"nums={nums!s:<20} -> {solve(nums)}  brute={brute_force(nums)}"
              f"  binsearch={count_binary_search(nums)}  sum-formula(wrong)={wrong_sum_formula(nums)}")
    happy = [x for x in range(1, 50) if is_happy(x)]
    print("happy numbers below 50:", happy)
    print("Floyd agrees with set on 1..2000:",
          all(is_happy(x) == is_happy_set(x) for x in range(1, 2001)))


if __name__ == "__main__":
    main()
