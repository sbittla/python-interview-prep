import random

import pytest


def test_examples(load):
    m = load("ex11_doubly_linked_list")
    dl = m.DList()
    a = dl.push_back("a", 1)
    b = dl.push_back("b", 2)
    dl.move_to_front(b)
    assert list(dl) == [("b", 2), ("a", 1)]
    assert dl.pop_back() is a
    assert len(dl) == 1


def test_empty_and_single(load):
    m = load("ex11_doubly_linked_list")
    dl = m.DList()
    assert list(dl) == [] and list(reversed(dl)) == [] and len(dl) == 0
    with pytest.raises(IndexError):
        dl.pop_back()
    x = dl.push_front("x", 0)
    dl.move_to_front(x)
    assert list(dl) == [("x", 0)]
    dl.remove(x)
    assert list(dl) == [] and x.prev is None and x.next is None
    dl.push_back("y", 1)
    assert list(dl) == [("y", 1)]


def test_random_against_list_backed(load):
    m = load("ex11_doubly_linked_list")
    rng = random.Random(1312)
    for _ in range(100):
        dl, ref = m.DList(), m.ListBackedDList()
        handles = {}                                  # key -> (dnode, ref item)
        key = 0
        for _ in range(60):
            op = rng.choice(["front", "back", "remove", "move", "pop"])
            if op in ("front", "back") or not handles:
                key += 1
                if op == "back":
                    handles[key] = (dl.push_back(key, -key), ref.push_back(key, -key))
                else:
                    handles[key] = (dl.push_front(key, -key), ref.push_front(key, -key))
            elif op == "remove":
                k = rng.choice(sorted(handles))
                d, r = handles.pop(k)
                dl.remove(d)
                ref.remove(r)
            elif op == "move":
                k = rng.choice(sorted(handles))
                dl.move_to_front(handles[k][0])
                ref.move_to_front(handles[k][1])
            else:
                node, item = dl.pop_back(), ref.pop_back()
                assert node.key == item[0]
                handles.pop(node.key)
            assert list(dl) == list(ref)
            assert list(reversed(dl)) == list(ref)[::-1]
            assert len(dl) == len(ref)
