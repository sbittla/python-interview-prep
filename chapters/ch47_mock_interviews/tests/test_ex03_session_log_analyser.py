import pytest


def _log(m, name):
    return m.parse_log((m.LOGS / name).read_text(encoding="utf-8"))


def test_strong_log_has_no_flags(load):
    m = load("ex03_session_log_analyser")
    a = m.analyse(_log(m, "s2_candidate_a.log"))
    assert a.flags == []
    assert (a.first_ask, a.first_code, a.first_green) == (65, 400, 970)
    assert (a.runs, a.hints, a.tests_added, a.duration) == (2, 0, 2, 1245)


def test_weak_log_flags(load):
    m = load("ex03_session_log_analyser")
    a = m.analyse(_log(m, "s2_candidate_b.log"))
    assert [k for k, _ in a.flags] == ["clarifying", "approach", "approach", "complexity",
                                       "testing", "communication"]
    assert a.first_ask is None and a.hints == 2 and a.first_green == 1040
    assert a.longest_gap == (340, 50)


def test_silence_flag_threshold(load):
    m = load("ex03_session_log_analyser")
    text = ("00:00 START\n00:10 ASK q\n00:20 PLAN p\n00:30 COMPLEXITY c\n00:40 CODE_START\n"
            "03:40 RUN 1/1\n03:50 TEST_ADDED t\n04:00 END")
    a = m.analyse(m.parse_log(text))
    assert a.longest_gap == (180, 40) and a.flags == []          # exactly 180 s: not flagged
    a = m.analyse(m.parse_log(text), silence=179)
    assert a.flags == [("communication", "silent 03:00 from 00:40")]


def test_only_events_before_code_count(load):
    m = load("ex03_session_log_analyser")
    text = ("00:00 START\n00:30 CODE_START\n01:00 ASK late\n01:30 PLAN late\n"
            "02:00 COMPLEXITY late\n02:30 RUN 3/3\n03:00 TEST_ADDED t\n03:30 END")
    assert [k for k, _ in m.analyse(m.parse_log(text)).flags] == [
        "clarifying", "approach", "complexity"]


def test_first_green_skips_partial_runs(load):
    m = load("ex03_session_log_analyser")
    a = m.analyse(m.parse_log("00:00 START\n00:30 RUN 2/3\n01:00 RUN 12/12\n01:30 END"))
    assert a.first_green == 60 and a.runs == 2
    a = m.analyse(m.parse_log("00:00 START\n00:30 ASK q\n01:00 RUN 2/3\n01:30 END"))
    assert a.first_green is None and a.first_code is None
    assert ("correctness", "no fully passing run") in a.flags


def test_comments_and_blank_lines(load):
    m = load("ex03_session_log_analyser")
    ev = m.parse_log("# header\n\n00:00 START\n  # indented comment\n00:05 SAY hi there\n00:09 END\n")
    assert [(e.t, e.kind, e.detail) for e in ev] == [
        (0, "START", ""), (5, "SAY", "hi there"), (9, "END", "")]


@pytest.mark.parametrize("text, where", [
    ("00:00 START\n0:10 ASK x\n00:20 END", "line 2"),
    ("00:00 START\n00:61 ASK x\n01:20 END", "line 2"),
    ("00:00 START\n00:10 SHOUT x\n00:20 END", "line 2"),
    ("00:00 START\n00:10 RUN 4/3\n00:20 END", "line 2"),
    ("00:00 START\n00:10 RUN 0/0\n00:20 END", "line 2"),
    ("00:00 START\n00:10 RUN\n00:20 END", "line 2"),
    ("00:00 START\n00:30 ASK x\n00:20 END", "line 3"),
    ("00:10 ASK x\n00:20 END", "line 1"),
    ("00:00 START\n00:05 START\n00:20 END", "line 2"),
    ("00:00 START\n00:20 END\n00:30 SAY late", "line 3"),
    ("00:00 START\n00:10 ASK x", "END"),
    ("", "END"),
])
def test_malformed(load, text, where):
    m = load("ex03_session_log_analyser")
    with pytest.raises(ValueError, match=where):
        m.parse_log(text)
