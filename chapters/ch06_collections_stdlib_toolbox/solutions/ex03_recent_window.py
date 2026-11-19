"""
Exercise 03 — Recent-Items Windows with deque and OrderedDict  [Tier: ★ Core]
Chapter 06 · Pattern: deque sliding window, OrderedDict recency · Target time: 20 min

Problem
-------
Implement three small "recent things" helpers.

1. `HitCounter(window)` — `hit(t)` records an event at integer second t
   (calls arrive with non-decreasing t); `count(t)` returns the number of hits
   in the half-open interval (t - window, t].
2. `RecentlyViewed(capacity)` — `view(item)` records that an item was opened;
   `items()` returns at most `capacity` DISTINCT items, most recent first.
3. `moving_average(values, k)` — list of the averages of each full window of
   k consecutive values (length len(values) - k + 1; empty if k > len(values)).

Examples
--------
>>> hc = HitCounter(300); hc.hit(1); hc.hit(2); hc.hit(300); hc.count(300), hc.count(301)
(3, 2)
>>> rv = RecentlyViewed(2); rv.view("a"); rv.view("b"); rv.view("a"); rv.items()
['a', 'b']
>>> moving_average([1, 2, 3, 4], 2)
[1.5, 2.5, 3.5]

Constraints
-----------
- Up to 10**5 operations; each should be amortised O(1). k >= 1.

Approach ladder
---------------
1. Brute force — plain lists: `count` scans every hit ever recorded (O(n));
   recency uses `list.remove` + `insert(0, x)` (O(capacity)); the moving
   average re-sums each window (O(n*k)).
2. Improved   — expire old hits with `list.pop(0)`: memory stays bounded but
   every pop shifts the whole list, O(n) per pop (→ §7.15).
3. Optimal    — `deque.popleft()` is O(1); `OrderedDict.move_to_end` and
   `popitem(last=False)` are O(1); a running sum over a `deque(maxlen=k)` makes
   the moving average O(n) total.

Hints
-----
- Expire from the left while `hits[0] <= t - window`.
- `deque(maxlen=k)` silently drops from the opposite end when full, so read
  `window[0]` BEFORE appending.

Follow-ups
----------
- Many hits per second: store (t, count) pairs to bound memory.
- RecentlyViewed plus O(1) lookup and eviction is an LRU cache (→ Ch 29).
"""
from __future__ import annotations

from collections import OrderedDict, deque


class HitCounter:
    def __init__(self, window: int) -> None:
        self.window = window
        self.hits: deque[int] = deque()

    def _expire(self, t: int) -> None:
        while self.hits and self.hits[0] <= t - self.window:
            self.hits.popleft()                     # O(1), unlike list.pop(0)

    def hit(self, t: int) -> None:
        self._expire(t)
        self.hits.append(t)

    def count(self, t: int) -> int:
        self._expire(t)
        return len(self.hits)


class RecentlyViewed:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.order: OrderedDict[str, None] = OrderedDict()

    def view(self, item: str) -> None:
        self.order[item] = None
        self.order.move_to_end(item)                # newest at the right end
        if len(self.order) > self.capacity:
            self.order.popitem(last=False)          # evict the oldest, O(1)

    def items(self) -> list[str]:
        return list(reversed(self.order))


def brute_force_moving_average(values: list[float], k: int) -> list[float]:
    return [sum(values[i:i + k]) / k for i in range(len(values) - k + 1)]


def moving_average(values: list[float], k: int) -> list[float]:
    window: deque[float] = deque(maxlen=k)
    total = 0.0
    out: list[float] = []
    for v in values:
        if len(window) == k:
            total -= window[0]                      # about to fall off the left
        window.append(v)
        total += v
        if len(window) == k:
            out.append(total / k)
    return out


def main() -> None:
    hc = HitCounter(300)
    for t in (1, 2, 3, 300):
        hc.hit(t)
    print("count(300) =", hc.count(300), "| count(301) =", hc.count(301),
          "| count(700) =", hc.count(700))
    rv = RecentlyViewed(3)
    for item in ["home", "cart", "shoes", "home", "socks"]:
        rv.view(item)
    print("recently viewed:", rv.items())
    vals = [3, 1, 4, 1, 5, 9, 2, 6]
    print("moving_average k=3:", moving_average(vals, 3))
    print("matches brute force:", moving_average(vals, 3) == brute_force_moving_average(vals, 3))
    print("k > len:", moving_average([1, 2], 3))
    d = deque([1, 2, 3], maxlen=3)
    d.append(4)
    print("deque(maxlen=3) after append(4):", list(d))


if __name__ == "__main__":
    main()
