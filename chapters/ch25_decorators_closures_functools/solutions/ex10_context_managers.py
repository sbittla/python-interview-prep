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

Approach ladder
---------------
1. Brute force — snapshot/try/except/restore pasted around every edit: O(n)
   per use, duplicated, and easy to forget the restore on one path.
2. Class — __enter__ snapshots (O(n) copy for n keys), __exit__(exc_type, exc,
   tb) restores when exc_type is not None and returns False so the exception
   propagates. O(n) extra memory for the snapshot.
3. Generator — @contextmanager: code before `yield` is __enter__, after is
   __exit__. The yield MUST sit in try/except (or try/finally): an exception in
   the block is thrown into the generator at the yield, so code after an
   unguarded yield never runs. Why move up: less boilerplate for one-off managers.

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
        self.store = store

    def __enter__(self) -> dict:
        self.snapshot = dict(self.store)            # shallow copy, O(n)
        return self.store

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is not None:                    # the block raised: roll back
            self.store.clear()
            self.store.update(self.snapshot)
        return False                                # never swallow the error


@contextmanager
def transaction(store: dict):
    snapshot = dict(store)
    try:
        yield store
    except BaseException:
        store.clear()
        store.update(snapshot)
        raise


_MISSING = object()


@contextmanager
def temp_attr(obj: object, name: str, value: object):
    own = getattr(obj, "__dict__", None)
    # Restore only what the instance itself held; a class attribute is "missing" here,
    # so we delete our instance attribute instead of shadowing the class value.
    old = own.get(name, _MISSING) if own is not None else getattr(obj, name, _MISSING)
    setattr(obj, name, value)
    try:
        yield obj
    finally:
        if old is _MISSING:
            delattr(obj, name)
        else:
            setattr(obj, name, old)


@contextmanager
def temp_attr_buggy(obj: object, name: str, value: object):
    old = getattr(obj, name)
    setattr(obj, name, value)
    yield obj                       # BUG: no try/finally, so on error the next
    setattr(obj, name, old)         # line never runs and the value leaks


class Suppress:
    def __init__(self, *exc_types: type[BaseException]) -> None:
        self.exc_types = exc_types

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type, exc, tb) -> bool:
        return exc_type is not None and issubclass(exc_type, self.exc_types)


def _transfer(store: dict, manager) -> str:
    try:
        with manager(store) as s:
            s["alice"] -= 30
            s["bob"] += 30
            if s["alice"] < 0:
                raise ValueError("overdraft")
        return "committed"
    except ValueError as exc:
        return f"rolled back ({exc})"


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
