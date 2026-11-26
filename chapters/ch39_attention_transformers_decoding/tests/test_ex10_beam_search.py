import math

import numpy as np
import pytest


def test_toy_model(load):
    m = load("ex10_beam_search")
    step = m.toy_model()
    g, gt = m.greedy(step, 4, 0, 4)
    assert g == (1, 1, 1, 1) and math.isclose(math.exp(gt), 0.55 * 0.3 ** 3)
    best, sc = m.beam_search(step, 4, 0, 2, 4)[0]
    assert best == (2, 0) and math.isclose(math.exp(sc), 0.405)
    assert m.beam_search(step, 4, 0, 1, 4)[0][0] == (1, 0)
    assert m.exhaustive(step, 4, 0, 4)[0][0] == (2, 0)


@pytest.mark.parametrize("seed", range(6))
@pytest.mark.parametrize("alpha", [0.0, 0.6, 1.0])
def test_huge_beam_equals_exhaustive(load, seed, alpha):
    m = load("ex10_beam_search")
    step = m.random_bigram_model(4, seed)
    full = m.beam_search(step, 4, 0, 4 ** 4, 4, alpha)
    ex = m.exhaustive(step, 4, 0, 4, alpha)
    # same candidate set with the same scores (float sums may order exact ties differently)
    assert sorted(s for s, _ in full) == sorted(s for s, _ in ex)
    ex_scores = dict(ex)
    assert all(np.isclose(c, ex_scores[s]) for s, c in full)
    assert np.isclose(full[0][1], ex[0][1])


def test_scores_are_normalised_sums(load):
    m = load("ex10_beam_search")
    step = m.random_bigram_model(5, 3)
    for alpha in (0.0, 0.7):
        for seq, sc in m.beam_search(step, 5, 0, 3, 5, alpha)[:5]:
            total = sum(float(step(list(seq[:i]))[t]) for i, t in enumerate(seq))
            assert math.isclose(sc, total / len(seq) ** alpha, rel_tol=1e-12)


def test_sorted_and_k_respected(load):
    m = load("ex10_beam_search")
    step = m.random_bigram_model(5, 8)
    res = m.beam_search(step, 5, 0, 2, 6)
    scores = [s for _, s in res]
    assert scores == sorted(scores, reverse=True)
    assert sum(1 for s, _ in res if len(s) == 6 and s[-1] != 0) <= 2       # alive at the end <= k
    assert all(0 not in s[:-1] for s, _ in res)


def test_length_normalisation_changes_winner(load):
    m = load("ex10_beam_search")
    step = m.random_bigram_model(5, 3910)
    short = m.beam_search(step, 5, 0, 3, 6, 0.0)[0][0]
    long = m.beam_search(step, 5, 0, 3, 6, 1.0)[0][0]
    assert len(short) < len(long)


def test_max_len_one(load):
    m = load("ex10_beam_search")
    step = m.toy_model()
    res = m.beam_search(step, 4, 0, 2, 1)
    assert res[0][0] == (1,) and len(res) == 3       # 'a', 'b' alive + '<eos>' finished
