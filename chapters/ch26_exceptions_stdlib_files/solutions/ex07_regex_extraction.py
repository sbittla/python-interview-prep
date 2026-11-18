r"""
Exercise 07 — Regex extraction from logs                       [Tier: ★ Core]
Chapter 26 · Pattern: compiled patterns + named groups · Target time: 25 min

Problem
-------
``data/app.log`` holds lines such as::

    2026-01-05 09:16:44 ERROR [db] query timeout after 3000ms request_id=REQ-48213

Write:

1. ``parse_line(line)`` -> dict with keys ``date, time, level, component, message`` or ``None``
   for lines that do not match.
2. ``extract_emails(text)`` -> sorted unique e-mail addresses (simple practical pattern).
3. ``durations_ms(lines)`` -> list of all integers written as ``<n>ms``, in order of appearance.
4. ``mask_request_ids(text)`` replaces ``REQ-48213`` with ``REQ-***13`` (keep the last two digits)
   using ``re.sub`` with a function.
5. ``level_counts(lines)`` -> ``{level: count}`` sorted by level for parseable lines.

Examples
--------
>>> parse_line("2026-01-05 09:15:02 INFO  [auth] login ok")["component"]
'auth'
>>> mask_request_ids("id=REQ-48213")
'id=REQ-***13'
>>> extract_emails("a@x.io, b@y.org; a@x.io")
['a@x.io', 'b@y.org']

Constraints
-----------
- Compile patterns once at module level.
- Use raw strings for regex literals.

Approach ladder
---------------
1. Brute force — ``line.split()`` and index positions: breaks when the message has spaces or the
   level is padded.
2. Improved   — one regex with positional groups (``m.group(3)``) — works but unreadable.
3. Optimal    — anchored, compiled pattern with *named* groups (``(?P<level>...)``) and
   ``fullmatch``/``match``; ``finditer`` for repeated tokens; ``sub`` with a callable for rewriting.

Hints
-----
- ``re.match`` anchors at the start only; ``re.fullmatch`` anchors both ends; ``re.search`` scans.
- ``\s+`` absorbs the variable padding after the level.
- ``.*`` is greedy; ``.*?`` is lazy — compare them on ``<b>x</b><b>y</b>``.

Follow-ups
----------
- Why can a careless pattern like ``(a+)+$`` hang? (Catastrophic backtracking.)
- When should you *not* use regex? (Real e-mail validation, HTML, nested structures.)
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "app.log"

LINE_RE = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})\s"
    r"(?P<time>\d{2}:\d{2}:\d{2})\s"
    r"(?P<level>[A-Z]+)\s+"
    r"\[(?P<component>\w+)\]\s"
    r"(?P<message>.*)"
)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
DURATION_RE = re.compile(r"\b(\d+)ms\b")
REQ_RE = re.compile(r"REQ-(\d+)")


def parse_line(line: str) -> dict | None:
    m = LINE_RE.fullmatch(line.rstrip("\n"))
    return m.groupdict() if m else None


def extract_emails(text: str) -> list[str]:
    return sorted(set(EMAIL_RE.findall(text)))


def durations_ms(lines: list[str]) -> list[int]:
    return [int(m.group(1)) for line in lines for m in DURATION_RE.finditer(line)]


def mask_request_ids(text: str) -> str:
    def repl(m: re.Match) -> str:
        digits = m.group(1)
        return "REQ-" + "*" * (len(digits) - 2) + digits[-2:]
    return REQ_RE.sub(repl, text)


def level_counts(lines: list[str]) -> dict[str, int]:
    counts = Counter(p["level"] for p in map(parse_line, lines) if p)
    return dict(sorted(counts.items()))


def main() -> None:
    lines = DATA.read_text(encoding="utf-8").splitlines()
    print("== parse_line ==")
    for line in lines[:3] + [lines[5]]:
        print(parse_line(line))

    print("\n== level_counts ==", level_counts(lines))
    print("== emails ==", extract_emails("\n".join(lines)))
    print("== durations_ms ==", durations_ms(lines))
    print("== errors, masked ==")
    for line in lines:
        parsed = parse_line(line)
        if parsed and parsed["level"] == "ERROR":
            print("  " + mask_request_ids(parsed["message"]))

    print("\n== greedy vs lazy ==")
    html = "<b>x</b><b>y</b>"
    print("greedy <b>.*</b> :", re.findall(r"<b>.*</b>", html))
    print("lazy   <b>.*?</b>:", re.findall(r"<b>.*?</b>", html))

    print("\n== match vs search vs fullmatch ==")
    s = "id=42"
    print("match(r'\\d+')    :", re.match(r"\d+", s))
    print("search(r'\\d+')   :", re.search(r"\d+", s).group())
    print("fullmatch(r'\\d+'):", re.fullmatch(r"\d+", "42").group())

    print("\n== split with a pattern ==")
    print(re.split(r"[,;]\s*", "a, b;c ,d"))


if __name__ == "__main__":
    main()
