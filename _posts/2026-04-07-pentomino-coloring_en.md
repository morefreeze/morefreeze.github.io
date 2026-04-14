---
layout: post
title: "Strong 3-Coloring Pentomino Tilings: Only 94 Out of 2339 Survive"
categories: algorithm combinatorics
tags: [DLX, algorithm, combinatorics, TAOCP, exact-cover, graph-coloring, pentomino]
description: "TAOCP Exercise 7.2.2.1-277: enumerate all 2339 pentomino packings of a 6x10 board, then test which ones admit a strong 3-coloring where even corner-touching pieces must differ"
math: true
---

{% include JB/setup %}

## Introduction

There are 2,339 ways to tile a 6×10 rectangle with the 12 pentominoes. But what if I add a twist: adjacent pieces must receive different colors, and even corner-touching doesn't count as "far enough"? How many survive?

This is Exercise 7.2.2.1-277 from *The Art of Computer Programming*, Volume 4B — difficulty rating [25] on Knuth's 0–50 scale. The answer: **94**, a mere 4%.

<!--more-->

## Problem Definition

### What Makes It "Strong"?

In ordinary graph coloring, two vertices are adjacent only if they share an edge. For pentomino tiling, two pieces are adjacent when they share at least one grid edge.

"Strong" coloring is stricter: **two pieces may not share an edge *or* a corner**. In graph-theoretic terms, this is 8-connectivity (Chebyshev distance ≤ 1), rather than 4-connectivity.

<img src="/images/pentomino-adjacency.svg" alt="4-connectivity vs 8-connectivity comparison" style="width:100%; max-width:560px;"/>

### Goal

Color all 12 pentominoes with red, white, and blue so that no two same-colored pieces share an edge or a corner. We need to enumerate all 2,339 packings of the 6×10 board and check each one for strong 3-colorability.

## Two-Phase Algorithm

### Phase 1: DLX Enumeration

This phase builds on the [Dancing Links solver](/2026/03/pentomino-tiling.html) from the previous post, wrapping it into a function that enumerates all packings:

```python
def get_all_packings(width: int = 6, height: int = 10):
    """Enumerate all pentomino tiling solutions"""
    dlx = DancingLinks(width * height + len(PENTOMINOES))
    # ... build exact cover matrix ...
    packings = []
    for solution in dlx.search():
        packing = {}
        for node in solution:
            name, x, y, orientation = row_info[node]
            packing[name] = set_of_cells
        packings.append(packing)
    return packings
```

This returns 9,356 solutions including board symmetries; after deduplication, we get 2,339 distinct packings.

### Phase 2: Building the Adjacency Graph

For each packing, we build an adjacency graph where vertices represent the 12 pieces and edges connect pieces within Chebyshev distance ≤ 1:

```python
def build_adjacency(packing):
    """Build strong adjacency graph: two pieces adjacent iff any of their cells are within Chebyshev distance 1"""
    names = list(packing.keys())
    adjacency = {name: set() for name in names}

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            adjacent = False
            for ax, ay in packing[a]:
                for bx, by in packing[b]:
                    if abs(ax - bx) <= 1 and abs(ay - by) <= 1:
                        adjacent = True
                        break
                if adjacent:
                    break
            if adjacent:
                adjacency[a].add(b)
                adjacency[b].add(a)
    return adjacency
```

This undirected graph has at most $$\binom{12}{2} = 66$$ edges. In practice, the count is lower due to spatial constraints.

### Phase 3: Backtracking 3-Colorability Test

Testing 3-colorability is another NP-complete problem, but the graph is tiny (12 vertices). Simple backtracking suffices:

```python
def is_three_colorable(adjacency):
    """Check 3-colorability via backtracking"""
    names = list(adjacency.keys())
    n = len(names)
    coloring = {}

    def backtrack(idx):
        if idx == n:
            return True
        name = names[idx]
        used = {coloring[nb] for nb in adjacency[name] if nb in coloring}
        for color in range(3):
            if color not in used:
                coloring[name] = color
                if backtrack(idx + 1):
                    return True
                del coloring[name]
        return False

    if backtrack(0):
        return True, coloring
    return False, None
```

The key optimization: only consider colors already assigned to neighbors, enabling early pruning.

## Results

### Statistics

Running the full program produces:

```
Total packings (with sym):  9356
3-colorable (with sym):     376
Non-3-colorable (with sym): 8980

Distinct packings:          2339
Distinct 3-colorable:       94
Distinct non-3-colorable:   2245
```

Only **94/2339 ≈ 4.0%** of packings satisfy the strong 3-coloring condition — a striking illustration of how restrictive the "strong" requirement is.

### Example Coloring

Here is one valid strong 3-coloring:

<img src="/images/pentomino-3coloring.svg" alt="Strong 3-coloring example" style="width:100%; max-width:480px;"/>

You can verify: no two same-colored pieces share an edge or a corner.

### Why So Few?

Three factors conspire to eliminate nearly all packings:

1. **Denser adjacency graph**: Corner-touching adds many edges that ordinary edge-adjacency misses.

2. **Spatial constraints**: 12 pieces in 60 cells means each piece occupies only 5 cells. Under Chebyshev distance ≤ 1, every piece's "influence zone" is larger, causing more conflicts.

3. **Color balance**: Three colors for 12 pieces ideally means 4 per color. The graph's density makes such an even split hard to achieve.

## Complexity Analysis

### Time

- **Phase 1**: DLX enumerates 9,356 solutions (with symmetries) in seconds.
- **Phase 2**: Per packing, checks $$\binom{12}{2} \times 5^2 = 1{,}650$$ cell pairs (upper bound $$12^2 \times 25 = 3{,}600$$).
- **Phase 3**: Worst case $$O(3^{12})$$, but adjacency constraints prune aggressively.

Total wall-clock time: a few minutes, dominated by DLX enumeration.

### Space

Storing 9,356 packings with position data for 12 pieces each — a few hundred MB, well within modern hardware.

## Extensions

- **k-coloring**: Higher k means more feasible solutions; k = 2 is almost certainly impossible.
- **Other boards**: How do 5×12, 4×15, 3×20 fare under strong 3-coloring?
- **Partial piece sets**: What if we drop or duplicate certain pentominoes?

## Conclusion

- **DLX's enumerative power**: Not just a solver — a complete enumeration engine that enables downstream analysis.
- **Backtracking for small NP-complete instances**: With pruning, even exponential algorithms run fast on tiny graphs.
- **The power of constraints**: Switching from "edge-adjacent" to "edge-or-corner-adjacent" — a seemingly minor change — collapses the feasible set from "nearly everything" to "almost nothing."

The complete implementation is available on [GitHub](https://github.com/morefreeze/morefreeze.github.io/blob/master/code/pentomino_coloring.py). For more on the DLX algorithm itself, see the [previous post](/2026/03/pentomino-tiling.html).

## References

- Donald Knuth, *The Art of Computer Programming*, Volume 4B, Section 7.2.2.1
- Dancing Links original paper: [Dancing Links](https://arxiv.org/abs/cs/0011047)
- Pentomino tiling on Wikipedia: [Pentomino](https://en.wikipedia.org/wiki/Pentomino)
