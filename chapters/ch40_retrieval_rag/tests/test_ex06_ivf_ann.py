import numpy as np
import pytest


def test_examples(load):
    m = load("ex06_ivf_ann")
    assert m.exact_top_k(np.eye(3), np.array([0.0, 1.0, 0.0]), 2) == [1, 0]


def test_exact_top_k_ties_and_order(load):
    m = load("ex06_ivf_ann")
    X = np.array([[0.0, 1.0], [1.0, 0.0], [1.0, 0.0], [0.6, 0.8]])
    assert m.exact_top_k(X, np.array([1.0, 0.0]), 3) == [1, 2, 3]
    assert m.exact_top_k(X, np.array([1.0, 0.0]), 10) == [1, 2, 3, 0]


def test_recall_at_k(load):
    m = load("ex06_ivf_ann")
    assert m.recall_at_k([1, 2, 3], [3, 4, 5]) == pytest.approx(1 / 3)
    assert m.recall_at_k([5, 4, 3], [3, 4, 5]) == 1.0                 # order does not matter
    assert m.recall_at_k([], [1]) == 0.0


def test_kmeans_deterministic_and_unit(load):
    m = load("ex06_ivf_ann")
    X, _ = m.make_data(n=500, n_queries=1)
    C1, a1 = m.spherical_kmeans(X, 8, seed=3)
    C2, a2 = m.spherical_kmeans(X, 8, seed=3)
    assert np.array_equal(C1, C2) and np.array_equal(a1, a2)
    assert np.allclose(np.linalg.norm(C1, axis=1), 1.0)
    assert np.array_equal(a1, np.argmax(X @ C1.T, axis=1))         # final assignment is consistent


def test_kmeans_two_obvious_clusters(load):
    m = load("ex06_ivf_ann")
    X = np.array([[1.0, 0.0], [0.99, 0.141], [0.0, 1.0], [0.141, 0.99]])
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    _, a = m.spherical_kmeans(X, 2, seed=0)
    assert a[0] == a[1] and a[2] == a[3] and a[0] != a[2]


@pytest.fixture
def setup(load):
    m = load("ex06_ivf_ann")
    X, Q = m.make_data(n=1500, n_queries=40)
    return m, X, Q, m.IVFIndex(X, 32)


def test_lists_partition_rows(setup):
    m, X, Q, idx = setup
    rows = np.sort(np.concatenate(idx.lists))
    assert np.array_equal(rows, np.arange(len(X)))


def test_full_probe_is_exact_and_scans_everything(setup):
    m, X, Q, idx = setup
    for q in Q:
        got, scanned = idx.search(q, 10, nprobe=32)
        assert got == m.exact_top_k(X, q, 10) and scanned == len(X)


def test_recall_monotone_in_nprobe_and_work_grows(setup):
    m, X, Q, idx = setup
    for q in Q:
        exact = m.exact_top_k(X, q, 10)
        prev_r, prev_s = -1.0, 0
        for nprobe in (1, 2, 4, 8, 16, 32):
            got, scanned = idx.search(q, 10, nprobe)
            r = m.recall_at_k(got, exact)
            assert r >= prev_r and scanned >= prev_s
            prev_r, prev_s = r, scanned
    mean1 = np.mean([m.recall_at_k(idx.search(q, 10, 1)[0], m.exact_top_k(X, q, 10)) for q in Q])
    assert mean1 < 0.9                                     # nprobe=1 really is approximate


def test_search_scans_only_probed_lists(setup):
    m, X, Q, idx = setup
    q = Q[0]
    best = int(np.argmax(idx.centroids @ q))
    got, scanned = idx.search(q, 5, nprobe=1)
    assert scanned == len(idx.lists[best]) and set(got) <= set(idx.lists[best].tolist())
