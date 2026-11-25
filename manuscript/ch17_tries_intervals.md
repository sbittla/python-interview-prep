# Chapter 17. Tries and Intervals

★ Core · Tracks S, M, L · Study time ≈ 6 h · Prerequisites: Ch. 6 (`heapq`, `bisect`),
Ch. 15 (heaps)

**Learning objectives**

- Build a trie from memory and extend its walk with wildcards, per-node aggregates and grid
  backtracking.
- Fix the interval convention (closed or half-open) before coding, and sort by start to merge,
  by end to keep the most.
- Turn "how many at once" into a line sweep with the correct tie rule.

> **Recognise it**
>
> | Signal in the problem | Reach for |
> |---|---|
> | "Starts with", autocomplete, many words sharing prefixes | Trie |
> | Pattern with `.` wildcards; many words in one grid | Trie + DFS / backtracking |
> | Ranges, bookings, "union", "overlap", "gaps" | Sort by start, one pass |
> | "Fewest to remove", "most that fit" | Sort by end, greedy |
> | "How many at the same time", rooms, peak load, skyline | Line sweep (+ heap) |
>
> Constraint hint: 10⁴–10⁵ intervals plus an all-pairs check means "sort once, then scan".

## 17.1 Trie node design; insert, search, startsWith

A trie stores strings as a tree of characters: each edge is a letter, the root is the empty
string, and a flag marks nodes where a stored word ends. All words with prefix `p` live in the
subtree reached by walking `p`, so a prefix question costs one walk instead of a scan.

**Worked problem 1 — A prefix set.** *Rung 1:* a `set` answers `search` in O(L) average
(hashing), but `starts_with` scans every word, O(n·L). *Rung 2:* a trie makes every
operation O(L), independent of n — the reason to move up.

```python
class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_word = False


class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_word = True

    def _walk(self, s: str) -> TrieNode | None:
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.is_word

    def starts_with(self, prefix: str) -> bool:
        node = self._walk(prefix)
        return node is not None and (node.is_word or bool(node.children))


t = Trie()
for w in ["apple", "app", "apply", "bat"]:
    t.insert(w)
print(t.search("app"), t.search("ap"), t.starts_with("ap"), t.starts_with("c"))
```

```text
True False True False
```

**Delete with pruning.** Record `(parent, letter)` pairs on the way down, clear `is_word`, then
walk back up deleting childless nodes that end no other word. Clearing the flag alone leaves
dead branches: `starts_with("appl")` stays `True` after deleting `apple` and `apply`.
→ repo: `chapters/ch17_tries_intervals/solutions/ex01_trie_basics.py`

Space is O(total characters) nodes worst case, less when prefixes are shared. A `dict` of
children fits any alphabet; a 26-slot list (`ord(ch) - 97`) avoids hashing but allocates 26 slots
per node (repo: `ArrayTrie`). `__slots__` drops each node's `__dict__`, which matters with
millions of nodes. Edge cases: `starts_with("")` is `True` iff the trie is non-empty; deleting an
absent word or a mere prefix (`"ap"`) returns `False` and changes nothing. Follow-ups: a count
instead of a bool for multisets; a radix tree (merged single-child chains) for large dictionaries.

## 17.2 Word dictionary with wildcards

`.` matches any one letter. A letter follows one child; a dot must try *every* child, so the
walk becomes a DFS. A dict-of-dicts trie with a `"$"` end marker is the compact interview form.

```python
def build(words: list[str]) -> dict:
    root: dict = {}
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = True                       # end-of-word marker
    return root


def search(root: dict, pattern: str) -> bool:
    stack = [(root, 0)]                        # (trie node, index into pattern)
    while stack:
        node, i = stack.pop()
        if i == len(pattern):
            if "$" in node:
                return True
            continue                           # a prefix, not a word: keep looking
        if pattern[i] == ".":
            stack.extend((child, i + 1) for ch, child in node.items() if ch != "$")
        elif pattern[i] in node:
            stack.append((node[pattern[i]], i + 1))
    return False


root = build(["bad", "dad", "mad", "bat"])
print([search(root, p) for p in ["pad", ".ad", "b..", "b.", "..t"]])
```

```text
[False, True, True, False, True]
```

Ladder: compare with every word, O(n·L) per query → bucket words by length (same worst case) →
trie, O(L) without dots and O(26^d · L) worst case with d dots, independent of n. Why move up:
shared prefixes are compared once, and a mismatch prunes a whole subtree. **Wrong but
tempting:** returning `True` whenever the walk ends on a node (`"b."` matches the prefix `ba`);
exploring only the first child of a dot.

## 17.3 Autocomplete / prefix counting

**Prefix counting:** store at each node `passes`, the number of words in its subtree;
`count_prefix(p)` walks `p` and returns it, O(|p|). Check the word is new before incrementing, or
duplicates inflate every count on the path. **Top-3 suggestions per keystroke:** insert words in
sorted order and let each node keep the first three that pass through — its three smallest.

```python
class Node:
    __slots__ = ("children", "top")

    def __init__(self) -> None:
        self.children: dict[str, "Node"] = {}
        self.top: list[str] = []               # up to 3 smallest words in this subtree


def suggestions(products: list[str], typed: str) -> list[list[str]]:
    root = Node()
    for word in sorted(products):              # sorted insert => first 3 seen are smallest
        node = root
        for ch in word:
            node = node.children.setdefault(ch, Node())
            if len(node.top) < 3:
                node.top.append(word)
    out, node = [], root
    for ch in typed:                           # one step per keystroke, never restart
        node = node.children.get(ch) if node else None
        out.append(list(node.top) if node else [])
    return out


for row in suggestions(["mobile", "mouse", "moneypot", "monitor", "mousepad"], "mox"):
    print(row)
```

```text
['mobile', 'moneypot', 'monitor']
['mobile', 'moneypot', 'monitor']
[]
```

Ladder per keystroke: filter and sort all products, O(n log n) → sort once, then
`bisect_left(products, prefix)` finds the contiguous block of matches, O(L log n) → trie, one
edge per keystroke after a sort (O(L·n log n)) plus an O(total chars) build. The
`bisect` rung is often the best interview answer; the trie wins for prefix counts, updates, or
strictly incremental input. Ranking and caching: the autocomplete service (→ §29.10).
→ repo: `chapters/ch17_tries_intervals/solutions/ex03_prefix_suggestions.py`

## 17.4 Word search II (trie + backtracking) ◆

Find every listed word traceable through adjacent grid cells, each cell used once per word.

Rung 1 runs single-word search (→ §18.6) once per word: O(W·R·C·3^L), re-exploring the same
paths for every word that shares a prefix. Rung 2 runs **one** DFS per cell that walks grid and
trie together: O(R·C·4·3^(L−1)) worst case, independent of W, plus O(ΣL) to build the trie.
Rung 3 adds pruning — same bound,
fewer calls once words are found (the repo counts them).

The DFS, with the word stored at its end node: `node = parent.get(board[r][c])`; return if
missing (no word continues this way — the whole gain). If `node` holds a word, record it and
clear it. Mark the cell `"#"` (no trie edge matches it), recurse into the four neighbours,
restore the letter, then `del parent[letter]` if `node` is now empty.
**Wrong but tempting:** stopping at the first word on a path (`oat` and `oath` share one); not
clearing the word, so it is reported once per path; forgetting to restore the cell.
→ repo: `chapters/ch17_tries_intervals/solutions/ex04_word_search_ii.py`

## 17.5 Interval basics: sorting by start

Most interval bugs are an off-by-one at a touching endpoint, so fix the convention first.

| Convention | `a` and `b` overlap when | `[1, 2]` vs `[2, 3]` |
|---|---|---|
| Closed `[s, e]` (integer ranges) | `a[0] <= b[1] and b[0] <= a[1]` | overlap |
| Half-open `[s, e)` (meetings, bookings) | `a[0] < b[1] and b[0] < a[1]` | disjoint |

The test negates "one ends before the other starts", so nesting needs no special case. Sorting
by start shrinks "compare with everyone" to "compare with the last one" (§17.6) or "with the
earliest-ending one" (§17.8); greedy selection sorts by end (§17.7).

## 17.6 Merge intervals, insert interval

**Worked problem 2 — Merge** closed intervals. *Rung 1:* connected components of the overlap
graph, O(n²) pairs. *Rung 2:* sort by start; each interval extends the last output interval or
starts a new one, O(n log n) — after the sort only one candidate can overlap.

**Worked problem 3 — Insert** into a sorted, disjoint list. Re-merging is O(n log n); three
phases are O(n): copy what ends before `new`, absorb what starts by its end, copy the rest.

```python
def merge(intervals: list[list[int]]) -> list[list[int]]:
    out: list[list[int]] = []
    for start, end in sorted(intervals):
        if out and start <= out[-1][1]:            # closed: touching merges
            out[-1][1] = max(out[-1][1], end)      # max: the new one may be nested
        else:
            out.append([start, end])               # fresh list: never alias input
    return out


def insert(intervals: list[list[int]], new: list[int]) -> list[list[int]]:
    lo, hi = new
    out, i, n = [], 0, len(intervals)
    while i < n and intervals[i][1] < lo:          # 1: entirely to the left
        out.append(list(intervals[i]))
        i += 1
    while i < n and intervals[i][0] <= hi:         # 2: overlaps or touches new
        lo, hi = min(lo, intervals[i][0]), max(hi, intervals[i][1])
        i += 1
    out.append([lo, hi])
    out.extend(list(iv) for iv in intervals[i:])   # 3: entirely to the right
    return out


print(merge([[1, 3], [8, 10], [2, 6], [15, 18]]), merge([[1, 10], [2, 3]]))
print(insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]),
      insert([[1, 2], [5, 6]], [2, 5]), insert([], [4, 7]))
```

```text
[[1, 6], [8, 10], [15, 18]] [[1, 10]]
[[1, 2], [3, 10], [12, 16]] [[1, 6]] [[4, 7]]
```

**Wrong but tempting:** `out[-1][1] = end` shrinks the union on nesting; comparing with the
previous *input* interval instead of the last *output*; phase 1 with `<=` leaves `[1, 2]`
touching `[2, 5]`. Half-open input: `start < out[-1][1]` (the repo's `merge_touching=False`).
Edge cases: empty list; `new` before, after, or covering everything. Follow-ups: remove an
interval (may split one in two); many inserts → a sorted container or an interval tree.
→ repo: `chapters/ch17_tries_intervals/solutions/ex05_merge_intervals.py`,
`chapters/ch17_tries_intervals/solutions/ex06_insert_interval.py`

## 17.7 Interval intersection and non-overlapping intervals

**Intersection** of two sorted, internally disjoint lists: two closed intervals meet in
`[max(starts), min(ends)]` when non-empty. Whichever ends first cannot meet anything later in the
other list, so advance it: O(m + n) instead of all O(mn) pairs.

```python
def intersect(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        lo, hi = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        if lo <= hi:                               # closed: one shared point counts
            out.append([lo, hi])
        if a[i][1] < b[j][1]:                      # the earlier end is finished
            i += 1
        else:
            j += 1
    return out


print(intersect([[0, 2], [5, 10], [13, 23], [24, 25]], [[1, 5], [8, 12], [15, 24], [25, 26]]))
```

```text
[[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]]
```

`lo < hi` would drop `[5, 5]` — right only for half-open input.

**Worked problem 4 — Fewest removals** = n − most non-overlapping kept. Rungs:
every subset, O(2ⁿ·n²) → DP sorted by end with `bisect`, O(n log n) but more code → greedy:
sort by **end**, keep each interval compatible with the last kept, O(n log n). The earliest end
leaves the most room (exchange-argument proof: §20.2).

```python
def min_removals(intervals: list[list[int]], closed: bool = False) -> int:
    removed, last_end = 0, None
    for s, e in sorted(intervals, key=lambda iv: iv[1]):
        if last_end is None or (s > last_end if closed else s >= last_end):
            last_end = e                           # keep it
        else:
            removed += 1
    return removed


iv = [[1, 2], [2, 3], [3, 4], [1, 3]]
print(min_removals(iv), min_removals(iv, closed=True), min_removals([[1, 10], [2, 3], [4, 5]]))
```

```text
1 2 1
```

**Wrong but tempting:** sorting by start and keeping whatever comes first — the repo's
`wrong_by_start` removes 3 from `[[1, 10], [2, 3], [4, 5], [6, 7]]` where 1 suffices; sorting by
length (`[1, 5], [4, 7], [6, 10]` keeps only the middle one). Edge cases: empty input,
duplicates (keep one copy), touching endpoints (the `closed` switch). Follow-ups: minimum arrows
to burst balloons (→ §20.2); weighted intervals need the DP rung.
→ repo: `chapters/ch17_tries_intervals/solutions/ex08_non_overlapping.py`

## 17.8 Meeting rooms with heaps (line-sweep scheduling)

Minimum rooms for half-open meetings with `start < end`. Rung 1 counts the meetings containing
each start, O(n²); the O(n log n) heap rung is in §15.8. For the count alone, two sorted arrays
replace the heap: before counting each start, release every meeting ended by then.

```python
def min_rooms(meetings: list[list[int]]) -> int:
    starts = sorted(s for s, _ in meetings)
    ends = sorted(e for _, e in meetings)
    rooms = best = j = 0
    for s in starts:
        while ends[j] <= s:                        # half-open: end at s frees a room
            rooms -= 1
            j += 1
        rooms += 1
        best = max(best, rooms)
    return best


print(min_rooms([[0, 30], [5, 10], [15, 20]]), min_rooms([[1, 2], [2, 3]]), min_rooms([]))
```

```text
2 1 0
```

O(n log n) for the sorts, O(n) extra, no heap. `ends[j]` cannot run off the end: a meeting that
ended by `s` started before `s` and was already counted. It cannot say *which* room a meeting
uses; for that the heap stores `(end, room)` and a second heap holds freed room numbers (repo:
`assign_rooms`). **Wrong but tempting:** `<` instead of `<=` (closed convention: back-to-back
meetings get two rooms); the most overlaps of any single meeting — overlap is not transitive, so
that overestimates.
→ repo: `chapters/ch17_tries_intervals/solutions/ex09_meeting_rooms.py`

## 17.9 Line sweep technique ◆

Turn intervals into endpoint events, sort, and walk left to right with a running state that
changes only at events: 2n steps after an O(n log n) sort.

```python
def busiest(meetings: list[list[int]]) -> tuple[int, int | None]:
    events = sorted([(s, +1) for s, _ in meetings] + [(e, -1) for _, e in meetings])
    best, when, cur = 0, None, 0
    for t, delta in events:                        # at equal t, -1 sorts before +1
        cur += delta
        if cur > best:
            best, when = cur, t
    return best, when


print(busiest([[1, 5], [2, 6], [4, 8], [6, 9]]), busiest([[1, 2], [2, 3]]))
```

```text
(3, 4) (1, 1)
```

**The tie rule encodes the convention.** `(2, -1)` sorts before `(2, +1)`, so an end at 2 is
processed before a start at 2 — right for half-open meetings; starts first suits closed ones.

**Skyline** (buildings `(left, right, height)`, half-open in x): the state is the *tallest*
active building — a max-heap of `(-height, right)`. Removing an arbitrary heap entry is O(n), so
delete **lazily**: at each x, push every building starting there, pop while the top's
`right <= x`, and emit `[x, height]` only when the height changed. Each building is pushed and
popped at most once: O(n log n), versus O(n²) for recomputing the max at every edge.
→ repo: `chapters/ch17_tries_intervals/solutions/ex10_skyline.py`

## 17.10 Practice set

Work the exercises in order; tests cross-check every rung on seeded random inputs. More
interval problems: Chapter 45, numbers 121–127.

## Interviewer's view

- **Convention first:** "Do touching intervals overlap?" decides every `<` vs `<=`.
- **Justify the sort key:** start to merge and schedule; end to keep the most (exchange argument).
- **Trie trade-off:** O(L) queries, many small objects; sort + `bisect` is lighter.

## Exercises

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Trie with delete and pruning; array trie | ★ | trie |
| ex02 | Word dictionary with `.` wildcards | ★ | trie + DFS |
| ex03 | Prefix counting and top-3 suggestions | ★ | trie aggregates; bisect |
| ex04 | Word Search II | ◆ | trie + backtracking |
| ex05 | Merge intervals (touching switch) | ★ | sort by start |
| ex06 | Insert an interval | ★ | three-phase scan |
| ex07 | Intersection of two interval lists | ★ | two pointers |
| ex08 | Fewest removals for non-overlapping | ★ | sort by end, greedy |
| ex09 | Meeting rooms: count, busiest, assignment | ★ | heap; two pointers; sweep |
| ex10 | The skyline | ◆ | sweep + lazy max-heap |

Index: `chapters/ch17_tries_intervals/README.md`.

## Checkpoint quiz

1. Why must `search` check `is_word`?
2. Worst-case cost of a wildcard search with d dots, and why is it independent of n?
3. In merge intervals, why `max(out[-1][1], end)` rather than `end`?
4. To keep the most non-overlapping intervals, why sort by end, not start?
5. In a half-open event sweep, which event goes first at equal times?

<details>
<summary>Answers</summary>

1. Every prefix of a stored word has a path: `ap` exists for `app` but is not a word.
2. O(26^d · L): each dot branches into at most 26 children; other words are never touched.
3. The current interval may be nested in the last one (`[1, 10]`, `[2, 3]`); `end` would shrink it.
4. The earliest end leaves the most room; by start, one long early interval blocks many short ones.
5. The end, so a room freed at t can host a meeting starting at t; `(t, -1)` sorts before `(t, +1)`.

</details>

## Summary card

- **Trie:** `children` + `is_word`; every operation O(L); delete prunes bottom-up.
- **Wildcards:** a dot pushes every child. **Autocomplete:** per-node counts and top-3, or `bisect`.
- **Word Search II:** one DFS per cell over grid + trie; clear found words, prune empty leaves.
- **Merge:** sort by start, extend with `max`. **Insert:** three phases, O(n).
- **Intersection:** advance the earlier end, O(m + n). **Fewest removals:** sort by end.
- **Rooms:** heap of ends or two sorted arrays; release `end <= start` first.
- **Sweep:** `(t, ±1)` events, ends first for half-open; skyline adds a lazy max-heap.
