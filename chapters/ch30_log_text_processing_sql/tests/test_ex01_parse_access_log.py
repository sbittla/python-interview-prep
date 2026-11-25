from datetime import timezone
from pathlib import Path

import pytest

GOOD = '1.2.3.4 - - [12/Mar/2025:10:00:35 +0000] "GET /a HTTP/1.1" 200 5 0.044'
LOG = Path(__file__).resolve().parent.parent / "data" / "access.log"


def test_example(load):
    m = load("ex01_parse_access_log")
    r = m.parse_line(GOOD)
    assert (r.ip, r.method, r.path, r.status, r.size, r.latency_ms) == ("1.2.3.4", "GET", "/a", 200, 5, 44)
    assert r.ts.isoformat() == "2025-03-12T10:00:35+00:00" and r.ts.tzinfo is not None


@pytest.mark.parametrize("line", [
    "",
    "garbage",
    '1.2.3.4 - - [12/Mar/2025:10:00:35 +0000] "GET /a',                       # truncated
    '1.2.3.4 - - [12/Mar/2025:10:00:35 +0000] "GET /a HTTP/1.1" 2OO 5 0.044',  # letter O
    '1.2.3.4 - - [31/Foo/2025:10:00:35 +0000] "GET /a HTTP/1.1" 200 5 0.044',  # bad month
    '1.2.3.4 - - [30/Feb/2025:10:00:35 +0000] "GET /a HTTP/1.1" 200 5 0.044',  # no such day
    'unknown - - [12/Mar/2025:10:00:35 +0000] "GET /a HTTP/1.1" 200 5 0.044',  # not an IP
    GOOD + " trailing",
])
def test_malformed_is_none(load, line):
    assert load("ex01_parse_access_log").parse_line(line) is None


def test_dash_size_crlf_and_optional_latency(load):
    m = load("ex01_parse_access_log")
    r = m.parse_line('1.2.3.4 - - [12/Mar/2025:10:00:35 +0000] "GET /a HTTP/1.1" 304 - 0.001\r\n')
    assert (r.status, r.size, r.latency_ms) == (304, 0, 1)
    r = m.parse_line('1.2.3.4 - - [12/Mar/2025:10:00:35 +0000] "GET /a HTTP/1.1" 200 7')
    assert (r.size, r.latency_ms) == (7, 0)
    r = m.parse_line('1.2.3.4 - - [12/Mar/2025:12:00:35 +0200] "GET /a HTTP/1.1" 200 7 0.5')
    assert r.ts.astimezone(timezone.utc).hour == 10 and r.latency_ms == 500


def test_iter_records_is_lazy_and_counts(load):
    m = load("ex01_parse_access_log")
    consumed = []

    def source():
        for line in [GOOD, "bad", GOOD]:
            consumed.append(line)
            yield line

    stats = {}
    gen = m.iter_records(source(), stats)
    assert consumed == []                      # nothing read before iteration starts
    first = next(gen)
    assert first.path == "/a" and len(consumed) == 1
    rest = list(gen)
    assert len(rest) == 1 and stats == {"ok": 2, "bad": 1}


def test_data_file(load):
    m = load("ex01_parse_access_log")
    stats = {}
    with open(LOG, encoding="utf-8") as f:
        recs = list(m.iter_records(f, stats))
    assert stats == {"ok": 39, "bad": 5}
    assert sum(r.ip == "198.51.100.7" for r in recs) == 9


def test_split_rung(load):
    m = load("ex01_parse_access_log")
    assert m.parse_split(GOOD) == m.parse_line(GOOD)
    assert m.parse_split("garbage") is None
