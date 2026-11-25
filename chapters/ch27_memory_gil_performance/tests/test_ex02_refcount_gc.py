import gc

import pytest


@pytest.mark.parametrize("scenario, expected", [
    ("plain", ["freed:a", "collect"]),
    ("chain", ["freed:a", "freed:b", "freed:c", "collect"]),
    ("weak", ["freed:a", "freed:b", "collect"]),
    ("self", ["collect", "freed:a"]),
    ("pair", ["collect", "freed:a", "freed:b"]),
])
def test_lifetimes(load, scenario, expected):
    assert load("ex02_refcount_gc").lifetime(scenario) == expected


def test_collector_state_restored(load):
    m = load("ex02_refcount_gc")
    assert gc.isenabled()
    m.lifetime("pair")
    assert gc.isenabled()
    gc.disable()
    try:
        m.lifetime("plain")
        assert not gc.isenabled()          # restores the caller's state, does not force-enable
    finally:
        gc.enable()


def test_unknown_scenario_restores_collector(load):
    m = load("ex02_refcount_gc")
    with pytest.raises(ValueError):
        m.lifetime("ring")
    assert gc.isenabled()
