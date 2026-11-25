import random


def test_queries(load):
    m = load("ex08_sql_joins")
    conn = m.make_db()
    assert m.staff_with_dept(conn) == [("Ada", "Eng"), ("Ben", "Eng"), ("Cy", "Eng"),
                                       ("Di", "Sales"), ("Ed", "Sales")]
    assert m.headcount(conn) == [("Eng", 3), ("Legal", 0), ("Sales", 2)]
    assert m.empty_departments(conn) == ["Legal"]
    assert m.out_earn_manager(conn) == [("Cy", 210, "Ada", 200), ("Ed", 130, "Di", 120)]


def test_queries_after_changes(load):
    m = load("ex08_sql_joins")
    conn = m.make_db()
    conn.execute("INSERT INTO departments VALUES (4, 'Ops')")
    conn.execute("INSERT INTO employees VALUES (8, 'Hal', 3, 4, 500)")   # Legal, out-earns Di
    assert m.headcount(conn) == [("Eng", 3), ("Legal", 1), ("Ops", 0), ("Sales", 2)]
    assert m.empty_departments(conn) == ["Ops"]
    assert ("Hal", 500, "Di", 120) in m.out_earn_manager(conn)


def test_hash_join(load):
    m = load("ex08_sql_joins")
    left = [{"k": 1, "v": "a"}, {"k": None, "v": "b"}, {"k": 2, "v": "c"}, {"k": 1, "v": "d"}]
    right = [{"id": 1, "w": "x"}, {"id": 1, "w": "y"}, {"id": None, "w": "z"}]
    got = m.hash_join(left, right, "k", "id")
    assert sorted((l["v"], r["w"]) for l, r in got) == [("a", "x"), ("a", "y"), ("d", "x"), ("d", "y")]
    assert m.hash_join([], right, "k", "id") == [] and m.hash_join(left, [], "k", "id") == []


def test_hash_join_random(load):
    m = load("ex08_sql_joins")
    rng = random.Random(8)
    for _ in range(100):
        left = [{"k": rng.choice([None, 1, 2, 3])} for _ in range(rng.randint(0, 8))]
        right = [{"id": rng.choice([None, 1, 2, 4])} for _ in range(rng.randint(0, 8))]
        assert m.hash_join(left, right, "k", "id") == m.nested_loop_join(left, right, "k", "id")
