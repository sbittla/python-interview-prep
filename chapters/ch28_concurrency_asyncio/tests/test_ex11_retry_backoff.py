import random

import pytest


def run(m, script, attempts=4, base=0.2, cap=1.0, timeout=0.5, seed=7):
    svc = m.FlakyService(script)
    out = m.run_virtual(m.retry(svc.call, attempts, base, cap, timeout, random.Random(seed)))
    return out, svc.calls


def test_examples(load):
    m = load("ex11_retry_backoff")
    (result, log), calls = run(m, ["fail", "ok"], attempts=3, base=0.1, cap=1.0, timeout=1.0,
                               seed=0)
    assert (result, len(log), calls) == ("payload", 2, 2)


def test_first_try_success_no_sleep(load):
    m = load("ex11_retry_backoff")
    (result, log), calls = run(m, ["ok"])
    assert result == "payload" and log == ["t=0.0 attempt 1: ok"] and calls == 1


def test_backoff_schedule_matches_full_jitter(load):
    m = load("ex11_retry_backoff")
    (result, log), _ = run(m, ["fail", "fail", "fail", "ok"], attempts=4, base=0.2, cap=0.5)
    rng = random.Random(7)
    t, expected = 0.0, []
    for n in range(1, 4):
        expected.append(round(t, 3))
        t += 0.05 + rng.uniform(0, min(0.5, 0.2 * 2 ** (n - 1)))   # call cost + jitter
    expected.append(round(t, 3))
    assert [float(line.split()[0][2:]) for line in log] == pytest.approx(expected, abs=1e-3)


def test_timeout_is_retried(load):
    m = load("ex11_retry_backoff")
    (result, log), calls = run(m, ["hang", "ok"], timeout=0.5)
    assert result == "payload" and calls == 2
    assert log[0] == "t=0.0 attempt 1: timeout"


def test_exhausted_raises_with_log(load):
    m = load("ex11_retry_backoff")
    with pytest.raises(m.RetryError) as info:
        run(m, ["fail", "hang", "fail"], attempts=3)
    assert [line.split(": ")[1] for line in info.value.log] == [
        "ConnectionError", "timeout", "ConnectionError"]


def test_no_sleep_after_last_attempt(load):
    m = load("ex11_retry_backoff")
    import asyncio

    async def go():
        svc = m.FlakyService(["fail"])
        try:
            await m.retry(svc.call, 1, 5.0, 5.0, 1.0, random.Random(1))
        except m.RetryError:
            return round(asyncio.get_running_loop().time(), 3)

    assert m.run_virtual(go()) == 0.05


def test_other_errors_not_retried(load):
    m = load("ex11_retry_backoff")
    svc = m.FlakyService(["bug", "ok"])
    with pytest.raises(KeyError):
        m.run_virtual(m.retry(svc.call, 3, 0.2, 1.0, 0.5, random.Random(7)))
    assert svc.calls == 1
