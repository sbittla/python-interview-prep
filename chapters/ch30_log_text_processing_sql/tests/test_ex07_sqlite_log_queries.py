import random
import sqlite3

import pytest


def rows_of(specs):
    return [("ip%d" % (i % 3), i, "GET", p, s, ms) for i, (p, s, ms) in enumerate(specs)]


def test_example(load):
    m = load("ex07_sqlite_log_queries")
    conn = m.make_db([("a", 0, "GET", "/x", 200, 10), ("b", 1, "GET", "/x", 503, 30)])
    assert m.path_report(conn, 1) == [("/x", 2, 20, 1)]


def test_having_and_order(load):
    m = load("ex07_sqlite_log_queries")
    conn = m.make_db(rows_of([("/b", 200, 1), ("/a", 500, 3), ("/b", 200, 2), ("/a", 200, 4),
                              ("/c", 200, 9)]))
    assert m.path_report(conn, 2) == [("/a", 2, 4, 1), ("/b", 2, 2, 0)]   # AVG 3.5 -> 4, 1.5 -> 2
    assert m.path_report(conn, 1)[-1] == ("/c", 1, 9, 0)
    assert m.path_report(conn, 3) == []


def test_client_errors(load):
    m = load("ex07_sqlite_log_queries")
    conn = m.make_db([("b", 0, "GET", "/", 404, 1), ("a", 1, "GET", "/", 401, 1),
                      ("b", 2, "GET", "/", 499, 1), ("c", 3, "GET", "/", 500, 1),
                      ("c", 4, "GET", "/", 399, 1)])
    assert m.client_errors(conn) == [("b", 2), ("a", 1)]


def test_injection_and_params(load):
    m = load("ex07_sqlite_log_queries")
    conn = m.make_db(rows_of([("/a", 200, 1), ("/o'k", 200, 1)]))
    assert m.find_by_path(conn, "x' OR '1'='1") == []
    assert m.find_by_path(conn, "/o'k") == [("ip1", 200)]   # quotes in data are fine


def test_insert_atomic_rolls_back(load):
    m = load("ex07_sqlite_log_queries")
    conn = m.make_db(rows_of([("/a", 200, 1)]))
    with pytest.raises(sqlite3.IntegrityError):
        m.insert_atomic(conn, [("z", 9, "GET", "/ok", 200, 1), ("z", 9, "GET", "/bad", 42, 1)])
    assert conn.execute("SELECT COUNT(*) FROM hits").fetchone()[0] == 1
    m.insert_atomic(conn, [("z", 9, "GET", "/ok", 200, 1)])
    assert conn.execute("SELECT COUNT(*) FROM hits").fetchone()[0] == 2


def test_random_sql_vs_python(load):
    m = load("ex07_sqlite_log_queries")
    rng = random.Random(7)
    for _ in range(50):
        rows = rows_of([(rng.choice(["/a", "/b", "/c"]), rng.choice([200, 404, 500, 503]),
                         rng.randint(0, 9)) for _ in range(rng.randint(0, 20))])
        k = rng.randint(1, 4)
        assert m.path_report(m.make_db(rows), k) == m.python_path_report(rows, k)


def test_data_file(load):
    m = load("ex07_sqlite_log_queries")
    rows = m.load_rows()
    conn = m.make_db(rows)
    assert m.path_report(conn, 10) == [("/login", 13, 95, 0), ("/static/app.js", 12, 155, 1)]
