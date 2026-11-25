import random

import pytest


def hits(m, specs):
    return [m.Hit("ip", i, "GET", p, s, ms) for i, (p, s, ms) in enumerate(specs)]


def test_examples(load):
    m = load("ex02_log_aggregations")
    h = [m.Hit("a", 0, "GET", "/x", 200, 10), m.Hit("b", 1, "GET", "/y", 500, 30),
         m.Hit("a", 2, "GET", "/y", 200, 20)]
    assert m.top_k_paths(h, 1) == [("/y", 2)]
    assert m.status_classes(h) == {"2xx": 2, "5xx": 1}
    assert m.error_rates(h) == {"/y": (1, 2)}


def test_ties_broken_by_path_not_order(load):
    m = load("ex02_log_aggregations")
    h = hits(m, [("/b", 200, 1), ("/a", 200, 1), ("/b", 200, 1), ("/a", 200, 1), ("/c", 200, 1)])
    assert m.top_k_paths(h, 2) == [("/a", 2), ("/b", 2)]
    assert m.top_k_paths(h, 10) == [("/a", 2), ("/b", 2), ("/c", 1)]


def test_status_classes_sorted(load):
    m = load("ex02_log_aggregations")
    h = hits(m, [("/a", 503, 1), ("/a", 301, 1), ("/a", 404, 1), ("/a", 200, 1), ("/a", 599, 1)])
    got = m.status_classes(h)
    assert got == {"2xx": 1, "3xx": 1, "4xx": 1, "5xx": 2} and list(got) == sorted(got)


def test_p95_nearest_rank(load):
    m = load("ex02_log_aggregations")
    h = hits(m, [("/x", 200, v) for v in range(1, 21)] + [("/one", 200, 7)])
    # n = 20: ceil(0.95 * 20) = 19 -> the 19th smallest value
    assert m.p95_latency(h) == {"/one": 7, "/x": 19}
    h = hits(m, [("/x", 200, v) for v in range(21, 0, -1)])   # n = 21, unsorted: ceil(19.95) = 20
    assert m.p95_latency(h) == {"/x": 20}


@pytest.mark.parametrize("fn", ["status_classes", "p95_latency", "error_rates"])
def test_empty(load, fn):
    assert getattr(load("ex02_log_aggregations"), fn)([]) == {}


def test_random_vs_brute(load):
    m = load("ex02_log_aggregations")
    rng = random.Random(2)
    for _ in range(100):
        h = hits(m, [(rng.choice("abcdef"), 200, 1) for _ in range(rng.randint(0, 30))])
        k = rng.randint(1, 7)
        assert m.top_k_paths(h, k) == m.brute_top_k(h, k)


def test_data_file(load):
    m = load("ex02_log_aggregations")
    h = m.load_hits()
    assert m.top_k_paths(h, 2) == [("/login", 13), ("/static/app.js", 12)]
    assert sum(m.status_classes(h).values()) == len(h) == 39
