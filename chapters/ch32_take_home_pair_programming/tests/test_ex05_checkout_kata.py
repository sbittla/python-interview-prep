import random

import pytest

M = "ex05_checkout_kata"
PRICES = {"A": 50, "B": 30, "C": 20}
OFFERS = {"A": (3, 130), "B": (2, 45)}


def checkout(m, skus, rules=()):
    co = m.Checkout(PRICES, rules)
    for s in skus:
        co.scan(s)
    return co


@pytest.mark.parametrize("skus, expected", [("", 0), ("A", 50), ("ABA", 130), ("CCC", 60)])
def test_v1(load, skus, expected):
    m = load(M)
    assert m.total_v1(skus, PRICES) == expected
    assert checkout(m, skus).total() == expected        # v1 spec still holds in v3


def test_unknown_sku(load):
    m = load(M)
    with pytest.raises(ValueError, match="unknown SKU 'Z'"):
        m.total_v1("AZ", PRICES)
    with pytest.raises(ValueError, match="unknown SKU 'Z'"):
        m.total_v2("Z", PRICES, OFFERS)
    with pytest.raises(ValueError, match="unknown SKU 'Z'"):
        checkout(m, "Z")


@pytest.mark.parametrize("skus, expected", [
    ("AA", 100), ("AAA", 130), ("AAAA", 180), ("AAAAAA", 260), ("BB", 45), ("BAB", 95),
    ("AAAAAABB", 305), ("C", 20),
])
def test_v2_and_v3_agree_on_multibuy(load, skus, expected):
    m = load(M)
    assert m.total_v2(skus, PRICES, OFFERS) == expected
    rules = [m.MultiBuy(s, q, p) for s, (q, p) in OFFERS.items()]
    assert checkout(m, skus, rules).total() == expected


def test_percent_off_threshold_and_rounding(load):
    m = load(M)
    rule = [m.PercentOff(10, 200)]
    assert checkout(m, "AAA" + "BBB" + "C", rule).total() == 260 - 26
    assert checkout(m, "AAAB", rule).total() == 180              # 180 < 200: no discount
    assert checkout(m, "AAAA", rule).total() == 180              # 200 >= 200: 20 off
    assert checkout(m, "AAAABC" + "C", [m.PercentOff(15, 0)]).total() == 270 - 40  # floor(40.5)
    assert checkout(m, "BBB", [m.PercentOff(15, 0)]).total() == 77       # 90 - floor(13.5)
    assert checkout(m, "", [m.PercentOff(100, 0)]).total() == 0


def test_basket_rule_applies_after_item_rules_whatever_the_list_order(load):
    m = load(M)
    rules = [m.PercentOff(10, 200), m.MultiBuy("A", 3, 130), m.MultiBuy("B", 2, 45)]
    co = checkout(m, "BAACABA", rules)
    assert co.total() == 221                 # 280 - 20 - 15 = 245; 10% -> 24
    assert co.receipt().splitlines() == [
        "A x 4                 200",
        "B x 2                  60",
        "C x 1                  20",
        "3 A for 130           -20",
        "2 B for 45            -15",
        "10% off over 200      -24",
        "TOTAL                 221",
    ]


def test_scan_order_never_matters(load):
    m = load(M)
    rules = [m.MultiBuy("A", 3, 130), m.MultiBuy("B", 2, 45), m.PercentOff(10, 200)]
    rng = random.Random(32)
    for _ in range(50):
        skus = [rng.choice("ABC") for _ in range(rng.randint(0, 12))]
        shuffled = skus[:]
        rng.shuffle(shuffled)
        assert checkout(m, skus, rules).total() == checkout(m, shuffled, rules).total()


def test_buy_two_get_one_free_is_just_a_multibuy(load):
    m = load(M)
    assert checkout(m, "CCCCCC", [m.MultiBuy("C", 3, 2 * PRICES["C"])]).total() == 80


@pytest.mark.parametrize("make, message", [
    (lambda m: m.MultiBuy("A", 0, 100), "qty must be > 0"),
    (lambda m: m.MultiBuy("A", 3, -1), "qty must be > 0"),
    (lambda m: m.PercentOff(101, 0), "bad coupon"),
    (lambda m: m.PercentOff(10, -1), "bad coupon"),
])
def test_invalid_rule_parameters(load, make, message):
    m = load(M)
    with pytest.raises(ValueError, match=message):
        make(m)


def test_rules_checked_against_prices_at_construction(load):
    m = load(M)
    with pytest.raises(ValueError, match="unknown SKU 'Z'"):
        m.Checkout(PRICES, [m.MultiBuy("Z", 2, 10)])
    with pytest.raises(ValueError, match="costs more than 3 singles"):
        m.Checkout(PRICES, [m.MultiBuy("A", 3, 151)])
    assert m.Checkout(PRICES, [m.MultiBuy("A", 3, 150)]).total() == 0   # equal is allowed
