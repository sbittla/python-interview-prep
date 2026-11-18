"""
Exercise 054 — Add Two Numbers Stored as Digit Lists                [Tier: ★ Core]
Chapter 45 · Linked lists · Intermediate · Pattern: Simulation with carry · Target time: 15 min

Problem
-------
Two non-negative integers are stored as linked lists of decimal digits, least
significant digit first (so 342 is 2 -> 4 -> 3). Return their sum in the same
format. Neither number has leading zeros except the number 0 itself.
(Resembles "Add Two Numbers".)

Examples
--------
>>> to_list(solve(build([2, 4, 3]), build([5, 6, 4])))
[7, 0, 8]
>>> to_list(solve(build([9, 9, 9]), build([1])))
[0, 0, 0, 1]
>>> to_list(solve(build([0]), build([0])))
[0]

Constraints
-----------
- 1 <= number of digits in each list <= 100 (the follow-up allows 10^5)
- Every node holds a digit 0..9.

Hidden edge cases
-----------------
- Lists of different length.
- A final carry that adds a new most-significant digit (999 + 1).
- 0 + 0 must return [0], not an empty list.

Hints
-----
1. This is grade-school addition. Which direction do you add digits, and what
   do you carry?
2. Keep looping while either list has digits *or* there is a carry.

Approach ladder
---------------
1. Brute force — convert each list to a Python int, add, convert back. O(n) digits
   here thanks to Python big ints, but it dodges the point of the question and in
   fixed-width languages it overflows.
2. Optimal — walk both lists at once, summing digit + digit + carry, emitting
   `total % 10` and carrying `total // 10`. O(max(n, m)) time, O(1) extra space
   beyond the output. This is the answer interviewers want.

Complexity
----------
Optimal: O(max(n, m)) time, O(max(n, m)) for the output list, O(1) otherwise.

Follow-ups
----------
- Digits stored most-significant first ("Add Two Numbers II"): use two stacks or reverse.
- Subtract or multiply two such numbers.
- Support base b instead of 10.

Common wrong answers
--------------------
- Stopping when the shorter list ends and dropping the rest of the longer one.
- Forgetting the final carry.
- Converting to int: correct in Python but usually rejected as "not the exercise".
"""
from __future__ import annotations


class ListNode:
    def __init__(self, val: int = 0, next: ListNode | None = None) -> None:
        self.val = val
        self.next = next


def build(values: list[int]) -> ListNode | None:
    dummy = ListNode()
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def to_list(head: ListNode | None) -> list[int]:
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def brute_force(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    """Convert to int, add, convert back (relies on Python big ints)."""
    def to_int(node):
        return int("".join(map(str, reversed(to_list(node)))) or "0")
    total = to_int(a) + to_int(b)
    return build([int(ch) for ch in reversed(str(total))])


def solve(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    """Digit-by-digit addition with a carry."""
    dummy = tail = ListNode()
    carry = 0
    while a or b or carry:
        total = carry
        if a:
            total, a = total + a.val, a.next
        if b:
            total, b = total + b.val, b.next
        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next
    return dummy.next


# Minimal interview version
def interview_version(a, b):
    dummy = tail = ListNode()
    carry = 0
    while a or b or carry:
        s = carry + (a.val if a else 0) + (b.val if b else 0)
        carry, d = divmod(s, 10)
        tail.next = tail = ListNode(d)
        a, b = a and a.next, b and b.next
    return dummy.next


def main() -> None:
    cases = [([2, 4, 3], [5, 6, 4]), ([9, 9, 9], [1]), ([0], [0]), ([1, 8], [0]), ([5], [5])]
    for a, b in cases:
        print(f"{a} + {b} -> {to_list(solve(build(a), build(b)))}")
    print(f"interview version: {to_list(interview_version(build([9, 9]), build([9])))}")


if __name__ == "__main__":
    main()
