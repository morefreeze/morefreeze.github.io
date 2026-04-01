### Optimization: Minimum Remaining Values

The key optimization of DLX—**always choose the column with the fewest options**—maximizes pruning.

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
- **Hexominoes**: 35 types—interestingly, all 35 free hexominoes **cannot** tile any rectangle. A checkerboard parity argument proves this: 24 "odd" hexominoes cover 3 black + 3 white, while 11 "even" ones cover 4 black + 2 white (or vice versa), so total black squares covered is always even; yet any 10×21 rectangle has 105 black squares (odd)—a contradiction. However, they can tile regions with holes (e.g., a 15×15 square with a central 3×5 removed). Full code at [hexomino_dlx.py](https://github.com/morefreeze/morefreeze.github.io/blob/master/code/hexomino_dlx.py).
- Heptominoes: 108 types

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
