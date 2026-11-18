"""
Exercise 12 — Linear Algebra: solve, inverse, least squares      [Tier: ★ Core]
Chapter 33 · Pattern: np.linalg · Target time: 20 min

Problem
-------
1. ``solve_system(A, b)``: solve the square system Ax = b. Raise ``ValueError`` if A is singular
   (or numerically so: condition number > 1e12).
2. ``fit_line(x, y)``: least-squares fit ``y ≈ m*x + c``; return ``(m, c)``.
3. ``normal_equation(X, y)``: ordinary-least-squares weights via the normal equation
   ``(XᵀX) w = Xᵀy`` using ``solve`` (not ``inv``).
4. ``gauss_solve(A, b)``: Gaussian elimination with partial pivoting written by hand (the
   "implement it from scratch" follow-up).

Examples
--------
>>> solve_system(np.array([[2., 1.], [1., 3.]]), np.array([3., 5.])).round(4).tolist()
[0.8, 1.4]
>>> [round(v, 4) for v in fit_line(np.array([0., 1., 2.]), np.array([1., 3., 5.]))]
[2.0, 1.0]

Constraints
-----------
- A is n x n, n <= 500.

Hints
-----
- ``np.linalg.solve`` uses an LU factorisation: O(n^3), more accurate than ``inv(A) @ b``.
- ``np.linalg.cond(A)`` measures how much errors in b are amplified.
- Design matrix ``[x, 1]`` then ``np.linalg.lstsq``.
- Partial pivoting: at each column, swap the row with the largest |value| into the pivot position.

Approach ladder
---------------
1. Brute force — Cramer's rule with determinants: O(n! ) naive or O(n^4) with LU dets.
2. Improved   — ``inv(A) @ b``: O(n^3) but ~2x the work and worse rounding error.
3. Optimal    — ``solve`` (LU with partial pivoting) for square; ``lstsq`` (SVD/QR) for
   over-determined or rank-deficient systems.

Follow-ups
----------
- When would you prefer ``lstsq`` over the normal equations? (ill-conditioned XᵀX: cond squares)
- What are ``@``, ``np.dot``, ``np.matmul`` differences? (batching rules; dot on N-D differs)
"""
from __future__ import annotations

import numpy as np


def solve_system(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    A = np.asarray(A, dtype=float)
    if np.linalg.cond(A) > 1e12:
        raise ValueError("matrix is singular or ill-conditioned")
    return np.linalg.solve(A, np.asarray(b, dtype=float))


def fit_line(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    X = np.column_stack([x, np.ones(len(x))])
    (m, c), *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(m), float(c)


def normal_equation(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.linalg.solve(X.T @ X, X.T @ y)


def gauss_solve(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    for col in range(n):
        piv = col + int(np.argmax(np.abs(A[col:, col])))
        if abs(A[piv, col]) < 1e-12:
            raise ValueError("matrix is singular")
        A[[col, piv]] = A[[piv, col]]
        b[[col, piv]] = b[[piv, col]]
        factors = A[col + 1:, col] / A[col, col]          # eliminate below the pivot (vectorised)
        A[col + 1:, col:] -= factors[:, None] * A[col, col:]
        b[col + 1:] -= factors * b[col]
    x = np.empty(n)
    for i in range(n - 1, -1, -1):                         # back substitution
        x[i] = (b[i] - A[i, i + 1:] @ x[i + 1:]) / A[i, i]
    return x


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    A = np.array([[2.0, 1.0], [1.0, 3.0]])
    b = np.array([3.0, 5.0])
    x = solve_system(A, b)
    print("x =", x, " residual ||Ax-b|| < 1e-12:", np.linalg.norm(A @ x - b) < 1e-12)
    print("inv(A) @ b agrees:", np.allclose(np.linalg.inv(A) @ b, x))
    print("gauss_solve agrees:", np.allclose(gauss_solve(A, b), x))
    print("det(A) =", round(float(np.linalg.det(A)), 4))

    print("\n== norms ==")
    v = np.array([3.0, -4.0])
    print("L2:", np.linalg.norm(v), " L1:", np.linalg.norm(v, 1), " Linf:", np.linalg.norm(v, np.inf))
    print("Frobenius of A:", round(float(np.linalg.norm(A)), 4))

    print("\n== singular / ill-conditioned ==")
    S = np.array([[1.0, 2.0], [2.0, 4.0]])
    for name, fn in [("solve_system", solve_system), ("gauss_solve", gauss_solve)]:
        try:
            fn(S, np.array([1.0, 2.0]))
        except ValueError as e:
            print(f"{name}: ValueError: {e}")
    H = 1.0 / (np.arange(1, 9)[:, None] + np.arange(8)[None, :])   # 8x8 Hilbert matrix
    print("Hilbert(8) cond > 1e9:", np.linalg.cond(H) > 1e9)

    print("\n== least squares line fit ==")
    rng = np.random.default_rng(5)
    xs = np.linspace(0, 10, 50)
    ys = 2.5 * xs - 1.0 + rng.normal(0, 0.5, size=xs.size)
    m, c = fit_line(xs, ys)
    print(f"fit: y = {m:.4f} x + {c:.4f}")
    X = np.column_stack([xs, np.ones_like(xs)])
    print("normal equation agrees:", np.allclose(normal_equation(X, ys), [m, c]))

    print("\n== random 50x50 system ==")
    R = rng.normal(size=(50, 50))
    rb = rng.normal(size=50)
    print("gauss == np.linalg.solve:", np.allclose(gauss_solve(R, rb), np.linalg.solve(R, rb)))

    print("\n== matmul vs dot on batches ==")
    P = rng.normal(size=(4, 2, 3))
    Q = rng.normal(size=(4, 3, 5))
    print("P @ Q shape:", (P @ Q).shape, " np.dot(P, Q) shape:", np.dot(P, Q).shape)


if __name__ == "__main__":
    main()
