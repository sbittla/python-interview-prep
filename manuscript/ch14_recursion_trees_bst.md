# Chapter 14. Recursion, Trees and BST

Tier ★ Core · Tracks S, M, L · Study time ≈ 8 h · Prerequisites: Ch 7 (§7.21 recursion limit), Ch 8 (Big-O), Ch 12 (stacks, queues)

**Learning objectives**

- Write recursion from base and recursive cases; convert it to an explicit stack when depth can
  exceed Python's recursion limit.
- Traverse a binary tree in all four orders, recursively and iteratively.
- Solve height, diameter, balance and path problems with one template: **return info up the tree**.
- Search, insert, delete and validate a BST; find kth smallest and successor.
- Rebuild and serialize trees; carry every template over to N-ary trees.

> **Recognise it**
>
> | Signal in the prompt | Reach for |
> |---|---|
> | "nested", "tree", "hierarchy", "expression", self-similar input | recursion (14.1); explicit stack if depth is unbounded (14.2) |
> | the same sub-call repeats with the same arguments | memoise (14.3) → DP (Ch 19) |
> | "level", "row by row", "minimum depth", "seen from the side" | BFS with `len(queue)` per level (14.6) |
> | "height", "diameter", "balanced", "longest path", "max path sum" | return info up the tree: postorder combine (14.7, 14.8) |
> | "ancestor", "distance between two nodes" | LCA (14.9) |
> | "sorted", "kth smallest", "next larger key", "valid BST" | BST inorder = sorted order; bounds passed down (14.12, 14.13) |
> | "rebuild", "encode", "send over the network" | traversal + null markers (14.10, 14.11) |

Listings run from `chapters/ch14_recursion_trees_bst/solutions/`, whose `treenode.py` provides
`TreeNode(val, left, right)`, `build(level_list)` (level order with `None` holes), `to_level`,
`render` (the ASCII drawings) and `inorder_values`.

## 14.1 Recursion fundamentals: base case, recursive case, call stack

A recursive function answers three questions: **what is the smallest input** (base case, answered
directly), **how does a bigger input shrink** (recursive case), and **how are the sub-answers
combined**. Each call gets its own frame (its own locals), which waits for the calls below it.
Ex01 weights every int in a nested list by its depth:

```python
def trace(nested, depth=1):
    pad = "  " * (depth - 1)
    print(f"{pad}call depth={depth} {nested}")
    total = 0
    for item in nested:
        if isinstance(item, list):            # recursive case: a sublist
            total += trace(item, depth + 1)
        else:                                 # base case: an int, weighted directly
            total += item * depth
    print(f"{pad}return {total}")
    return total

trace([1, [4, [6]]])
```

```text
call depth=1 [1, [4, [6]]]
  call depth=2 [4, [6]]
    call depth=3 [6]
    return 18
  return 26
return 27
```

The indentation *is* the call stack: three frames are alive at the deepest point. Stack memory is
O(depth), not O(n). CPython's default limit is 1,000 frames and there is no tail-call optimisation,
so a 5,000-deep input raises `RecursionError` (→ §7.21).

## 14.2 Recursion → iteration with an explicit stack

Anything recursion does, a loop with a list used as a stack can do: push what a frame would hold,
pop to "return". Push **iterators**:
each is a paused frame that remembers where it stopped.

```python
def flatten(nested):
    out, stack = [], [iter(nested)]
    while stack:
        for item in stack[-1]:
            if isinstance(item, list):
                stack.append(iter(item))      # "call": descend, resume parent later
                break
            out.append(item)
        else:                                 # iterator exhausted: "return"
            stack.pop()
    return out

deep = cur = [1]
for _ in range(4999):                         # [1, [1, [1, ...]]], 5,000 levels
    cur.append([1]); cur = cur[-1]
print(flatten([1, [2, [3, 4]], [], 5]), len(flatten(deep)))
```

```text
[1, 2, 3, 4, 5] 5000
```

Convert when depth can reach the input size (chains, user-supplied nesting, "what if the tree is
10⁵ nodes in a line?"); keep recursion when depth is O(log n) or constraints are small.

## 14.3 Memoisation preview (→ DP)

How many differently shaped BSTs hold keys 1..n? Choose a root r: the r − 1 smaller keys form the
left subtree and the n − r larger keys the right, independently, so
count(n) = Σ count(r − 1) · count(n − r). Plain recursion recomputes the same sizes;
caching by n fixes it.

```python
from functools import lru_cache

def count_naive(n, calls):
    calls[0] += 1
    if n <= 1:
        return 1
    return sum(count_naive(r - 1, calls) * count_naive(n - r, calls) for r in range(1, n + 1))

@lru_cache(maxsize=None)
def count_memo(n):
    if n <= 1:
        return 1
    return sum(count_memo(r - 1) * count_memo(n - r) for r in range(1, n + 1))

calls = [0]
print(count_naive(10, calls), "naive calls:", calls[0])
print(count_memo(10), count_memo.cache_info())
```

```text
16796 naive calls: 32805
16796 CacheInfo(hits=98, misses=11, maxsize=None, currsize=11)
```

Exponential calls (5 · 3ⁿ⁻² for n ≥ 2) become 11 distinct sub-problems, O(n²) total. Repeated
arguments → memoise; a bottom-up table is the next step: DP (→ §19.2). Ex02 also generates every tree, where the empty range must
return `[None]`, not `[]`. → repo: `chapters/ch14_recursion_trees_bst/solutions/ex02_count_bst_shapes.py`

## 14.4 Binary tree basics and representations

Each node has at most two children. **Depth** of a node = edges from the root; **height** of a tree
= nodes on the longest root-to-leaf path (some texts count edges; say which you use). A **full** tree has 0 or 2 children everywhere; **complete** fills every level
except possibly the last, left to right; **perfect** is full with all leaves at one depth;
**height-balanced** means sibling subtree heights differ by ≤ 1 at every node, so h = O(log n).

| Representation | Where you meet it | Notes |
|---|---|---|
| `TreeNode` objects with `left`/`right` | almost every interview | the default |
| level-order list with `None` holes | test inputs: `[1, None, 2, 3]` | parse with a queue (`build`) |
| array, children of `i` at `2i+1`, `2i+2` | heaps (→ Ch 15), complete trees | no pointers; gaps waste space otherwise |
| parent array / `dict` of children | org charts, file systems, N-ary input | becomes a graph problem (→ Ch 16) |

```python
from treenode import build, render, to_level

root = build([1, None, 2, 3])
print(render(root))
print(to_level(root), root.right.left)
```

```text
1__
   \
    2
   /
  3
[1, None, 2, 3] TreeNode(3)
```

## 14.5 DFS traversals: preorder, inorder, postorder (recursive and iterative)

| Order | Visit | Use it for |
|---|---|---|
| preorder | node, left, right | copying, serializing (14.11), passing info *down* (bounds, path so far) |
| inorder | left, node, right | BSTs: yields keys in sorted order (14.13) |
| postorder | left, right, node | computing from children: height, diameter, deleting a tree (14.7) |
| level order | by depth | "per level" questions (14.6) |

Recursively each order is three lines. Iteratively, preorder is "pop, record, push right then left".
Inorder and postorder share one walk: go left as far as possible, then inspect the stack top.

```python
from treenode import build

def inorder(root):
    out, stack, node = [], [], root
    while stack or node:
        while node:                           # go left as far as possible
            stack.append(node); node = node.left
        node = stack.pop()                    # leftmost unvisited node
        out.append(node.val)
        node = node.right                     # then its right subtree
    return out

def postorder(root):
    out, stack, node, last = [], [], root, None
    while stack or node:
        while node:
            stack.append(node); node = node.left
        top = stack[-1]
        if top.right and top.right is not last:
            node = top.right                  # right subtree not done yet
        else:
            out.append(top.val)               # both subtrees done
            last = stack.pop()
    return out

root = build([1, 2, 3, 4, 5, None, 6])
print(inorder(root), postorder(root))
```

```text
[4, 2, 5, 1, 3, 6] [4, 5, 2, 6, 3, 1]
```

Each is O(n) time and O(h) stack. Two shortcuts: postorder = reverse of (node, **right**, left), and
a "unified" stack of `(node, visited)` pairs that re-pushes a node between its children in any
order. Wrong-but-tempting: reversing ordinary preorder gives right, left, node, not postorder.
→ repo: `chapters/ch14_recursion_trees_bst/solutions/ex03_traversals.py`

## 14.6 BFS / level-order traversal and variants (zigzag, right view)

A `deque`; at the top of each round `len(queue)` is exactly the current level's width.

```python
from collections import deque
from treenode import build

def level_order(root):
    levels, queue = [], deque([root] if root else [])
    while queue:
        level = []
        for _ in range(len(queue)):          # freeze this level's size
            node = queue.popleft()
            level.append(node.val)
            queue.extend(c for c in (node.left, node.right) if c)
        levels.append(level)
    return levels

levels = level_order(build([1, 2, 3, 4, None, None, 5, 6]))
print(levels)
print("zigzag:", [lv if d % 2 == 0 else lv[::-1] for d, lv in enumerate(levels)])
print("right view:", [lv[-1] for lv in levels])
```

```text
[[1], [2, 3], [4, 5], [6]]
zigzag: [[1], [3, 2], [4, 5], [6]]
right view: [1, 3, 5, 6]
```

O(n) time, O(w) queue (w = widest level, ≤ (n+1)/2). Right view is *not* "walk right from the root":
here the 6 hangs on the left. A right-first DFS that records the first node at each new depth gives
the same view in O(h) space. `list.pop(0)` instead of `deque.popleft()` turns O(n) into O(n²).

## 14.7 Height, depth, diameter, balanced check

Depth flows **down** (pass `depth + 1` to children, preorder). Height flows **up**. Most "compute
something about the whole tree" questions use one template:

> **Return info up the tree.** Write `info(node)` returning a small tuple about the subtree rooted
> at `node`. Base case: the tuple for an empty tree. Recursive case: call both children
> **first** (postorder), then combine their tuples in O(1). Total: O(n) time, O(h) stack.

### Worked problem 1 — diameter and balanced, in one pass (ex05)

*Return the longest path between any two nodes (in edges) and whether every node's subtree heights
differ by at most 1.*

```text
          ____1          height 4, diameter 4 (path 6-4-2-3-5):
         /               the longest path never touches the root,
        2__              and node 1 is unbalanced (left height 3, right 0)
       /   \
      3     4
     /     /
    5     6
```

| Rung | Idea | Time / space | Why move up |
|---|---|---|---|
| 1 | At each node call `height()` on both children; diameter = max(hl + hr, child diameters) | O(n·h) time (O(n²) on a chain), O(h) stack | heights recomputed by every ancestor |
| 2 | **Info up the tree:** return `(height, diameter, balanced)` | O(n), O(h) stack | recursion depth on chains |
| 3 | Same combine step, explicit postorder stack + dict of results | O(n), O(n) | survives 10⁵-node chains |

```python
from treenode import build

def diameter_and_balanced(root):
    def info(node):
        """(height, best diameter inside this subtree, subtree balanced?)"""
        if node is None:
            return 0, 0, True
        lh, ld, lb = info(node.left)        # children first: postorder
        rh, rd, rb = info(node.right)
        h = 1 + max(lh, rh)
        d = max(ld, rd, lh + rh)            # best path inside, or through node
        b = lb and rb and abs(lh - rh) <= 1
        return h, d, b

    _, d, b = info(root)
    return d, b

for lst in ([1, 2, None, 3, 4, 5, None, 6], [1, 2, 3, 4, 5], [], [1, 2, None, 3]):
    print(f"{lst!s:<30} {diameter_and_balanced(build(lst))}")
```

```text
[1, 2, None, 3, 4, 5, None, 6] (4, False)
[1, 2, 3, 4, 5]                (3, True)
[]                             (0, True)
[1, 2, None, 3]                (2, False)
```

**Wrong-but-tempting.** (1) Diameter = `height(left) + height(right)` at the root: 3 here, not 4.
(2) Balanced checked at the root only. (3) A module-level `best` updated inside the helper instead of
a returned tuple is right on the first call, then stale:

```python
from ex05_diameter_balanced import diameter_global_bug
from treenode import build

print(diameter_global_bug(build([1, 2, None, 3, 4, 5, None, 6])),
      diameter_global_bug(build([1])))   # second answer should be 0
```

```text
4 4
```

A `nonlocal` reset per call also works; the returned tuple is cleaner. Edge cases: empty tree (0, True), single node (0, True), chains.

## 14.8 Path problems: path sum, max path sum ◆

**Root-to-leaf paths with sum = target.** Preorder DFS with *one* shared path list: append on entry,
pop on exit (backtracking, → §18.1); at a leaf with remaining 0, append `path[:]` (plain `path`
makes every result the same, finally empty, list). **Downward paths anywhere**: keep
a `Counter` of prefix sums on the current root path; paths ending here = count of
`running − target` (→ §10.9); O(n) instead of O(n·h).

### Worked problem 2 — maximum path sum (ex06)

*Values may be negative. Return the largest sum of any non-empty path; it may bend at any node.*

| Rung | Idea | Time | Why move up |
|---|---|---|---|
| 1 | Every pair of nodes, sum the path between them via a parent map | O(n²·h) | quadratic pairs |
| 2 | **Info up:** return (best *downward* gain from this node, best path anywhere below) | O(n), O(h) stack | — |

Two quantities differ: what a node can **offer its parent** (a straight path: `val + max(gains)`)
and the best path that **bends here** (`val + left + right`), which the parent can't extend.

```python
from treenode import build

def max_path_sum(root):
    def gain(node):
        """(best downward path starting here, best path anywhere in subtree)"""
        if node is None:
            return 0, float("-inf")
        lg, lbest = gain(node.left)
        rg, rbest = gain(node.right)
        lg, rg = max(lg, 0), max(rg, 0)       # drop negative branches
        bend = node.val + lg + rg             # path that turns at this node
        return node.val + max(lg, rg), max(lbest, rbest, bend)

    return gain(root)[1]

for lst in ([-10, 9, 20, None, None, 15, 7], [-2, -1, -5], [2, -1, -2]):
    print(lst, "->", max_path_sum(build(lst)))
```

```text
[-10, 9, 20, None, None, 15, 7] -> 42
[-2, -1, -5] -> -1
[2, -1, -2] -> 2
```

Wrong-but-tempting: returning `bend` to the parent (a path can't fork); starting `best` at 0 (an
all-negative tree answers −1, not 0). → repo: `chapters/ch14_recursion_trees_bst/solutions/ex06_path_sums.py`

## 14.9 Lowest common ancestor

The LCA of p and q is the deepest node with both below it (a node counts as its own descendant).
General tree: info up the tree again. Each call returns p, q, the LCA, or `None`; the first node
that receives non-`None` from **both** sides is the answer. BST: the keys say which way to go,
so a loop suffices.

```python
from ex07_lca import find
from treenode import build

def lca(root, p, q):
    if root is None or root is p or root is q:
        return root
    left, right = lca(root.left, p, q), lca(root.right, p, q)
    return root if left and right else left or right

def lca_bst(root, p, q):
    node = root
    while True:
        if p.val < node.val and q.val < node.val:
            node = node.left
        elif p.val > node.val and q.val > node.val:
            node = node.right
        else:
            return node                       # keys split here (or one equals node)

t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
b = build([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
print(lca(t, find(t, 5), find(t, 4)).val, lca(t, find(t, 7), find(t, 8)).val,
      lca_bst(b, find(b, 3), find(b, 5)).val, lca_bst(b, find(b, 2), find(b, 8)).val)
```

```text
5 3 4 6
```

General: O(n) time, O(h) stack; the parent-map rung (ancestor set of p, walk up from q) uses O(n)
space but survives any depth. BST: O(h) time, O(1) space. Compare nodes with `is`: values may repeat. If q
might be absent, the early return on p is wrong; count the targets found.

## 14.10 Construct tree from traversals ◆

### Worked problem 3 — preorder + inorder (ex08)

*Distinct values. Rebuild the tree.* `preorder[0]` is the root; its position `mid` in inorder
splits the left subtree (everything before) from the right.

| Rung | Idea | Time | Why move up |
|---|---|---|---|
| 1 | `inorder.index(root)`, recurse on slices | O(n²) on a chain | linear search + slice copies |
| 2 | dict value → inorder index; pass `(lo, hi)` bounds; consume preorder with one iterator | O(n) | — |

```python
from treenode import TreeNode, render

def build_pre_in(preorder, inorder):
    where = {v: i for i, v in enumerate(inorder)}
    roots = iter(preorder)                     # next root, in creation order

    def make(lo, hi):                          # builds inorder[lo:hi]
        if lo == hi:
            return None
        node = TreeNode(next(roots))
        mid = where[node.val]
        node.left = make(lo, mid)              # left first: preorder order
        node.right = make(mid + 1, hi)
        return node

    return make(0, len(inorder))

print(render(build_pre_in([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])))
```

```text
  _3____
 /      \
9        20
        /  \
      15    7
```

Postorder + inorder: take roots from the **end** of postorder and build the **right** subtree first.
Duplicates make the split ambiguous, and preorder + postorder doesn't fix a lone child's side, so
neither pair determines the tree in general.

## 14.11 Serialize / deserialize ◆

Preorder **with null markers** is unambiguous; without them `[1, 2]` and `[1, None, 2]` both print
`1,2`. Reading back uses one shared iterator, so each recursive call consumes exactly its subtree:

```python
from treenode import TreeNode, build, to_level

def serialize(node):
    if node is None:
        return "#"
    return f"{node.val},{serialize(node.left)},{serialize(node.right)}"

def deserialize(data):
    vals = iter(data.split(","))
    def read():
        v = next(vals)
        if v == "#":
            return None
        return TreeNode(int(v), read(), read())   # arguments run left to right
    return read()

s = serialize(build([1, 2, 3, None, None, 4, -50]))
print(s, "->", to_level(deserialize(s)))
```

```text
1,2,#,#,3,4,#,#,-50,#,# -> [1, 2, 3, None, None, 4, -50]
```

O(n) both ways. Separate values with a delimiter (`1,23` vs `12,3`) and never `eval`. The repo
adds an iterative serializer and a level-order codec.
For a BST, preorder *without* markers suffices: the keys fix the shape.

## 14.12 Binary search trees: search, insert, delete, validate

BST invariant: **every** key in the left subtree < node < **every** key in the right subtree.
Search and insert walk one path: O(h): log n balanced, n after sorted inserts.
Delete: 0 children → remove; 1 → splice the child up; 2 → copy in the inorder successor
(leftmost of the right subtree), then delete that key from the right subtree. Python has no
built-in balanced BST; for small data use a sorted list + `bisect` (→ §11.2).

### Worked problem 4 — validate a BST (ex10)

```text
  5__        Every parent/child pair looks right (1 < 5 < 6, 3 < 6 < 7),
 /   \       but 3 is in 5's RIGHT subtree, so it must be > 5.
1     6      Inorder: 1 5 3 6 7, not sorted -> not a BST.
     / \
    3   7
```

| Rung | Idea | Time / space | Verdict |
|---|---|---|---|
| 0 | each node vs its direct children | O(n) | **wrong**: passes the tree above |
| 1 | inorder must be strictly increasing | O(n), O(n) list (O(h) comparing on the fly) | correct |
| 2 | pass an open interval (low, high) down; left gets (low, val), right (val, high) | O(n), O(h) stack | correct, the expected answer |

```python
from treenode import build

def is_valid_bst(node, low=None, high=None):
    if node is None:
        return True
    if (low is not None and node.val <= low) or (high is not None and node.val >= high):
        return False
    return (is_valid_bst(node.left, low, node.val)
            and is_valid_bst(node.right, node.val, high))

for lst in ([5, 1, 6, None, None, 3, 7], [2, 1, 3], [2, 2], [-2**31, None, 2**31 - 1]):
    print(f"{lst!s:<30} {is_valid_bst(build(lst))}")
```

```text
[5, 1, 6, None, None, 3, 7]    False
[2, 1, 3]                      True
[2, 2]                         False
[-2147483648, None, 2147483647] True
```

`None` bounds accept any int at the root; `<=`/`>=` reject duplicates. Information flows **down**
here (preorder), unlike 14.7. Sorted inserts build a chain, so the repo adds
`is_valid_bst_iterative` (a stack of `(node, low, high)`) and `delete_iterative`.
→ repo: `chapters/ch14_recursion_trees_bst/solutions/ex10_bst_ops.py`

## 14.13 BST inorder properties: kth smallest, successor

Inorder of a BST is sorted, so the k-th smallest is the k-th pop of the iterative inorder: stop
early for O(h + k). The successor of x (smallest key > x, x need not be present) needs no
traversal: every node with key > x is a candidate; record it and go left for a smaller one.

```python
from treenode import build

def kth_smallest(root, k):
    stack, node = [], root
    while stack or node:
        while node:
            stack.append(node); node = node.left
        node = stack.pop()
        k -= 1
        if k == 0:
            return node.val
        node = node.right

def successor(root, x):
    best, node = None, root
    while node:
        if node.val > x:
            best, node = node.val, node.left   # candidate; look for smaller
        else:
            node = node.right
    return best

root = build([5, 3, 6, 2, 4, None, None, 1])
print([kth_smallest(root, k) for k in (1, 3, 6)], [successor(root, x) for x in (0, 4, 6)])
```

```text
[1, 3, 6] [1, 5, None]
```

Successor is O(h) time and O(1) space; "leftmost of the right subtree" alone fails when x has no
right subtree (successor(4) is the ancestor 5). Many kth queries with updates: store subtree
sizes and descend in O(h).

## 14.14 N-ary trees

Replace `left, right` with `for child in node.children`. Depth is `1 + max(..., default=0)`; BFS is
unchanged; iterative preorder pushes children **reversed**. The left-child right-sibling encoding
turns any N-ary tree into a binary tree, so binary codecs (14.11) apply.

```python
class Node:
    def __init__(self, val, children=None):
        self.val, self.children = val, children or []

def max_depth(node):
    return 0 if node is None else 1 + max((max_depth(c) for c in node.children), default=0)

def preorder(root):
    out, stack = [], [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.val)
        stack.extend(reversed(node.children))  # first child popped first
    return out

t = Node(1, [Node(3, [Node(5), Node(6)]), Node(2), Node(4)])
print(max_depth(t), preorder(t))
```

```text
3 [1, 3, 5, 6, 2, 4]
```

→ repo: `chapters/ch14_recursion_trees_bst/solutions/ex12_nary_tree.py` (levels, postorder, encoding)

## 14.15 Practice set

Drill order: ex03 and ex04 until the iterative loops are automatic; ex05 → ex06 → ex07 (info up,
three times); ex10 → ex11 (BST); ex08 and ex09 last. Recursive repo solutions state their height
limit; the iterative twins are tested on deep chains. More trees: problem bank 067–078
(→ Ch 45).

## Interviewer's view

- **Name the template** before coding ("info flows up: postorder returning a tuple").
- **State h, not just n** ("log n if balanced, n on a chain"), then offer the iterative version.
- **Trace** a 5–7 node drawing aloud, covering empty, single node, chain, negatives, duplicates.
- Red flags: stale globals, a BST checked against direct children only.

## Exercises

Code: `chapters/ch14_recursion_trees_bst/` (stubs in `exercises/`, run tests with `TARGET=exercises`).

| Id | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Depth-weighted sum and flatten of nested lists | ★ | recursion → explicit stack |
| ex02 | How many BST shapes? (count and generate) | ★ | memoisation preview |
| ex03 | Preorder / inorder / postorder, recursive and iterative | ★ | DFS with a stack |
| ex04 | Level order, zigzag, right-side view | ★ | BFS by level |
| ex05 | Height, diameter, balanced in one pass | ★ | info up the tree |
| ex06 | Path sums: root-to-leaf, downward count, max path sum | ◆ | backtracking; info up |
| ex07 | Lowest common ancestor (binary tree, BST) | ★ | info up; BST descent |
| ex08 | Build tree from preorder/postorder + inorder | ◆ | divide & conquer + index map |
| ex09 | Serialize / deserialize (DFS and BFS codecs) | ◆ | null markers |
| ex10 | BST search, insert, delete, validate | ★ | bounds passed down |
| ex11 | Kth smallest and successor in a BST | ★ | inorder = sorted |
| ex12 | N-ary trees: depth, levels, traversals, encoding | ◆ | child loop; LCRS |

## Checkpoint quiz

1. Why does the iterative `flatten` push iterators rather than sublists?
2. In `diameter_and_balanced`, why must both children be processed before the node itself?
3. In max path sum, why does `gain` return `val + max(lg, rg)` but record `val + lg + rg`?
4. Give a tree that passes the "check each node against its children" BST test but is not a BST.
5. Your tree has 10⁵ nodes. Which of this chapter's functions are at risk, and what do you do?

<details>
<summary>Answers</summary>

1. An iterator keeps its own position, like a paused call frame: no copying or reversing of
   sublists, and the parent resumes exactly where it stopped after the child is exhausted.
2. The node's tuple is computed *from* its children's tuples: a postorder
   dependency.
3. A parent can extend only a straight path (one branch); a path bending here can't be extended,
   so it only competes for the global best.
4. `[5, 1, 6, None, None, 3, 7]`: 3 is a right descendant of 5 but smaller than it.
5. Every recursive helper, if the tree can degenerate into a chain: depth 10⁵ exceeds the ~1,000
   frame limit. Use explicit-stack or BFS versions (14.2), not a higher limit (→ §7.21).

</details>

## Summary card

- Recursion = base case + shrinking recursive case + combine; stack O(depth), ~1,000-frame cap.
- Deep input → explicit stack; iterators on the stack keep order.
- Repeated arguments → memoise (`lru_cache`), then consider a table (→ §19.2).
- Preorder passes info **down** (depth, bounds, path); postorder returns info **up** as a tuple,
  combined in O(1), no stale globals; inorder of a BST is sorted; BFS answers "per level".
- Iterative inorder: go left, pop, record, turn right. Postorder: same walk plus `last`.
- Max path sum: offer `val + max(gains)` up, record `val + left + right`, clamp gains at 0.
- LCA: node where both sides report a find; BST: walk until the keys split, O(h), O(1).
- Validate BST with (low, high) bounds, not direct children. Rebuild needs inorder + pre/post
  and distinct values; serialize with null markers.
- N-ary: same templates with `for child in node.children`; `max(..., default=0)`.
