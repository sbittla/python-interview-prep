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

Approach ladder
---------------
1. Brute force — a `(currency, float)` tuple: hashable and ordered for free, O(1), but
   `0.1 + 0.2 != 0.3` breaks equality, and tuples happily compare USD with EUR.
2. Improved   — a class with `__eq__` only: correct equality, but defining `__eq__` sets
   `__hash__ = None`, so instances cannot go in a set (→ §7.7). Still O(1).
3. Optimal    — integer cents, `__eq__` + matching `__hash__` over the same fields,
   `__lt__` plus `functools.total_ordering` (→ §25.7) for the rest, arithmetic dunders
   that return `NotImplemented` for foreign types, `__radd__` for `sum`. O(1) per op.

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
        if not isinstance(cents, int) or isinstance(cents, bool):
            raise ValueError("cents must be an int")
        if not (len(currency) == 3 and currency.isalpha() and currency.isupper()):
            raise ValueError(f"bad currency code {currency!r}")
        self._cents = cents
        self._currency = currency

    @property
    def cents(self) -> int:
        return self._cents

    @property
    def currency(self) -> str:
        return self._currency

    def __repr__(self) -> str:
        return f"Money({self._cents}, {self._currency!r})"

    def __str__(self) -> str:
        sign = "-" if self._cents < 0 else ""
        whole, frac = divmod(abs(self._cents), 100)
        return f"{self._currency} {sign}{whole}.{frac:02d}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented         # lets Python try other.__eq__, then fall back
        return (self._cents, self._currency) == (other._cents, other._currency)

    def __hash__(self) -> int:
        return hash((self._cents, self._currency))   # same fields as __eq__

    def _check(self, other: Money) -> None:
        if self._currency != other._currency:
            raise TypeError(f"currency mismatch: {self._currency} vs {other._currency}")

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return self._cents < other._cents

    def __add__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money(self._cents + other._cents, self._currency)

    def __radd__(self, other: object) -> Money:
        if other == 0:                    # sum() starts from 0
            return self
        return NotImplemented

    def __sub__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return self + (-other)

    def __neg__(self) -> Money:
        return Money(-self._cents, self._currency)

    def __mul__(self, n: object) -> Money:
        if not isinstance(n, int) or isinstance(n, bool):
            return NotImplemented
        return Money(self._cents * n, self._currency)

    __rmul__ = __mul__                    # 3 * m works too

    def __bool__(self) -> bool:
        return self._cents != 0

    def allocate(self, ratios: list[int]) -> list[Money]:
        total = sum(ratios)
        if total <= 0 or any(r < 0 for r in ratios):
            raise ValueError("ratios must be >= 0 with a positive sum")
        shares = [self._cents * r // total for r in ratios]
        takers = [i for i, r in enumerate(ratios) if r > 0]
        for i in takers[: self._cents - sum(shares)]:   # leftover < len(takers)
            shares[i] += 1
        return [Money(s, self._currency) for s in shares]


class EqOnlyMoney:
    """Rung 2: defines __eq__ but not __hash__, so Python sets __hash__ = None."""

    def __init__(self, cents: int, currency: str) -> None:
        self.cents, self.currency = cents, currency

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EqOnlyMoney):
            return NotImplemented
        return (self.cents, self.currency) == (other.cents, other.currency)


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
