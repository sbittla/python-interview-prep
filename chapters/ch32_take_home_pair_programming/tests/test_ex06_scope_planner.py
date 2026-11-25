import pytest

M = "ex06_scope_planner"


def names(tasks):
    return [t.name for t in tasks]


def test_demo_budget_180(load):
    m = load(M)
    p = m.plan(m.TASKS, 180)
    assert (p.reserve, p.used, p.slack) == (45, 130, 5)
    assert names(p.in_scope)[-1] == "JSON output"
    assert names(p.deferred) == ["month filter", "multi-currency", "--strict flag"]


def test_greedy_lets_a_later_small_task_in(load):
    m = load(M)
    p = m.plan(m.TASKS, 170)                      # build budget 128, musts 115
    assert names(p.in_scope)[4:] == ["--strict flag"]
    assert p.slack == 3


def test_should_before_could_regardless_of_list_order(load):
    m = load(M)
    tasks = [m.Task("c", 10, "could"), m.Task("m", 10, "must"), m.Task("s", 10, "should")]
    p = m.plan(tasks, 40)                          # reserve 10, build 30: everything fits
    assert names(p.in_scope) == ["m", "s", "c"]
    p = m.plan(tasks, 26)                          # reserve 6, build 20
    assert names(p.in_scope) == ["m", "s"] and names(p.deferred) == ["c"]


def test_musts_too_big_raises(load):
    m = load(M)
    with pytest.raises(m.ScopeError, match="need 115 min, build budget is 90 min"):
        m.plan(m.TASKS, 120)


def test_bad_priority_and_empty(load):
    m = load(M)
    with pytest.raises(ValueError, match="unknown priority 'nice'"):
        m.plan([m.Task("x", 5, "nice")], 60)
    p = m.plan([], 60, reserve_pct=0)
    assert (p.in_scope, p.deferred, p.reserve, p.slack) == ([], [], 0, 60)


def test_readme_scope(load):
    m = load(M)
    p = m.plan([m.Task("core", 30, "must"), m.Task("json", 60, "could")], 80)
    assert m.readme_scope(p) == ("## Scope\n\n- [x] core\n\nNot done (next steps):\n"
                                 "- [ ] json (~60 min)")
    assert m.readme_scope(m.plan([m.Task("core", 30, "must")], 80)) == "## Scope\n\n- [x] core"


def test_reserve_rounds_down(load):
    m = load(M)
    p = m.plan(m.TASKS, 171)                      # 171 * 25 / 100 = 42.75
    assert p.reserve == 42 and p.slack == 171 - 42 - p.used
    assert m.plan(m.TASKS, 180, reserve_pct=10).reserve == 18
