import pytest


def test_above_avg_both_forms(load):
    m = load("ex09_subqueries_ctes")
    conn = m.make_db()
    expected = [("Ada", 200), ("Cy", 210), ("Ed", 130), ("Gil", 130)]
    assert m.above_dept_avg(conn) == expected == m.above_dept_avg_cte(conn)
    conn.execute("INSERT INTO employees VALUES (9, 'Ivo', 3, 1, 999)")    # sole member of Legal
    assert m.above_dept_avg(conn) == expected == m.above_dept_avg_cte(conn)


@pytest.mark.parametrize("n, salary", [(1, 210), (2, 200), (3, 150), (4, 130), (5, 120),
                                       (6, 90), (7, None), (99, None)])
def test_nth_highest_distinct(load, n, salary):
    m = load("ex09_subqueries_ctes")
    assert m.nth_highest_salary(m.make_db(), n) == salary   # 130 appears twice, counted once


def test_non_managers(load):
    m = load("ex09_subqueries_ctes")
    conn = m.make_db()
    assert m.non_managers(conn) == ["Ben", "Cy", "Ed", "Flo", "Gil"]
    assert m.non_managers_not_in(conn) == []                 # the NULL trap


def test_org_chart(load):
    m = load("ex09_subqueries_ctes")
    chart = m.org_chart(m.make_db())
    assert chart[0] == (0, "Ada", "Ada")
    assert (2, "Ed", "Ada/Di/Ed") in chart and (1, "Flo", "Ada/Flo") in chart
    assert len(chart) == 7 and [p for _, _, p in chart] == sorted(p for _, _, p in chart)
    assert max(d for d, _, _ in chart) == 2


def test_manager_chain_terminates_on_cycle(load):
    m = load("ex09_subqueries_ctes")
    conn = m.make_db()
    assert m.manager_chain(conn, "Ed") == ["Ed", "Di", "Ada"]
    assert m.manager_chain(conn, "Ada") == ["Ada"]
    assert m.manager_chain(conn, "Nobody") == []
    conn.execute("UPDATE employees SET manager_id = 5 WHERE id = 1")    # Ada -> Ed: cycle
    assert m.manager_chain(conn, "Ed") == ["Ed", "Di", "Ada"]
    assert m.manager_chain(conn, "Di") == ["Di", "Ada", "Ed"]


def test_union_does_not_stop_cycle_with_depth_column(load):
    # bounded at depth 10 in the query, so this can never hang
    assert load("ex09_subqueries_ctes").cycle_demo() == (11, 2)
