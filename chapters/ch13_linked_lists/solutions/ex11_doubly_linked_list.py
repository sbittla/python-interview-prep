"""
Exercise 11 — Doubly Linked List with a Sentinel                 [Tier: ★ Core]
Chapter 13 · Pattern: circular sentinel, O(1) unlink · Target time: 25 min

Problem
-------
Implement `DList`, a doubly linked list whose operations are all O(1):

- push_front(key, val) -> DNode     add at the front, return the new node
- push_back(key, val)  -> DNode     add at the back
- remove(node)                      unlink a node you hold a reference to
- move_to_front(node)               remove + re-insert at the front
- pop_back() -> DNode               remove and return the last node (IndexError if empty)
- len(dl), iter(dl) yields (key, val) front to back, reversed(dl) back to front

Chapter 29 builds an LRU cache from exactly this class plus a dict key -> node:
"get" calls move_to_front, "evict" calls pop_back.

Examples
--------
>>> dl = DList(); a = dl.push_back("a", 1); b = dl.push_back("b", 2)
>>> dl.move_to_front(b); list(dl)
[('b', 2), ('a', 1)]
>>> dl.pop_back().key
'a'

Constraints
-----------
- Up to 10**5 operations. remove(node) is only called with nodes of this list.

Hints
-----
- One sentinel node whose next is the first real node and whose prev is the last.
  Empty list: sentinel.next is sentinel.prev is sentinel.
- With the sentinel, insert and unlink never see None, so there are no `if head`
  special cases: unlink is two writes, insert-after is four.
- After unlinking, clear node.prev/next so a stale reference cannot corrupt the list.

Approach ladder
---------------
1. Brute force — a Python list of (key, val): remove/move are O(n) (search + shift).
2. Improved   — head/tail pointers with None ends: O(1), but every operation needs
   "is this the head? the tail? the only node?" branches.
3. Optimal    — circular sentinel: O(1) everything, no branches.

Edge cases
----------
- pop_back on empty; remove the only node; move_to_front of the front node.

Follow-ups
----------
- LRU cache (Ch 29); LFU cache: one DList per frequency.
- CPython's pure-Python OrderedDict (Lib/collections/__init__.py) uses the same
  circular-sentinel doubly linked list behind move_to_end / popitem.
"""
from __future__ import annotations

from collections.abc import Iterator


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

    def push_front(self, key, val) -> DNode:
        return self._insert_after(self._s, DNode(key, val))

    def push_back(self, key, val) -> DNode:
        return self._insert_after(self._s.prev, DNode(key, val))

    def remove(self, node: DNode) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node.next = None       # detach: stale handles fail loudly
        self._n -= 1

    def move_to_front(self, node: DNode) -> None:
        self.remove(node)
        self._insert_after(self._s, node)

    def pop_back(self) -> DNode:
        if self._n == 0:
            raise IndexError("pop_back from empty DList")
        node = self._s.prev
        self.remove(node)
        return node

    def __len__(self) -> int:
        return self._n

    def __iter__(self) -> Iterator[tuple]:
        cur = self._s.next
        while cur is not self._s:
            yield cur.key, cur.val
            cur = cur.next

    def __reversed__(self) -> Iterator[tuple]:
        cur = self._s.prev
        while cur is not self._s:
            yield cur.key, cur.val
            cur = cur.prev


class ListBackedDList:
    """Rung 1 reference: same API on a Python list (O(n) remove/move)."""

    def __init__(self) -> None:
        self._items: list[list] = []

    def push_front(self, key, val):
        item = [key, val]
        self._items.insert(0, item)
        return item

    def push_back(self, key, val):
        item = [key, val]
        self._items.append(item)
        return item

    def remove(self, item) -> None:
        self._items.remove(item)          # equality search: fine with unique keys

    def move_to_front(self, item) -> None:
        self.remove(item)
        self._items.insert(0, item)

    def pop_back(self):
        if not self._items:
            raise IndexError("pop_back from empty list")
        return self._items.pop()

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return (tuple(x) for x in self._items)


def main() -> None:
    dl = DList()
    a = dl.push_back("a", 1)
    b = dl.push_back("b", 2)
    c = dl.push_back("c", 3)
    print("start          :", list(dl), "len", len(dl))
    dl.move_to_front(c)
    print("move_to_front c:", list(dl))
    dl.remove(a)
    print("remove a       :", list(dl))
    print("reversed       :", list(reversed(dl)))
    print("pop_back       :", dl.pop_back().key, "->", list(dl))
    print("pop_back       :", dl.pop_back().key, "->", list(dl), "len", len(dl))
    try:
        dl.pop_back()
    except IndexError as e:
        print("pop_back empty -> IndexError:", e)
    dl.push_front("z", 26)
    print("reuse after empty:", list(dl), "| b detached:", b.prev is None and b.next is None)


if __name__ == "__main__":
    main()
