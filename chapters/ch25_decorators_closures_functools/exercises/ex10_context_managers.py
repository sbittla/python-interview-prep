"""
Exercise 10 — Context Managers: Transaction, temp_attr, Suppress        [Tier: ★ Core]
Chapter 25 · Pattern: setup/teardown with __enter__/__exit__ · Target time: 25 min

Problem
-------
1. `Transaction(store)` — a class-based context manager over a dict. Inside the
   `with` block the caller edits `store` freely (`as` gives the store). On a
   clean exit the edits stay; if the block raises, `store` is restored to its
   exact contents at entry and the exception propagates.
2. `transaction(store)` — the same behaviour with `contextlib.contextmanager`.
3. `temp_attr(obj, name, value)` — a @contextmanager that sets an attribute for
   the duration of the block and restores the old value afterwards (deleting it
   if it did not exist on the instance, so a class attribute is not shadowed),
   even when the block raises. `temp_attr_buggy` shows the
   classic mistake: no try/finally around the yield.
4. `Suppress(*exc_types)` — a re-implementation of contextlib.suppress: swallow
   the listed exception types (and subclasses); let others propagate.

Examples
--------
>>> store = {"a": 1}
>>> with Transaction(store) as s:
...     s["b"] = 2
>>> store
{'a': 1, 'b': 2}

Constraints
-----------
- Values in the store are treated as immutable (the snapshot is shallow).

Hints
-----
- `__exit__` returning a truthy value SUPPRESSES the exception. Return False
  (or None) unless suppression is the whole point (Suppress).
- `issubclass(exc_type, self.exc_types)` accepts a tuple.
- Restore in place (`store.clear(); store.update(snapshot)`): other references
  to the same dict must see the rollback. Shallow vs deep copy is §7.2.

Follow-ups
----------
- Nested transactions (savepoints): a stack of snapshots.
- Many managers at once: contextlib.ExitStack.
- Make Transaction usable as a decorator: contextlib.ContextDecorator.
"""
from __future__ import annotations

from contextlib import contextmanager


class Transaction:
    def __init__(self, store: dict) -> None:
        raise NotImplementedError("TODO")

    def __enter__(self) -> dict:
        raise NotImplementedError("TODO")

    def __exit__(self, exc_type, exc, tb) -> bool:
        raise NotImplementedError("TODO")


@contextmanager
def transaction(store: dict):
    raise NotImplementedError("TODO")


_MISSING = object()


@contextmanager
def temp_attr(obj: object, name: str, value: object):
    raise NotImplementedError("TODO")


@contextmanager
def temp_attr_buggy(obj: object, name: str, value: object):
    old = getattr(obj, name)
    setattr(obj, name, value)
    yield obj                       # BUG: no try/finally, so on error the next
    setattr(obj, name, old)         # line never runs and the value leaks


class Suppress:
    def __init__(self, *exc_types: type[BaseException]) -> None:
        raise NotImplementedError("TODO")

    def __enter__(self) -> None:
        raise NotImplementedError("TODO")

    def __exit__(self, exc_type, exc, tb) -> bool:
        raise NotImplementedError("TODO")


def _transfer(store: dict, manager) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    for manager in (Transaction, transaction):
        store = {"alice": 50, "bob": 0}
        first = _transfer(store, manager)
        second = _transfer(store, manager)
        print(f"{manager.__name__:17} {first} | {second} -> {store}")

    class Config:
        debug = False

    for helper in (temp_attr, temp_attr_buggy):
        cfg = Config()
        try:
            with helper(cfg, "debug", True):
                inside = cfg.debug
                raise RuntimeError("boom")
        except RuntimeError:
            pass
        print(f"{helper.__name__:15} inside={inside} after error={cfg.debug}")

    with Suppress(KeyError, IndexError):
        [][1]
    print("IndexError suppressed")
    try:
        with Suppress(KeyError):
            int("x")
    except ValueError as exc:
        print("ValueError propagates:", exc)


if __name__ == "__main__":
    main()
