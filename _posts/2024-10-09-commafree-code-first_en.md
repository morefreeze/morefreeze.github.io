---
layout: post
title: "Commafree Codes: First Encounter — Generation"
description: ""
category: algorithm
comments: true
tags: [algorithm, knuth, code]
---

{% include JB/setup %}

## Introduction

A commafree code is a **self-synchronizing** fixed-length code — fundamentally different from Huffman coding, which is a variable-length compression scheme. Given a set D of codewords of length n over an m-letter alphabet, D is commafree if for any two codewords $$x_1x_2x_3x_4$$ and $$x_5x_6x_7x_8$$ placed side by side, the shifted substrings $$x_2x_3x_4x_5$$, $$x_3x_4x_5x_6$$, and $$x_4x_5x_6x_7$$ are never codewords. This property lets a receiver correctly segment a concatenated message without any delimiters.

Take n=4 as an example: in "likethis", "like" and "this" are codewords, while the shifted substrings "iket", "keth", and "ethi" are not. Also, periodic strings like "dodo" or "gaga" cannot be codewords, since placing two copies side by side produces the original string as an interior substring.

<!--more-->

## m=2

For clarity we work with symbols 0 through m−1 rather than actual letters.

First, the upper bound: periodic strings are excluded, leaving $$m^4 - m^2$$ aperiodic strings of length 4. Choosing a codeword also rules out its 3 other cyclic shifts, so the maximum set size is $$\frac{m^4 - m^2}{4}$$.

When m=2, the bound is $$\frac{16-4}{4} = 3$$, and there are exactly 3 cyclic classes:

1. [0001] = {0001, 0010, 0100, 1000}
2. [0011] = {0011, 0110, 1100, 1001}
3. [0111] = {0111, 1110, 1101, 1011}

Each set on the right consists of cyclic rotations of the representative on the left. We call the lexicographically smallest member of each class its **prime word**.

For m=2 there is a neat special property: simply taking the lexicographically smallest element from each cyclic class — 0001, 0011, 0111 — already yields a valid commafree code that attains the upper bound of 3. This "take the minimum" trick does **not** generalize to m≥3.

## m=3

When m=3, the bound is $$\frac{81-9}{4} = 18$$, so there are 18 cyclic classes (prime words). Listed in lexicographic order: {0001, 0002, 0011, 0012, 0021, 0022, 0102, 0111, 0112, 0121, 0122, 0211, 0212, 0221, 0222, 1112, 1122, 1222}.

Can we actually choose all 18 words and reach the upper bound? No — for instance, after choosing 0001 and 0011, adding 1112 is impossible (because 0001 ∘ 1112 contains 0011 as an interior substring). The true maximum requires a search, which is the topic of the next post.

Generating the list of prime words is straightforward:

{% highlight python linenos %}
def find_prime_codes(n, alphabet_str):
    codes = []

    def generate_words(length, prefix=""):
        """Generate all possible words of given length"""
        if length == 0:
            if not is_periodic(prefix) and is_prime_code(prefix):
                codes.append(prefix)
            return

        for letter in alphabet_str:
            generate_words(length-1, prefix + letter)

    generate_words(n)
    return tuple(sorted(codes))
{% endhighlight %}

The time complexity is $$O(m^n)$$, which is acceptable for generating candidates. But when the problem becomes picking a maximum commafree subset from these candidates, the complexity is entirely different — that general solution will be covered in the next post.
