"""
Exercise 08 — Pluggable Storage: Abstract Base Classes and Protocols  [Tier: ★ Core]
Chapter 24 · Pattern: ABC contract + template methods, structural Protocol · Target time: 25 min

Problem
-------
1. `Storage` is an ABC with three abstract methods — `get(key) -> str | None`,
   `put(key, value)`, `keys() -> list[str]` — and two CONCRETE template methods built only
   on them: `put_many(pairs) -> int` (returns how many pairs were written) and
   `snapshot() -> dict` (all pairs, keys sorted).
2. `MemoryStorage(Storage)` keeps a dict. `LogStorage(Storage)` keeps an append-only list
   of `(key, value)` writes; `get` returns the LATEST value for a key and `keys()` the
   distinct keys sorted.
3. A subclass that forgets an abstract method cannot be instantiated (`TypeError`).
4. `migrate(src, dst) -> int` copies every pair from any Storage to any other.
5. `Closeable` is a `@runtime_checkable` `Protocol` with `close() -> None`.
   `close_all(objects)` calls `close()` on each object that has one (no inheritance
   required) and returns how many it closed.

Examples
--------
>>> m = MemoryStorage(); m.put_many([("b", "2"), ("a", "1")]); m.snapshot()
2
{'a': '1', 'b': '2'}

Constraints
-----------
- MemoryStorage: O(1) get/put. LogStorage: O(1) put, O(n) get (it scans the log).

Approach ladder
---------------
1. Brute force — pure duck typing, no declared contract: O(1) to write, but a backend
   missing `keys` fails only when `snapshot()` finally calls it, maybe in production.
2. Improved   — a base class whose methods `raise NotImplementedError` (`NaiveBase`):
   documents the contract, but an incomplete subclass still instantiates and fails late.
3. Optimal    — `abc.ABC` + `@abstractmethod`: the incomplete subclass fails at
   construction time; shared logic lives once in template methods. Use a `Protocol`
   when you cannot (or should not) make implementers inherit from you. Checking costs
   O(1) per call; the abstract-method set is computed once at class creation.

Hints
-----
- `isinstance(x, SomeProtocol)` needs `@runtime_checkable` and only checks that the
  attribute EXISTS — not its signature or return type.
- `Storage.register(cls)` makes `isinstance` true without checking any method: a
  promise, not a proof.

Follow-ups
----------
- `collections.abc.Sized` recognises any class with `__len__` via `__subclasshook__`;
  which other `collections.abc` classes do that? (`Iterable`, `Container`, `Hashable`, ...)
- ABC or Protocol for a plugin API that third parties implement? (Protocol: no import
  dependency on your package.)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sized
from typing import Protocol, runtime_checkable


class Storage(ABC):
    @abstractmethod
    def get(self, key: str) -> str | None: ...

    @abstractmethod
    def put(self, key: str, value: str) -> None: ...

    @abstractmethod
    def keys(self) -> list[str]: ...

    def put_many(self, pairs: Iterable[tuple[str, str]]) -> int:   # template method
        n = 0
        for k, v in pairs:
            self.put(k, v)
            n += 1
        return n

    def snapshot(self) -> dict[str, str]:
        return {k: self.get(k) for k in sorted(self.keys())}


class MemoryStorage(Storage):
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def put(self, key: str, value: str) -> None:
        self._data[key] = value

    def keys(self) -> list[str]:
        return list(self._data)


class LogStorage(Storage):
    def __init__(self) -> None:
        self._log: list[tuple[str, str]] = []

    def get(self, key: str) -> str | None:
        for k, v in reversed(self._log):        # latest write wins
            if k == key:
                return v
        return None

    def put(self, key: str, value: str) -> None:
        self._log.append((key, value))

    def keys(self) -> list[str]:
        return sorted({k for k, _ in self._log})


class NaiveBase:
    """Rung 2: a contract that is only enforced when the method is finally called."""

    def get(self, key: str) -> str | None:
        raise NotImplementedError

    def keys(self) -> list[str]:
        raise NotImplementedError


def migrate(src: Storage, dst: Storage) -> int:
    return dst.put_many(src.snapshot().items())


@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...


def close_all(objects: Iterable[object]) -> int:
    closed = 0
    for obj in objects:
        if isinstance(obj, Closeable):           # structural: no inheritance needed
            obj.close()
            closed += 1
    return closed


class Connection:                                # never mentions Closeable
    def __init__(self) -> None:
        self.open = True

    def close(self) -> None:
        self.open = False


def main() -> None:
    mem, log = MemoryStorage(), LogStorage()
    print("put_many:", mem.put_many([("b", "2"), ("a", "1")]), "| snapshot:", mem.snapshot())
    log.put_many([("x", "old"), ("y", "1"), ("x", "new")])
    print("log get x:", log.get("x"), "| keys:", log.keys(), "| missing:", log.get("zz"))
    print("migrate log -> mem:", migrate(log, mem), "->", mem.snapshot())

    class Partial(Storage):                      # forgot keys()
        def get(self, key: str) -> str | None:
            return None

        def put(self, key: str, value: str) -> None:
            pass

    try:
        Partial()
    except TypeError as exc:
        print("TypeError at construction; abstract left:", sorted(Partial.__abstractmethods__),
              "| mentions keys:", "keys" in str(exc))
    print("NaiveBase() constructs fine:", type(NaiveBase()).__name__, "(fails later)")
    try:
        Storage()
    except TypeError:
        print("Storage() itself -> TypeError")

    conn, other = Connection(), Connection()
    print("closed:", close_all([conn, mem, "text", other]), "| conn.open:", conn.open)
    print("isinstance(mem, Closeable):", isinstance(mem, Closeable))

    class Box:
        def __len__(self) -> int:
            return 3

    print("Box is Sized without inheriting:", isinstance(Box(), Sized))

    class Fake:
        pass

    Storage.register(Fake)
    print("registered Fake isinstance Storage:", isinstance(Fake(), Storage),
          "| has get:", hasattr(Fake(), "get"))


if __name__ == "__main__":
    main()
