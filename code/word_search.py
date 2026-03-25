"""
Word search puzzle creation and word rectangle solving using Algorithm C (XCC).

Demonstrates Knuth's "Color-controlled covering" framework from TAOCP Vol. 4B.

The key insight: a word search puzzle creation is an XCC problem where
  - Primary items: one per word (must be placed exactly once)
  - Colored secondary items: one per cell (can be covered by multiple words,
    but all must agree on the same letter = color)
"""

from __future__ import annotations
from typing import List, Optional, Tuple, Any
from dlx_colors import DLX_C


# ---------------------------------------------------------------------------
# Word search puzzle creator
# ---------------------------------------------------------------------------

DIRECTIONS = {
    'E':  (0, 1),   # East (horizontal →)
    'W':  (0, -1),  # West (horizontal ←)
    'S':  (1, 0),   # South (vertical ↓)
    'N':  (-1, 0),  # North (vertical ↑)
    'SE': (1, 1),   # Diagonal ↘
    'SW': (1, -1),  # Diagonal ↙
    'NE': (-1, 1),  # Diagonal ↗
    'NW': (-1, -1), # Diagonal ↖
}


def create_word_search(
    rows: int,
    cols: int,
    words: List[str],
    allow_diagonal: bool = True,
) -> List[Tuple[str, int, int, str]]:
    """
    Find all ways to hide `words` in an rows×cols grid.

    Returns a list of solutions, each solution being a list of
    (word, start_row, start_col, direction) tuples.

    XCC encoding
    ------------
    Primary items  : one per word index (0 .. W-1)
    Secondary items: one per cell (W .. W + rows*cols - 1), colored by letter
    """
    W = len(words)
    num_primary = W
    num_items = W + rows * cols

    def cell(r, c):
        return W + r * cols + c

    dirs = DIRECTIONS if allow_diagonal else {
        k: v for k, v in DIRECTIONS.items() if k in ('E', 'W', 'S', 'N')
    }

    options = []
    labels = []  # (word_idx, start_r, start_c, dir_name)

    for w_idx, word in enumerate(words):
        L = len(word)
        for dir_name, (dr, dc) in dirs.items():
            for sr in range(rows):
                for sc in range(cols):
                    # Check bounds
                    er = sr + dr * (L - 1)
                    ec = sc + dc * (L - 1)
                    if not (0 <= er < rows and 0 <= ec < cols):
                        continue
                    # Build option: primary item + colored secondary items
                    option = [(w_idx, None)]
                    for k, ch in enumerate(word):
                        option.append((cell(sr + dr * k, sc + dc * k), ch))
                    options.append(option)
                    labels.append((w_idx, sr, sc, dir_name))

    dlx = DLX_C(num_primary, num_items, options)

    solutions = []
    for sol in dlx.solve():
        placement = []
        for idx in sol:
            w_idx, sr, sc, dir_name = labels[idx]
            placement.append((words[w_idx], sr, sc, dir_name))
        solutions.append(placement)
    return solutions


def render_grid(rows: int, cols: int, placement: List[Tuple[str, int, int, str]]) -> List[str]:
    """Render a placement as a list of rows (unused cells = '.')."""
    grid = [['.' for _ in range(cols)] for _ in range(rows)]
    for word, sr, sc, dir_name in placement:
        dr, dc = DIRECTIONS[dir_name]
        for k, ch in enumerate(word):
            grid[sr + dr * k][sc + dc * k] = ch
    return [''.join(row) for row in grid]


# ---------------------------------------------------------------------------
# Word rectangle solver (bonus)
# ---------------------------------------------------------------------------

def solve_word_rectangle(
    across_words: List[str],
    down_words: List[str],
) -> Optional[List[List[str]]]:
    """
    Find a grid where across_words fill the rows and down_words fill the columns.

    E.g., across_words=['CAT','DOG'], down_words=['CD','AO','TG'] would give:
        C A T
        D O G

    XCC encoding
    ------------
    Primary items  : row-word indices (0..R-1) + col-word indices (R..R+C-1)
    Secondary items: cell (r,c) colored by letter
    """
    R = len(across_words)  # number of rows
    C = len(down_words)    # number of columns
    if R == 0 or C == 0:
        return None
    # Validate dimensions
    if any(len(w) != C for w in across_words):
        return None
    if any(len(w) != R for w in down_words):
        return None

    num_primary = R + C
    num_items = R + C + R * C

    def cell(r, c):
        return R + C + r * C + c

    options = []
    labels = []  # ('across'/'down', word_idx, row_or_col)

    # Across options: place across_words[w] in row r
    for r in range(R):
        for w_idx, word in enumerate(across_words):
            if len(word) != C:
                continue
            option = [(r, None)]  # primary: row r
            for c, ch in enumerate(word):
                option.append((cell(r, c), ch))
            options.append(option)
            labels.append(('across', w_idx, r))

    # Down options: place down_words[w] in column c
    for c in range(C):
        for w_idx, word in enumerate(down_words):
            if len(word) != R:
                continue
            option = [(R + c, None)]  # primary: col c
            for r, ch in enumerate(word):
                option.append((cell(r, c), ch))
            options.append(option)
            labels.append(('down', w_idx, c))

    dlx = DLX_C(num_primary, num_items, options)
    for sol in dlx.solve():
        grid = [['?' for _ in range(C)] for _ in range(R)]
        for idx in sol:
            kind, w_idx, pos = labels[idx]
            if kind == 'across':
                word = across_words[w_idx]
                for c, ch in enumerate(word):
                    grid[pos][c] = ch
        return grid
    return None


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_word_search():
    print("=" * 55)
    print("Word Search Creation (XCC with colored cells)")
    print("=" * 55)

    words = ["ABEL", "CANTOR", "GAUSS", "EULER"]
    rows, cols = 6, 6

    print(f"\nGrid: {rows}x{cols}, words: {words}")
    solutions = create_word_search(rows, cols, words)
    print(f"Found {len(solutions)} solutions")

    if solutions:
        sol = solutions[0]
        print("\nFirst solution:")
        for word, sr, sc, d in sorted(sol, key=lambda x: x[0]):
            print(f"  {word:10s}  start=({sr},{sc})  dir={d}")
        print()
        for line in render_grid(rows, cols, sol):
            print("  " + line)


def demo_word_search_shared():
    print("\n" + "=" * 55)
    print("Word Search with Shared Letters")
    print("=" * 55)

    # ABEL ends with L; LAND starts with L — they can share 'L'
    words = ["ABEL", "LAND"]
    rows, cols = 4, 4

    solutions = create_word_search(rows, cols, words, allow_diagonal=False)
    shared = [s for s in solutions
              if _has_shared_cell(words, rows, cols, s)]

    print(f"\n{len(shared)} solutions where ABEL and LAND share a letter:")
    for sol in shared[:3]:
        print()
        for word, sr, sc, d in sol:
            print(f"  {word} at ({sr},{sc}) dir {d}")
        for line in render_grid(rows, cols, sol):
            print("  " + line)


def _has_shared_cell(words, rows, cols, placement):
    from collections import defaultdict
    cell_letters = defaultdict(set)
    for word, sr, sc, dir_name in placement:
        dr, dc = DIRECTIONS[dir_name]
        for k, ch in enumerate(word):
            cell_letters[(sr + dr * k, sc + dc * k)].add((word, ch))
    # Shared cell = same (row,col) appears in options from different words
    for pos, entries in cell_letters.items():
        if len({w for w, _ in entries}) > 1:
            return True
    return False


def demo_word_rectangle():
    print("\n" + "=" * 55)
    print("Word Rectangle (rows + columns via XCC)")
    print("=" * 55)

    # 3-letter rows, 2-letter columns
    # Rows (3 letters each):  CAT, DOG, EEL
    # Cols (3 letters each):  CDE, AOE, TGL
    across = ["CAT", "DOG", "EEL"]
    down   = ["CDE", "AOE", "TGL"]  # columns read top-to-bottom

    print(f"\nAcross: {across}")
    print(f"Down:   {down}")
    result = solve_word_rectangle(across, down)
    if result:
        print("Solution found:")
        for row in result:
            print("  " + " ".join(row))
    else:
        print("No solution.")

    # More interesting: find 2x3 rectangle from word banks
    print("\nSearching for 2x3 rectangle:")
    print("  Across (3-letter words): any of SEA, CAT, RAN, BIT, TAR, NET, SET")
    print("  Down   (2-letter words): any of SC, EA, AT")
    across2 = ["SEA", "CAT", "RAN", "BIT", "TAR", "NET", "SET"]
    down2   = ["SC", "EA", "AT"]
    result2 = solve_word_rectangle(across2, down2)
    if result2:
        print("Solution:")
        for row in result2:
            print("  " + " ".join(row))
    else:
        print("No solution.")


if __name__ == "__main__":
    demo_word_search()
    demo_word_search_shared()
    demo_word_rectangle()
