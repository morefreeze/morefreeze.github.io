---
layout: post
title: "Who Owns the Zebra? Solving Logic Puzzles with Algorithms"
description: "The classic Einstein riddle can drive you crazy with manual table-drawing. Translate it to an XCC problem and the algorithm finds the unique solution in under a millisecond—then we reverse it to let the algorithm automatically generate new puzzles."
category: algorithm
comments: true
tags: [knuth, exact-cover, dancing-links, CSP, zebra-puzzle, TAOCP]
---

{% include JB/setup %}

I spent an hour without solving it, then wrote 30 lines of code, and the algorithm solved it in under a millisecond.

This is the famous "Zebra Puzzle" (also known as the Einstein Riddle): five people live in a row of houses, each with a different nationality, occupation, pet, drink, and house color. You're given a bunch of clues and asked—**who owns the zebra?**

First published in *Life International* magazine in 1962, legend has it that only 2% of people can solve it.

This article introduces a completely different approach: **translate the puzzle into an XCC problem and let the Dancing Links algorithm solve it automatically**. No drawing tables, no manual reasoning—just describe "what constitutes a valid answer."

**Then we reverse it—letting the algorithm automatically generate a new logic puzzle.**

<!--more-->

---

## The Puzzle

Here are the complete 16 clues (including two implicit ones):

1. The Englishman lives in the red house
2. The diplomat lives in the yellow house
3. The painter is from Japan
4. The coffee drinker lives in the green house
5. The Norwegian lives in the leftmost house
6. The Spaniard owns the dog
7. The person in the middle house drinks milk
8. The violinist drinks orange juice
9. The white house is immediately to the left of the green house
10. The Ukrainian drinks tea
11. The horse lives next to the diplomat
12. The sculptor owns snails
13. The Norwegian lives next to the blue house
14. The nurse lives next to the fox
15. Someone owns a zebra (implicit)
16. Someone drinks water (implicit)

Question: Who owns the zebra? Who drinks water?

---

## The Pain of Manual Solving

Five categories, each with five values, assigned to five houses. Without constraints, there are $$(5!)^5 = 24{,}883{,}200{,}000$$ possible assignments.

The manual approach involves drawing an elimination matrix and gradually narrowing the scope. But "next door" type clues (9, 11, 13, 14) are particularly difficult to handle—processing them requires maintaining multiple branches of deduction chains, basically exceeding human working memory limits. Once one branch goes wrong, the entire table is void and you start over.

We need a method that doesn't fear branching, doesn't fear backtracking.

---

## Translating Clues to XCC

The previous two articles ([Colors and Stickers][dlx-colors], [Crossword Puzzle][dlx-xcc]) introduced the core idea of XCC and its applications: **primary items must be covered exactly once, secondary items can be covered multiple times but colors must be consistent**. Secondary items represent "attribute slots at the same position"—multiple clues can constrain them simultaneously, and as long as they give the same color (attribute value), the algorithm won't report a conflict.

The translation rules for the zebra puzzle are straightforward:

| Concept | Role in XCC | Description |
|:---|:---|:---|
| Each clue | **Primary item** | Each clue must be satisfied exactly once |
| Each house's attribute slot | **Secondary item** | $$N_j, J_j, P_j, D_j, C_j$$ (N=nationality, J=job, P=pet, D=drink, C=color; $$j=0..4$$) |

The color value of a secondary item is the specific attribute value. For example, "$$N_2$$ has color England" means "house 2 is occupied by the Englishman."

Generic CSP solvers can also handle this, but the XCC framework has advantages: secondary items natively support the semantic "multiple clues constrain the same slot," and solving and puzzle generation use the same modeling pattern, calling the same solver—as we'll see later.

### How Do Clues Become Options?

Take clue 1 ("The Englishman lives in the red house") as an example. We don't know which house the Englishman lives in, so we generate an option for each possibility:

```
#1  N0:England  C0:red     ← Englishman in house 0 (red)
#1  N1:England  C1:red     ← Englishman in house 1 (red)
#1  N2:England  C2:red     ← Englishman in house 2 (red)
#1  N3:England  C3:red     ← Englishman in house 3 (red)
#1  N4:England  C4:red     ← Englishman in house 4 (red)
```

Each option contains one primary item (`#1`, meaning "clue 1 is satisfied") and several secondary items (meaning "these attribute slots are set to these values").

The algorithm selects exactly one from these 5 options—once selected, the corresponding secondary items are "locked." If a subsequent clue tries to color the same $$N_j$$ a different color, the algorithm automatically backtracks.

### "Next Door" Type Clues

Clue 11 ("The horse lives next to the diplomat") is slightly more complex. "Next door" means two possibilities: horse on the left, diplomat on the right, or vice versa. For each adjacent position $$(i, i+1)$$, we must enumerate both cases:

```
#11  P0:horse  J1:diplomat    ← Horse at 0, diplomat at 1
#11  J0:diplomat  P1:horse    ← Diplomat at 0, horse at 1
#11  P1:horse  J2:diplomat    ← Horse at 1, diplomat at 2
...
```

4 pairs of adjacent positions × 2 directions = 8 options.

### Fixed Position Clues

Clue 5 ("The Norwegian lives in the leftmost house") is simplest—only one option:

```
#5  N0:Norway
```

### Total

16 clues generate a total of **80 options**. Once built, call the `DLX_C` solver from the previous article to get the unique solution instantly.

---

## Code

```python
from dlx_colors import DLX_C

# 16 primary items (clues), 25 secondary items (attribute slots)
num_primary = 16
sec_base = 16
def sec_idx(cat, house):  # cat: 0=N,1=J,2=P,3=D,4=C
    return sec_base + cat * 5 + house

# Clue 1: Englishman in red house (5 options, clue_id=0)
for j in range(5):
    add_option(0, f"#1 N{j}:England C{j}:red",
               [(sec_idx(0, j), 'England'), (sec_idx(4, j), 'red')])

# Clue 9: White house immediately left of green (4 options, clue_id=8)
for i in range(4):
    add_option(8, f"#9 C{i}:white C{i+1}:green",
               [(sec_idx(4, i), 'white'), (sec_idx(4, i+1), 'green')])

# Clue 11: Horse next to diplomat (8 options, clue_id=10)
for i in range(4):
    add_option(10, f"#11 P{i}:horse J{i+1}:diplomat",
               [(sec_idx(2, i), 'horse'), (sec_idx(1, i+1), 'diplomat')])
    add_option(10, f"#11 J{i}:diplomat P{i+1}:horse",
               [(sec_idx(1, i), 'diplomat'), (sec_idx(2, i+1), 'horse')])
```

See [zebra_puzzle.py][code_zebra] for the complete implementation. Running it produces:

```
       House       0       1       2       3       4
  --------------------------------------------------------
 Nationality  Norway Ukraine England   Spain   Japan
         Job diplomat   nurse sculptor violinist painter
         Pet     fox   horse  snails     dog   zebra
       Drink   water     tea    milk      oj  coffee
       Color  yellow    blue     red   white   green
```

**The Japanese owns the zebra, the Norwegian drinks water.**

![Zebra Puzzle Solution]({{ "/images/zebra-puzzle-solution.svg" | relative_url }})

---

## Reversing It: Automatic Puzzle Generation

Solving is "given clues, find the assignment." Reversing it—**given an assignment, find the minimum clues that make the solution unique**—is automatic puzzle generation.

### Algorithm

1. **Randomly generate a valid assignment**: randomly permute 5 values from each category into 5 houses
2. **Enumerate all possible clues**:
   - Same-house clues: $$\binom{5}{2} \times 5 = 50$$ ("attribute A and B are in the same house")
   - Adjacent-house clues: $$\binom{5}{2} \times 4 \times 2 + 5 \times 4 = 100$$ ("attribute A and B are in adjacent houses")
   - Fixed-position clues: $$5 \times 5 = 25$$ ("attribute A is in house k")
3. **Greedy removal**: shuffle clue order, try removing each one. If removal still yields a unique solution (verified by XCC), remove it; otherwise keep it

This doesn't guarantee a globally minimal clue set (that's NP-hard), but works well in practice—usually compressing to 15-20 clues.

### An Example

```python
clues, answer = generate_puzzle(seed=42)
```

Output:

```
 1. The person with Nationality=Canadian also has Color=green.
 2. The person with Drink=coffee also has Color=blue.
 3. The person with Nationality=French lives next to the person with Drink=soda.
 4. The person with Job=lawyer also has Color=yellow.
 5. The person with Job=teacher lives next to the person with Job=artist.
 6. The person with Job=artist also has Pet=cat.
 7. The person with Job=lawyer also has Drink=juice.
 8. The person with Nationality=British lives next to the person with Job=chef.
 9. The person with Pet=hamster also has Drink=coffee.
10. The person with Drink=water lives in the fourth house.
11. The person with Job=lawyer lives next to the person with Color=green.
12. The person with Pet=bird also has Color=white.
13. The person with Nationality=British also has Job=lawyer.
14. The person with Nationality=Dutch lives in the first house.
15. The person with Pet=bird lives next to the person with Pet=dog.
16. The person with Nationality=British lives next to the person with Job=teacher.
17. The person with Drink=juice lives in the second house.
```

17 clues, unique solution. Use it to test your friends.

### Key Code

Puzzle generation and solving use the same XCC modeling pattern. The only difference: when generating puzzles, we need additional **all-different** primary items—because now there aren't enough clues, the algorithm needs to explicitly know "each attribute value appears exactly once":

```python
# Each attribute value corresponds to a primary item, 5 options (which house)
for cat_i in range(num_cats):
    for v_i, val in enumerate(values[cat_i]):
        for j in range(n):
            options.append([
                (ad_idx(cat_i, v_i), None),   # primary: this value must be assigned
                (sec_idx(cat_i, j), val)       # secondary: put in house j
            ])
```

This is exactly the **CSP → XCC general translation** Knuth discusses in Exercise 100(c), with the zebra puzzle (Exercise 101) as its classic application: each variable's each value is an option, constraints are automatically guaranteed through secondary item color consistency.

---

## Knuth's Small Optimization

Knuth mentions a trick in his TAOCP 4B answers: the modeling above **does not** explicitly constrain "each attribute value can only appear in one house." For example, the algorithm doesn't directly know "if England is in house 2, it can't appear in other houses"—it just happens to derive this from the cross-constraints of the 16 clues.

If we add 25 additional **inverse mapping** secondary items (one per attribute value, color = house number), letting the algorithm detect conflicts earlier, the search tree shrinks from **112 nodes** to **32 nodes**. A few lines of code, but the time saved "just offsets" the overhead of these extra items—Knuth's words.

---

## Recap

This is the third in the series. The first two are [Colors and Stickers][dlx-colors] and [Crossword Puzzle][dlx-xcc]—recommended reading in order.

Four articles used the same solver (`DLX_C`) to solve four completely different problems:

| Article | Problem | Primary Items | Secondary Items |
|:---|:---|:---|:---|
| [Colors and Stickers][dlx-colors] | Color item bug and fix | Each word | Each cell (color = letter) |
| [Crossword Puzzle][dlx-xcc] | Packing words into grid | Each word | Each cell (color = letter) |
| This article (solving) | Satisfy logic clues | Each clue | Each attribute slot (color = attribute value) |
| This article (generating) | Find minimum clues | Clues + all-different | Same as above |

Four seemingly unrelated problems share the same underlying structure: describe "what constitutes a valid choice" and let the algorithm find the set that covers everything.

We never wrote any code about "how to reason." Each time, we just described "what constitutes a valid answer" in a different way, and the algorithm automatically found all answers.

This is the most fascinating thing about XCC: **you describe the problem, it solves it.**

---

## Complete Code

[zebra_puzzle.py][code_zebra] contains both solving and puzzle generation, depending on [dlx_colors.py][code_dlx_colors]. Just run it directly.

Change the random seed to generate a new puzzle—use it to test your friends.

[dlx-colors]: /2026/03/dlx-colors.html
[dlx-xcc]: /2026/03/dlx-xcc.html
[code_zebra]: https://github.com/morefreeze/morefreeze.github.io/blob/master/code/zebra_puzzle.py
[code_dlx_colors]: https://github.com/morefreeze/morefreeze.github.io/blob/master/code/dlx_colors.py
