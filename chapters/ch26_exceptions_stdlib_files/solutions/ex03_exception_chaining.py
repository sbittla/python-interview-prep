"""
Exercise 03 — Exception chaining: raise ... from ...           [Tier: ★ Core]
Chapter 26 · Pattern: wrap low-level errors in domain errors · Target time: 20 min

Problem
-------
Write ``load_config(text)`` that parses a JSON config string and returns a dict with an integer
``port`` in 1..65535 and a non-empty string ``host``. Every failure must surface as a
``ConfigError``:

- invalid JSON          -> ``ConfigError("config is not valid JSON")`` chained *explicitly* to the
                           original ``json.JSONDecodeError`` (``raise ... from exc``)
- missing key           -> ``ConfigError("missing key: <name>")`` chained to the ``KeyError``
- bad port type/range   -> ``ConfigError("port must be an int in 1..65535")`` with the original
                           context *suppressed* (``from None``)

Then write ``describe_chain(exc)`` that walks ``__cause__`` / ``__context__`` and returns a list of
strings like ``"ConfigError: missing key: host"`` / ``"  caused by KeyError: 'host'"``, honouring
``__suppress_context__``. Finally ``implicit_context()`` must show *implicit* chaining: an error
raised inside an ``except`` block without ``from``.

Examples
--------
>>> load_config('{"host": "db", "port": 5432}')
{'host': 'db', 'port': 5432}
>>> try:
...     load_config('{"port": 1}')
... except ConfigError as e:
...     describe_chain(e)
['ConfigError: missing key: host', "  caused by KeyError: 'host'"]

Constraints
-----------
- Do not lose the original traceback information for genuine bugs.

Approach ladder
---------------
1. Brute force — ``except Exception: raise ConfigError("bad config")``: the caller loses *why*.
2. Improved   — put the original message into the new message; still loses type and traceback.
3. Optimal    — ``raise ConfigError(...) from exc`` keeps the full original exception on
   ``__cause__`` (and the traceback prints "The above exception was the direct cause...");
   use ``from None`` only when the inner error is pure noise.

Hints
-----
- ``exc.__cause__`` is set by ``from``; ``exc.__context__`` is set automatically when raising
  inside ``except``/``finally``; ``from X`` also sets ``__suppress_context__ = True``.
- ``json.JSONDecodeError`` is a subclass of ``ValueError``.

Follow-ups
----------
- When should a library re-raise unchanged (bare ``raise``) instead of wrapping?
- How does ``add_note()`` (3.11+) differ from chaining? (It annotates the *same* exception.)
"""
from __future__ import annotations

import json


class ConfigError(Exception):
    pass


def load_config(text: str) -> dict:
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConfigError("config is not valid JSON") from exc
    try:
        host = raw["host"]
        port = raw["port"]
    except KeyError as exc:
        raise ConfigError(f"missing key: {exc.args[0]}") from exc
    try:
        port_ok = isinstance(port, int) and not isinstance(port, bool) and 1 <= port <= 65535
        if not port_ok:
            raise ValueError(port)
    except ValueError:
        raise ConfigError("port must be an int in 1..65535") from None
    if not isinstance(host, str) or not host:
        raise ConfigError("host must be a non-empty string")
    return {"host": host, "port": port}


def describe_chain(exc: BaseException) -> list[str]:
    lines = [f"{type(exc).__name__}: {exc}"]
    current = exc
    while True:
        if current.__cause__ is not None:
            current, how = current.__cause__, "caused by"
        elif current.__context__ is not None and not current.__suppress_context__:
            current, how = current.__context__, "during handling of"
        else:
            break
        lines.append(f"  {how} {type(current).__name__}: {current}")
    return lines


def implicit_context() -> BaseException:
    """Return an exception whose __context__ was set implicitly."""
    try:
        try:
            {}["missing"]
        except KeyError:
            # a bug in the handler itself: no 'from', so Python links it via __context__
            raise RuntimeError("handler failed")
    except RuntimeError as err:
        return err


def main() -> None:
    samples = [
        '{"host": "db", "port": 5432}',
        '{"host": "db", "port": 5432',
        '{"port": 8080}',
        '{"host": "db", "port": "80"}',
        '{"host": "db", "port": 70000}',
    ]
    for text in samples:
        print(f"input: {text}")
        try:
            print("  ok ->", load_config(text))
        except ConfigError as exc:
            for line in describe_chain(exc):
                print("  " + line)
            print(f"  __cause__ set: {exc.__cause__ is not None}, "
                  f"suppress_context: {exc.__suppress_context__}")

    print("\nimplicit chaining:")
    err = implicit_context()
    for line in describe_chain(err):
        print("  " + line)
    print("  __cause__ is None:", err.__cause__ is None)


if __name__ == "__main__":
    main()
