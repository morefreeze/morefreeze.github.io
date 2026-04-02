---
layout: post
title: "Pentomino Tiling with Dancing Links"
categories: algorithm combinatorics
tags: [DLX, algorithm, combinatorics, TAOCP, exact-cover]
description: "Exploring the pentomino tiling problem from TAOCP, learning how to transform a tiling problem into exact cover using the Dancing Links algorithm"
math: true
---

{% include JB/setup %}

## Introduction

Donald Knuth introduced the Dancing Links (DLX) algorithm in *The Art of Computer Programming* Volume 4B — an elegant backtracking algorithm for solving exact cover problems. This post explores the classic application mentioned in Exercise 7.2.2.1-31: **pentomino tiling**.

### What Are Pentominoes?

Pentominoes are polyominoes made of 5 unit squares connected edge to edge. Ignoring rotations and reflections, there are **12** distinct pentominoes, typically named after letters they resemble: F, I, L, P, N, T, U, V, W, X, Y, Z:

<img src="/images/pentominoes.svg" alt="12 pentomino shapes" style="width:100%; max-width:840px;"/>

### Problem Definition

**Classic problem**: Can you tile a 6×10 rectangle using all 12 pentominoes, each exactly once?

This generalizes to other rectangle sizes:
- 5×12
- 4×15
- 3×20

<!--more-->

## From Tiling to Exact Cover

Dancing Links solves **exact cover problems**:

> Given a 0-1 matrix, select a set of rows such that every column contains exactly one 1.

### Constructing the Matrix

For pentomino tiling, we build the following matrix:

**Columns**:
- Each grid cell (6×10 = 60 columns)
- Each pentomino type (12 columns)
- Total: 72 columns

**Rows**:
- For each pentomino type
- Consider all valid placements (position + orientation) within the rectangle
- Each row = one "placement option"
- The 1s mark occupied cells and the piece type used

### Example

Suppose we place the **L pentomino** at position (0,0):

<img src="/images/pentomino-L-example.svg" alt="L pentomino placement example" style="width:100%; max-width:300px;"/>

Row: `[L-type, (0,0), (1,0), (2,0), (3,0), (3,1)]` — six 1s.

## The Dancing Links Algorithm

DLX uses a **doubly-linked circular list** (a "toroidal" structure) to represent the sparse matrix, enabling efficient backtracking:

### Data Structure

```
ColumnHeader ↔ ColumnHeader ↔ ColumnHeader ↔ ...
       ↓              ↓               ↓
    DataNode ↔ DataNode ↔ DataNode
       ↓
    DataNode
```

### Algorithm Flow

```
Algorithm X(cover):
    if matrix empty:
        solution found!
    choose column c (fewest options)
    cover column c
    for each row r in column c:
        add r to solution
        for each column j in row r:
            cover column j
        X(cover)
        remove r from solution
        for each column j in row r:
            uncover column j
    uncover column c
```

### Optimization: Minimum Remaining Values

The key optimization of DLX — **always choose the column with the fewest options** — maximizes pruning.

## Core Implementation

The heart of DLX lies in the `cover` and `uncover` operations, which use doubly-linked lists for efficient backtracking:

```python
def cover(self, col):
    """Cover column col: remove column and all intersecting rows from matrix"""
    # 1. Remove column from column list
    self.R[self.L[col]] = self.R[col]
    self.L[self.R[col]] = self.L[col]

    # 2. Remove all rows that intersect this column
    i = self.D[col]
    while i != col:
        j = self.R[i]
        while j != i:
            self.D[self.U[j]] = self.D[j]  # Skip node j
            self.U[self.D[j]] = self.U[j]
            self.S[self.C[j]] -= 1  # Decrement column count
            j = self.R[j]
        i = self.D[i]

def uncover(self, col):
    """Uncover column col: exact reverse of cover operation"""
    # 1. Restore all removed rows (in reverse order)
    i = self.U[col]
    while i != col:
        j = self.L[i]
        while j != i:
            self.S[self.C[j]] += 1  # Restore column count
            self.D[self.U[j]] = j
            self.U[self.D[j]] = j
            j = self.L[j]
        i = self.U[i]

    # 2. Restore column to column list
    self.R[self.L[col]] = col
    self.L[self.R[col]] = col
```

**Key Points**:
- `cover` operation must be **reversible** for exact backtracking
- Use `L` and `R` pointers to skip nodes horizontally
- Use `U` and `D` pointers to skip nodes vertically
- `S` array tracks node count per column for MRV heuristic

Full implementation available at: [GitHub - pentomino_dlx.py](https://github.com/morefreeze/morefreeze.github.io/blob/master/code/pentomino_dlx.py)

## Sample Output

<img src="/images/pentomino-6x10-solution.svg" alt="6x10 pentomino tiling solution" style="width:100%; max-width:480px;"/>

*A solution tiling a 6×10 rectangle with all 12 pentominoes*

## Complexity Analysis

### Space Complexity

- For 6×10 rectangle, each column has $$O(n)$$ nodes at most
- Total nodes ≈ number of placement options
- Space: $$O(\text{placements})$$

### Time Complexity

- Worst case: exponential $$O(2^n)$$
- In practice, DLX's pruning is very effective
- Pentomino problems typically solve in milliseconds

## Extensions and Variations

### 1. Other Polyominoes

- **Trominoes**: 2 types (straight, L-shaped)
- **Tetrominoes**: 5 types
- **Hexominoes**: 35 types — interestingly, all 35 free hexominoes **cannot** tile any rectangle. A checkerboard parity argument proves this: 24 "odd" hexominoes cover 3 black + 3 white, while 11 "even" ones cover 4 black + 2 white (or vice versa), so total black squares covered is always even; yet any 10×21 rectangle has 105 black squares (odd) — a contradiction. However, they can tile regions with holes (e.g., a 15×15 square with a central 3×5 removed). Full code at [hexomino_dlx.py](https://github.com/morefreeze/morefreeze.github.io/blob/master/code/hexomino_dlx.py).

### 2. Counting Problems

According to the literature, the 6×10 pentomino tiling has **9,356** distinct solutions (counting rotations and reflections). This is a classic result in combinatorial mathematics that has been verified by multiple different methods.

### 3. Variants

- Rectangles with holes
- Non-rectangular regions
- Using a subset of pieces
- Allowing repeated pieces

## Conclusion

The pentomino tiling problem perfectly showcases the power of Dancing Links:

1. **Elegant Modeling**: Transform geometric problems into exact cover
2. **Efficient Algorithm**: Doubly-linked lists enable fast backtracking
3. **Highly Extensible**: Generalizes to other constraint satisfaction problems

This embodies Knuth's design philosophy: **Find the essential representation of the problem, then implement it with the most appropriate data structure.**

## References

- Knuth, D. E. (2022). *The Art of Computer Programming, Volume 4B: Combinatorial Algorithms, Part 2*. Addison-Wesley.
- [Dancing Links - Wikipedia](https://en.wikipedia.org/wiki/Dancing_Links)
- [Exact Cover - Wikipedia](https://en.wikipedia.org/wiki/Exact_cover)

---
