import random

import pytest

M = "ex04_knapsack_coin_change"
ITEMS = [(1, 1), (3, 4), (4, 5), (5, 7)]


def test_examples(load):
    m = load(M)
    assert m.knapsack(ITEMS, 7) == 9
    assert m.knapsack_unbounded(ITEMS, 7) == 9
    assert (m.min_coins([1, 3, 4], 6), m.greedy_coins([1, 3, 4], 6)) == (2, 3)
    assert (m.count_combinations([1, 2, 5], 5), m.count_permutations([1, 2, 5], 5)) == (4, 9)


@pytest.mark.parametrize("items, cap, expected", [
    ([], 10, 0), ([(5, 10)], 4, 0), ([(5, 10)], 5, 10), ([(2, 3)], 6, 3), (ITEMS, 0, 0),
])
def test_knapsack_edges(load, items, cap, expected):
    m = load(M)
    assert m.knapsack(items, cap) == m.knapsack_table(items, cap)[0] == expected


def test_item_reuse_is_the_loop_direction(load):
    m = load(M)
    assert m.knapsack([(2, 3)], 6) == 3                # 0/1: once
    assert m.knapsack_unbounded([(2, 3)], 6) == 9      # unbounded: three times


def test_knapsack_random_against_brute(load):
    m = load(M)
    rng = random.Random(4)
    for _ in range(150):
        items = [(rng.randint(1, 8), rng.randint(0, 20)) for _ in range(rng.randint(0, 8))]
        cap = rng.randint(0, 20)
        best = m.knapsack_brute(items, cap)
        assert m.knapsack(items, cap) == m.knapsack_memo(items, cap) == best
        value, chosen = m.knapsack_table(items, cap)
        assert value == best
        assert len(set(chosen)) == len(chosen)
        assert sum(items[i][0] for i in chosen) <= cap
        assert sum(items[i][1] for i in chosen) == best
        small = min(cap, 10)                    # unbounded brute force is exponential in cap
        assert m.knapsack_unbounded(items, small) == m.knapsack_unbounded_brute(items, small)


@pytest.mark.parametrize("coins, amount, expected", [
    ([1, 3, 4], 6, 2), ([2], 3, -1), ([7, 3], 0, 0), ([5], 5, 1), ([186, 419, 83, 408], 6249, 20),
])
def test_min_coins_edges(load, coins, amount, expected):
    assert load(M).min_coins(coins, amount) == expected


def test_greedy_is_wrong_but_dp_is_right(load):
    m = load(M)
    assert m.greedy_coins([1, 3, 4], 6) == 3 and m.min_coins([1, 3, 4], 6) == 2
    assert m.greedy_coins([5, 2], 6) == -1 and m.min_coins([5, 2], 6) == 3


def test_coins_random_against_brute(load):
    m = load(M)
    rng = random.Random(8)
    for _ in range(150):
        coins = rng.sample(range(1, 10), rng.randint(1, 4))
        amount = rng.randint(0, 22)
        expected = m.min_coins_brute(coins, amount)
        assert m.min_coins(coins, amount) == m.min_coins_memo(coins, amount) == expected
        combos = m.count_combinations_brute(coins, amount)
        assert m.count_combinations(coins, amount) == m.count_combinations_memo(coins, amount) == combos
        assert m.count_permutations(coins, amount) == m.count_permutations_brute(coins, amount)


@pytest.mark.parametrize("coins, amount, comb, perm", [
    ([1, 2, 5], 5, 4, 9), ([2, 3], 7, 1, 3), ([3], 2, 0, 0), ([1, 2], 4, 3, 5), ([4], 0, 1, 1),
])
def test_counting_order_matters(load, coins, amount, comb, perm):
    m = load(M)
    assert m.count_combinations(coins, amount) == comb
    assert m.count_permutations(coins, amount) == perm
