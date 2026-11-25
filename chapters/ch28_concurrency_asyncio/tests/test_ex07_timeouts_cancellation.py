import sys

import pytest


def test_examples(load):
    m = load("ex07_timeouts_cancellation")
    assert m.run_virtual(m.with_timeout(0.5, 1.0)) == "done"
    assert m.run_virtual(m.with_timeout(5, 1.0)) == "timeout"
    assert m.run_virtual(m.cancel_with_cleanup(0.1)) == ["start", "cleanup", "cancelled"]


@pytest.mark.parametrize("delay, limit, expected", [(0.99, 1.0, "done"), (1.01, 1.0, "timeout"),
                                                    (0, 0.1, "done"), (100, 0.001, "timeout")])
def test_with_timeout_boundaries(load, delay, limit, expected):
    m = load("ex07_timeouts_cancellation")
    assert m.run_virtual(m.with_timeout(delay, limit)) == expected


@pytest.mark.skipif(sys.version_info < (3, 11), reason="asyncio.timeout is 3.11+")
def test_with_timeout_311(load):
    m = load("ex07_timeouts_cancellation")
    assert m.run_virtual(m.with_timeout_311(0.5, 1.0)) == "done"
    assert m.run_virtual(m.with_timeout_311(5, 1.0)) == "timeout"


def test_timeout_happens_at_the_limit(load):
    m = load("ex07_timeouts_cancellation")

    async def timed():
        import asyncio
        loop = asyncio.get_running_loop()
        out = await m.with_timeout(30, 2.5)
        return out, round(loop.time(), 3)

    assert m.run_virtual(timed()) == ("timeout", 2.5)


SPECS = [("slow", 0.5, False), ("broken", 0.1, True), ("quick", 0.05, False)]


def test_fail_fast_cancels_siblings(load):
    m = load("ex07_timeouts_cancellation")
    log = []
    with pytest.raises(ValueError, match="broken failed"):
        m.run_virtual(m.fail_fast(SPECS, log))
    assert log == ["quick finished", "slow cancelled"]


def test_fail_fast_success_and_empty(load):
    m = load("ex07_timeouts_cancellation")
    log = []
    assert m.run_virtual(m.fail_fast([("b", 0.2, False), ("a", 0.1, False)], log)) == ["b", "a"]
    assert log == ["a finished", "b finished"]
    assert m.run_virtual(m.fail_fast([], [])) == []


@pytest.mark.skipif(sys.version_info < (3, 11), reason="TaskGroup is 3.11+")
def test_taskgroup_variant(load):
    m = load("ex07_timeouts_cancellation")
    log = []
    with pytest.raises(Exception) as info:
        m.run_virtual(m.fail_fast_taskgroup(SPECS, log))
    assert type(info.value).__name__ == "ExceptionGroup"
    assert [str(e) for e in info.value.exceptions] == ["broken failed"]
    assert log == ["quick finished", "slow cancelled"]


def test_plain_gather_does_not_cancel(load):
    m = load("ex07_timeouts_cancellation")
    log = []
    m.run_virtual(m.gather_no_cancel(SPECS, log))
    assert log == ["quick finished", "caller saw: broken failed", "slow finished"]
