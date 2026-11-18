def test_counter(load):
    m = load("ex10_closures_nonlocal")
    inc, cur = m.solve(10, 5)
    assert cur() == 10
    assert (inc(), inc(), cur()) == (15, 20, 20)


def test_counters_are_independent(load):
    m = load("ex10_closures_nonlocal")
    inc_a, cur_a = m.solve()
    inc_b, cur_b = m.solve()
    inc_a()
    inc_a()
    inc_b()
    assert (cur_a(), cur_b()) == (2, 1)


def test_averager(load):
    m = load("ex10_closures_nonlocal")
    avg = m.make_averager()
    assert [avg(x) for x in (10, 20, 60, 10)] == [10.0, 15.0, 30.0, 25.0]
    other = m.make_averager()
    assert other(1) == 1.0
