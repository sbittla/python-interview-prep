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


def test_state_lives_in_closure_cells(load):
    m = load("ex10_closures_nonlocal")
    inc, cur = m.solve(0, 2)
    assert inc.__closure__ is not None          # state is captured, not global
    inc()
    assert cur() == 2
    avg = m.make_averager()
    for x in range(100):
        avg(x)
    # O(1) memory: no captured list/dict that grows with the number of values seen
    assert not any(isinstance(c.cell_contents, (list, dict, tuple)) for c in avg.__closure__)
