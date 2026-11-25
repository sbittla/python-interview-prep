# Chapter 14 — Recursion, Trees and BST (code)

Manuscript: `manuscript/ch14_recursion_trees_bst.md`. Standard library only.

| Id | Title | Tier | Pattern | Section |
|---|---|---|---|---|
| ex01 | Depth-weighted sum and flatten of nested lists (recursive + explicit stack) | ★ | recursion → explicit stack | 14.1, 14.2 |
| ex02 | How many BST shapes? naive vs `lru_cache` vs table; generate them | ★ | memoisation preview | 14.3 |
| ex03 | Preorder / inorder / postorder: recursive, iterative, unified | ★ | DFS with a stack | 14.4, 14.5 |
| ex04 | Level order, zigzag, right-side view (BFS and DFS) | ★ | BFS by level | 14.6 |
| ex05 | Height, diameter and balanced check in one pass (+ iterative, + global-variable bug) | ★ | return info up the tree | 14.7 |
| ex06 | Path sums: root-to-leaf list, downward-path count, max path sum (+ iterative) | ◆ | backtracking; prefix sums; info up | 14.8 |
| ex07 | Lowest common ancestor: binary tree, parent map, BST | ★ | info up; BST descent | 14.9 |
| ex08 | Build a tree from preorder+inorder (recursive + explicit stack) and postorder+inorder | ◆ | divide & conquer + index map | 14.10 |
| ex09 | Serialize / deserialize (preorder with markers, level order) | ◆ | DFS/BFS codec | 14.11 |
| ex10 | BST search, insert, delete, validate (bounds vs the local-only trap; iterative delete/validate) | ★ | BST ordering, bounds | 14.12 |
| ex11 | Kth smallest and inorder successor in a BST | ★ | inorder = sorted | 14.13 |
| ex12 | N-ary trees: depth, levels, traversals, left-child right-sibling encoding | ◆ | same templates, child loop | 14.14 |

Shared helper: `solutions/treenode.py` (copy in `exercises/`) defines `TreeNode`, `build` (level-order
list with `None` holes → tree), `to_level`, `render` (ASCII drawing), `inorder_values`, `chain`
(degenerate tree for depth tests) and the seeded generators `random_tree` / `random_bst` used by the
tests. Every helper is iterative, so it works on trees deeper than the recursion limit.

Every test file cross-checks the optimal solution against a brute-force or recursive reference on
seeded random trees, and the iterative versions are run on 3,000–100,000-node chains.

## Run

```bash
.venv/Scripts/python chapters/ch14_recursion_trees_bst/solutions/ex05_diameter_balanced.py  # one demo
.venv/Scripts/python tools/run_all.py --chapter 14                                          # all demos -> outputs/
.venv/Scripts/python -m pytest chapters/ch14_recursion_trees_bst                            # tests vs solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch14_recursion_trees_bst           # tests vs your stubs
```
