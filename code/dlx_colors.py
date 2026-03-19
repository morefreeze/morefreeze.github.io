"""
Algorithm C: Exact Cover with Secondary Items and Colors
(Knuth, TAOCP Vol. 4B)

Extends standard DLX (Algorithm X) with:
  - Secondary items: covered at most once (optional)
  - Colored secondary items: can be covered multiple times if all
    coverings agree on the same color

Key operation added: purify / unpurify (instead of cover / uncover)
for colored secondary items.

Demos:
  1. N-Queens (secondary items for diagonals)
  2. Sudoku (colored secondary items for cells)
"""

from __future__ import annotations
from typing import Any, Generator, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Node (same as DLX, extended with .color)
# ---------------------------------------------------------------------------

class _Node:
    __slots__ = ('L', 'R', 'U', 'D', 'C', 'row_id', 'S', 'name', 'color')

    def __init__(self):
        self.L = self.R = self.U = self.D = self
        self.C: '_Node' = self
        self.row_id: int = -1
        self.S: int = 0
        self.name: Any = None
        self.color: Any = None   # None = "no color" (uncolored secondary)


# ---------------------------------------------------------------------------
# Algorithm C
# ---------------------------------------------------------------------------

class DLX_C:
    """
    Algorithm C: Exact cover with secondary items and colors.

    Parameters
    ----------
    num_primary : int
        Number of primary items (must be covered exactly once).
        They occupy indices 0 .. num_primary-1.
    num_items : int
        Total number of items (primary + secondary).
        Secondary items occupy indices num_primary .. num_items-1.
    options : list of list of (int, color)
        Each option is a list of (item_index, color) pairs.
        - For primary items, color is ignored (use None).
        - For secondary items, color=None means "uncolored" (at most once).
        - For secondary items, color=<value> means colored (same value required
          across all options covering this item in a given solution).
    """

    def __init__(self, num_primary: int, num_items: int,
                 options: List[List[Tuple[int, Any]]]):
        self.num_primary = num_primary
        self._build(num_items, options)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build(self, num_items: int, options):
        root = _Node()
        root.name = 'root'
        self._root = root

        cols: List[_Node] = []
        prev = root
        for i in range(num_items):
            h = _Node()
            h.name = i
            h.S = 0
            h.C = h
            h.L = prev
            h.R = root
            prev.R = h
            root.L = h
            prev = h
            cols.append(h)

        for row_id, option in enumerate(options):
            first = prev_node = None
            for item, color in option:
                node = _Node()
                node.row_id = row_id
                node.color = color
                col = cols[item]
                node.C = col
                node.U = col.U
                node.D = col
                col.U.D = node
                col.U = node
                col.S += 1
                if first is None:
                    first = node
                    node.L = node
                    node.R = node
                else:
                    node.L = prev_node
                    node.R = first
                    prev_node.R = node
                    first.L = node
                prev_node = node

    # ------------------------------------------------------------------
    # Cover / Uncover (primary items and uncolored secondary items)
    # ------------------------------------------------------------------

    @staticmethod
    def _cover(col: _Node):
        col.R.L = col.L
        col.L.R = col.R
        i = col.D
        while i is not col:
            j = i.R
            while j is not i:
                j.D.U = j.U
                j.U.D = j.D
                j.C.S -= 1
                j = j.R
            i = i.D

    @staticmethod
    def _uncover(col: _Node):
        i = col.U
        while i is not col:
            j = i.L
            while j is not i:
                j.C.S += 1
                j.D.U = j
                j.U.D = j
                j = j.L
            i = i.U
        col.R.L = col
        col.L.R = col

    # ------------------------------------------------------------------
    # Purify / Unpurify (colored secondary items)
    # ------------------------------------------------------------------

    @staticmethod
    def _purify(node: _Node):
        """
        For colored secondary item node.C, hide the ROW SIBLINGS of every
        row in the column whose color differs from node.color.

        Critically: different-color nodes are NOT removed from the column
        chain itself — only their siblings in other columns are hidden.
        This keeps them reachable during _unpurify.
        """
        col = node.C
        color = node.color
        i = col.D
        while i is not col:
            if i.color != color:
                # Hide siblings of row i from their respective columns,
                # but leave i itself in col's chain.
                j = i.R
                while j is not i:
                    j.D.U = j.U
                    j.U.D = j.D
                    j.C.S -= 1
                    j = j.R
            i = i.D

    @staticmethod
    def _unpurify(node: _Node):
        """
        Reverse of _purify: walk column backward, restore siblings of
        different-color rows (same-color rows were untouched, skip them).
        """
        col = node.C
        color = node.color
        i = col.U
        while i is not col:
            if i.color != color:
                # Restore siblings of row i (reverse order).
                j = i.L
                while j is not i:
                    j.C.S += 1
                    j.D.U = j
                    j.U.D = j
                    j = j.L
            i = i.U

    # ------------------------------------------------------------------
    # Algorithm C search
    # ------------------------------------------------------------------

    def _choose_column(self) -> Optional[_Node]:
        """Choose the primary item with minimum size."""
        best = None
        j = self._root.R
        while j is not self._root:
            if j.name >= self.num_primary:
                break   # reached secondary items — stop
            if best is None or j.S < best.S:
                best = j
                if best.S == 0:
                    break
            j = j.R
        return best

    def solve(self) -> Generator[List[int], None, None]:
        """Yield each solution as a list of option row indices."""
        yield from self._search([])

    def _search(self, solution: List[int]) -> Generator[List[int], None, None]:
        col = self._choose_column()
        if col is None:
            # All primary items covered.
            yield list(solution)
            return
        if col.S == 0:
            return  # Dead end.

        self._cover(col)
        r = col.D
        while r is not col:
            solution.append(r.row_id)
            j = r.R
            while j is not r:
                if j.C.name < self.num_primary:
                    self._cover(j.C)            # primary item
                elif j.color is not None:
                    self._purify(j)             # colored secondary item
                else:
                    self._cover(j.C)            # uncolored secondary item
                j = j.R

            yield from self._search(solution)

            j = r.L
            while j is not r:
                if j.C.name < self.num_primary:
                    self._uncover(j.C)
                elif j.color is not None:
                    self._unpurify(j)
                else:
                    self._uncover(j.C)
                j = j.L
            solution.pop()
            r = r.D
        self._uncover(col)


# ---------------------------------------------------------------------------
# Demo 1: N-Queens with secondary items (diagonals)
# ---------------------------------------------------------------------------

def solve_nqueens(n: int) -> List[List[int]]:
    """
    Primary items   : n rows (0..n-1) + n columns (n..2n-1)
    Secondary items : (2n-1) positive diagonals + (2n-1) negative diagonals
    """
    num_primary = 2 * n
    diag_base   = num_primary
    adiag_base  = diag_base + (2 * n - 1)
    num_items   = adiag_base + (2 * n - 1)

    options = []
    option_labels = []  # (row, col) for each option

    for r in range(n):
        for c in range(n):
            options.append([
                (r,                              None),  # row — primary
                (n + c,                          None),  # col — primary
                (diag_base  + r + c,             None),  # +diag — uncolored secondary
                (adiag_base + r - c + n - 1,     None),  # -diag — uncolored secondary
            ])
            option_labels.append((r, c))

    dlx = DLX_C(num_primary, num_items, options)
    solutions = []
    for sol in dlx.solve():
        placement = [None] * n
        for idx in sol:
            r, c = option_labels[idx]
            placement[r] = c
        solutions.append(placement)
    return solutions


def demo_nqueens(n: int = 8):
    print(f"{'='*55}")
    print(f"N-Queens (n={n}) — secondary items for diagonals")
    print(f"{'='*55}")
    sols = solve_nqueens(n)
    print(f"  Solutions found: {len(sols)}")
    # Known counts: 1,0,0,2,10,4,40,92,352,724,...
    known = {1:1, 4:2, 5:10, 6:4, 7:40, 8:92, 9:352, 10:724}
    if n in known:
        status = "✓ CORRECT" if len(sols) == known[n] else f"✗ WRONG (expected {known[n]})"
        print(f"  Known answer:    {known[n]}   {status}")
    # Show first solution as board
    if sols:
        board = sols[0]
        print(f"\n  First solution (col of queen per row):")
        for r, c in enumerate(board):
            print("  " + "." * c + "Q" + "." * (n - 1 - c))


# ---------------------------------------------------------------------------
# Demo 2: Sudoku with colored secondary items
# ---------------------------------------------------------------------------

def solve_sudoku(grid: List[List[int]]) -> Optional[List[List[int]]]:
    """
    Solve a 9x9 sudoku using Algorithm C with colored secondary items.

    grid: 9x9 list of ints; 0 = unknown, 1-9 = given digit.

    Primary items (must each be satisfied exactly once):
      row r has digit d  →  index r*9 + (d-1)         [0..80]
      col c has digit d  →  index 81 + c*9 + (d-1)    [81..161]
      box b has digit d  →  index 162 + b*9 + (d-1)   [162..242]

    Colored secondary items (can be covered multiple times, same color):
      cell (r,c)         →  index 243 + r*9 + c        [243..323]
      color = digit placed in the cell

    The colored cell item handles pre-filled cells naturally:
      if cell (r,c) = 5, only options with color=5 survive purification.
    """
    NUM_PRIMARY = 243
    NUM_ITEMS   = 243 + 81

    def row_d(r, d):  return r * 9 + (d - 1)
    def col_d(c, d):  return 81 + c * 9 + (d - 1)
    def box_d(b, d):  return 162 + b * 9 + (d - 1)
    def cell(r, c):   return 243 + r * 9 + c

    options = []
    labels  = []   # (r, c, d)

    for r in range(9):
        for c in range(9):
            b = (r // 3) * 3 + (c // 3)
            given = grid[r][c]
            digits = [given] if given != 0 else range(1, 10)
            for d in digits:
                options.append([
                    (row_d(r, d), None),   # primary
                    (col_d(c, d), None),   # primary
                    (box_d(b, d), None),   # primary
                    (cell(r, c),  d),      # colored secondary
                ])
                labels.append((r, c, d))

    dlx = DLX_C(NUM_PRIMARY, NUM_ITEMS, options)
    for sol in dlx.solve():
        result = [row[:] for row in grid]
        for idx in sol:
            r, c, d = labels[idx]
            result[r][c] = d
        return result
    return None


def demo_sudoku():
    print(f"\n{'='*55}")
    print("Sudoku — colored secondary items for cells")
    print(f"{'='*55}")

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

    expected = [
        [5,3,4, 6,7,8, 9,1,2],
        [6,7,2, 1,9,5, 3,4,8],
        [1,9,8, 3,4,2, 5,6,7],
        [8,5,9, 7,6,1, 4,2,3],
        [4,2,6, 8,5,3, 7,9,1],
        [7,1,3, 9,2,4, 8,5,6],
        [9,6,1, 5,3,7, 2,8,4],
        [2,8,7, 4,1,9, 6,3,5],
        [3,4,5, 2,8,6, 1,7,9],
    ]

    print("\n  Puzzle:")
    for row in puzzle:
        print("  " + " ".join(str(d) if d else "." for d in row))

    answer = solve_sudoku(puzzle)
    assert answer is not None, "No solution found!"
    assert answer == expected, "Wrong answer!"

    print("\n  Solution:")
    for row in answer:
        print("  " + " ".join(str(d) for d in row))
    print("\n  ✓ Matches expected answer.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    demo_nqueens(n=8)
    demo_sudoku()
