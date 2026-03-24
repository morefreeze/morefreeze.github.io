---
layout: post
title: "From Chinese Rings to Gray Code: Traversing All Binary Strings One Bit at a Time"
description: "How a Song Dynasty puzzle connects to 5G signal modulation: derive the recurrence formula, reflected construction, and Knuth's Algorithm G for Gray codes, with full Python implementation and real-world applications."
category: algorithm
comments: true
tags: [knuth, gray-code, TAOCP, python, combinatorics, puzzle]
---

{% include JB/setup %}

## Introduction

A traditional puzzle documented in Song Dynasty China shares the exact same mathematical structure as the signal modulation inside your 5G phone. Believe it?

In the previous posts, we've been dealing with [exact cover][exact-cover] and [Dancing Links][dancing-link], where the core problem is "finding subsets that satisfy constraints in a combinatorial space." This time we're switching gears — instead of selecting, we're **traversing**: how do you visit all n-bit binary strings exactly once, changing only one bit at each step?

The answer is hidden in a traditional Chinese puzzle.

<!--more-->

## Chinese Rings

The Chinese Rings puzzle looks roughly like this: a bar passes through n rings, which are connected by chains. The goal is simple — remove all the rings from the bar.

```
    ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐
    │○│ │○│ │○│ │○│ │○│   ← n rings
    └┬┘ └┬┘ └┬┘ └┬┘ └┬┘
     │   │   │   │   │
═════╪═══╪═══╪═══╪═══╪═════  ← bar
     5   4   3   2   1      ← numbered right to left
```

There are only two rules:

**Rule a) The rightmost ring** can always be removed or put back:

```
    ┌─┐ ┌─┐ ┌─┐              ┌─┐ ┌─┐
    │○│ │○│ │○│              │○│ │○│
    └┬┘ └┬┘ └┬┘              └┬┘ └┬┘
     │   │   │        →       │   │    ┌─┐
═════╪═══╪═══╪═════      ═════╪═══╪════│○│══
     3   2   1                3   2    └─┘
   state: 111              state: 110    ↑ ring 1 removed
```

**Rule b) Any other ring** can only be operated when the ring immediately to its right is on the bar AND all rings further to the right are off the bar:

```
    ┌─┐ ┌─┐                     ┌─┐
    │○│ │○│                     │○│
    └┬┘ └┬┘                     └┬┘
     │   │            →          │
═════╪═══╪════════      ═════════╪════════
     3   2                       2
   state: 110                 state: 010
   ring 2 on ✓ ring 1 off ✓     ↑ ring 3 removed
```

In other words, to operate ring k (counting from the right, k > 1), ring k-1 must be on the bar, and rings k-2, k-3, ... must all be off. This constraint makes the problem far less simple than it looks.

**Question: With n rings, what is the minimum number of steps to remove them all?**

## Working Through Small Cases

Let's start small. We'll use 1 to mean the ring is on the bar and 0 to mean it's off, with the leftmost position being ring n (the "deepest") and the rightmost being ring 1.

**n = 1**: Just remove it. 1 step.

**n = 2**: Remove ring 1, then ring 2. 2 steps. (State transitions: `11 → 10 → 00`)

**n = 3**: This is where it gets interesting.

| Step | State | Action |
|------|-------|--------|
| 0 | `111` | Initial |
| 1 | `110` | Remove ring 1 |
| 2 | `010` | Remove ring 3 (ring 2 on, ring 1 off ✓) |
| 3 | `011` | Put ring 1 back |
| 4 | `001` | Remove ring 2 (ring 1 on, no rings further right ✓) |
| 5 | `000` | Remove ring 1 |

Done in 5 steps. The recursive structure is already emerging: to disassemble n rings, first remove rings 1 through n-2 (to clear the way), operate ring n, put rings 1 through n-2 back (to prepare for removing ring n-1), and finally disassemble the first n-1 rings. Letting T(n) denote the minimum number of steps:

$$T(n) = T(n-2) + 1 + T(n-2) + T(n-1) = T(n-1) + 2T(n-2) + 1 \tag{1}$$

## From Binary Strings to Gray Code

Let's look back at the state sequence for n=3:

```
111 → 110 → 010 → 011 → 001 → 000
```

Between every pair of adjacent states, **exactly one bit differs**. This is no coincidence — the rules themselves require that each step changes only one ring.

But here's what's more interesting: these 6 states only pass through 6 of the 8 possible 3-bit strings, missing `100` and `101`. Can the puzzle not reach those states?

It can. The rules of the Chinese Rings actually define a path through **all** $$2^n$$ states. It's just that `111` isn't at the end of the path — the full path is:

```
000 - 001 - 011 - 010 - 110 - 111 - 101 - 100
```

`111` sits in the middle of the path (at position 5), so going from `111` to `000` only takes 5 steps to the left, while `101` and `100` are to its right and don't need to be visited.

This path has a name: **Gray code**.

Formal definition: an n-bit Gray code is a permutation $$v_0, v_1, \ldots, v_{2^n-1}$$ of all $$2^n$$ n-bit binary strings such that consecutive strings $$v_k$$ and $$v_{k+1}$$ differ in exactly one bit. The state transition graph of the Chinese Rings is precisely such a path — from $$0\ldots0$$ to $$10\ldots0$$, visiting all $$2^n$$ states, changing one bit at each step.

Gray code is named after Frank Gray (1953 Bell Labs patent), but French judge Louis Gros discovered it as early as 1872 through his analysis of the Chinese Rings puzzle. Knuth makes a point in TAOCP that Gros is "the true inventor of Gray binary code."

## The Reflected Construction

How do you construct a Gray code? The most elegant way is the **reflected construction**.

Let $$\Gamma_n$$ be the n-bit Gray code sequence, defined as:

$$\Gamma_0 = \varepsilon \text{ (empty string)}$$

$$\Gamma_{n+1} = 0\Gamma_n, \; 1\Gamma_n^R \tag{2}$$

where $$\Gamma_n^R$$ is $$\Gamma_n$$ in reverse order, $$0\Gamma_n$$ means prepending 0 to each string, and $$1\Gamma_n^R$$ means prepending 1 to each string in the reversed sequence.

Let's expand it:

**n=1**: $$\Gamma_1 = 0, 1$$

**n=2**: $$\Gamma_2 = 0\Gamma_1, 1\Gamma_1^R = 00, 01, 11, 10$$

**n=3**: $$\Gamma_3 = 0\Gamma_2, 1\Gamma_2^R = 000, 001, 011, 010, 110, 111, 101, 100$$

Notice how the first half and second half of $$\Gamma_3$$ are mirror images — the second half is the "reflection" of the first half with the leading bit flipped from 0 to 1. That's where the name "reflected" comes from.

Why does this correspond to the Chinese Rings? Because the recursive disassembly of the puzzle has exactly the same recursive structure as the reflected construction: when disassembling n rings, you first go through all states of the first n-1 rings (corresponding to $$0\Gamma_{n-1}$$), then operate ring n (the leading bit changes from 0 to 1), and then traverse the first n-1 rings' states in reverse (corresponding to $$1\Gamma_{n-1}^R$$).

The reflected construction also yields a beautifully simple formula. The k-th element of the Gray code can be computed directly:

$$g(k) = k \oplus \lfloor k/2 \rfloor \tag{3}$$

where $$\oplus$$ is the XOR operation. One line in Python:

{% highlight python %}
def gray(k):
    return k ^ (k >> 1)
{% endhighlight %}

For example, `gray(0)=0, gray(1)=1, gray(2)=3, gray(3)=2, gray(4)=6, gray(5)=7, gray(6)=5, gray(7)=4`, which in binary is `000, 001, 011, 010, 110, 111, 101, 100` — exactly $$\Gamma_3$$ from above.

## Algorithm G

Formula (3) is certainly enough to generate Gray codes, but Knuth presents a cleverer online algorithm in TAOCP called **Algorithm G**. Instead of computing $$g(k)$$, it maintains a **parity bit** to decide which bit to flip at each step.

The core logic is:

- If the current parity is even, flip the rightmost bit (bit 0)
- If the current parity is odd, find the rightmost 1 and flip the bit to its left

Then toggle the parity. That's it.

{% highlight python linenos %}
def algorithm_g(n):
    """Generate all n-bit Gray code using Knuth's Algorithm G."""
    a = [0] * (n + 1)  # a[0..n-1] is the n-tuple, a[n] is sentinel
    # G1: Initialize
    parity = 0
    while True:
        # G2: Visit
        yield a[:n]

        # G3: Choose j
        if parity == 0:
            j = 0
        else:
            # Find rightmost 1, then go one position left
            k = 0
            while a[k] == 0:
                k += 1
            j = k + 1

        # G4: Complement coordinate j
        if j == n:
            break  # Terminate: we've visited all 2^n tuples
        a[j] = 1 - a[j]
        parity = 1 - parity
{% endhighlight %}

Step by step:

- **G1** (lines 3-5): Initialize the n-tuple to all zeros, parity to 0. An extra `a[n]` is allocated as a sentinel.
- **G2** (line 8): Output the current n-tuple.
- **G3** (lines 11-16): If parity is even, $$j=0$$ (flip the rightmost bit). If odd, find the position $$k$$ of the rightmost 1, and set $$j=k+1$$. When $$j=n$$, all $$2^n$$ strings have been visited and the algorithm terminates.
- **G4** (lines 20-21): Flip $$a_j$$ and toggle the parity.

Let's run it for n=4:

{% highlight python %}
for code in algorithm_g(4):
    print(''.join(map(str, reversed(code))))  # high bits first
{% endhighlight %}

Output:

```
0000
0001
0011
0010
0110
0111
0101
0100
1100
1101
1111
1110
1010
1011
1001
1000
```

All 16 four-bit strings appear, with each consecutive pair differing in exactly one bit. Note that `1111` appears at position 10 (counting from 0), so disassembling 4 rings from `1111` to `0000` means walking 10 steps back along this path — exactly matching T(4) = 10, which we'll compute below.

## Minimum Number of Steps

Back to the opening question.

We now know that the state graph of the Chinese Rings is a Gray code path from $$0\ldots0$$ to $$10\ldots0$$, with $$2^n$$ nodes and $$2^n - 1$$ edges. The state $$1\ldots1$$ (all rings on the bar) sits somewhere in the middle of this path; let T(n) be its distance to $$0\ldots0$$.

Using the recursive structure of the reflected construction, we can derive an elegant relation. In $$\Gamma_n$$, the string $$1\ldots1$$ (n ones) appears in the second half $$1\Gamma_{n-1}^R$$, corresponding to $$1\ldots1$$ (n-1 ones) in $$\Gamma_{n-1}^R$$. Because of the reversal:

$$T(n) = 2^{n-1} + (2^{n-1} - 1 - T(n-1)) = 2^n - 1 - T(n-1) \tag{4}$$

That is, $$T(n) + T(n-1) = 2^n - 1$$. Solving this recurrence gives the closed-form formula:

$$T(n) = \left\lfloor \frac{2^{n+1} - 1}{3} \right\rfloor \tag{5}$$

Let's verify: $$T(1)=1, T(2)=2, T(3)=5, T(4)=10, T(5)=21, T(6)=42, T(7)=85$$.

7 rings require 85 steps — no wonder the ancients called it a brain-teaser. Interestingly, John Wallis pointed out in 1693 that starting from state $$10\ldots0$$ (only the deepest ring on the bar) makes the disassembly even harder — you'd have to traverse the entire path, taking $$2^n - 1$$ steps. The everyday starting point $$1\ldots1$$ (all rings on) happens to sit slightly past the middle of the path, so the number of steps is roughly $$\frac{2}{3}$$ of $$2^n$$.

## Gray Code in the Real World

Gray code isn't just a mathematical curiosity — it shows up in devices you use every day.

**Rotary encoders**: Mouse scroll wheels, volume knobs, industrial robot joints — all need to convert "how many degrees rotated" into digital signals. With ordinary binary, jumping from `011` to `100` changes all three bits simultaneously. If the sensor reads them with even a tiny timing difference, it could momentarily see `000`, `111`, or other erroneous intermediate states. With Gray code, only one bit changes per step, so a misread is off by at most one unit.

**Frank Gray's motivation**: Gray was at Bell Labs working on pulse code modulation (PCM) for television signals. When quantizing analog signals, encoding adjacent quantization levels in Gray code dramatically reduces the distortion caused by sampling errors. That's the engineering story behind his 1953 patent.

**Digital communications**: The QAM (Quadrature Amplitude Modulation) constellation diagrams used in 4G/5G label adjacent symbol points with Gray codes. The most common "one-step" errors only affect a single bit instead of multiple bits, directly improving error correction efficiency. Every time you stream video or make a call, the modem quietly uses Gray code under the hood.

## Practice Problems

> Difficulty ratings follow TAOCP convention: `[00]` trivial → `[50]` research-level; prefix `M` = mathematically oriented, `HM` = requires higher mathematics.

1. **[20] Inverse Gray code**: Given $$g(k) = k \oplus \lfloor k/2 \rfloor$$, and a Gray code value $$v$$, can you recover the original index $$k$$ efficiently? Try to write an O(log n) algorithm.

2. **[10] Step count**: Using the formula $$T(n) = \lfloor (2^{n+1} - 1) / 3 \rfloor$$, how many steps does a 10-ring Chinese Rings puzzle require at minimum?

   <details>
   <summary>Click to reveal</summary>
   T(10) = 341
   </details>

3. **[M30] Correctness of Algorithm G**: Why does maintaining a single parity bit guarantee that each step flips exactly one bit while visiting all $$2^n$$ states? Try to sketch a proof using the reflected construction.

4. **[M46] Open problem**: Instead of "change exactly one bit per step," what if we required "change exactly two bits per step"? Does such a Hamiltonian path exist on the n-cube?

Feel free to share your solutions — or your code — in the comments below.

## What's Next

Gray code comes in far more than one flavor. The standard reflected Gray code is just the most classic one — there are also balanced (each bit flips as evenly as possible), monotonic (the center of gravity of black/white tokens moves monotonically), complementary (the first and second halves are complements), and many other variants. Next time, we'll look at Knuth's **Algorithm L** — a loopless Gray code generation algorithm using focus pointers, where each step takes strictly O(1) time, echoing the pointer tricks of Dancing Links.

If you found this useful, sharing it with a friend who loves algorithms is the best way to support this blog.

## Further Reading

- **The Art of Computer Programming, Volume 4A** (Knuth): Section 7.2.1.1 is the authoritative source for everything in this post, with complete proofs and many more variants. If you read only one algorithm book in your lifetime, make it this one.
- [Gray code — Wikipedia](https://en.wikipedia.org/wiki/Gray_code): Covers non-binary Gray codes, balanced Gray codes, and many variants not discussed here, along with richer historical context.
- [Louis Gros (1872)](https://en.wikipedia.org/wiki/Gray_code#History): The French judge who discovered the connection between Chinese Rings and Gray code 81 years before Frank Gray's patent — Knuth calls him the "true inventor."

[exact-cover]: {% post_url 2024-07-11-exact-cover %}
[dancing-link]: {% post_url 2024-07-15-dancing-link %}
[backtrack]: {% post_url 2024-08-13-backtrack %}
