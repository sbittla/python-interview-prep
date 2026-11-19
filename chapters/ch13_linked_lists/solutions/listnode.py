"""Shared singly-linked-list helpers for Chapter 13 (imported by every exercise).

    ListNode(val, next)   one node; __slots__ keeps it small (no per-node __dict__)
    build(values)         Python list -> head (None for [])
    to_list(head, limit)  head -> Python list; raises ValueError if more than `limit` nodes
                          (so a buggy cycle fails loudly instead of hanging a test)
    render(head)          "1 -> 2 -> 3 -> None"
    nodes(head)           list of the node objects themselves (for identity checks)
"""
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


def to_list(head: ListNode | None, limit: int = 10**6) -> list[int]:
    out: list[int] = []
    while head is not None:
        if len(out) >= limit:
            raise ValueError(f"more than {limit} nodes: cycle?")
        out.append(head.val)
        head = head.next
    return out


def render(head: ListNode | None, limit: int = 20) -> str:
    vals = to_list(head, limit=10**6)
    shown = [str(v) for v in vals[:limit]] + (["..."] if len(vals) > limit else [])
    return " -> ".join(shown + ["None"])


def nodes(head: ListNode | None) -> list[ListNode]:
    out: list[ListNode] = []
    while head is not None:
        out.append(head)
        head = head.next
    return out
