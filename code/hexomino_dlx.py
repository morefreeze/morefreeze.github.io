#!/usr/bin/env python3
"""
Hexomino Tiling with Dancing Links (DLX) Algorithm

Solves the problem of tiling a 10x21 (or 15x14) rectangle with all 35 free
hexominoes. Extends the pentomino DLX solver from pentomino_dlx.py.

Usage:
    python3 hexomino_dlx.py              # Solve 10x21 (default)
    python3 hexomino_dlx.py 15 14        # Solve 15x14
"""

import sys
import time
import colorsys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pentomino_dlx import DancingLinks, get_all_orientations


def generate_hexominoes():
    """Generate all 35 free hexominoes via BFS from a single cell.

    Returns a list of 35 shapes, each shape is a list of (x, y) tuples.
    """
    def normalize(shape):
        min_x = min(x for x, y in shape)
        min_y = min(y for x, y in shape)
        return tuple(sorted((x - min_x, y - min_y) for x, y in shape))

    def get_canonical(shape):
        """Return the lexicographically smallest form under all D4 symmetries."""
        forms = []
        s = list(shape)
        for _ in range(4):
            s = normalize([(y, -x) for x, y in s])
            forms.append(s)
            forms.append(normalize([(-x, y) for x, y in s]))
        return min(forms)

    # BFS: grow polyomino from size 1 to size 6
    current = {((0, 0),)}
    for _ in range(5):
        nxt = set()
        for shape in current:
            sl = list(shape)
            ss = set(shape)
            for x, y in shape:
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in ss:
                        nxt.add(normalize(sl + [(nx, ny)]))
        current = nxt

    # Deduplicate under rotations and reflections
    seen = set()
    result = []
    for shape in current:
        canon = get_canonical(shape)
        if canon not in seen:
            seen.add(canon)
            result.append(list(shape))
    return result


def solve_hexomino(width, height, hexominoes, max_solutions=1, hint_piece=None):
    """Solve hexomino tiling using DLX.

    Args:
        width: Board width
        height: Board height
        hexominoes: List of 35 hexomino shapes
        max_solutions: Stop after finding this many solutions
        hint_piece: (piece_idx, cells) to pre-place for symmetry breaking,
                    e.g. (7, [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0)])

    Returns:
        List of solved boards (each a 2D list of piece indices)
    """
    num = len(hexominoes)
    dlx = DancingLinks(width * height + num)
    row_info = {}

    # Build exact cover matrix
    for idx, shape in enumerate(hexominoes):
        for orient in get_all_orientations(shape):
            for y in range(height):
                for x in range(width):
                    cells = []
                    valid = True
                    for dx, dy in orient:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            cells.append(ny * width + nx + 1)
                        else:
                            valid = False
                            break
                    if not valid:
                        continue
                    cols = cells + [width * height + idx + 1]
                    first = dlx.add_row(cols)
                    if first >= 0:
                        info = (idx, x, y, orient)
                        node = first
                        row_info[node] = info
                        for _ in range(len(cols) - 1):
                            node = dlx.R[node]
                            row_info[node] = info

    # Pre-place hint piece to break symmetry
    if hint_piece:
        hint_idx, hint_cells = hint_piece
        for cx, cy in hint_cells:
            dlx.cover(cy * width + cx + 1)
        dlx.cover(width * height + hint_idx + 1)

    # Search for solutions
    solutions = []
    for sol in dlx.search():
        board = [[-1] * width for _ in range(height)]
        if hint_piece:
            hint_idx, hint_cells = hint_piece
            for cx, cy in hint_cells:
                board[cy][cx] = hint_idx
        for node in sol:
            if node in row_info:
                idx, x, y, orient = row_info[node]
                for dx, dy in orient:
                    board[y + dy][x + dx] = idx
        solutions.append(board)
        if len(solutions) >= max_solutions:
            break
    return solutions


def generate_svg(board, width, height, out_path):
    """Generate SVG visualization of hexomino tiling."""
    num = len(set(c for row in board for c in row if c >= 0))
    cs = 28  # cell size
    pad = 15
    sw = width * cs + pad * 2
    sh = height * cs + pad * 2 + 18

    colors = []
    for i in range(35):
        r, g, b = colorsys.hls_to_rgb(i / 35, 0.50, 0.70)
        colors.append('#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255)))

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d">' % (sw, sh),
        '<style>',
        '.c{stroke:#fff;stroke-width:1.5}',
        '.l{font-family:Arial,sans-serif;font-size:8px;font-weight:bold;fill:#fff;text-anchor:middle;dominant-baseline:central}',
        '.t{font-family:Arial,sans-serif;font-size:11px;font-weight:bold;fill:#2d3748;text-anchor:middle}',
        '</style>',
        '<text x="%d" y="13" class="t">%d x %d Hexomino Tiling (35 pieces)</text>' % (sw / 2, width, height),
        '<g transform="translate(%d,%d)">' % (pad, pad + 14),
    ]
    for r in range(height):
        for c in range(width):
            idx = board[r][c]
            x, y = c * cs, r * cs
            lines.append('<rect x="%d" y="%d" width="%d" height="%d" class="c" style="fill:%s"/>' % (x, y, cs, cs, colors[idx]))
            lines.append('<text x="%d" y="%d" class="l">%d</text>' % (x + cs / 2, y + cs / 2, idx))
    lines.append('</g></svg>')

    with open(out_path, 'w') as f:
        f.write('\n'.join(lines))


def print_board(board):
    """Print a board nicely formatted."""
    print('+ ' + '- ' * len(board[0]) + '+')
    for row in board:
        print('| ' + ' '.join(str(c).rjust(2) for c in row) + ' |')
    print('+ ' + '- ' * len(board[0]) + '+')
    print()


def main():
    t0 = time.time()
    hexominoes = generate_hexominoes()
    print("%d hexominoes generated in %.1fs" % (len(hexominoes), time.time() - t0))

    # Default board dimensions
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    height = int(sys.argv[2]) if len(sys.argv) > 2 else 21

    # Find the straight hexomino (piece 7) for symmetry breaking
    straight_idx = None
    for i, shape in enumerate(hexominoes):
        xs = [x for x, y in shape]
        ys = [y for x, y in shape]
        if len(shape) == 6 and len(set(ys)) == 1 and max(xs) - min(xs) == 5:
            straight_idx = i
            break

    hint = None
    if straight_idx is not None and width >= 6:
        hint = (straight_idx, [(x, 0) for x in range(6)])
        print("Pre-placing straight hexomino (#%d) at row 0, cols 0-5" % straight_idx)

    print("Solving %dx%d..." % (width, height))
    t1 = time.time()
    solutions = solve_hexomino(width, height, hexominoes, max_solutions=1, hint_piece=hint)
    dt = time.time() - t1

    if solutions:
        print("Solution found in %.1fs" % dt)
        print_board(solutions[0])

        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out = os.path.join(base, 'images', 'hexomino-tiling-solution.svg')
        generate_svg(solutions[0], width, height, out)
        print("SVG saved to %s" % out)
    else:
        print("No solution found in %.1fs" % dt)


if __name__ == '__main__':
    main()
