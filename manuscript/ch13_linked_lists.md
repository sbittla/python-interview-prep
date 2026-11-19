# Chapter 13. Linked Lists

Tier ★ Core · Tracks S, M, L · Study time ≈ 5 h · Prerequisites: Ch 8 (Big-O), Ch 9 (hash maps)

**Learning objectives**

- Build and walk lists; remove head special cases with a dummy node.
- Reverse iteratively, and explain why recursion fails on long lists.
- Find the middle, a cycle and its entry with fast/slow pointers — with proof.
- Merge sorted lists; build a sentinel doubly linked list with O(1) remove.

> **Recognise it**
>
> | Signal in the prompt | Reach for |
> |---|---|
> | "given the head of a list", "in place", "O(1) extra space" | pointer rewiring, no copying to a Python list |
> | head itself may be deleted or replaced | dummy head (13.2) |
> | "reverse", "in groups of k", "reorder", "palindrome" | three-pointer reversal (13.3) |
> | "middle", "cycle", "kth from the end" | fast/slow or fixed-gap pointers (13.4, 13.6) |
> | "sorted lists", "merge" | dummy tail; k lists → min-heap (13.5) |
> | "O(1) remove given the node", "LRU", "move to front" | doubly linked list + dict (13.7) |

Listings run standalone next to `chapters/ch13_linked_lists/solutions/listnode.py`, which they import. Classics with full files in the
problem bank (`ex049`–`ex056`) are taught here by their core move, with the file cited.

## 13.1 Node class, building and printing lists

A node is a value plus a reference to the next node; the list is just "the head node, or `None`".
Python has no built-in singly linked list (`collections.deque` is a doubly linked list of blocks),
so interviewers hand you this class:

```python
from __future__ import annotations

from collections.abc import Iterable


class ListNode:
    __slots__ = ("val", "next")

    def __init__(self, val: int = 0, next: ListNode | None = None) -> None:
        self.val = val
        self.next = next

    def __repr__(self) -> str:          # shows the value only, never the address
        return f"ListNode({self.val!r})"


def build(values: Iterable[int]) -> ListNode | None:
    dummy = tail = ListNode()
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next
```

```python
from listnode import build, render, to_list

head = build([3, 1, 4])
print(to_list(head), '|', render(head))
```

```text
[3, 1, 4] | 3 -> 1 -> 4 -> None
```

Write `build`/`to_list` first: every test becomes a one-liner (ours raises `ValueError` on an
accidental cycle). Index access is O(n); insert/delete *after a node you hold* is O(1).

## 13.2 Traversal, insertion, deletion; dummy head technique

To delete or insert at position *i* you need the node **before** *i*. Position 0 has no
predecessor — unless you invent one:

Delete every 7 from `7 -> 1 -> 7`:

| Step | `prev` | `prev.next` | Action | List after the step |
|---|---|---|---|---|
| 1 | dummy | 7 | unlink, `prev` stays | dummy → 1 → 7 → None |
| 2 | dummy | 1 | keep, advance `prev` | dummy → 1 → 7 → None |
| 3 | 1 | 7 | unlink, `prev` stays | dummy → 1 → None |
| 4 | 1 | None | stop, return `dummy.next` | 1 → None (old head gone) |

```python
from __future__ import annotations

from listnode import ListNode


def solve(head: ListNode | None, x: int) -> ListNode | None:
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next is not None:
        if prev.next.val == x:
            prev.next = prev.next.next    # unlink; do NOT advance prev
        else:
            prev = prev.next
    return dummy.next
```

```text
[7, 1, 7, 7, 2, 7]   x=7 -> 1 -> 2 -> None
[7, 7]               x=7 -> None
```

Wrong-but-tempting: advancing `prev` after a deletion skips the node that slid into place, so
`[7, 7]` keeps a 7. Stripping matching heads in a separate loop works but doubles the code. → repo: `chapters/ch13_linked_lists/solutions/ex02_remove_value.py`

## 13.3 Reversal: iterative and recursive; reverse in k-groups ◆

Flip one arrow per step. You hold three names; the order of the four lines is the whole trick:

```text
 None <- [1]    [2] -> [3] -> None         prev=[1]  cur=[2]
 1. nxt = cur.next          save [3] BEFORE overwriting cur.next
 2. cur.next = prev         None <- [1] <- [2]    [3] -> None
 3. prev = cur; 4. cur = nxt
```

```python
from __future__ import annotations

from listnode import ListNode


def reverse(head: ListNode | None) -> ListNode | None:
    prev, cur = None, head
    while cur:
        nxt = cur.next      # 1. save the rest of the list
        cur.next = prev     # 2. flip this arrow
        prev = cur          # 3. advance prev
        cur = nxt           # 4. advance cur
    return prev             # cur is None; prev is the old tail


def reverse_recursive(head: ListNode | None) -> ListNode | None:
    if head is None or head.next is None:
        return head
    new_head = reverse_recursive(head.next)
    head.next.next = head   # the old successor now points back at us
    head.next = None        # we are the new tail
    return new_head
```

```text
iterative 100000 nodes, new head: 99999
recursion limit: 1000
recursive 5000 nodes -> RecursionError
```

Wrong-but-tempting:

- **Losing `next` before re-linking** — writing `cur.next = prev` before saving `nxt` orphans the
  rest of the list.
- **Forgetting the tail's `None`** — omit `head.next = None` in the recursive version and the
  first two nodes point at each other: a 2-cycle that makes any later walk loop forever.
- **Recursion depth** — CPython's default limit is 1,000 frames and recursion is O(n) stack.
  Mention the recursive form; ship the loop.

**Reverse in k-groups** repeats the same loop on each block of k nodes, with a dummy head and a
`group_prev` pointer that re-attaches each reversed block; a short final block stays as is.
Pair swapping (k = 2) is ex10. → repo: `chapters/ch13_linked_lists/solutions/ex01_list_toolkit.py`
(both listings), `chapters/ch45_problem_bank/solutions/ex049_reverse_linked_list.py`,
`chapters/ch45_problem_bank/solutions/ex056_reverse_k_group.py`

## 13.4 Fast/slow pointers: middle, cycle detection (Floyd), cycle start

`slow` moves 1, `fast` moves 2. With `while fast and fast.next`, slow stops on the middle
(the second middle for even length). If the list has a cycle, fast laps slow and they meet
inside it — O(1) memory where a `set` of visited nodes needs O(n). The bank file
`chapters/ch45_problem_bank/solutions/ex051_linked_list_cycle.py` solves the same detect-and-find-entry
problem as ex04 below, with the set rung as its brute force.

### Worked problem 1 — where does the cycle begin?

*Return the first node of the loop, or `None`; don't modify the list.* (ex04)

| Rung | Idea | Time / space | Why move up |
|---|---|---|---|
| 1 | Walk, store visited **nodes** in a set; first repeat is the entry | O(n) / O(n) | asked for O(1) memory |
| 2 | Floyd: detect a meeting point, then restart one pointer at head | O(n) / O(1) | — |

**Why phase 1 meets.** Once both pointers are inside the loop, fast gains exactly one node per
step, so the gap behind slow shrinks by 1 each step: they meet within one lap, never jumping over
each other. **Why phase 2 works.** Let *a* = steps from head to the entry, *b* = entry to the meeting point,
*c* = cycle length. Fast has walked twice as far as slow: 2(*a*+*b*) = *a*+*b*+*kc* for some
*k* ≥ 1, so *a* = *kc* − *b*. A pointer at the meeting point that walks *a* steps lands at
*b* + *kc* − *b* = *kc* steps past the entry: the entry itself. The pointer from head
also arrives there after *a* steps, so they meet exactly at the entry — and not earlier, because
the head pointer is not inside the loop before step *a*, so it cannot share a node with the
loop pointer sooner.

```python
from __future__ import annotations

from listnode import ListNode


def solve(head: ListNode | None) -> ListNode | None:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow, fast = slow.next, fast.next.next
        if slow is fast:                  # phase 1: they met inside the loop
            slow = head                   # phase 2: restart one pointer at head
            while slow is not fast:
                slow, fast = slow.next, fast.next
            return slow
    return None
```

```text
[3, 2, 0, -4]                    pos=1  -> entry index 1, loop length 3, brute agrees True
[5, 5, 5, 5, 5]                  pos=3  -> entry index 3, loop length 2, brute agrees True
```

Wrong-but-tempting: storing **values** in the set (duplicates fake a cycle). Follow-up: "find the
duplicate" in n+1 values from 1..n is this algorithm on the implicit list *i → nums[i]*.

## 13.5 Merge two sorted lists; merge k lists (→ heaps)

Two lists: dummy plus `tail`; append the smaller head, then `tail.next = a or b`. Ties from
the first list keep it stable. → repo: `chapters/ch45_problem_bank/solutions/ex050_merge_two_sorted_lists.py`

**Merge k lists** (full treatment in Ch 15; here ex06): one-at-a-time merging is O(kN); a heap
of the k current heads is O(N log k) time, O(k) space:

```python
from __future__ import annotations

import heapq

from listnode import ListNode


def solve(heads: list[ListNode | None]) -> ListNode | None:
    heap = [(h.val, i, h) for i, h in enumerate(heads) if h is not None]
    heapq.heapify(heap)
    dummy = tail = ListNode()
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next is not None:
            heapq.heappush(heap, (node.next.val, i, node.next))
    tail.next = None
    return dummy.next
```

```text
heap      : [1, 1, 2, 3, 4, 4, 5, 6]
(val, node) tuples -> TypeError
```

The middle field `i` matters: with `(val, node)` tuples the first tie makes Python compare two
`ListNode`s → `TypeError`. The index breaks ties first and keeps the merge stable. Tuple
tie-breakers (→ §15.2); more merge-k variants (→ §15.6).

## 13.6 Remove nth from end, intersection, palindrome list

**Remove nth from end** — give `lead` a head start of n+1 nodes from a dummy, then move both
until `lead` is `None`; `trail` is now the victim's predecessor. One pass, and the dummy covers
"remove the head". → repo: `chapters/ch45_problem_bank/solutions/ex052_remove_nth_from_end.py`

**Intersection** (ex05) — two lists sharing a tail of the same node objects. Rungs: nested scan
O(mn); set of node ids, O(m) space; O(1) space by letting each pointer jump to the *other* head at
its end — both walk m+n steps and meet at the shared node, or both reach `None`.
→ repo: `chapters/ch13_linked_lists/solutions/ex05_intersection.py`

### Worked problem 2 — palindrome list, restored

*Return whether the values read the same both ways, in O(1) extra space, leaving the list as you
found it.* (ex03)

| Rung | Idea | Time / space | Why move up |
|---|---|---|---|
| 1 | `vals = to_list(head); vals == vals[::-1]` | O(n) / O(n) | asked for O(1) space |
| 2 | Push the first half on a stack while finding the middle | O(n) / O(n/2) | still linear space |
| 3 | Middle → reverse second half → compare → reverse back | O(n) / O(1) | — |

```python
from __future__ import annotations

from listnode import ListNode


def _reverse(head: ListNode | None) -> ListNode | None:
    prev = None
    while head is not None:
        head.next, prev, head = prev, head, head.next
    return prev


def is_palindrome(head: ListNode | None) -> bool:
    if head is None or head.next is None:
        return True
    # first-middle split so the first half is never shorter than the second
    slow = fast = head
    while fast.next is not None and fast.next.next is not None:
        slow, fast = slow.next, fast.next.next
    second = _reverse(slow.next)          # slow is the tail of the first half
    ok, a, b = True, head, second
    while b is not None:                  # second half is the shorter (or equal) one
        if a.val != b.val:
            ok = False
            break
        a, b = a.next, b.next
    slow.next = _reverse(second)          # restore the original list
    return ok
```

```text
palindrome [1, 2, 3, 2, 1]  -> True  restored=True
palindrome [1, 2]           -> False restored=True
```

The loop condition differs from 13.4: we want the *first* middle so the halves split cleanly.
Wrong-but-tempting: returning early from the compare loop and skipping the restore. Say aloud
that the list is mutated while the function runs.

## 13.7 Doubly linked lists

Add `prev` and you can unlink a node you hold in O(1) — no walk to find its predecessor. A
**circular sentinel** (one dummy whose `next` is the first node and `prev` the last) removes every
`None` check: the empty list is the sentinel pointing at itself.

```text
 +-> [S] <-> [c] <-> [a] <-> [b] <-+      S = sentinel; S.next = first, S.prev = last
 +---------------------------------+      empty list: S.next is S.prev is S
```

```python
from __future__ import annotations


class DNode:
    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key=None, val=None) -> None:
        self.key, self.val = key, val
        self.prev: DNode | None = None
        self.next: DNode | None = None


class DList:
    def __init__(self) -> None:
        self._s = DNode()                  # sentinel: s.next = first, s.prev = last
        self._s.prev = self._s.next = self._s
        self._n = 0

    def _insert_after(self, where: DNode, node: DNode) -> DNode:
        node.prev, node.next = where, where.next
        where.next.prev = node
        where.next = node
        self._n += 1
        return node

    def remove(self, node: DNode) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node.next = None       # detach: stale handles fail loudly
        self._n -= 1
```

```text
move_to_front c: [('c', 3), ('a', 1), ('b', 2)]
remove a       : [('c', 3), ('b', 2)]
```

`move_to_front` is remove + insert-after-sentinel; `pop_back` removes `sentinel.prev`. A dict from
key to node plus this class is an LRU cache, built in (→ Ch 29). → repo:
`chapters/ch13_linked_lists/solutions/ex11_doubly_linked_list.py`

## 13.8 Copy list with random pointer ◆

Deep-copy a list whose nodes also have a `random` pointer. Rung 1 (write it first): a dict
`original → copy` seeded with `None: None`, two passes, O(n) space. Rung 2, O(1) extra: weave
copies in (A → A′ → B → B′), set `copy.random = orig.random.next`, unzip. → repo:
`chapters/ch45_problem_bank/solutions/ex055_copy_random_list.py`

## 13.9 Practice set

Odd-even regroup, stable partition and rotate (ex07–ex09) drill "build two chains, glue,
terminate". Skip partition's `rest_tail.next = None` and the output loops (more practice: bank
`ex053` reorder, `ex054` add two numbers):

```text
forgot rest_tail.next = None -> more than 100 nodes: cycle?
```

## Interviewer's view

- **Draw first:** three boxes; narrate which pointer you save before each write.
- **Edge cases aloud:** empty, one node, two nodes, change at the head or tail.
- Compare nodes with `is`; `to_list()` is a fine rung 1 — name it, then remove it.
- Mentioning the recursion limit unprompted is a strong signal.

## Exercises

Code: `chapters/ch13_linked_lists/` (stubs in `exercises/`, run tests with `TARGET=exercises`).

| Id | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Toolkit: length, insert/delete at index, reverse ×2 | ★ | pointer walk, dummy head |
| ex02 | Delete every node holding a value | ★ | dummy head |
| ex03 | Middle node and palindrome list (restored) | ★ | fast/slow + reversal |
| ex04 | Cycle start and cycle length | ★ | Floyd |
| ex05 | Intersection of two lists | ★ | two pointers |
| ex06 | Merge k sorted lists | ★ | dummy tail + heap |
| ex07 | Odd-even regroup | ★ | two running tails |
| ex08 | Stable partition around x | ★ | two dummy heads |
| ex09 | Rotate right by k | ★ | ring and cut |
| ex10 | Swap adjacent pairs | ◆ | local reversal |
| ex11 | Doubly linked list with sentinel | ★ | O(1) unlink |

## Checkpoint quiz

1. Why does `remove_value` return `dummy.next` rather than `head`?
2. In iterative reversal, what goes wrong if `cur.next = prev` runs before `nxt = cur.next`?
3. Why does Floyd's phase 2, restarted from head, stop at the cycle's entry?
4. Why push `(val, i, node)` instead of `(val, node)` onto the heap?
5. What makes `DList.remove(node)` O(1), and why no `None` checks?

<details>
<summary>Answers</summary>

1. The original head may have been deleted; `dummy.next` is always the current first node.
2. The only reference to the rest of the list is overwritten; those nodes are lost.
3. 2(*a*+*b*) = *a*+*b*+*kc* gives *a* = *kc* − *b*; walking *a* from the meeting point ends
   exactly on the entry, where the head pointer also arrives after *a* steps — and the head
   pointer isn't on the loop before step *a*, so they can't meet sooner.
4. On ties Python compares the `ListNode`s, which aren't orderable → `TypeError`. The unique
   index settles ties first and keeps the merge stable.
5. The node knows its `prev`, so unlinking is two writes; the circular sentinel means
   `prev`/`next` are never `None`.

</details>

## Summary card

- Head can change → dummy head, return `dummy.next`.
- Reverse: save, flip, advance, advance; return `prev`. Loop, not recursion.
- Fast/slow → middle, cycle, entry (*a* = *kc* − *b*). Gap → nth from end. Switch heads → intersection.
- Merge → dummy tail; k lists → heap of `(val, i, node)`, O(N log k).
- New chain built → terminate its tail with `None`.
- Doubly linked + sentinel → O(1) unlink; + dict = LRU (Ch 29).
