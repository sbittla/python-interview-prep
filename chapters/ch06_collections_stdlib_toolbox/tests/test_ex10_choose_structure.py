import pytest


@pytest.mark.parametrize("need, tool", [
    ("membership", "set"), ("fifo queue", "collections.deque"),
    ("count items", "collections.Counter"), ("group by key", "collections.defaultdict"),
    ("repeated min", "heapq"), ("sorted inserts", "bisect.insort"),
    ("index access", "list"), ("lru order", "collections.OrderedDict"),
])
def test_recommend(load, need, tool):
    assert load("ex10_choose_structure").recommend(need) == tool


@pytest.mark.parametrize("need", ["teleport", "", "Membership"])
def test_unknown_need(load, need):
    with pytest.raises(ValueError):
        load("ex10_choose_structure").recommend(need)


def test_race_returns_booleans(load):
    result = load("ex10_choose_structure").race(500)      # small n: check shape, not speed
    assert set(result) == {"set beats list for membership", "deque beats list for popleft",
                           "bisect beats linear scan for rank"}
    assert all(isinstance(v, bool) for v in result.values())


def test_large_n_set_beats_list(load):
    result = load("ex10_choose_structure").race(5_000)
    assert result["set beats list for membership"] is True
