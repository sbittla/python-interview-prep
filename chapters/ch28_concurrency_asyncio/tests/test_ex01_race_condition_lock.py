import threading
import time

import pytest


def test_examples(load):
    m = load("ex01_race_condition_lock")
    assert m.lost_update_demo(4) == 1
    assert m.run_counter(m.LockedCounter(), 4, 1000) == 4000
    assert m.concurrent_withdrawals(m.Account(100), 10, 30) == (3, 10)


@pytest.mark.parametrize("n", [1, 2, 8])
def test_lost_update_is_forced(load, n):
    assert load("ex01_race_condition_lock").lost_update_demo(n) == 1


@pytest.mark.parametrize("threads, per", [(1, 0), (1, 500), (8, 5000)])
def test_locked_and_sharded_counts(load, threads, per):
    m = load("ex01_race_condition_lock")
    assert m.run_counter(m.LockedCounter(), threads, per) == threads * per
    assert m.run_sharded(threads, per) == threads * per


def test_unsafe_account_overdraws_with_forced_interleaving(load):
    m = load("ex01_race_condition_lock")
    barrier = threading.Barrier(3)
    acct = m.UnsafeAccount(50, pause=barrier.wait)
    assert m.concurrent_withdrawals(acct, 3, 50) == (3, -100)


def test_account_lock_covers_check_and_act(load):
    # A pause between check and act makes an unlocked version overdraw almost every time.
    m = load("ex01_race_condition_lock")
    acct = m.Account(100, pause=lambda: time.sleep(0.002))
    assert m.concurrent_withdrawals(acct, 12, 30) == (3, 10)


def test_account_edges(load):
    m = load("ex01_race_condition_lock")
    assert m.concurrent_withdrawals(m.Account(0), 3, 1) == (0, 0)
    assert m.concurrent_withdrawals(m.Account(60), 4, 30) == (2, 0)   # exact balance


def test_locked_counter_lock_covers_read_and_write(load):
    # The pause between read and write makes an unlocked counter lose updates almost always.
    m = load("ex01_race_condition_lock")
    counter = m.LockedCounter(pause=lambda: time.sleep(0.001))
    assert m.run_counter(counter, 4, 25) == 100
