---
layout: post
title: "Knight's Tours: Fitting Hamiltonian Circuits into Exact Cover"
description: ""
category: algorithm
comments: true
tags: [knuth, exact-cover, dancing-links, hamilton, TAOCP]
---

{% include JB/setup %}

## Introduction

In December 2025, the 87-year-old Knuth gave his 29th Annual Christmas Lecture at Stanford, on the topic of **Knight's Tours**. The audience probably didn't expect that he had started studying this problem back in 1973 — fifty-some years later he dug out those old notes and made a new breakthrough in 2025: he counted all closed tours on an 8×8 board that are symmetric under 180° rotation. The answer: **2,432,932** — less than 0.1% of all closed tours. How that number was obtained, we'll get to that.

This post is a continuation of the TAOCP series. We've already covered [exact cover][exact-cover], [Dancing Links][dancing-link], and [backtracking][backtrack]. Knight's Tours are a perfect example that ties all of these together — it's a **Hamiltonian path problem**, but Knuth has a beautiful trick that transforms it into exact cover.

<!--more-->

## What Is a Knight's Tour?

In chess, a knight moves in an "L" shape. The knight's tour problem asks: **can a knight start from some square and visit every square on the board exactly once?**

- **Open Tour**: the start and end squares are different
- **Closed Tour (Circuit)**: the knight can jump from the last square back to the starting square, forming a cycle

In graph theory terms: make each square a node, connect two nodes with an edge if a knight can move between them in one step — this is the **knight's graph**. A knight's tour is a Hamiltonian path on this graph (a closed tour is a Hamiltonian circuit).

On an 8×8 board, the number of closed tours is approximately 26 billion. Even on a smaller 6×6 board, there are tens of thousands of distinct closed tours (after removing symmetries).

## The Naive Encoding Doesn't Work

The first instinct is natural: encode "each square is visited exactly once" as exact cover.

Use $$n^2$$ items for the squares, then… then you're stuck. Visiting squares has an order — you need to ensure the sequence is connected, and step $$k$$ must be reachable from step $$k-1$$ by a knight move. This "adjacency" constraint can't be expressed directly as a 0-1 exact cover matrix.

## A Different View: From Squares to Moves

Knuth's key insight is to **change what we observe**.

Instead of tracking "which squares have been visited," track "which moves have been selected." In a closed tour (circuit), each square is:

- **departed from exactly once** (out)
- **arrived at exactly once** (in)

So we define:

- **Items**: $$out[cell]$$ and $$in[cell]$$, for $$2n^2$$ items total, each covered exactly once
- **Options**: each legal knight move $$(r_1, c_1) \to (r_2, c_2)$$ on the board, covering $$out[r_1 \cdot n + c_1]$$ and $$in[r_2 \cdot n + c_2]$$

Selecting a set of moves such that every square has exactly one in and one out is an exact cover. The code is clean:

{% highlight python linenos %}
def build_closed_tour(n):
    num_cells = n * n
    num_items = 2 * num_cells   # out[0..n²-1] then in[0..n²-1]
    options, labels = [], []

    for r1 in range(n):
        for c1 in range(n):
            src = r1 * n + c1
            for (r2, c2) in knight_moves(r1, c1, n):
                dst = r2 * n + c2
                # index of out[src] is src, index of in[dst] is num_cells + dst
                options.append([src, num_cells + dst])
                labels.append(((r1, c1), (r2, c2)))

    return num_items, options, labels
{% endhighlight %}

On a 6×6 board, this generates 72 items and 160 options (160 legal knight moves).

## An Important Pitfall

Is the encoding above correct? Almost.

Exact cover guarantees each square has exactly one outgoing and one incoming move — meaning the selected moves form a **permutation**: a set of disjoint directed cycles covering all squares. But this isn't necessarily **one** Hamiltonian circuit; it could be a combination of several short cycles.

For example, on a 6×6 board, the vast majority (~99.98%) of valid exact cover solutions found by DLX are multi-cycle solutions; only a small fraction are true Hamiltonian circuits. So you must verify after reconstruction:

{% highlight python linenos %}
def reconstruct_circuit(solution, labels, n):
    nxt = {labels[i][0]: labels[i][1] for i in solution}
    # Start from (0,0) and see how many steps we take
    cur, steps = (0, 0), 0
    while True:
        cur = nxt[cur]
        steps += 1
        if cur == (0, 0):
            break
    # If steps != n², it's a multi-cycle solution — discard
    if steps != n * n:
        return None
    # Reconstruct the ordered path
    path, cur = [], (0, 0)
    for _ in range(n * n):
        path.append(cur)
        cur = nxt[cur]
    return path
{% endhighlight %}

This check also reveals an interesting point: exact cover **cannot rule out multi-cycle solutions** on its own. To find Hamiltonian circuits, you either add extra constraints to the encoding (Knuth's Pre-Fascicle 8a has a more refined approach), or filter after the fact as we do here.

## Open Tours: Add a Virtual Node

The closed tour encoding is clean. What about open paths?

The trick is to add a **virtual node** $$v$$ with bidirectional edges to every real square. An open path $$s \to \cdots \to e$$ becomes a closed circuit $$v \to s \to \cdots \to e \to v$$, reusing the closed tour framework directly:

{% highlight python linenos %}
def build_open_tour(n):
    v = n * n              # virtual node index
    total = n * n + 1      # real squares + virtual node
    num_items = 2 * total
    options, labels = [], []

    # Real knight moves (item indices in extended space)
    for r1 in range(n):
        for c1 in range(n):
            src = r1 * n + c1
            for (r2, c2) in knight_moves(r1, c1, n):
                dst = r2 * n + c2
                options.append([src, total + dst])
                labels.append(((r1, c1), (r2, c2)))

    # Virtual edges: v → cell (choose start)
    for r2 in range(n):
        for c2 in range(n):
            dst = r2 * n + c2
            options.append([v, total + dst])
            labels.append(('v', (r2, c2)))

    # Virtual edges: cell → v (choose end)
    for r1 in range(n):
        for c1 in range(n):
            src = r1 * n + c1
            options.append([src, total + v])
            labels.append(((r1, c1), 'v'))

    return num_items, options, labels
{% endhighlight %}

On a 5×5 board, items become 52 ($$2 \times 26$$) and options are 146 (100 real moves + 25 virtual outgoing + 25 virtual incoming).

One solution looks like this:

```
 5 20  9 14  7
10 15  6 19 24
21  4 23  8 13
16 11  2 25 18
 3 22 17 12  1
```

Starting from square (4,4), ending at (3,3), visiting all 25 squares, every step a legal knight move.

## Deeper: Symmetry Analysis

Back to Knuth's number 2,432,932.

The board has 8 symmetry operations, forming the **dihedral group $$D_4$$**:

| # | Operation | Transform $$(r, c) \to$$ |
|:---:|:---|:---|
| 0 | Identity | $$(r, c)$$ |
| 1 | Rotate 90° | $$(c, n{-}1{-}r)$$ |
| 2 | Rotate 180° | $$(n{-}1{-}r,\ n{-}1{-}c)$$ |
| 3 | Rotate 270° | $$(n{-}1{-}c,\ r)$$ |
| 4 | Flip horizontal | $$(r,\ n{-}1{-}c)$$ |
| 5 | Flip vertical | $$(n{-}1{-}r,\ c)$$ |
| 6 | Flip diagonal | $$(c, r)$$ |
| 7 | Flip antidiagonal | $$(n{-}1{-}c,\ n{-}1{-}r)$$ |

**Two closed tours count as the same** if one can be transformed into the other by a symmetry operation, a change of starting point, or reversal of direction. To check if a tour is invariant under 180° rotation:

{% highlight python linenos %}
def has_sym(path, sym, n):
    transformed = apply_symmetry(path, sym, n)
    m = len(path)
    # Build the set of all cyclic rotations of the original path (including reversed)
    rotations = set()
    for i in range(m):
        rotations.add(tuple(path[i:] + path[:i]))
    rev = list(reversed(path))
    for i in range(m):
        rotations.add(tuple(rev[i:] + rev[:i]))
    # Check if the transformed path matches any rotation
    for i in range(m):
        if tuple(transformed[i:] + transformed[:i]) in rotations:
            return True
    return False
{% endhighlight %}

Randomly sampling 329 distinct closed tours on a 6×6 board and checking invariance under all 8 symmetries:

```
sym 0 identity           : 329  ← identity holds for all (sanity check)
sym 1 rot90              :   0
sym 2 rot180             :   1  ← only 1 tour is 180°-symmetric
sym 3 rot270             :   0
sym 4 flip_horizontal    :   0
sym 5 flip_vertical      :   0
sym 6 flip_diagonal      :   0
sym 7 flip_antidiagonal  :   0
```

**180° symmetry is extremely rare.** That's why this count is worth computing separately — it's a small pocket of order left behind by symmetry within the combinatorial explosion.

Knuth also showed in his lecture a knight's tour with the minimum number of obtuse angles — unique under symmetry, and visually beautiful. And an 18×18 board tour that maps exactly to itself under 90° rotation. These aren't just mathematics — they're geometric elegance.

## Summary

This post showed the core trick for fitting Hamiltonian circuits into exact cover:

1. **From squares to moves**: in/out items + one option per knight move — minimal encoding
2. **The multi-cycle trap**: exact cover doesn't guarantee a single circuit; check afterward
3. **Virtual node**: one small change, and open tours reuse the closed tour framework
4. **Symmetry**: $$D_4$$ has 8 operations; 180°-invariant tours are extremely rare

Full code (with DLX implementation, symmetry analysis, and verification) is [here][code].

Knuth's Pre-Fascicle 8a on Hamiltonian paths and circuits is still being written and hasn't been formally published. We'll continue along this line in the next post.

[exact-cover]: /2024/07/exact-cover.html
[dancing-link]: /2024/07/dancing-link.html
[backtrack]: /2024/08/backtrack.html
[code]: https://github.com/morefreeze/morefreeze.github.io/blob/master/code/knight_tour.py
