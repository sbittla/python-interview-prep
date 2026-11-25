import pytest


@pytest.mark.parametrize("workload, expected", [
    ({}, "sequential"),
    ({"cpu_bound": True}, "sequential"),
    ({"parallel_worth_it": True, "cpu_bound": True}, "processes"),
    ({"parallel_worth_it": True, "cpu_bound": True, "gil_free": True}, "threads"),
    ({"parallel_worth_it": True}, "threads"),
    ({"parallel_worth_it": True, "many_connections": True}, "threads"),
    ({"parallel_worth_it": True, "async_libraries": True}, "threads"),
    ({"parallel_worth_it": True, "many_connections": True, "async_libraries": True}, "asyncio"),
    ({"parallel_worth_it": True, "cpu_bound": True, "many_connections": True,
      "async_libraries": True}, "processes"),
])
def test_choose(load, workload, expected):
    assert load("ex06_choose_concurrency").choose(workload) == expected


def test_overlap_demo(load):
    assert load("ex06_choose_concurrency").overlap_demo(10, 0.03) == {
        "threads overlap": True, "asyncio overlaps": True}
