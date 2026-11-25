"""
Exercise 02 — Money: a Hashable, Ordered Value Type  [Tier: ★ Core]
Chapter 24 · Pattern: dunder methods, eq/hash contract, NotImplemented · Target time: 25 min

Problem
-------
Write an immutable value class `Money(cents, currency)` (`cents` an int, `currency` a
3-letter upper-case code, else `ValueError`) that behaves like a built-in number:

- `repr` -> `Money(1234, 'USD')`; `str` -> `USD 12.34` (negative: `USD -0.05`).
- `==` compares value (cents AND currency); comparing with a non-Money returns False
  rather than raising. Equal objects must hash equally, so Money works in sets/dict keys.
- `<, <=, >, >=` order amounts of the SAME currency; mixing currencies raises `TypeError`.
- `a + b`, `a - b` (same currency, else `TypeError`), `-a`, `a * n` and `n * a` for an
  int n. `sum(list_of_money)` must work (it starts from the int 0).
- `bool(m)` is False only for zero cents.
- `allocate(ratios)` splits the amount by integer ratios WITHOUT losing a cent: the
  parts sum exactly to the original, and leftover cents go to the earliest parts.

Examples
--------
>>> Money(1000, "USD").allocate([1, 1, 1])
[Money(334, 'USD'), Money(333, 'USD'), Money(333, 'USD')]
>>> len({Money(5, "EUR"), Money(5, "EUR")})
1

Constraints
-----------
- All operators O(1); `allocate` O(k) for k ratios (ratios are >= 0 with a positive sum).

Hints
-----
- Return `NotImplemented` (not `False`, not raise) from a binary dunder when the other
  operand is a type you do not understand; Python then tries the reflected method.
- Hash exactly the fields that `__eq__` compares: `hash((self._cents, self._currency))`.
- For `allocate`, give each part `amount * r // total`, then hand out the remainder one
  cent at a time from the front.

Follow-ups
----------
- Why make it immutable? A hash that changes after insertion strands the key in a dict.
- Rewrite it as `@dataclass(frozen=True, order=True)` — what do you lose? (ordering would
  then compare currencies alphabetically instead of raising.)
- Add currency conversion with a rate table: keep it OUT of the value class (→ §24.4).
"""
from __future__ import annotations

from functools import total_ordering


@total_ordering                     # derives <=, >, >= from __eq__ and __lt__ (→ §25.7)
class Money:
    __slots__ = ("_cents", "_currency")

    def __init__(self, cents: int, currency: str) -> None:
        raise NotImplementedError("TODO")

    @property
    def cents(self) -> int:
        raise NotImplementedError("TODO")

    @property
    def currency(self) -> str:
        raise NotImplementedError("TODO")

    def __repr__(self) -> str:
        raise NotImplementedError("TODO")

    def __str__(self) -> str:
        raise NotImplementedError("TODO")

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("TODO")

    def __hash__(self) -> int:
        raise NotImplementedError("TODO")

    def _check(self, other: Money) -> None:
        raise NotImplementedError("TODO")

    def __lt__(self, other: object) -> bool:
        raise NotImplementedError("TODO")

    def __add__(self, other: object) -> Money:
        raise NotImplementedError("TODO")

    def __radd__(self, other: object) -> Money:
        raise NotImplementedError("TODO")

    def __sub__(self, other: object) -> Money:
        raise NotImplementedError("TODO")

    def __neg__(self) -> Money:
        raise NotImplementedError("TODO")

    def __mul__(self, n: object) -> Money:
        raise NotImplementedError("TODO")

    __rmul__ = __mul__                    # 3 * m works too

    def __bool__(self) -> bool:
        raise NotImplementedError("TODO")

    def allocate(self, ratios: list[int]) -> list[Money]:
        raise NotImplementedError("TODO")


class EqOnlyMoney:
    """Rung 2: defines __eq__ but not __hash__, so Python sets __hash__ = None."""

    def __init__(self, cents: int, currency: str) -> None:
        raise NotImplementedError("TODO")

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("TODO")


def main() -> None:
    a, b = Money(1999, "USD"), Money(1, "USD")
    print(repr(a), "|", str(a), "|", str(Money(-5, "USD")))
    print("a + b =", a + b, "| a - b =", a - b, "| 3 * b =", 3 * b, "| -b =", -b)
    print("sum:", sum([a, b, Money(100, "USD")]))
    print("a > b:", a > b, "| a <= a:", a <= a, "| sorted:", sorted([a, b, Money(500, "USD")]))
    print("set dedupes:", len({Money(5, "EUR"), Money(5, "EUR"), Money(5, "USD")}))
    print("a == 1999:", a == 1999, "| bool(Money(0,'USD')):", bool(Money(0, "USD")))
    print("allocate 10.00 by [1,1,1]:", Money(1000, "USD").allocate([1, 1, 1]))
    print("allocate 0.05 by [3,7]:", Money(5, "USD").allocate([3, 7]))
    for expr in (lambda: a + Money(1, "EUR"), lambda: a < Money(1, "EUR"), lambda: a + 1):
        try:
            expr()
        except TypeError as exc:
            print("TypeError:", exc)
    print("float tuple rung: (0.1 + 0.2) == 0.3 ->", ("USD", 0.1 + 0.2) == ("USD", 0.3))
    print("EqOnlyMoney.__hash__ is None:", EqOnlyMoney.__hash__ is None)
    try:
        {EqOnlyMoney(5, "USD")}
    except TypeError as exc:
        print("TypeError:", exc)


if __name__ == "__main__":
    main()
