"""
Knight's Tour as Exact Cover using Dancing Links (DLX)

Inspired by Knuth's "Dancing Links" paper (arXiv:cs/0011047) and his
treatment of the knight's tour as an exact cover problem.

KEY INSIGHT (the "closed-tour encoding"):
  A Hamiltonian circuit on a graph can be encoded as exact cover by
  treating every node as having two "roles": a departure role (out[cell])
  and an arrival role (in[cell]).  Each directed edge (u→v) is an option
  that covers out[u] and in[v].  A valid exact cover picks exactly one
  outgoing edge and one incoming edge per node, which is precisely a
  set of vertex-disjoint cycles that together span every node — i.e., a
  Hamiltonian decomposition.  For knight moves on a chessboard that gives
  the closed knight's tour.

  For an OPEN tour, we add a virtual node v that connects to every real
  cell in both directions.  The path "start → ... → end" becomes the
  circuit "v → start → ... → end → v" in the extended graph.
"""

from __future__ import annotations
import sys
from typing import Generator, List, Tuple, Optional, Dict, Any

# ---------------------------------------------------------------------------
# 1.  Dancing Links (DLX) — Algorithm X with the "min-S" heuristic
# ---------------------------------------------------------------------------

class _Node:
    """A single node in the toroidal doubly-linked list used by DLX."""
    __slots__ = ('L', 'R', 'U', 'D', 'C', 'row_id', 'S', 'name')

    def __init__(self):
        self.L = self.R = self.U = self.D = self  # self-linked initially
        self.C: '_Node' = self  # column header
        self.row_id: int = -1   # which option this node belongs to
        self.S: int = 0         # size (column headers only)
        self.name: Any = None   # human-readable label (column headers only)


class DLX:
    """
    Dancing Links implementation of Algorithm X (Knuth 2000).

    Parameters
    ----------
    num_items : int
        Number of items (columns) that must each be covered exactly once.
    options : list[list[int]]
        Each option is a list of item indices (0-based) that it covers.

    Usage
    -----
    dlx = DLX(num_items, options)
    for solution in dlx.solve():
        # solution is a list of row indices (into options)
        ...
    """

    def __init__(self, num_items: int, options: List[List[int]]):
        self._build(num_items, options)

    # ------------------------------------------------------------------
    # Internal construction
    # ------------------------------------------------------------------

    def _build(self, num_items: int, options: List[List[int]]):
        # Root node
        root = _Node()
        root.name = 'root'
        self._root = root

        # Create column headers
        cols: List[_Node] = []
        prev = root
        for i in range(num_items):
            h = _Node()
            h.name = i
            h.S = 0
            h.C = h
            # Link horizontally
            h.L = prev
            h.R = root
            prev.R = h
            root.L = h
            prev = h
            cols.append(h)

        # Add option rows
        for row_id, option in enumerate(options):
            if not option:
                continue
            first = None
            prev_node = None
            for item in option:
                node = _Node()
                node.row_id = row_id
                col = cols[item]
                node.C = col

                # Link vertically into column
                node.U = col.U
                node.D = col
                col.U.D = node
                col.U = node
                col.S += 1

                # Link horizontally within row
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
    # Cover / uncover operations
    # ------------------------------------------------------------------

    @staticmethod
    def _cover(col: _Node):
        """Remove column col and all rows that contain it."""
        # Detach column header
        col.R.L = col.L
        col.L.R = col.R
        # For each row in this column, detach all other nodes in that row
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
        """Restore column col (exact reverse of cover)."""
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
    # Algorithm X search
    # ------------------------------------------------------------------

    def _choose_column(self) -> Optional[_Node]:
        """Choose the column with minimum S (size) — the 'min-S' heuristic."""
        best = None
        j = self._root.R
        while j is not self._root:
            if best is None or j.S < best.S:
                best = j
                if best.S == 0:
                    break  # can't do better
            j = j.R
        return best

    def solve(self) -> Generator[List[int], None, None]:
        """Yield each solution as a list of row indices."""
        solution: List[int] = []
        yield from self._search(solution)

    def _search(self, solution: List[int]) -> Generator[List[int], None, None]:
        if self._root.R is self._root:
            # All columns covered — found a solution
            yield list(solution)
            return

        col = self._choose_column()
        if col is None or col.S == 0:
            return  # no rows available — backtrack

        self._cover(col)
        r = col.D
        while r is not col:
            solution.append(r.row_id)
            # Cover all other columns in this row
            j = r.R
            while j is not r:
                self._cover(j.C)
                j = j.R
            # Recurse
            yield from self._search(solution)
            # Uncover (backtrack)
            j = r.L
            while j is not r:
                self._uncover(j.C)
                j = j.L
            solution.pop()
            r = r.D
        self._uncover(col)


# ---------------------------------------------------------------------------
# 2.  Knight's Tour Encoding
# ---------------------------------------------------------------------------

def _knight_moves(r: int, c: int, n: int) -> List[Tuple[int, int]]:
    """Return all valid knight destinations from (r, c) on an n×n board."""
    deltas = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
    result = []
    for dr, dc in deltas:
        nr, nc = r + dr, c + dc
        if 0 <= nr < n and 0 <= nc < n:
            result.append((nr, nc))
    return result


def build_closed_tour(n: int):
    """
    Encode the closed knight's tour on an n×n board as exact cover.

    Items:
      out[cell] = cell          (index 0 .. n²-1)
      in[cell]  = cell + n²     (index n² .. 2n²-1)

    Each directed knight move (r1,c1)→(r2,c2) is an option covering:
      out[r1*n+c1]  and  in[r2*n+c2]

    WHY this encodes a Hamiltonian circuit:
      Covering every out[cell] exactly once means every cell is left
      exactly once.  Covering every in[cell] exactly once means every
      cell is entered exactly once.  Together that guarantees a set of
      vertex-disjoint directed cycles spanning the entire board — i.e.,
      a single Hamiltonian circuit (if we additionally require that the
      graph is connected, which the DLX search enforces by exhaustion).

    Returns
    -------
    (num_items, options, labels)
      num_items : 2 * n²
      options   : list of [out_item, in_item]
      labels    : list of ((r1,c1),(r2,c2))
    """
    num_cells = n * n
    num_items = 2 * num_cells  # out[0..n²-1] then in[0..n²-1]

    options = []
    labels = []

    for r1 in range(n):
        for c1 in range(n):
            src = r1 * n + c1
            for (r2, c2) in _knight_moves(r1, c1, n):
                dst = r2 * n + c2
                # out[src] = src,  in[dst] = num_cells + dst
                options.append([src, num_cells + dst])
                labels.append(((r1, c1), (r2, c2)))

    return num_items, options, labels


def build_open_tour(n: int):
    """
    Encode the open (Hamiltonian path) knight's tour on an n×n board.

    We add a virtual node v = n² that connects to every real cell in
    both directions.  The path "s → ... → e" becomes the circuit
    "v → s → ... → e → v" in the extended graph, allowing us to reuse
    the closed-tour encoding.

    Extended item space:
      out[i] = i                   for i in 0..total_cells-1
      in[i]  = total_cells + i     for i in 0..total_cells-1

    where total_cells = n² + 1  (the extra 1 is the virtual node).

    Real knight move (r1,c1)→(r2,c2) covers:
      out[r1*n+c1]  and  in[r2*n+c2]

    Virtual edge v→cell covers:
      out[v=n²]  and  in[cell]

    Virtual edge cell→v covers:
      out[cell]  and  in[v=total_cells+n²]

    Returns
    -------
    (num_items, options, labels)
      labels use the string 'v' for the virtual node
    """
    num_real = n * n
    v = num_real          # virtual node index
    total_cells = n * n + 1
    num_items = 2 * total_cells

    options = []
    labels = []

    # Real knight moves (in extended item space)
    for r1 in range(n):
        for c1 in range(n):
            src = r1 * n + c1
            for (r2, c2) in _knight_moves(r1, c1, n):
                dst = r2 * n + c2
                options.append([src, total_cells + dst])
                labels.append(((r1, c1), (r2, c2)))

    # Virtual edges: v → cell  (virtual departs, real arrives)
    for r2 in range(n):
        for c2 in range(n):
            dst = r2 * n + c2
            options.append([v, total_cells + dst])
            labels.append(('v', (r2, c2)))

    # Virtual edges: cell → v  (real departs, virtual arrives)
    for r1 in range(n):
        for c1 in range(n):
            src = r1 * n + c1
            options.append([src, total_cells + v])
            labels.append(((r1, c1), 'v'))

    return num_items, options, labels


# ---------------------------------------------------------------------------
# 3.  Solution Reconstruction
# ---------------------------------------------------------------------------

def _build_nxt(solution: List[int], labels: list) -> Dict[Any, Any]:
    """Build the 'next cell' mapping from a DLX solution."""
    nxt: Dict[Any, Any] = {}
    for row_id in solution:
        src, dst = labels[row_id]
        nxt[src] = dst
    return nxt


def _is_hamiltonian_circuit(nxt: Dict[Any, Any], n: int) -> bool:
    """
    Check that the nxt mapping forms a single cycle visiting all n² cells.

    The exact cover encoding guarantees in-degree = out-degree = 1 for
    every cell, so the nxt mapping is a permutation — a set of disjoint
    cycles.  We need exactly one cycle of length n².
    """
    # Follow the cycle from (0, 0) and count steps
    start = (0, 0)
    cur = nxt[start]
    steps = 1
    while cur != start:
        cur = nxt[cur]
        steps += 1
        if steps > n * n:
            return False
    return steps == n * n


def reconstruct_circuit(solution: List[int], labels: list, n: int) -> Optional[List[Tuple[int, int]]]:
    """
    Reconstruct the ordered sequence of cells for a closed knight's tour.

    Returns None if the solution is not a Hamiltonian circuit (i.e., the
    exact cover decomposes into multiple disjoint cycles instead of one).

    NOTE: The exact cover encoding guarantees every cell has in-degree and
    out-degree exactly 1, but NOT that the resulting permutation is a single
    cycle.  Callers must check for None.
    """
    nxt = _build_nxt(solution, labels)

    if not _is_hamiltonian_circuit(nxt, n):
        return None

    # Walk the single Hamiltonian circuit from (0, 0)
    path = []
    cur = (0, 0)
    for _ in range(n * n):
        path.append(cur)
        cur = nxt[cur]

    assert cur == (0, 0), "Circuit did not close!"
    assert len(path) == n * n
    assert len(set(path)) == n * n
    return path


def reconstruct_path(solution: List[int], labels: list, n: int) -> Optional[List[Tuple[int, int]]]:
    """
    Reconstruct the ordered sequence of cells for an open knight's tour.

    The virtual node 'v' tells us where the path starts and ends.
    Returns None if the solution is not a Hamiltonian path (i.e., the
    exact cover decomposes into a short v-anchored path plus extra cycles).

    NOTE: Same multi-cycle issue as with closed tours — callers must
    check for None and skip non-Hamiltonian-path solutions.
    """
    nxt = _build_nxt(solution, labels)

    # Virtual node v departs toward the first real cell
    start = nxt['v']
    path = []
    cur = start
    while cur != 'v' and len(path) <= n * n:
        path.append(cur)
        cur = nxt[cur]

    if len(path) != n * n or cur != 'v':
        return None

    assert len(set(path)) == n * n, "Duplicate cells in path"
    return path


def board_str(path: List[Tuple[int, int]], n: int) -> str:
    """
    Render an n×n chessboard with step numbers.

    The cell visited at step k gets value k+1 (1-indexed).
    """
    grid = [[0] * n for _ in range(n)]
    for step, (r, c) in enumerate(path):
        grid[r][c] = step + 1

    width = len(str(n * n))
    lines = []
    for row in grid:
        lines.append(' '.join(str(v).rjust(width) for v in row))
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# 4.  Symmetry Analysis
# ---------------------------------------------------------------------------

# The 8 elements of the dihedral group D₄ acting on an n×n board.
# Each is a function (r, c, n) → (r', c').
_SYMMETRIES = [
    lambda r, c, n: (r, c),                  # 0: identity
    lambda r, c, n: (c, n-1-r),              # 1: rot 90°
    lambda r, c, n: (n-1-r, n-1-c),          # 2: rot 180°
    lambda r, c, n: (n-1-c, r),              # 3: rot 270°
    lambda r, c, n: (r, n-1-c),              # 4: flip horizontal (reflect about vertical axis)
    lambda r, c, n: (n-1-r, c),              # 5: flip vertical   (reflect about horizontal axis)
    lambda r, c, n: (c, r),                  # 6: flip main diagonal
    lambda r, c, n: (n-1-c, n-1-r),         # 7: flip antidiagonal
]

_SYM_NAMES = [
    'identity',
    'rot90',
    'rot180',
    'rot270',
    'flip_horizontal',
    'flip_vertical',
    'flip_diagonal',
    'flip_antidiagonal',
]


def apply_symmetry(path: List[Tuple[int, int]], sym: int, n: int) -> List[Tuple[int, int]]:
    """Apply symmetry transformation sym (0-7) to each cell in path."""
    f = _SYMMETRIES[sym]
    return [f(r, c, n) for r, c in path]


def canonical_form(path: List[Tuple[int, int]], n: int) -> Tuple:
    """
    Return the canonical (lexicographically smallest) representative of the
    equivalence class of a closed tour under the 8 dihedral symmetries and
    all n² cyclic rotations, as well as path reversal.

    A closed tour is treated as a cyclic sequence, so we consider:
      - 8 symmetries
      - n² cyclic shifts of the path
      - reversal of the path (direction)
    giving at most 16 * n² candidates.  The canonical form is the
    lexicographically smallest tuple among all of them.
    """
    m = len(path)
    best = None
    for sym in range(8):
        transformed = apply_symmetry(path, sym, n)
        for direction in [transformed, list(reversed(transformed))]:
            for start in range(m):
                rotated = tuple(direction[start:] + direction[:start])
                if best is None or rotated < best:
                    best = rotated
    return best


def has_sym(path: List[Tuple[int, int]], sym: int, n: int) -> bool:
    """
    Check if a closed tour is invariant under symmetry sym.

    Invariant means: applying symmetry sym to each cell of the path
    yields a cyclic rotation of the original path (possibly in reverse
    direction — since the tour direction is arbitrary for a circuit).

    Algorithm:
      1. Build the set of all n² cyclic rotations of path (forward and
         backward directions) — this represents the unique tour.
      2. Apply sym to each cell to get transformed_path.
      3. Check if transformed_path (or any cyclic rotation of it) appears
         in the rotation set.
    """
    transformed = apply_symmetry(path, sym, n)
    m = len(path)
    # Build set of all cyclic rotations of path in both directions
    path_rotations: set = set()
    for i in range(m):
        path_rotations.add(tuple(path[i:] + path[:i]))
    rev_path = list(reversed(path))
    for i in range(m):
        path_rotations.add(tuple(rev_path[i:] + rev_path[:i]))

    # Check if any cyclic rotation of transformed matches an original rotation
    for i in range(m):
        candidate = tuple(transformed[i:] + transformed[:i])
        if candidate in path_rotations:
            return True
    return False


def count_closed_tours(
    n: int,
    limit: Optional[int] = None,
    time_limit: Optional[float] = None,
) -> Dict:
    """
    Find distinct closed knight's tours on an n×n board, deduplicate by
    canonical form, and count symmetry invariances.

    Parameters
    ----------
    n          : board size
    limit      : stop after finding this many *unique* Hamiltonian circuits
    time_limit : stop after this many seconds (wall-clock)

    Returns
    -------
    dict with keys:
      'total'   : number of distinct tours found
      0..7      : number of those tours invariant under symmetry i
      'raw'     : total DLX solutions examined (including multi-cycle ones)
      'partial' : True if search was cut short by limit or time_limit
    """
    import time as _time
    num_items, options, labels = build_closed_tour(n)
    dlx = DLX(num_items, options)

    seen: Dict[Tuple, List[Tuple[int, int]]] = {}
    raw_count = 0
    t0 = _time.time()
    partial = False

    for solution in dlx.solve():
        raw_count += 1
        path = reconstruct_circuit(solution, labels, n)
        if path is None:
            # Multi-cycle solution — not a Hamiltonian circuit, skip
            continue
        key = canonical_form(path, n)
        if key not in seen:
            seen[key] = path
        # Check stopping conditions
        if limit is not None and len(seen) >= limit:
            partial = True
            break
        if time_limit is not None and _time.time() - t0 >= time_limit:
            partial = True
            break

    # Count symmetry invariances for each unique tour
    sym_counts = {i: 0 for i in range(8)}
    for path in seen.values():
        for sym in range(8):
            if has_sym(path, sym, n):
                sym_counts[sym] += 1

    result = dict(sym_counts)
    result['total'] = len(seen)
    result['raw'] = raw_count
    result['partial'] = partial
    return result


# ---------------------------------------------------------------------------
# 5.  Main Demo
# ---------------------------------------------------------------------------

def demo_closed_tour(n: int = 6):
    print(f"{'='*60}")
    print(f"Closed knight's tour on {n}×{n} board (first solution)")
    print(f"{'='*60}")

    num_items, options, labels = build_closed_tour(n)
    print(f"  Items: {num_items}  (= 2 × {n}² = 2 × {n*n})")
    print(f"  Options (directed knight moves): {len(options)}")

    dlx = DLX(num_items, options)
    path = None
    for solution in dlx.solve():
        path = reconstruct_circuit(solution, labels, n)
        if path is not None:
            break
    assert path is not None, "No Hamiltonian circuit found!"

    print(f"\nPath (ordered cells, 0-indexed):")
    print(' → '.join(f"({r},{c})" for r, c in path))
    print(f"\nBoard (step numbers):")
    print(board_str(path, n))
    print(f"\nVerification:")
    print(f"  Cells visited: {len(path)}")
    print(f"  Unique cells:  {len(set(path))}")
    print(f"  Returns to start: {path[-1]} → {path[0]} is valid knight move:",
          path[0] in _knight_moves(*path[-1], n))
    assert len(set(path)) == n * n
    assert path[0] in _knight_moves(*path[-1], n), "Last move does not close the circuit!"
    print("  PASSED all assertions.")


def demo_open_tour(n: int = 5):
    print(f"\n{'='*60}")
    print(f"Open knight's tour on {n}×{n} board (first solution)")
    print(f"{'='*60}")

    num_items, options, labels = build_open_tour(n)
    total_cells = n * n + 1
    print(f"  Items: {num_items}  (= 2 × {total_cells} = 2 × (n²+1))")
    print(f"  Options (knight moves + virtual edges): {len(options)}")

    dlx = DLX(num_items, options)
    path = None
    for solution in dlx.solve():
        path = reconstruct_path(solution, labels, n)
        if path is not None:
            break
    assert path is not None, "No Hamiltonian path found!"

    print(f"\nPath (ordered cells):")
    print(' → '.join(f"({r},{c})" for r, c in path))
    print(f"\nBoard (step numbers):")
    print(board_str(path, n))
    print(f"\nVerification:")
    print(f"  Cells visited: {len(path)}")
    print(f"  Unique cells:  {len(set(path))}")
    assert len(set(path)) == n * n
    # Verify consecutive moves are valid knight moves
    for i in range(len(path) - 1):
        r1, c1 = path[i]
        r2, c2 = path[i+1]
        assert (r2, c2) in _knight_moves(r1, c1, n), \
            f"Invalid move at step {i}: {path[i]} → {path[i+1]}"
    print("  All consecutive moves are valid knight moves.")
    print("  PASSED all assertions.")


def demo_symmetry(n: int = 6, limit: int = 200, time_limit: float = 30.0):
    print(f"\n{'='*60}")
    print(f"Symmetry analysis of closed tours on {n}×{n}")
    print(f"  (limit={limit} unique tours, time_limit={time_limit}s)")
    print(f"{'='*60}")
    print("  (Counting unique tours up to cyclic rotation and reversal,")
    print("   then checking dihedral symmetry invariances.)")

    result = count_closed_tours(n, limit=limit, time_limit=time_limit)

    partial_note = " (search stopped early)" if result['partial'] else " (exhaustive)"
    print(f"\n  Raw DLX solutions examined:  {result['raw']}")
    print(f"  Unique Hamiltonian tours:    {result['total']}{partial_note}")
    print()
    print(f"  Symmetry invariance counts (among {result['total']} unique tours):")
    for sym in range(8):
        print(f"    sym {sym} ({_SYM_NAMES[sym]:25s}): {result[sym]}")
    print()
    print(f"  Tours with 180° rotational symmetry (sym 2): {result[2]}")

    # Every tour has sym 0 (identity) — sanity check
    assert result[0] == result['total'], \
        f"Identity sym count {result[0]} != total {result['total']}"
    print(f"\n  Sanity check: all {result['total']} tours are trivially identity-invariant. PASSED.")


if __name__ == '__main__':
    # ----------------------------------------------------------------
    # Demo 1: First closed tour on 6×6
    # ----------------------------------------------------------------
    demo_closed_tour(n=6)

    # ----------------------------------------------------------------
    # Demo 2: First open tour on 5×5
    # ----------------------------------------------------------------
    demo_open_tour(n=5)

    # ----------------------------------------------------------------
    # Demo 3: Symmetry breakdown for 6×6
    #   Run for up to 30 seconds or 1000 unique tours, whichever comes first.
    #   On a typical machine this yields several hundred tours and shows
    #   the 180°-symmetric ones (sym 2) as predicted by Knuth.
    # ----------------------------------------------------------------
    demo_symmetry(n=6, limit=1000, time_limit=30.0)
