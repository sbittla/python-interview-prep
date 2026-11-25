"""
Exercise 02 — When Is an Object Freed? Refcounts vs the Cycle GC  [Tier: ★ Core]
Chapter 27 · Pattern: object lifetime, weakref.finalize · Target time: 20 min

Problem
-------
CPython frees an object the moment its reference count drops to zero. A
reference cycle keeps every count above zero, so cyclic garbage waits for the
cycle collector (the `gc` module).

Write `lifetime(scenario)` that builds one of these scenarios with the cycle
collector disabled, drops every external name, and returns a list of events:

  "plain"     one Node, no cycle
  "self"      a Node whose .other points to itself
  "pair"      two Nodes pointing at each other
  "chain"     a -> b -> c, no cycle
  "weak"      a pair where one direction is a weakref.ref (no strong cycle)

Events are "freed:<name>" (recorded by `weakref.finalize` when an object
dies), and the marker "collect" just before an explicit `gc.collect()`.
Return names in the order they die. The collector must be re-enabled even if
something fails.

Examples
--------
>>> lifetime("plain")
['freed:a', 'collect']
>>> lifetime("pair")
['collect', 'freed:a', 'freed:b']

Constraints
-----------
- Deterministic: disable automatic collection while the scenario runs, and
  sort names that die in the same `gc.collect()` call (its order is not
  specified).


Hints
-----
- Record the "collect" marker before calling `gc.collect()`.
- A finalize callback must not reference the object (pass the name instead).

Follow-ups
----------
- Why does the cycle collector only track containers? (Only objects that can
  refer to others can form a cycle; ints and strs are never tracked.)
- How do `weakref.WeakValueDictionary` caches avoid keeping entries alive?
"""
from __future__ import annotations

import gc
import weakref


class Node:
    def __init__(self, name: str) -> None:
        self.name = name
        self.other: object = None


def _build(scenario: str, events: list[str]) -> list[Node]:
    def watch(*nodes: Node) -> list[Node]:
        for node in nodes:
            weakref.finalize(node, events.append, f"freed:{node.name}")
        return list(nodes)

    if scenario == "plain":
        return watch(Node("a"))
    if scenario == "self":
        a = Node("a")
        a.other = a
        return watch(a)
    if scenario == "pair":
        a, b = Node("a"), Node("b")
        a.other, b.other = b, a
        return watch(a, b)
    if scenario == "chain":
        a, b, c = Node("a"), Node("b"), Node("c")
        a.other, b.other = b, c
        return watch(a, b, c)
    if scenario == "weak":
        a, b = Node("a"), Node("b")
        a.other, b.other = b, weakref.ref(a)      # b -> a is weak: no strong cycle
        return watch(a, b)
    raise ValueError(f"unknown scenario: {scenario!r}")


def lifetime(scenario: str) -> list[str]:
    raise NotImplementedError("TODO")


def main() -> None:
    for scenario in ["plain", "chain", "weak", "self", "pair"]:
        print(f"{scenario:6} {lifetime(scenario)}")
    print("collector re-enabled:", gc.isenabled())
    print("generations tracked:", len(gc.get_count()))
    print("ints are GC-tracked:", gc.is_tracked(12345))
    print("lists are GC-tracked:", gc.is_tracked([]))
    try:
        lifetime("ring")
    except ValueError as exc:
        print("ValueError:", exc)


if __name__ == "__main__":
    main()
