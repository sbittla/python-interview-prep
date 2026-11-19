import random

import pytest


@pytest.mark.parametrize("meetings, rooms", [
    ([[0, 30], [5, 10], [15, 20]], 2),
    ([[1, 2], [2, 3]], 1),                       # touching: end before start
    ([[1, 5], [2, 6], [4, 8], [6, 9]], 3),
    ([[1, 2], [1, 2], [1, 2]], 3),
    ([], 0),
])
def test_rooms_all_rungs(load, meetings, rooms):
    m = load("ex09_meeting_rooms")
    assert m.min_rooms(meetings) == m.min_rooms_heap(meetings) == m.min_rooms_brute(meetings) == rooms


def test_busiest_and_wrong_tie(load):
    m = load("ex09_meeting_rooms")
    assert m.busiest([[1, 5], [2, 6], [4, 8], [6, 9]]) == (3, 4)
    assert m.busiest([]) == (0, None)
    assert m.sweep_wrong_tie([[1, 2], [2, 3]]) == 2 != m.min_rooms([[1, 2], [2, 3]])


def test_assign_rooms(load):
    m = load("ex09_meeting_rooms")
    assert m.assign_rooms([[0, 30], [5, 10], [15, 20]]) == [0, 1, 1]
    assert m.assign_rooms([]) == []


def test_random_against_brute(load):
    m = load("ex09_meeting_rooms")
    rng = random.Random(9)
    for _ in range(300):
        meetings = []
        for _ in range(rng.randint(0, 9)):
            s = rng.randint(0, 10)
            meetings.append([s, s + rng.randint(1, 4)])
        rooms = m.min_rooms_brute(meetings)
        assert m.min_rooms(meetings) == m.min_rooms_heap(meetings) == rooms
        count, when = m.busiest(meetings)
        assert count == rooms
        if meetings:
            assert sum(s <= when < e for s, e in meetings) == count
        assign = m.assign_rooms(meetings)
        assert len(set(assign)) == rooms
        for i, (s1, e1) in enumerate(meetings):          # same room => no overlap
            for j in range(i + 1, len(meetings)):
                s2, e2 = meetings[j]
                if assign[i] == assign[j]:
                    assert e1 <= s2 or e2 <= s1
