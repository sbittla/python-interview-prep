"""
Exercise 01 — Duration Parser with a pytest Suite         [Tier: ★ Core]
Chapter 31 · Pattern: pytest fixtures + parametrize · Target time: 25 min

Problem
-------
Write ``parse_duration(text)`` that turns a human duration such as ``"1h30m"`` or
``"2d 4h 5s"`` into a whole number of seconds, then write a pytest suite for it that uses
parametrisation (with readable ids), ``pytest.raises``, a plain fixture, a yield fixture with
teardown, and a parametrised fixture.

Rules: units are d (86400 s), h (3600 s), m (60 s), s (1 s). Each unit appears at most once
and in that descending order. Spaces between tokens are allowed. Anything else is a
``ValueError``; a non-string argument is a ``TypeError``.

Examples
--------
>>> parse_duration("1h30m")
5400
>>> parse_duration("2d 4h 5s")
187205
>>> parse_duration("90")
Traceback (most recent call last):
ValueError: bad token at position 0: '90'

Constraints
-----------
- Input length <= 100 characters; numbers are non-negative integers.

Approach ladder
---------------
1. Brute force — split on letters with str methods and many if-branches; easy to get wrong
   on "1h30" (number with no unit) and repeated units. O(n).
2. Improved   — one regex ``(\\d+)([dhms])`` with ``re.findall``; O(n) but silently skips junk
   between tokens ("1hXX30m" parses), which a good test suite catches.
3. Optimal    — anchored scanning with ``pattern.match(text, pos)`` so every character must
   be consumed, plus a rank check for unit order. O(n) time, O(1) extra space.

Follow-ups
----------
- Allow fractional values ("1.5h")? Then return a float or Decimal and say so in the API.
- Should "0s" be valid? (Yes here; a timeout API might reject it.)
- How would you add property-style tests? (See Exercise 03: format then parse round trip.)
"""
from __future__ import annotations

import re

import pytest

UNIT_SECONDS = {"d": 86_400, "h": 3_600, "m": 60, "s": 1}
UNIT_ORDER = "dhms"
_TOKEN = re.compile(r"\s*(\d+)\s*([dhms])\s*")


def parse_duration(text: str) -> int:
    if not isinstance(text, str):
        raise TypeError(f"expected str, got {type(text).__name__}")
    if not text.strip():
        raise ValueError("empty duration")
    pos, total, last_rank = 0, 0, -1
    while pos < len(text):
        match = _TOKEN.match(text, pos)
        if match is None:
            raise ValueError(f"bad token at position {pos}: {text[pos:]!r}")
        value, unit = int(match.group(1)), match.group(2)
        rank = UNIT_ORDER.index(unit)
        if rank <= last_rank:
            raise ValueError(f"unit {unit!r} repeated or out of order")
        last_rank = rank
        total += value * UNIT_SECONDS[unit]
        pos = match.end()
    return total


def solve(text: str) -> int:
    return parse_duration(text)


# --------------------------------------------------------------------------- embedded tests
# Real pytest tests. Run them with:  python -m pytest solutions/ex01_pytest_fixtures_parametrize.py

VALID_CASES = [
    pytest.param("45s", 45, id="seconds-only"),
    pytest.param("1h30m", 5_400, id="hours-minutes"),
    pytest.param("2d 4h 5s", 187_205, id="spaces-between-tokens"),
    pytest.param(" 0s ", 0, id="zero-with-padding"),
    pytest.param("1d1h1m1s", 90_061, id="all-units"),
]


@pytest.mark.parametrize("text, expected", VALID_CASES)
def test_valid_durations(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize(
    "bad, message",
    [
        ("", "empty"),
        ("   ", "empty"),
        ("90", "bad token"),
        ("1h30", "bad token"),
        ("5x", "bad token"),
        ("1m1h", "out of order"),
        ("1h1h", "repeated"),
    ],
    ids=["empty", "blank", "no-unit", "trailing-number", "unknown-unit", "wrong-order", "repeat"],
)
def test_invalid_input_raises_value_error(bad, message):
    with pytest.raises(ValueError, match=message):
        parse_duration(bad)


def test_non_string_raises_type_error():
    with pytest.raises(TypeError):
        parse_duration(90)


@pytest.fixture
def playlist():
    """A plain fixture: shared, read-only test data built fresh for each test."""
    return ["3m20s", "4m", "2m45s"]


def test_total_of_playlist(playlist):
    assert sum(parse_duration(t) for t in playlist) == 605


@pytest.fixture
def audit_log():
    """A yield fixture: code after ``yield`` is teardown and runs even if the test fails."""
    log: list[str] = ["setup"]
    yield log
    log.append("teardown")
    assert log[-1] == "teardown"


def test_yield_fixture_gives_fresh_state(audit_log):
    audit_log.append(f"parsed {parse_duration('10s')}")
    assert audit_log == ["setup", "parsed 10"]


@pytest.fixture(params=["1h", "60m", "3600s", "0h60m"], ids=lambda p: f"one-hour-as-{p}")
def one_hour(request):
    """A parametrised fixture: every test that uses it runs once per param."""
    return request.param


def test_equivalent_spellings(one_hour):
    assert parse_duration(one_hour) == 3_600


def main() -> None:
    for text in ["45s", "1h30m", "2d 4h 5s", "1d1h1m1s"]:
        print(f"parse_duration({text!r}) = {parse_duration(text)}")
    for bad in ["90", "1m1h", ""]:
        try:
            parse_duration(bad)
        except ValueError as exc:
            print(f"parse_duration({bad!r}) -> ValueError: {exc}")
    print()
    from ch31_testkit import print_results, run_embedded_tests

    print_results(run_embedded_tests(__file__))


if __name__ == "__main__":
    main()
