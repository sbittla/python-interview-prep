from fractions import Fraction

import pytest


def test_example(load):
    m = load("ex03_bayes_rule")
    assert m.posterior(Fraction(1, 100), Fraction(9, 10), Fraction(91, 100)) == Fraction(10, 109)


def test_hand_computed_negative_result(load):
    m = load("ex03_bayes_rule")
    # P(sick|-) = 0.1*0.01 / (0.1*0.01 + 0.91*0.99) = 10 / 9019
    assert m.posterior(Fraction(1, 100), Fraction(9, 10), Fraction(91, 100), positive=False) == Fraction(10, 9019)


@pytest.mark.parametrize("prior, sens, spec", [(Fraction(1, 100), Fraction(9, 10), Fraction(91, 100)),
                                               (Fraction(1, 5), Fraction(3, 4), Fraction(4, 5)),
                                               (Fraction(1, 2), Fraction(1, 2), Fraction(1, 2))])
@pytest.mark.parametrize("positive", [True, False])
def test_formula_matches_counting(load, prior, sens, spec, positive):
    m = load("ex03_bayes_rule")
    assert m.posterior(prior, sens, spec, positive) == m.count_posterior(10_000, prior, sens, spec, positive)


def test_sequential_equals_odds_form(load):
    m = load("ex03_bayes_rule")
    prior, sens, spec = Fraction(1, 100), Fraction(9, 10), Fraction(91, 100)
    lr = sens / (1 - spec)
    for k in range(1, 5):
        odds = prior / (1 - prior) * lr ** k
        assert m.sequential(prior, sens, spec, [True] * k) == odds / (1 + odds)
    assert m.sequential(prior, sens, spec, [True, True]) == Fraction(100, 199)


def test_simulation_close_to_exact(load):
    m = load("ex03_bayes_rule")
    est = m.simulate_posterior(0.2, 0.75, 0.8, trials=400_000, seed=0)
    assert est == pytest.approx(0.15 / (0.15 + 0.16), abs=0.01)


def test_edge_priors(load):
    m = load("ex03_bayes_rule")
    assert m.posterior(Fraction(0), Fraction(9, 10), Fraction(9, 10)) == 0
    assert m.posterior(Fraction(1), Fraction(9, 10), Fraction(9, 10)) == 1
    with pytest.raises(ValueError):
        m.posterior(Fraction(0), Fraction(0), Fraction(1))   # a positive cannot happen
