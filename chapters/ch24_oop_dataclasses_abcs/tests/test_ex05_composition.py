import pytest


@pytest.fixture
def m(load):
    return load("ex05_composition")


def test_example(m):
    a = m.AuditedList()
    a.append(1)
    a.extend([2, 3])
    a.pop()
    assert repr(a) == "AuditedList([1, 2], added=3)"


def test_every_entry_point_counts(m):
    a = m.AuditedList([9])
    a.append(1)
    a.extend(iter([2, 3]))
    a.insert(0, 0)
    same = a
    a += [4]
    assert a is same                       # __iadd__ returned self
    assert list(a) == [0, 9, 1, 2, 3, 4] and a.added == 6 and len(a) == 6
    assert a[0] == 0 and a[-1] == 4


def test_inheritance_rung_undercounts(m):
    inh = m.InheritedAuditList()
    inh.append(1)
    inh.extend([2, 3])
    inh.insert(0, 0)
    inh += [4]
    assert len(inh) == 5 and inh.added == 1


def test_not_a_list_subclass(m):
    assert not isinstance(m.AuditedList(), list)
    assert not hasattr(m.AuditedList(), "sort")


def test_stack(m):
    s = m.Stack()
    assert not s and len(s) == 0
    for x in "abc":
        s.push(x)
    assert s and s.peek() == "c" and s.pop() == "c" and len(s) == 2
    for name in ("insert", "append", "__getitem__", "sort"):
        assert not hasattr(s, name)


@pytest.mark.parametrize("op", ["pop", "peek"])
def test_empty_stack_raises(m, op):
    with pytest.raises(IndexError, match="empty stack"):
        getattr(m.Stack(), op)()


def test_documentation_userlist_vs_mutablesequence():
    """Documentation test (checks the stdlib claim in the hints; passes on stubs too)."""
    from collections import UserList
    from collections.abc import MutableSequence

    class U(UserList):
        added = 0

        def append(self, x):
            self.added += 1
            super().append(x)

    class MS(MutableSequence):
        def __init__(self):
            self._d, self.added = [], 0

        def __getitem__(self, i):
            return self._d[i]

        def __setitem__(self, i, v):
            self._d[i] = v

        def __delitem__(self, i):
            del self._d[i]

        def __len__(self):
            return len(self._d)

        def insert(self, i, v):
            self.added += 1
            self._d.insert(i, v)

    for obj, expected in ((U(), 1), (MS(), 4)):
        obj.append(1)
        obj.extend([2, 3])
        obj += [4]
        assert (len(obj), obj.added) == (4, expected)
