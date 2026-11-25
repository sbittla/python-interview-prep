"""
Exercise 09 — Order Workflow with Enums: Enum, IntEnum, Flag  [Tier: ★ Core]
Chapter 24 · Pattern: enum-driven state machine, bit flags · Target time: 20 min

Problem
-------
1. `Status(Enum)` has members PENDING, PAID, SHIPPED, DELIVERED, CANCELLED with string
   values "pending", "paid", ... Legal moves:
   PENDING -> PAID | CANCELLED;  PAID -> SHIPPED | CANCELLED;  SHIPPED -> DELIVERED.
   DELIVERED and CANCELLED are terminal.
2. `Order(order_id)` starts PENDING. `order.advance(to)` accepts a `Status` OR its string
   value ("paid"); an unknown string raises `ValueError`, an illegal move raises
   `InvalidTransition` (a `ValueError` subclass) naming both states. `order.trail`
   lists the statuses visited, oldest first.
3. `Priority(IntEnum)` LOW=1, NORMAL=2, HIGH=3: comparable with ints, so
   `sort_orders(orders)` sorts by priority descending, then order_id.
4. `Perm(Flag)` READ, WRITE, DELETE with `auto()`. `can(granted, needed)` is True when
   every bit in `needed` is in `granted`.

Examples
--------
>>> o = Order("A1"); o.advance("paid"); o.advance(Status.SHIPPED); [s.value for s in o.trail]
['pending', 'paid', 'shipped']
>>> can(Perm.READ | Perm.WRITE, Perm.READ), can(Perm.READ, Perm.READ | Perm.DELETE)
(True, False)

Constraints
-----------
- advance and can are O(1); sort_orders O(n log n).

Hints
-----
- Store the table as `dict[Status, frozenset[Status]]`.
- `Status(value)` raises `ValueError` for an unknown value; `Status[name]` raises `KeyError`.
- `needed & granted == needed` tests "all bits present"; `in` also works for flags.

Follow-ups
----------
- Why is `IntEnum` riskier than `Enum`? (`Priority.HIGH == 3` is True, so it silently
  mixes with unrelated ints.) In 3.11+ `str()` of an IntEnum member is the number.
- Add `@enum.unique` to forbid two names sharing a value (otherwise the second is an
  alias of the first).
"""
from __future__ import annotations

from enum import Enum, Flag, IntEnum, auto, unique


@unique
class Status(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


TRANSITIONS: dict[Status, frozenset[Status]] = {
    Status.PENDING: frozenset({Status.PAID, Status.CANCELLED}),
    Status.PAID: frozenset({Status.SHIPPED, Status.CANCELLED}),
    Status.SHIPPED: frozenset({Status.DELIVERED}),
    Status.DELIVERED: frozenset(),
    Status.CANCELLED: frozenset(),
}


class Priority(IntEnum):
    LOW = 1
    NORMAL = 2
    HIGH = 3


class Perm(Flag):
    READ = auto()        # 1
    WRITE = auto()       # 2
    DELETE = auto()      # 4


class InvalidTransition(ValueError):
    pass


class Order:
    def __init__(self, order_id: str, priority: Priority = Priority.NORMAL) -> None:
        raise NotImplementedError("TODO")

    def advance(self, to: Status | str) -> None:
        raise NotImplementedError("TODO")


def naive_advance(state: str, to: str) -> str:
    """Rung 1: bare strings. Nothing stops a typo or an illegal jump."""
    raise NotImplementedError("TODO")


def sort_orders(orders: list[Order]) -> list[str]:
    raise NotImplementedError("TODO")


def can(granted: Perm, needed: Perm) -> bool:
    raise NotImplementedError("TODO")


def main() -> None:
    o = Order("A1")
    for step in ("paid", Status.SHIPPED, "delivered"):
        o.advance(step)
    print("trail:", [s.value for s in o.trail], "| terminal:", not TRANSITIONS[o.status])
    for bad in ("cancelled", "refunded"):
        try:
            o.advance(bad)
        except InvalidTransition as exc:
            print("InvalidTransition:", exc)
        except ValueError as exc:
            print("ValueError:", exc)
    print("rung 1 accepts a typo:", naive_advance("pending", "payed"))
    print("by value:", Status("paid").name, "| by name:", Status["PAID"].value,
          "| identity:", Status("paid") is Status.PAID)
    print("members:", [m.name for m in Status])
    orders = [Order("b", Priority.LOW), Order("c", Priority.HIGH),
              Order("a", Priority.HIGH), Order("d")]
    print("sorted orders:", sort_orders(orders))
    print("IntEnum compares with int:", Priority.HIGH == 3, Priority.LOW < 2,
          "| Enum does not:", Status.PAID == "paid")
    rw = Perm.READ | Perm.WRITE
    print("values:", Perm.READ.value, Perm.WRITE.value, Perm.DELETE.value, "| rw =", rw.value)
    print("can rw READ:", can(rw, Perm.READ), "| can rw READ|DELETE:",
          can(rw, Perm.READ | Perm.DELETE), "| WRITE in rw:", Perm.WRITE in rw)


if __name__ == "__main__":
    main()
