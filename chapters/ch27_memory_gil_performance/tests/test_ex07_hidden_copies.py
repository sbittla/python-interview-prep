import pytest


@pytest.mark.parametrize("n", [0, 1, 10, 1000])
def test_variants_agree(load, n):
    m = load("ex07_hidden_copies")
    assert m.squares_gen(n) == m.squares_list(n) == sum(i * i for i in range(n))
    xs = list(range(n))
    assert m.drain_index(xs) == m.drain_slices(xs) == sum(xs)
    data = bytes(range(256)) * (n // 10 + 1)
    assert m.checksum_view(data, 7) == m.checksum_bytes(data, 7)


def test_peak_sees_temporaries(load):
    m = load("ex07_hidden_copies")
    assert m.peak(lambda: len([0] * 100_000)) > 700_000      # 100k pointers, freed before return
    assert m.peak(lambda: None) < 10_000


def test_report(load):
    assert load("ex07_hidden_copies").report(100_000) == {
        "generator vs list": (True, True),
        "memoryview vs bytes slice": (True, True),
        "index vs slice loop": (True, True)}


def test_overallocation(load):
    assert load("ex07_hidden_copies").overallocation() == {
        "append-built list is larger than list(range)": True, "resizes are rare": True}
