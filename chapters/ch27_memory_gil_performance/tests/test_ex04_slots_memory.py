def test_peak_bytes_grows_with_n(load):
    m = load("ex04_slots_memory")
    small = m.peak_bytes(lambda i: m.Plain(i, i), 2_000)
    large = m.peak_bytes(lambda i: m.Plain(i, i), 20_000)
    assert large > 5 * small


def test_compare(load):
    assert load("ex04_slots_memory").compare(20_000) == {
        "slots smaller": True, "saves at least 25%": True}


def test_behaviour(load):
    assert load("ex04_slots_memory").behaviour() == {
        "plain has __dict__": True,
        "slotted has __dict__": False,
        "slotted rejects new attribute": True,
        "slotted weakref-able": False,
        "dataclass(slots=True) has __dict__": False,
    }


def test_slotted_values_still_work(load):
    m = load("ex04_slots_memory")
    s = m.Slotted(3, 4)
    s.x = 10
    assert (s.x, s.y) == (10, 4)
