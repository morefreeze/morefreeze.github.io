#!/usr/bin/env python3
"""
Verify knight's tour counts for 7x7 and 8x8 boards.

Known results (from literature / OEIS):
  - 7x7 closed tours: 0  (odd board, bipartite impossibility)
  - 8x8 closed tours: 26,534,728,821,064 directed Hamiltonian circuits
                      (= 13,267,364,410,532 undirected circuits × 2)

What this script does:
  1. Prove 7x7 has 0 closed tours via bipartite argument (no DLX needed)
  2. Count 8x8 closed tours for a fixed time, report rate & projected total
"""
import sys
import time

sys.path.insert(0, '/Users/bytedance/mygit/morefreeze.github.io/code')
from knight_tour import build_closed_tour, DLX, reconstruct_circuit

KNOWN_8x8_DIRECTED = 26_534_728_821_064  # directed Hamiltonian circuits on 8x8


def bipartite_check(n: int) -> tuple[bool, str]:
    """
    A knight always alternates between black and white squares.
    A Hamiltonian *circuit* must visit equal numbers of each color.
    On an odd×odd board, the two colors are unequal → impossible.
    """
    total = n * n
    if total % 2 == 1:
        black = (total + 1) // 2
        white = total - black
        return (False,
                f"{n}×{n} has {black} black + {white} white squares; "
                f"circuit needs equal visits → IMPOSSIBLE")
    return (True,
            f"{n}×{n} has {total//2} black + {total//2} white squares → may exist")


def count_raw_closed(n: int, time_limit: float = 120.0,
                     report_every: int = 50_000) -> tuple[int, int, bool]:
    """
    Count directed Hamiltonian circuits by DLX.
    Returns (n_circuits, n_raw_dlx_solutions, exhausted).

    NOTE: the time check runs per DLX *solution*, not per node visited.
    This is fine for 8x8 which has abundant solutions; do NOT call this
    for boards with zero solutions (DLX would never yield → time check hangs).
    """
    num_items, options, labels = build_closed_tour(n)
    dlx = DLX(num_items, options)

    circuits = 0
    raw = 0
    t0 = time.time()

    for sol in dlx.solve():
        raw += 1
        if reconstruct_circuit(sol, labels, n) is not None:
            circuits += 1

        if raw % report_every == 0:
            elapsed = time.time() - t0
            rate_raw = raw / elapsed
            rate_cir = circuits / elapsed
            eta_h = KNOWN_8x8_DIRECTED / rate_cir / 3600 if n == 8 and rate_cir > 0 else None
            eta_str = f"  ETA full≈{eta_h:,.0f}h" if eta_h else ""
            print(f"  raw={raw:>12,}  circuits={circuits:>10,}  "
                  f"elapsed={elapsed:6.1f}s  rate={rate_raw:,.0f}/s{eta_str}",
                  flush=True)

        if time.time() - t0 >= time_limit:
            return circuits, raw, False

    return circuits, raw, True


# ──────────────────────────────────────────────────────────────
# 7×7
# ──────────────────────────────────────────────────────────────
print("=" * 65)
print("7×7 Closed Knight's Tours")
print("=" * 65)
possible, reason = bipartite_check(7)
print(f"Bipartite check: {reason}")
if not possible:
    print("→ Closed tours on 7×7: 0  (no DLX run needed)")
    print()
    print("  Proof sketch:")
    print("  • Color the 7×7 board like a chessboard: 25 black, 24 white squares")
    print("  • A knight move always goes black↔white")
    print("  • A Hamiltonian circuit has 49 edges, forming a closed walk")
    print("  • Closed walk on a bipartite graph requires equal #black and #white")
    print("  • 25 ≠ 24  →  contradiction  →  no closed tour exists")
print()

# ──────────────────────────────────────────────────────────────
# 8×8
# ──────────────────────────────────────────────────────────────
print("=" * 65)
print("8×8 Closed Knight's Tours")
print("=" * 65)
possible, reason = bipartite_check(8)
print(f"Bipartite check: {reason}")
print(f"Known exact total (directed): {KNOWN_8x8_DIRECTED:,}")
print()

TIME_LIMIT = 120.0  # seconds — full enumeration would take ~weeks in Python
print(f"Running DLX for up to {TIME_LIMIT:.0f} s …")
print(f"(Full enumeration at Python speed would take many days)")
print()

t_start = time.time()
circuits_8, raw_8, done_8 = count_raw_closed(8, time_limit=TIME_LIMIT)
elapsed_8 = time.time() - t_start

print()
if done_8:
    print(f"✓  DLX exhausted: found {circuits_8:,} directed Hamiltonian circuits.")
    match = "✓ MATCH" if circuits_8 == KNOWN_8x8_DIRECTED else "✗ MISMATCH"
    print(f"   Known: {KNOWN_8x8_DIRECTED:,}  →  {match}")
else:
    if raw_8 == 0:
        print("  No DLX solutions found yet (board space unexplored — check encoding).")
    else:
        rate_raw = raw_8 / elapsed_8
        rate_cir = circuits_8 / elapsed_8
        multi_pct = (raw_8 - circuits_8) / raw_8 * 100
        projected_h = KNOWN_8x8_DIRECTED / rate_cir / 3600 if rate_cir > 0 else float('inf')
        pct_done = circuits_8 / KNOWN_8x8_DIRECTED * 100

        print(f"  Search incomplete after {elapsed_8:.1f} s.")
        print(f"  DLX solutions examined : {raw_8:>14,}")
        print(f"  Hamiltonian circuits   : {circuits_8:>14,}  ({100-multi_pct:.1f}% of DLX solutions)")
        print(f"  Multi-cycle (discarded): {raw_8-circuits_8:>14,}  ({multi_pct:.1f}%)")
        print(f"  Rate (DLX sol/s)       : {rate_raw:>14,.0f}")
        print(f"  Rate (circuits/s)      : {rate_cir:>14,.0f}")
        print()
        print(f"  Known total            : {KNOWN_8x8_DIRECTED:>14,}")
        print(f"  Found so far           : {circuits_8:>14,}  ({pct_done:.5f}%)")
        print(f"  Projected full time    : {projected_h:,.1f} hours at current Python rate")
