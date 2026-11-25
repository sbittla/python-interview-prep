"""
Exercise 01 — Bank Account: State, Class Attributes and Properties  [Tier: ★ Core]
Chapter 24 · Pattern: class vs instance attributes, @property validation · Target time: 20 min

Problem
-------
Write a class `Account` that models a simple bank account.

- `Account(owner, balance=0)` — `owner` is stripped of surrounding spaces and must be
  non-empty; `balance` is an int number of cents and must be >= 0 (else `ValueError`).
- Every account gets a sequential `number` starting at 1001, shared across all accounts
  (a class-level counter). `Account.reset_numbers()` restarts the counter (for tests).
- `balance` is READ-ONLY from outside: `acct.balance = 5` raises `AttributeError`.
  Change it only through `deposit(cents)` and `withdraw(cents)`; both reject amounts <= 0,
  and `withdraw` rejects overdrafts (all with `ValueError`).
- `owner` is a read/write property; the setter applies the same validation as `__init__`.
- `history` is a PER-ACCOUNT list of `(kind, cents)` tuples, e.g. `("deposit", 500)`.
- `interest_rate` is a class attribute (0.02) that applies to every account unless an
  account overrides it; `add_interest()` deposits `round(balance * rate)` cents
  (skip the deposit when that rounds to 0).
- `repr(acct)` looks like `Account(number=1001, owner='Ada', balance=1500)`.

Examples
--------
>>> Account.reset_numbers(); a = Account(" Ada ", 1000); a.deposit(500); a
Account(number=1001, owner='Ada', balance=1500)
>>> a.history
[('open', 1000), ('deposit', 500)]

Constraints
-----------
- Every operation is O(1) (amortised for the history append).

Approach ladder
---------------
1. Brute force — a dict `{"owner": ..., "balance": ...}` plus free functions: O(1) per
   operation, but any caller can write `d["balance"] = -10**9`; nothing enforces invariants.
2. Improved   — a class with a public `balance` attribute: methods document intent, but the
   attribute is still writable and `history = []` as a CLASS attribute would be shared by
   every account (→ §7.4).
3. Optimal    — store state in `_balance`, expose a read-only `@property`, validate in one
   place (`_clean_owner`), create `history` inside `__init__`. Still O(1) per operation;
   the gain is that invalid states become unrepresentable.

Hints
-----
- A property with no setter raises `AttributeError` on assignment.
- `self.interest_rate` reads the instance first, then the class: assigning
  `acct.interest_rate = 0.05` creates an instance attribute that shadows the class one.
- Bump the counter through the class (`Account._next_number += 1`), not `self`, or you
  create a per-instance copy and every account gets the same number.

Follow-ups
----------
- Use `Decimal` or integer cents, never `float`, for money (→ §7.8).
- How would you make `Account` thread-safe? (a lock around balance changes, → Ch 28)
"""
from __future__ import annotations


class Account:
    interest_rate = 0.02          # class attribute: shared default
    _next_number = 1001           # class attribute: shared counter

    def __init__(self, owner: str, balance: int = 0) -> None:
        if balance < 0:
            raise ValueError("opening balance must be >= 0")
        self._owner = self._clean_owner(owner)
        self._balance = balance
        self.number = Account._next_number      # write through the class, not self
        Account._next_number += 1
        self.history: list[tuple[str, int]] = [("open", balance)]   # per instance

    @classmethod
    def reset_numbers(cls) -> None:
        cls._next_number = 1001

    @staticmethod
    def _clean_owner(owner: str) -> str:
        owner = owner.strip()
        if not owner:
            raise ValueError("owner must be non-empty")
        return owner

    @property
    def balance(self) -> int:                    # read-only: no setter
        return self._balance

    @property
    def owner(self) -> str:
        return self._owner

    @owner.setter
    def owner(self, value: str) -> None:
        self._owner = self._clean_owner(value)

    def deposit(self, cents: int) -> None:
        if cents <= 0:
            raise ValueError("deposit must be positive")
        self._balance += cents
        self.history.append(("deposit", cents))

    def withdraw(self, cents: int) -> None:
        if cents <= 0:
            raise ValueError("withdrawal must be positive")
        if cents > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= cents
        self.history.append(("withdraw", cents))

    def add_interest(self) -> int:
        earned = round(self._balance * self.interest_rate)   # instance first, then class
        if earned > 0:
            self.deposit(earned)
        return earned

    def __repr__(self) -> str:
        return (f"{type(self).__name__}(number={self.number}, "
                f"owner={self._owner!r}, balance={self._balance})")


def main() -> None:
    Account.reset_numbers()
    a = Account(" Ada ", 1000)
    b = Account("Grace")
    a.deposit(500)
    a.withdraw(200)
    print(a)
    print(b)
    print("history a:", a.history)
    print("history b:", b.history, "(separate lists:", a.history is not b.history, ")")
    try:
        a.balance = 10**9
    except AttributeError:
        print("a.balance = ... -> AttributeError (read-only property)")
    for bad in (lambda: a.withdraw(10**6), lambda: a.deposit(0), lambda: Account("   ")):
        try:
            bad()
        except ValueError as exc:
            print("ValueError:", exc)
    b.interest_rate = 0.10                       # shadows the class attribute for b only
    b.deposit(1000)
    print("interest a:", a.add_interest(), "| interest b:", b.add_interest())
    print("Account.interest_rate still", Account.interest_rate,
          "| 'interest_rate' in vars(b):", "interest_rate" in vars(b))
    a.owner = "Ada Lovelace"
    print(a)


if __name__ == "__main__":
    main()
