#!/usr/bin/env python3
"""
Pentomino Tiling with Dancing Links (DLX) Algorithm
Based on TAOCP Vol 4B, Section 7.2.2.1

This program solves the classic pentomino tiling problem:
Using all 12 pentominoes to tile a 6x10 rectangle.
"""

from typing import List, Tuple, Optional


class DancingLinks:
    """Dancing Links (DLX) algorithm implementation for exact cover.

    Uses a sparse matrix representation with doubly-linked circular lists
    for efficient backtracking.
    """

    def __init__(self, num_cols: int):
        # Arrays for linked list structure
        self.L: List[int] = list(range(num_cols + 1))
        self.R: List[int] = list(range(num_cols + 1))
        self.U: List[int] = list(range(num_cols + 1))
        self.D: List[int] = list(range(num_cols + 1))
        self.C: List[int] = list(range(num_cols + 1))  # Column header for each node
        self.S: List[int] = [0] * (num_cols + 1)  # Size of each column
        self.size: int = num_cols
        self.root: int = 0

        # Initialize circular column headers
        # Each column points to neighbors: ... <-> i-1 <-> i <-> i+1 <-> ...
        for i in range(num_cols + 1):
            self.L[i] = i - 1
            self.R[i] = i + 1
        # Wrap around: first column (1) <-> root (0) <-> last column (num_cols)
        self.L[0] = num_cols
        self.R[num_cols] = 0

    def add_row(self, cols: List[int]) -> int:
        """Add a row with 1s in the specified columns.

        Args:
            cols: List of column indices where this row has 1s

        Returns:
            The index of the first node in this row
        """
        if not cols:
            return -1

        first = len(self.L)
        prev = first

        # Create first node
        self._append_node(prev, cols[0])
        prev = len(self.L) - 1

        # Create remaining nodes
        for col in cols[1:]:
            self._append_node(prev, col)
            prev = len(self.L) - 1

        # Link into circular row
        self.L[first] = prev
        self.R[prev] = first

        return first

    def _append_node(self, prev: int, col: int) -> None:
        """Append a node after 'prev' in column 'col'."""
        node = len(self.L)

        self.L.append(0)
        self.R.append(0)
        self.U.append(self.U[col])
        self.D.append(col)
        self.C.append(col)

        # Link vertically in column
        self.D[self.U[col]] = node
        self.U[col] = node

        # Link horizontally in row
        self.L[node] = prev
        self.R[node] = self.R[prev]
        self.R[prev] = node
        self.L[self.R[node]] = node

        self.S[col] += 1

    def cover(self, col: int) -> None:
        """Cover column 'col' - remove it and all rows that intersect it."""
        # Remove column header from list
        self.R[self.L[col]] = self.R[col]
        self.L[self.R[col]] = self.L[col]

        # Remove all rows in this column
        i = self.D[col]
        while i != col:
            j = self.R[i]
            while j != i:
                self.D[self.U[j]] = self.D[j]
                self.U[self.D[j]] = self.U[j]
                self.S[self.C[j]] -= 1
                j = self.R[j]
            i = self.D[i]

    def uncover(self, col: int) -> None:
        """Uncover column 'col' - reverse the cover operation."""
        i = self.U[col]
        while i != col:
            j = self.L[i]
            while j != i:
                self.S[self.C[j]] += 1
                self.D[self.U[j]] = j
                self.U[self.D[j]] = j
                j = self.L[j]
            i = self.U[i]

        # Restore column header
        self.R[self.L[col]] = col
        self.L[self.R[col]] = col

    def search(self, solution: Optional[List[int]] = None):
        """Search for all solutions to the exact cover problem.

        Yields:
            Lists of row indices that form valid solutions
        """
        if solution is None:
            solution = []

        # If no columns remain, we found a solution
        if self.R[self.root] == self.root:
            yield solution.copy()
            return

        # Choose column with fewest rows (MRV heuristic)
        c = self.R[self.root]
        j = self.R[c]
        while j != self.root:
            if self.S[j] < self.S[c]:
                c = j
            j = self.R[j]

        # Cover this column
        self.cover(c)

        # Try each row in the column
        r = self.D[c]
        while r != c:
            solution.append(r)

            # Cover all columns that this row intersects
            j = self.R[r]
            while j != r:
                self.cover(self.C[j])
                j = self.R[j]

            # Recurse
            yield from self.search(solution)

            # Backtrack
            solution.pop()

            j = self.L[r]
            while j != r:
                self.uncover(self.C[j])
                j = self.L[j]

            r = self.D[r]

        # Uncover column
        self.uncover(c)


# Pentomino definitions
# Each pentomino is defined as a list of (x, y) coordinates
#
#  F: .#.    I: #####    L: ...#    P: ###    N: ###.
#     ##.                   ####       ##.       ..##
#     .##
#
#  T: #..    U: #.#    V: ..#    W: ##.    X: .#.
#     ###       ###       ..#       .##       ###
#     #..                 ###       ..#       .#.
#
#  Y: .#..    Z: .##
#     ####       .#.
#                ##.
PENTOMINOES = {
    'F': [(0, 1), (1, 0), (1, 1), (1, 2), (2, 2)],
    'I': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
    'L': [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1)],
    'P': [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)],
    'N': [(0, 1), (1, 1), (2, 0), (2, 1), (3, 0)],
    'T': [(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)],
    'U': [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)],
    'V': [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],
    'W': [(0, 2), (1, 1), (1, 2), (2, 0), (2, 1)],
    'X': [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],
    'Y': [(0, 0), (1, 0), (2, 0), (3, 0), (1, 1)],
    'Z': [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)],
}


def rotate(shape: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Rotate shape 90 degrees clockwise."""
    return [(y, -x) for x, y in shape]


def flip(shape: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Flip shape horizontally."""
    return [(x, -y) for x, y in shape]


def normalize(shape: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Normalize shape to start at origin (0, 0)."""
    if not shape:
        return shape
    min_x = min(x for x, _ in shape)
    min_y = min(y for _, y in shape)
    return sorted([(x - min_x, y - min_y) for x, y in shape])


def get_all_orientations(shape: List[Tuple[int, int]]) -> List[List[Tuple[int, int]]]:
    """Get all unique orientations of a shape (rotations and flips)."""
    orientations = []

    # Try all 4 rotations
    current = shape
    for _ in range(4):
        current = normalize(current)
        if current not in orientations:
            orientations.append(current)
        current = rotate(current)

    # Flip and try all 4 rotations again
    current = flip(shape)
    for _ in range(4):
        current = normalize(current)
        if current not in orientations:
            orientations.append(current)
        current = rotate(current)

    return orientations


def solve_pentomino(width: int = 6, height: int = 10,
                    max_solutions: int = 1) -> List[List[List[str]]]:
    """Solve the pentomino tiling problem using DLX.

    Args:
        width: Board width
        height: Board height
        max_solutions: Maximum number of solutions to find

    Returns:
        List of solved boards (each is a 2D list of characters)
    """
    dlx = DancingLinks(width * height + len(PENTOMINOES))
    pentomino_names = list(PENTOMINOES.keys())

    # Maps any node in a row to the placement info
    row_info = {}

    # Build the exact cover matrix
    for name, shape in PENTOMINOES.items():
        pentomino_idx = pentomino_names.index(name)

        for orientation in get_all_orientations(shape):
            for y in range(height):
                for x in range(width):
                    # Check if placement is valid
                    cells = []
                    valid = True

                    for dx, dy in orientation:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            # Add 1 because column 0 is the root in DLX
                            cells.append(ny * width + nx + 1)
                        else:
                            valid = False
                            break

                    if not valid:
                        continue

                    # Add row: cell columns + pentomino type column (also +1 for 1-indexing)
                    cols = cells + [width * height + pentomino_idx + 1]
                    first_node = dlx.add_row(cols)
                    if first_node >= 0:
                        info = (name, x, y, orientation)
                        # Map ALL nodes in this row to the placement info
                        # (the solution may return any node from the row, not just the first)
                        node = first_node
                        row_info[node] = info
                        for _ in range(len(cols) - 1):
                            node = dlx.R[node]
                            row_info[node] = info

    # Search for solutions
    solutions = []
    for solution in dlx.search():
        board = [['.' for _ in range(width)] for _ in range(height)]

        for node in solution:
            if node in row_info:
                name, x, y, orientation = row_info[node]
                for dx, dy in orientation:
                    board[y + dy][x + dx] = name

        solutions.append(board)

        if len(solutions) >= max_solutions:
            break

    return solutions


def print_board(board: List[List[str]]) -> None:
    """Print a board nicely formatted."""
    print('+ ' + '- ' * len(board[0]) + '+')
    for row in board:
        print('| ' + ' '.join(row) + ' |')
    print('+ ' + '- ' * len(board[0]) + '+')
    print()


def main():
    """Solve and display pentomino tilings."""
    print("Pentomino Tiling with Dancing Links")
    print("=" * 40)
    print()

    # Standard 6x10 puzzle
    print("Solving 6x10 pentomino tiling...")
    solutions = solve_pentomino(6, 10, max_solutions=1)

    if solutions:
        print(f"Found solution:")
        print_board(solutions[0])
    else:
        print("No solution found!")

    # Try other board sizes
    sizes = [(5, 12), (4, 15), (3, 20)]
    for w, h in sizes:
        print(f"Solving {w}x{h} pentomino tiling...")
        solutions = solve_pentomino(w, h, max_solutions=1)
        if solutions:
            print(f"Found solution:")
            print_board(solutions[0])
        else:
            print("No solution found!")
        print()


if __name__ == "__main__":
    main()
