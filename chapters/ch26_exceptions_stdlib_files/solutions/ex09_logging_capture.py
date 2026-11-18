"""
Exercise 09 — Logging you can test                             [Tier: ★ Core]
Chapter 26 · Pattern: named loggers, handlers, formatters · Target time: 20 min

Problem
-------
1. ``make_logger(name, stream, level)`` returns a logger that writes to ``stream`` (any file-like
   object, e.g. ``io.StringIO``) with the format ``LEVEL:name:message``, does *not* propagate to
   the root logger, and does not add duplicate handlers if called twice with the same name.
2. ``ShortExceptionFormatter`` renders ``logger.exception(...)`` records with a single extra line
   ``  ! <ExcType>: <message>`` instead of a full traceback (tracebacks contain absolute paths).
3. ``process(items, logger)`` logs ``DEBUG`` per item, ``WARNING`` for negative items (skipped) and
   ``logger.exception`` when an item is zero (division fails); it returns the sum of ``1/item`` of
   the good items rounded to 4 places.

Examples
--------
>>> buf = io.StringIO(); log = make_logger("demo", buf, logging.INFO)
>>> log.info("hello %s", "world"); buf.getvalue()
'INFO:demo:hello world\\n'

Constraints
-----------
- Use lazy %-style arguments (``log.debug("x=%s", x)``) not f-strings, so disabled levels cost
  almost nothing.
- Libraries must not call ``logging.basicConfig()``.

Approach ladder
---------------
1. Brute force — ``print()`` everywhere; no levels, no routing, impossible to silence.
2. Improved   — ``logging.basicConfig`` + root logger; fine for scripts, but libraries then fight over
   global configuration.
3. Optimal    — ``logging.getLogger(__name__)`` in code; handlers/formatters configured once by the
   application (or a test) at the edge.

Hints
-----
- A logger has a level *and* each handler has a level; a record must pass both.
- ``logging.Formatter.formatException(exc_info)`` controls how tracebacks are rendered.
- Child loggers (``"app.db"``) propagate records to ancestors' handlers (``"app"``).

Follow-ups
----------
- How do you add a request id to every line? (``LoggerAdapter`` or a ``logging.Filter``.)
- Structured (JSON) logging — when and why?
"""
from __future__ import annotations

import io
import logging

FORMAT = "%(levelname)s:%(name)s:%(message)s"


class ShortExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info) -> str:
        exc_type, exc, _tb = exc_info
        return f"  ! {exc_type.__name__}: {exc}"


def make_logger(name: str, stream, level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    for handler in list(logger.handlers):      # idempotent: replace, never duplicate
        logger.removeHandler(handler)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(ShortExceptionFormatter(FORMAT))
    logger.addHandler(handler)
    return logger


def process(items: list[float], logger: logging.Logger) -> float:
    total = 0.0
    for item in items:
        logger.debug("processing %s", item)
        if item < 0:
            logger.warning("skipping negative item %s", item)
            continue
        try:
            total += 1 / item
        except ZeroDivisionError:
            logger.exception("cannot invert item %s", item)
    return round(total, 4)


def main() -> None:
    print("== levels: INFO logger hides DEBUG ==")
    buf = io.StringIO()
    log = make_logger("orders", buf, logging.INFO)
    result = process([2, -1, 0, 4], log)
    print(buf.getvalue(), end="")
    print("result:", result)

    print("\n== same name, DEBUG level, called twice (no duplicates) ==")
    buf = io.StringIO()
    make_logger("orders", buf, logging.DEBUG)
    log = make_logger("orders", buf, logging.DEBUG)
    print("handlers attached:", len(log.handlers))
    process([5], log)
    print(buf.getvalue(), end="")

    print("\n== hierarchy: app.db propagates to app ==")
    buf = io.StringIO()
    make_logger("app", buf, logging.DEBUG)
    child = logging.getLogger("app.db")
    child.info("connected to %s", "primary")
    child.debug("pool size %d", 5)
    print("child has own handlers:", bool(child.handlers))
    print("effective level of child:", logging.getLevelName(child.getEffectiveLevel()))
    print(buf.getvalue(), end="")

    print("\n== handler level filters independently ==")
    buf = io.StringIO()
    log = make_logger("audit", buf, logging.DEBUG)
    log.handlers[0].setLevel(logging.ERROR)
    log.warning("not shown")
    log.error("shown")
    print(buf.getvalue(), end="")

    print("\n== lazy formatting: argument object is never formatted when disabled ==")

    class Expensive:
        calls = 0

        def __str__(self) -> str:
            Expensive.calls += 1
            return "expensive"

    log = make_logger("lazy", io.StringIO(), logging.INFO)
    log.debug("value %s", Expensive())
    print("__str__ calls with %-style:", Expensive.calls)
    log.debug(f"value {Expensive()}")
    print("__str__ calls with f-string:", Expensive.calls)


if __name__ == "__main__":
    main()
