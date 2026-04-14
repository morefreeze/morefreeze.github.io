#!/usr/bin/env python3
"""
Pentomino Three-Colorability Solver
Based on TAOCP Vol 4B, Exercise 7.2.2.1-277 (rated [25])

Problem: How many of the 6×10 pentomino packings are strongly three-colorable?
"Strong" means no two pentominoes of the same color touch each other,
not even at corner points (8-connected adjacency).

Two-phase approach:
  Phase 1: Enumerate all 2339 packings via Dancing Links (DLX)
  Phase 2: For each packing, check 3-colorability of the adjacency graph
"""

from typing import Dict, List, Optional, Set, Tuple

from pentomino_dlx import (
    DancingLinks,
    PENTOMINOES,
    get_all_orientations,
)


def get_all_packings(
    width: int = 6, height: int = 10
) -> List[Dict[str, Set[Tuple[int, int]]]]:
    """Enumerate all pentomino packings of a width×height rectangle.

    Returns a list of packings, where each packing maps pentomino name
    to the set of (x, y) cells it occupies.
    """
    dlx = DancingLinks(width * height + len(PENTOMINOES))
    pentomino_names = list(PENTOMINOES.keys())

    # Map any node in a DLX row to its placement info
    row_info = {}

    for name, shape in PENTOMINOES.items():
        pentomino_idx = pentomino_names.index(name)
        for orientation in get_all_orientations(shape):
            for y in range(height):
                for x in range(width):
                    cells = []
                    valid = True
                    for dx, dy in orientation:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            cells.append(ny * width + nx + 1)
                        else:
                            valid = False
                            break
                    if not valid:
                        continue

                    cols = cells + [width * height + pentomino_idx + 1]
                    first_node = dlx.add_row(cols)
                    if first_node >= 0:
                        info = (name, x, y, orientation)
                        node = first_node
                        row_info[node] = info
                        for _ in range(len(cols) - 1):
                            node = dlx.R[node]
                            row_info[node] = info

    packings = []
    for solution in dlx.search():
        packing = {}
        for node in solution:
            if node in row_info:
                name, px, py, orientation = row_info[node]
                cells = set()
                for dx, dy in orientation:
                    cells.add((px + dx, py + dy))
                packing[name] = cells
        packings.append(packing)

    return packings


def build_adjacency(
    packing: Dict[str, Set[Tuple[int, int]]]
) -> Dict[str, Set[str]]:
    """Build the strong adjacency graph for a packing.

    Two pentominoes are adjacent if any of their cells are within
    Chebyshev distance 1 (sharing an edge OR a corner).

    Returns adjacency list: piece_name -> set of adjacent piece names.
    """
    names = list(packing.keys())
    adjacency = {name: set() for name in names}

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            # Check if any cell from piece a is within Chebyshev distance 1
            # of any cell from piece b
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


def is_three_colorable(
    adjacency: Dict[str, Set[str]],
) -> Tuple[bool, Optional[Dict[str, int]]]:
    """Check if the adjacency graph is 3-colorable via backtracking.

    Returns (True, coloring) if colorable, (False, None) otherwise.
    Coloring maps piece name to color index (0, 1, or 2).
    """
    names = list(adjacency.keys())
    n = len(names)
    coloring = {}

    def backtrack(idx: int) -> bool:
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


def count_three_colorable(
    width: int = 6, height: int = 10
) -> Tuple[int, int, List[Tuple[Dict[str, Set[Tuple[int, int]]], Dict[str, int]]]]:
    """Count strongly 3-colorable packings.

    Returns (total, colorable_count, examples) where examples is a list
    of (packing, coloring) tuples for colorable packings.
    """
    print(f"Enumerating all {width}×{height} packings...")
    packings = get_all_packings(width, height)
    total = len(packings)
    print(f"Found {total} packings.")

    colorable_count = 0
    examples = []
    max_examples = 3

    for i, packing in enumerate(packings):
        if (i + 1) % 500 == 0:
            print(f"  Checked {i + 1}/{total} packings...")

        adjacency = build_adjacency(packing)
        ok, coloring = is_three_colorable(adjacency)
        if ok:
            colorable_count += 1
            if len(examples) < max_examples:
                examples.append((packing, coloring))

    return total, colorable_count, examples


def render_colored_board(
    packing: Dict[str, Set[Tuple[int, int]]],
    coloring: Dict[str, int],
    width: int = 6,
    height: int = 10,
) -> str:
    """Render a packing with color annotations as ASCII art."""
    color_symbols = {0: "R", 1: "W", 2: "B"}
    board = [["." for _ in range(width)] for _ in range(height)]

    for name, cells in packing.items():
        color = color_symbols.get(coloring[name], "?")
        for x, y in cells:
            board[y][x] = name

    lines = ["+ " + "- " * width + "+"]
    for row in board:
        lines.append("| " + " ".join(row) + " |")
    lines.append("+ " + "- " * width + "+")

    legend = []
    for name in sorted(coloring.keys()):
        legend.append(f"{name}={color_symbols[coloring[name]]}")
    lines.append("Colors: " + ", ".join(legend))

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("Pentomino Strong Three-Colorability (TAOCP 7.2.2.1-277)")
    print("=" * 60)
    print()

    width, height = 6, 10
    total, colorable_count, examples = count_three_colorable(width, height)

    print()
    # The DLX solver counts all board symmetries (4 for a non-square rectangle).
    # The canonical counts are: 2339 total packings for 6×10.
    symmetry_factor = 4
    distinct_total = total // symmetry_factor
    distinct_colorable = colorable_count // symmetry_factor

    print(f"Total packings (with sym):  {total}")
    print(f"3-colorable (with sym):     {colorable_count}")
    print(f"Non-3-colorable (with sym): {total - colorable_count}")
    print()
    print(f"Distinct packings:          {distinct_total}")
    print(f"Distinct 3-colorable:       {distinct_colorable}")
    print(f"Distinct non-3-colorable:   {distinct_total - distinct_colorable}")
    print()

    if examples:
        print("Example colorings:")
        color_names = {0: "Red", 1: "White", 2: "Blue"}
        for i, (packing, coloring) in enumerate(examples):
            print(f"\n--- Example {i + 1} ---")
            print(render_colored_board(packing, coloring, width, height))
            # Show adjacency info
            groups = {0: [], 1: [], 2: []}
            for name, c in coloring.items():
                groups[c].append(name)
            for c in range(3):
                print(f"  {color_names[c]}: {', '.join(sorted(groups[c]))}")


if __name__ == "__main__":
    main()
