"""
Exercise 10 — pickle, its security hole, and shelve            [Tier: ○ Reference]
Chapter 26 · Pattern: serialisation trust boundaries · Target time: 20 min

Problem
-------
1. ``roundtrip(obj)`` pickles and unpickles ``obj`` and returns the copy.
2. ``Tracer`` is a class whose ``__reduce__`` tells pickle to call ``record_call("payload ran")``
   while *loading*. ``unsafe_load_runs_code()`` dumps a ``Tracer`` and loads it with plain
   ``pickle.loads``, returning the module-level ``CALLS`` list to prove that loading executed a
   function chosen by whoever produced the bytes. (The function is harmless — it only appends to
   a list — but an attacker would name ``os.system`` instead.)
3. ``RestrictedUnpickler`` allows only an explicit allow-list of globals; ``safe_loads(data)``
   uses it, so the ``Tracer`` payload raises ``pickle.UnpicklingError``.
4. ``shelve_demo(directory)`` stores two records in a ``shelve`` database inside ``directory``
   and returns the sorted keys and one value read back.

Examples
--------
>>> roundtrip({"a": [1, 2], "b": (3, 4)})
{'a': [1, 2], 'b': (3, 4)}

Constraints
-----------
- Never unpickle data from an untrusted source. The restricted unpickler reduces the risk; it is
  not a sandbox. Prefer JSON (or a schema'd format) across trust boundaries.
- Do not execute anything harmful — the demo only appends to a list.

Approach ladder
---------------
1. Brute force — ``pickle.loads(untrusted_bytes)``: arbitrary code execution.
2. Improved   — sign the bytes with ``hmac`` so only your own services' pickles are accepted.
3. Optimal    — use a data-only format (JSON, MessagePack, protobuf) at trust boundaries; keep pickle
   for same-process/same-trust caching (and multiprocessing, which uses it internally).

Hints
-----
- ``__reduce__`` returns ``(callable, args)``; pickle stores the callable *by name*.
- ``pickle.Unpickler.find_class(module, name)`` is the hook to override.
- ``shelve.open(path)`` behaves like a dict whose values are pickled; use it as a context manager.

Follow-ups
----------
- Why can pickle not serialise a lambda or an open file?
- What does ``protocol=pickle.HIGHEST_PROTOCOL`` change?
"""
from __future__ import annotations

import builtins
import pickle
import shelve
import tempfile
from dataclasses import dataclass
from pathlib import Path

CALLS: list[str] = []


def record_call(message: str) -> str:  # provided
    """Harmless stand-in for an attacker's callable (e.g. os.system)."""
    CALLS.append(message)
    return message


@dataclass
class Point:
    x: int
    y: int


class Tracer:
    def __reduce__(self):
        # On load, pickle will call record_call("payload ran") — chosen by the *producer* of the bytes.
        return (record_call, ("payload ran",))


def roundtrip(obj):
    return pickle.loads(pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL))


def unsafe_load_runs_code() -> list[str]:
    CALLS.clear()
    data = pickle.dumps(Tracer())
    result = pickle.loads(data)            # <- executes record_call during loading
    CALLS.append(f"loads returned {result!r}")
    return list(CALLS)


SAFE_BUILTINS = {"list", "dict", "set", "frozenset", "tuple", "str", "int", "float", "bool", "complex"}


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module: str, name: str):
        if module == "builtins" and name in SAFE_BUILTINS:
            return getattr(builtins, name)
        raise pickle.UnpicklingError(f"global '{module}.{name}' is forbidden")


def safe_loads(data: bytes):
    import io
    return RestrictedUnpickler(io.BytesIO(data)).load()


def shelve_demo(directory: Path) -> tuple[list[str], dict]:
    path = str(Path(directory) / "store")
    with shelve.open(path) as db:
        db["ada"] = {"lang": "python", "level": 3}
        db["grace"] = {"lang": "cobol", "level": 5}
    with shelve.open(path, flag="r") as db:
        return sorted(db.keys()), db["grace"]


def main() -> None:
    print("== roundtrip ==")
    for obj in [{"a": [1, 2], "b": (3, 4)}, Point(1, 2), {1, 2, 3}]:
        copy = roundtrip(obj)
        print(f"{copy!r:<28} equal: {copy == obj}  same object: {copy is obj}")
    try:
        pickle.dumps(lambda x: x)
    except (pickle.PicklingError, AttributeError) as exc:
        print("lambda cannot be pickled:", type(exc).__name__)

    print("\n== loading a pickle can run code ==")
    for line in unsafe_load_runs_code():
        print("  ", line)

    print("\n== restricted unpickler ==")
    print("plain data ok:", safe_loads(pickle.dumps({"k": [1, 2.5, "x"]})))
    try:
        safe_loads(pickle.dumps(Tracer()))
    except pickle.UnpicklingError as exc:
        print("blocked:", exc)

    print("\n== shelve ==")
    with tempfile.TemporaryDirectory() as tmp:
        keys, grace = shelve_demo(Path(tmp))
        print("keys:", keys, "| grace:", grace)


if __name__ == "__main__":
    main()
