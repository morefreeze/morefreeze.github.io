---
layout: post
title: "Dancing Links Advanced: Secondary Items and Colors"
description: ""
category: algorithm
comments: true
tags: [knuth, exact-cover, dancing-links, sudoku, TAOCP]
---

{% include JB/setup %}

## Introduction

In [Exact Cover][exact-cover] and [Dancing Links][dancing-link], we worked exclusively with **standard exact cover**: every item must be covered exactly once. That constraint is clean and elegant, but real-world problems are rarely so tidy.

Puzzles like the Wisdom Ball fit naturally — each piece is used exactly once, every cell is filled exactly once. But try modeling something like N-Queens and you hit a wall: each row and column must have exactly one queen — that's still exact cover — but each diagonal can have **at most** one queen, not "exactly one." Many diagonals along the edges of the board don't need to be occupied at all.

Standard DLX has no clean way to express "at most once." You'd have to hack around it with manual preprocessing — far from elegant.

Knuth's solution in TAOCP 4B: **secondary items** and **colors**. Together, these extensions form **Algorithm C**, dramatically expanding the reach of exact cover.

<!--more-->

## Limitations of Standard Exact Cover

Let's recap the semantics of standard exact cover: given a set of items and a set of options (each covering some items), select a subset of options so that every item is **covered exactly once**.

"Exactly once" breaks down into two constraints:
- **At least once**: every item must be covered
- **At most once**: every item can be covered no more than once

Many problems only need one of these directions:

| Scenario | Constraint |
|:---|:---|
| N-Queens: diagonals | At most once (a diagonal might have no queen) |
| Sudoku: pre-filled cells | A cell's value must be a specific digit |
| Crossword puzzles: shared cells | Letters must match where words intersect |

None of these can be expressed directly with standard exact cover.

## Secondary Items: Relaxing "Exactly" to "At Most"

**Definition**: A secondary item doesn't have to be covered, but if it is covered, it can be covered **at most once**.

In the matrix representation, items are split into two categories:
- **Primary items**: must be covered exactly once, listed first
- **Secondary items**: covered at most once, listed after, separated by `|`

The termination condition for Algorithm X changes from "all items are covered" to "all **primary items** are covered."

### N-Queens: Diagonals as Secondary Items

Place $$n$$ queens on an $$n \times n$$ board so that no two attack each other.

The classic encoding:
- **Primary items**: $$n$$ rows (`r0`..`rn-1`) and $$n$$ columns (`c0`..`cn-1`) — each must have exactly one queen
- **Secondary items**: $$(2n-1)$$ forward diagonals (`d0`..`d2n-2`) and $$(2n-1)$$ backward diagonals (`a0`..`a2n-2`) — each has at most one queen
- **Each option**: placing a queen at $$(r, c)$$ covers `rr`, `cc`, `d(r+c)`, and `a(r-c+n-1)`

Here's a fragment of the matrix for 4-Queens (many columns omitted):

```
Option           r0 r1 r2 r3 | c0 c1 c2 c3 | d0 d1 d2 d3 d4 d5 d6 | a0 a1 ...
(0,1) queen       1  .  .  .    .  1  .  .    .  1  .  .  .  .  .    .  .  ...
(1,3) queen       .  1  .  .    .  .  .  1    .  .  .  .  1  .  .    .  1  ...
```

The diagonal columns (secondary items) get "locked" when an option is selected, but the termination check only looks at whether all rows and columns (primary items) have been covered.

At the implementation level, the "cover" operation for secondary items is identical to primary items — once an option covers it, the item is removed from the linked list, and all other options containing it are deleted. The only difference: **a solution doesn't require every secondary item to have been covered**.

```python
def solve_nqueens(n):
    """
    Primary items: rows 0..n-1, columns n..2n-1
    Secondary items: forward diags 2n..4n-2, backward diags 4n-1..6n-3
    """
    num_primary = 2 * n
    num_secondary = 2 * (2 * n - 1)
    num_items = num_primary + num_secondary

    options = []
    for r in range(n):
        for c in range(n):
            diag  = 2 * n + (r + c)          # forward diagonal, 2n-1 total
            adiag = 2 * n + (2*n-1) + (r - c + n - 1)  # backward diagonal
            options.append([r, n + c, diag, adiag])

    dlx = DLX(num_items, options, num_primary=num_primary)
    return list(dlx.solve())
```

The 8-Queens puzzle yields 92 solutions — matching the classic result.

## Color Items: From "At Most Once" to "Multiple Times, Same Color"

Secondary items solve the "doesn't have to be covered" problem, but that's not enough.

Consider crossword puzzles: a horizontal word and a vertical word intersect at some cell, and both words must place the **same letter** in that cell. The cell gets covered by two options (one for each word), but as long as the letter matches, it's legal — this is the "multiple times, same color" semantics.

**Definition**: A color item is an enhanced secondary item. When an option covers a color item, it can specify a **color value**. The rule is:

> A color item may be covered by multiple options if and only if all covering options specify the **same color**.

Colors can be any label — digits in Sudoku, letters in crosswords, color names in graph coloring.

### The Purify Operation

Standard DLX performs "cover" on primary items: remove the column header and delete all rows containing that column.

The corresponding operation for color items is called **purify**:

1. Find the selected color item $$i$$ with color $$c$$
2. In $$i$$'s column, **delete all rows whose color is not $$c$$** (they conflict with the current choice)
3. **Keep rows whose color is $$c$$** (they're compatible with the current choice)
4. $$i$$ itself is **not removed from the column header list** (future same-color covers are still possible)

On backtracking, the reverse operation — **unpurify** — restores the deleted rows.

In pseudocode:

```
purify(i, color):
    x ← i.D
    while x ≠ i:
        if color(x) ≠ color:
            hide(x)   # delete this row (same as row deletion in cover)
        x ← x.D

unpurify(i, color):  # reverse order
    x ← i.U
    while x ≠ i:
        if color(x) ≠ color:
            unhide(x)
        x ← x.U
```

The key difference from cover:
- cover: removes the column header + deletes all rows
- purify: **does not remove the column header** + only deletes rows with a different color

### Sudoku: Cells as Color Items

Sudoku is the classic application of color items.

**Primary items** (must be satisfied exactly once):
- `row-r-d`: row $$r$$ contains digit $$d$$ ($$9 \times 9 = 81$$ items)
- `col-c-d`: column $$c$$ contains digit $$d$$ (81 items)
- `box-b-d`: box $$b$$ (3×3 block) contains digit $$d$$ (81 items)

**Secondary color items** (can be covered multiple times, but colors must match):
- `cell-(r,c)`: the cell at row $$r$$, column $$c$$ — color = the digit placed there

**Options**: placing digit $$d$$ in cell $$(r, c)$$ covers:
- Primary items: `row-r-d`, `col-c-d`, `box-b-d`
- Color item: `cell-(r,c)` colored as $$d$$

The elegance of color items shows up when handling **pre-filled cells**:

If cell $$(r, c)$$ already contains a 5, then during the solve, all options covering `cell-(r,c)` with a color other than 5 get pruned by the purify operation. Known cells automatically eliminate conflicts — no preprocessing needed.

Compare this to the traditional approach: standard exact cover handles known cells by manually pre-selecting the corresponding option, then manually removing conflicting rows before starting the search. Color items automate all of that.

## Algorithm C Implementation

`DLX_C` extends the standard DLX four-way linked list (full implementation in [knight_tour.py][code_dlx]) with two additions: `_Node` gains a `.color` field, and the search loop branches on secondary items using purify/unpurify instead of cover/uncover. Everything else — the column headers, cover/uncover themselves, the min-S heuristic — stays the same.

The differences from standard DLX boil down to three points:

1. The header list tracks primary and secondary items separately
2. Column selection only considers primary items
3. Secondary items use purify/unpurify instead of cover/uncover

{% highlight python linenos %}
class DLX_C:
    """Algorithm C: Exact cover with secondary items and colors."""

    def __init__(self, num_primary: int, num_items: int, options):
        """
        num_primary: the first num_primary items are primary (must be covered)
        num_items:   total item count (primary + secondary)
        options:     each option is a list of [(item_index, color), ...]
                     color is ignored for primary items (use None)
                     color = None for secondary items means "no color" (at most once)
        """
        self.num_primary = num_primary
        self._build(num_items, options)

    def _build(self, num_items, options):
        root = _Node(); root.name = 'root'
        self._root = root

        cols = []
        prev = root
        for i in range(num_items):
            h = _Node(); h.name = i; h.S = 0; h.C = h
            h.L = prev; h.R = root
            prev.R = h; root.L = h
            prev = h
            cols.append(h)
        # Secondary items at the end don't link back to root's left side
        # Simplified here: _choose_column controls the range via num_primary
        self._cols = cols

        for row_id, option in enumerate(options):
            first = prev_node = None
            for item, color in option:
                node = _Node()
                node.row_id = row_id
                node.color = color   # New: color field
                col = cols[item]; node.C = col
                node.U = col.U; node.D = col
                col.U.D = node; col.U = node
                col.S += 1
                if first is None:
                    first = node; node.L = node; node.R = node
                else:
                    node.L = prev_node; node.R = first
                    prev_node.R = node; first.L = node
                prev_node = node

    def _choose_column(self):
        """Only select among primary items (first num_primary columns)."""
        best = None
        j = self._root.R
        while j is not self._root:
            if j.name >= self.num_primary:
                break   # Secondary items start here, stop
            if best is None or j.S < best.S:
                best = j
            j = j.R
        return best

    @staticmethod
    def _cover(col):
        col.R.L = col.L; col.L.R = col.R
        i = col.D
        while i is not col:
            j = i.R
            while j is not i:
                j.D.U = j.U; j.U.D = j.D; j.C.S -= 1
                j = j.R
            i = i.D

    @staticmethod
    def _uncover(col):
        i = col.U
        while i is not col:
            j = i.L
            while j is not i:
                j.C.S += 1; j.D.U = j; j.U.D = j
                j = j.L
            i = i.U
        col.R.L = col; col.L.R = col

    @staticmethod
    def _purify(node):
        """
        Purify: for rows in this column with a different color, hide their
        row siblings (nodes in other columns), but keep the row node itself
        in the column chain so _unpurify can find it later.
        """
        col = node.C
        color = node.color
        i = col.D
        while i is not col:
            if i.color != color:
                j = i.R
                while j is not i:
                    j.D.U = j.U; j.U.D = j.D; j.C.S -= 1
                    j = j.R
            i = i.D

    @staticmethod
    def _unpurify(node):
        """Unpurify (reverse order): restore the row siblings of different-color rows."""
        col = node.C
        color = node.color
        i = col.U
        while i is not col:
            if i.color != color:
                j = i.L
                while j is not i:
                    j.C.S += 1; j.D.U = j; j.U.D = j
                    j = j.L
            i = i.U

    def solve(self):
        yield from self._search([])

    def _search(self, solution):
        col = self._choose_column()
        if col is None:
            yield list(solution)
            return
        if col.S == 0:
            return

        self._cover(col)
        r = col.D
        while r is not col:
            solution.append(r.row_id)
            # Process the other items in this row
            j = r.R
            while j is not r:
                if j.C.name < self.num_primary:
                    self._cover(j.C)          # Primary item: normal cover
                else:
                    if j.color is not None:
                        self._purify(j)        # Color secondary item: purify
                    else:
                        self._cover(j.C)       # Colorless secondary item: normal cover (at most once)
                j = j.R
            yield from self._search(solution)
            # Backtrack
            j = r.L
            while j is not r:
                if j.C.name < self.num_primary:
                    self._uncover(j.C)
                else:
                    if j.color is not None:
                        self._unpurify(j)
                    else:
                        self._uncover(j.C)
                j = j.L
            solution.pop()
            r = r.D
        self._uncover(col)
{% endhighlight %}

## Verification

### N-Queens (Secondary Items)

{% highlight python linenos %}
def solve_nqueens(n):
    num_primary = 2 * n
    diag_base  = num_primary
    adiag_base = diag_base + (2 * n - 1)
    num_items  = adiag_base + (2 * n - 1)

    options = []
    for r in range(n):
        for c in range(n):
            options.append([
                (r,         None),  # row: primary item
                (n + c,     None),  # column: primary item
                (diag_base  + r + c,         None),  # forward diagonal: secondary, no color
                (adiag_base + r - c + n - 1, None),  # backward diagonal: secondary, no color
            ])

    dlx = DLX_C(num_primary, num_items, options)
    return list(dlx.solve())

solutions = solve_nqueens(8)
print(f"Number of 8-Queens solutions: {len(solutions)}")  # → 92
{% endhighlight %}

### Sudoku (Color Items)

{% highlight python linenos %}
def solve_sudoku(grid):
    """
    grid: 9x9 list, 0 = empty, 1-9 = given
    Returns the solved 9x9 list, or None
    """
    # Primary items: row-digit, col-digit, box-digit (81 each, 243 total)
    ROW_D  = lambda r, d: r * 9 + (d - 1)
    COL_D  = lambda c, d: 81 + c * 9 + (d - 1)
    BOX_D  = lambda b, d: 162 + b * 9 + (d - 1)
    # Secondary color items: cells (81 total, color = digit)
    CELL   = lambda r, c: 243 + r * 9 + c

    num_primary = 243
    num_items   = 243 + 81

    options = []
    option_labels = []  # (r, c, d)

    for r in range(9):
        for c in range(9):
            b = (r // 3) * 3 + (c // 3)
            digits = [grid[r][c]] if grid[r][c] != 0 else range(1, 10)
            for d in digits:
                options.append([
                    (ROW_D(r, d), None),  # primary item
                    (COL_D(c, d), None),
                    (BOX_D(b, d), None),
                    (CELL(r, c),  d),     # color secondary item, color = digit
                ])
                option_labels.append((r, c, d))

    dlx = DLX_C(num_primary, num_items, options)
    for sol in dlx.solve():
        result = [row[:] for row in grid]
        for idx in sol:
            r, c, d = option_labels[idx]
            result[r][c] = d
        return result
    return None

# A standard Sudoku puzzle
puzzle = [
    [5,3,0, 0,7,0, 0,0,0],
    [6,0,0, 1,9,5, 0,0,0],
    [0,9,8, 0,0,0, 0,6,0],

    [8,0,0, 0,6,0, 0,0,3],
    [4,0,0, 8,0,3, 0,0,1],
    [7,0,0, 0,2,0, 0,0,6],

    [0,6,0, 0,0,0, 2,8,0],
    [0,0,0, 4,1,9, 0,0,5],
    [0,0,0, 0,8,0, 0,7,9],
]

answer = solve_sudoku(puzzle)
for row in answer:
    print(row)
{% endhighlight %}

Output:

```
[5, 3, 4, 6, 7, 8, 9, 1, 2]
[6, 7, 2, 1, 9, 5, 3, 4, 8]
[1, 9, 8, 3, 4, 2, 5, 6, 7]
[8, 5, 9, 7, 6, 1, 4, 2, 3]
[4, 2, 6, 8, 5, 3, 7, 9, 1]
[7, 1, 3, 9, 2, 4, 8, 5, 6]
[9, 6, 1, 5, 3, 7, 2, 8, 4]
[2, 8, 7, 4, 1, 9, 6, 3, 5]
[3, 4, 5, 2, 8, 6, 1, 7, 9]
```

## Comparing the Three Constraint Types

| Type | Coverage | DLX Operation | Typical Use |
|:---|:---|:---|:---|
| Primary item | Exactly once | cover / uncover | Board cells, Sudoku rows/cols/boxes |
| Colorless secondary item | At most once | cover / uncover (not required to be covered) | N-Queens diagonals |
| Color secondary item | Any number of times, same color | purify / unpurify | Sudoku cells, crossword intersections |

Algorithm C = Algorithm X + secondary items + color purification.

All three share the same linked-list structure. The differences are simple: primary items determine when the search terminates; secondary and color items determine how conflicts are detected.

## Wrap-up

1. **Secondary items**: relax "exactly once" to "at most once," enabling direct modeling of constraint-relaxation problems like N-Queens and graph coloring
2. **Color items**: allow a secondary item to be covered multiple times as long as all covers use the same color, naturally expressing shared constraints (Sudoku cells, crossword intersections)
3. **The purify operation**: symmetric with cover, but without removing the column header — the core mechanism behind color constraints

In the knight's tour post, I mentioned that exact cover can't rule out multi-cycle solutions. That's really another case of "missing extra constraints." In Knuth's Pre-Fascicle 8a, he uses colored secondary items to track path connectivity, ruling out multi-cycle solutions directly at the exact cover level — we'll dig into that approach another time.

Full code on [Github][code].

[exact-cover]: /2024/07/exact-cover.html
[dancing-link]: /2024/07/dancing-link.html
[backtrack]: /2024/08/backtrack.html
[knight-tour]: /2026/03/knight-tour.html
[code]: https://github.com/morefreeze/morefreeze.github.io/blob/master/code/dlx_colors.py
[code_dlx]: https://github.com/morefreeze/morefreeze.github.io/blob/master/code/knight_tour.py
