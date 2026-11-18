"""
Exercise 10 — Generators that Receive Values: send, return, yield from   [Tier: ◆ Extended]
Chapter 23 · Pattern: generator-based coroutine · Target time: 20 min

Problem
-------
1. ``running_average()`` is a generator you drive with ``send(x)``; each send returns the average
   of all values sent so far. Sending ``None`` stops it, and the generator *returns* a summary
   dict ``{"count": n, "average": avg}``.
2. ``collect_summaries(groups)`` takes ``{name: [values]}`` and returns ``{name: summary}`` by
   delegating each group to ``running_average`` through ``yield from`` in a helper generator,
   capturing the return value.
3. ``primed(genfunc)`` is a decorator that advances a new generator to its first ``yield`` so
   callers can ``send`` immediately.

Examples
--------
>>> avg = primed(running_average)()
>>> avg.send(10), avg.send(20), avg.send(30)
(10.0, 15.0, 20.0)

Constraints
-----------
- Averages are rounded to 2 decimals.

Hints
-----
- ``value = yield result`` both produces ``result`` and receives the next ``send``.
- A generator's ``return x`` becomes ``StopIteration.value``; ``yield from`` hands it back as the
  value of the ``yield from`` expression.
- You must call ``next(gen)`` (or ``gen.send(None)``) once before the first real ``send``.

Approach ladder
---------------
1. A class with ``add()`` and ``average`` — perfectly fine and often clearer in production.
2. A generator coroutine — state lives in local variables; shows you understand the protocol
   (``send``, ``throw``, ``close``, return values) that ``asyncio`` grew out of.

Follow-ups
----------
- What does ``gen.close()`` do? (raises ``GeneratorExit`` at the paused ``yield``)
- How did generator coroutines evolve into ``async``/``await``? (see Chapter 28)
"""
from __future__ import annotations

import functools
from typing import Callable, Generator


def primed(genfunc: Callable) -> Callable:
    @functools.wraps(genfunc)
    def wrapper(*args, **kwargs):
        gen = genfunc(*args, **kwargs)
        next(gen)  # advance to the first yield
        return gen
    return wrapper


def running_average() -> Generator[float | None, float | None, dict]:
    total = 0.0
    count = 0
    average = None
    while True:
        value = yield average
        if value is None:
            break
        total += value
        count += 1
        average = round(total / count, 2)
    return {"count": count, "average": average}


def _summarise(results: dict, name: str):
    """Delegating generator: forwards every send to running_average, keeps its return value."""
    results[name] = yield from running_average()


def collect_summaries(groups: dict[str, list[float]]) -> dict[str, dict]:
    results: dict[str, dict] = {}
    for name, values in groups.items():
        gen = _summarise(results, name)
        next(gen)
        for v in values:
            gen.send(v)
        try:
            gen.send(None)  # tell the inner generator to finish
        except StopIteration:
            pass
    return results


def main() -> None:
    avg = primed(running_average)()
    print("sends:", [avg.send(x) for x in (10, 20, 30, 40)])
    try:
        avg.send(None)
    except StopIteration as stop:
        print("returned via StopIteration.value:", stop.value)

    raw = running_average()
    try:
        raw.send(5)
    except TypeError as exc:
        print("unprimed send -> TypeError:", exc)

    print("summaries:", collect_summaries({"latency": [12, 35, 9], "size": [100, 300]}))

    g = primed(running_average)()
    g.send(1)
    g.close()
    print("closed generator state:", g.gi_frame is None)


if __name__ == "__main__":
    main()
