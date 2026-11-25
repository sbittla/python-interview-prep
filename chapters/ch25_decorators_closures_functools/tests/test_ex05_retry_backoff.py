import pytest


def test_succeeds_after_failures(load):
    m = load("ex05_retry_backoff")
    waits, flaky = [], m.Flaky(2)
    assert m.retry(3, sleep=waits.append)(flaky)() == "ok after 3 attempts"
    assert flaky.attempts == 3 and waits == [0.1, 0.2]


def test_first_try_success_never_sleeps(load):
    m = load("ex05_retry_backoff")
    waits = []
    assert m.retry(5, sleep=waits.append)(lambda: 7)() == 7
    assert waits == []


def test_gives_up_with_last_exception(load):
    m = load("ex05_retry_backoff")
    waits, flaky = [], m.Flaky(10)
    with pytest.raises(ConnectionError, match="attempt 4 failed"):
        m.retry(4, base_delay=0.5, factor=3, sleep=waits.append)(flaky)()
    assert flaky.attempts == 4 and waits == [0.5, 1.5, 4.5]   # no sleep after the last attempt


def test_max_delay_caps(load):
    m = load("ex05_retry_backoff")
    waits = []
    m.retry(5, base_delay=1.0, max_delay=3.0, sleep=waits.append)(m.Flaky(4))()
    assert waits == [1.0, 2.0, 3.0, 3.0]


def test_non_retryable_propagates_immediately(load):
    m = load("ex05_retry_backoff")
    waits, flaky = [], m.Flaky(1, KeyError)
    with pytest.raises(KeyError):
        m.retry(3, exceptions=(ConnectionError,), sleep=waits.append)(flaky)()
    assert flaky.attempts == 1 and waits == []


def test_subclass_is_retried(load):
    m = load("ex05_retry_backoff")
    waits, flaky = [], m.Flaky(1, ConnectionRefusedError)
    assert m.retry(2, exceptions=(OSError,), sleep=waits.append)(flaky)() == "ok after 2 attempts"
    assert waits == [0.1]


def test_times_one_means_no_retry(load):
    m = load("ex05_retry_backoff")
    waits, flaky = [], m.Flaky(1)
    with pytest.raises(ConnectionError):
        m.retry(1, sleep=waits.append)(flaky)()
    assert flaky.attempts == 1 and waits == []


def test_bad_times_and_metadata(load):
    m = load("ex05_retry_backoff")
    with pytest.raises(ValueError):
        m.retry(0)

    def fetch(url, *, timeout=1):
        """Fetch a URL."""
        return (url, timeout)

    wrapped = m.retry(2, sleep=lambda s: None)(fetch)
    assert wrapped("u", timeout=3) == ("u", 3)
    assert (wrapped.__name__, wrapped.__doc__) == ("fetch", "Fetch a URL.")
