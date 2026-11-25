import math

import pytest


@pytest.fixture
def m(load):
    return load("ex10_broken_training_loops")


def test_fixed_loop_trains(m):
    r = m.train(None)
    assert r["error"] is None
    assert r["last_loss"] < 0.1 and r["acc"] > 0.95
    assert r["body_changed"] and r["eval_repeatable"]


def test_no_zero_grad_blows_up(m):
    good, bad = m.train(None), m.train("no_zero_grad")
    assert bad["last_loss"] > 100 * good["last_loss"]
    assert bad["last_loss"] > bad["first_loss"]


def test_softmax_before_ce_has_a_floor(m):
    assert m.SOFTMAX_CE_FLOOR == pytest.approx(math.log(1 + 2 / math.e))
    r = m.train("softmax_ce", steps=300)
    assert r["last_loss"] >= m.SOFTMAX_CE_FLOOR - 1e-6
    assert r["acc"] > 0.9                       # accuracy hides the bug


def test_detached_body_never_moves(m):
    r = m.train("detached_body")
    assert not r["body_changed"]
    assert m.train(None)["body_changed"]


def test_missing_eval_is_not_repeatable(m):
    assert not m.train("no_eval")["eval_repeatable"]


def test_inplace_raises(m):
    r = m.train("inplace")
    assert r["error"] == "RuntimeError" and "inplace" in r["message"]


def test_regression_broadcast(m):
    assert m.regression(None) < 1e-3
    assert m.regression("broadcast") > 1.0
