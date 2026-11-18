"""
Exercise 08 — Dates, durations and time zones                  [Tier: ★ Core]
Chapter 26 · Pattern: aware datetimes, UTC internally · Target time: 25 min

Problem
-------
Using only ``datetime`` and ``zoneinfo`` (3.9+):

1. ``add_business_days(start, n)`` returns the date ``n`` business days (Mon–Fri) after ``start``.
2. ``format_duration(seconds)`` -> ``"1d 02h 03m 04s"`` (always all four fields).
3. ``to_utc(local_iso, utc_offset_hours)`` parses a naive ISO timestamp, attaches a *fixed* offset
   and returns the UTC ISO string.
4. ``minutes_between(a_iso, b_iso)`` parses two ISO strings that include offsets and returns the
   whole minutes from ``a`` to ``b`` (may be negative).
5. ``wall_clock_after(local_iso, tz_name, hours)`` adds ``hours`` of *elapsed* time to a local
   wall-clock time in a named zone and returns the new local ISO string — correct across DST.

Examples
--------
>>> add_business_days(date(2026, 1, 9), 1)       # Friday -> Monday
datetime.date(2026, 1, 12)
>>> format_duration(93784)
'1d 02h 03m 04s'
>>> to_utc("2026-07-01T09:00:00", -4)
'2026-07-01T13:00:00+00:00'

Constraints
-----------
- Never call ``datetime.now()`` in logic you want to test; pass times in.
- Named zones need a time-zone database. On Windows that comes from the ``tzdata`` PyPI package;
  if it is missing ``ZoneInfo`` raises ``ZoneInfoNotFoundError`` — the demo guards for this.

Approach ladder
---------------
1. Brute force — do arithmetic on naive local datetimes: silently wrong across DST changes.
2. Improved   — fixed UTC offsets: correct for one instant, wrong for future dates in zones with DST.
3. Optimal    — store and compute in UTC; convert to a named ``ZoneInfo`` only for display; for
   "add N hours of elapsed time" convert to UTC, add, convert back.

Hints
-----
- ``date.weekday()``: Monday is 0, Sunday is 6.
- ``divmod`` peels off days, hours, minutes.
- ``datetime + timedelta`` on an *aware* datetime with a ZoneInfo keeps the wall-clock fields
  (it does "calendar" arithmetic); go through UTC for elapsed-time arithmetic.

Follow-ups
----------
- ``time.time()`` vs ``time.monotonic()`` vs ``time.perf_counter()``: which to use for measuring a
  duration? (``perf_counter``/``monotonic`` — they never jump backwards.)
- How do you represent "every day at 09:00 local time"? (Store the wall time + zone name, not UTC.)
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # Python < 3.9
    ZoneInfo = None
    ZoneInfoNotFoundError = Exception


def add_business_days(start: date, n: int) -> date:
    current = start
    remaining = n
    while remaining > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current


def format_duration(seconds: int) -> str:
    days, rem = divmod(int(seconds), 86_400)
    hours, rem = divmod(rem, 3_600)
    minutes, secs = divmod(rem, 60)
    return f"{days}d {hours:02d}h {minutes:02d}m {secs:02d}s"


def to_utc(local_iso: str, utc_offset_hours: float) -> str:
    naive = datetime.fromisoformat(local_iso)
    aware = naive.replace(tzinfo=timezone(timedelta(hours=utc_offset_hours)))
    return aware.astimezone(timezone.utc).isoformat()


def minutes_between(a_iso: str, b_iso: str) -> int:
    a = datetime.fromisoformat(a_iso)
    b = datetime.fromisoformat(b_iso)
    if a.tzinfo is None or b.tzinfo is None:
        raise ValueError("both timestamps need an offset")
    return int((b - a).total_seconds() // 60)


def wall_clock_after(local_iso: str, tz_name: str, hours: float) -> str:
    tz = ZoneInfo(tz_name)
    local = datetime.fromisoformat(local_iso).replace(tzinfo=tz)
    later_utc = local.astimezone(timezone.utc) + timedelta(hours=hours)
    return later_utc.astimezone(tz).isoformat()


def main() -> None:
    print("== add_business_days ==")
    for start, n in [(date(2026, 1, 9), 1), (date(2026, 1, 9), 5), (date(2026, 1, 10), 0)]:
        end = add_business_days(start, n)
        print(f"{start} ({start:%a}) + {n} -> {end} ({end:%a})")

    print("\n== format_duration ==")
    for s in [0, 59, 3_600, 93_784]:
        print(f"{s:>6} s -> {format_duration(s)}")

    print("\n== fixed offsets ==")
    print("to_utc 09:00 at UTC-4  ->", to_utc("2026-07-01T09:00:00", -4))
    print("to_utc 09:00 at UTC+5.5->", to_utc("2026-07-01T09:00:00", 5.5))
    print("minutes_between        ->",
          minutes_between("2026-07-01T09:00:00+02:00", "2026-07-01T09:30:00+00:00"))
    try:
        minutes_between("2026-07-01T09:00:00", "2026-07-01T10:00:00+00:00")
    except ValueError as exc:
        print("naive input            -> ValueError:", exc)

    print("\n== naive vs aware ==")
    naive = datetime(2026, 1, 1, 12, 0)
    aware = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    try:
        naive < aware
    except TypeError as exc:
        print("compare naive/aware -> TypeError:", exc)
    print("strftime:", aware.strftime("%Y-%m-%d %H:%M %Z"), "| isoformat:", aware.isoformat())
    print("strptime:", datetime.strptime("05/01/2026 14:30", "%d/%m/%Y %H:%M"))

    print("\n== named zones across DST (US spring-forward 2026-03-08) ==")
    try:
        start = "2026-03-08T01:30:00"
        print("naive +1h wall clock :", (datetime.fromisoformat(start) + timedelta(hours=1)).time(),
              "(02:30 does not exist in New York that day)")
        print("elapsed +1h correctly:", wall_clock_after(start, "America/New_York", 1))
        print("Kolkata (no DST)     :", wall_clock_after(start, "Asia/Kolkata", 1))
    except ZoneInfoNotFoundError:
        print("time-zone database not installed; run 'pip install tzdata' to see this demo")


if __name__ == "__main__":
    main()
