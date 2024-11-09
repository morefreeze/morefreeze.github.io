---
layout: post
title: "commafree code初次见面——生成"
description: ""
category: note
comments: true
tags: [algorithm, knuth, code]
---

{% include JB/setup %}

## 引言

commafree code是一种编码方式，就像Huffman编码一样，在一个由m个字母构成的长度为n的单词集合D中，如果相邻的两个单词之间的任意长度为n的字串不在D中出现，那么这个D最多可以由多少个不同的单词组成就是要研究的问题。但这里我们先把问题简化，考虑n=4的情况，比如likethis就符合条件，因为iket、keth、ethi就不是单词。另外，自身循环的也不考虑，比如dodo，如果是两个dodo拼接，那么dodo一定会出现在中间的子串中。

<!--more-->

## m=2

为了便于表达和研究，我们不关心单词是否是真实的单词，只用0到m-1来表示单词。当m=2时，容易看出只有3种情况：

1. [0001] = {0001, 0010, 0100, 1000}
2. [0011] = {0011, 0110, 1100, 1001}
3. [0111] = {0111, 1110, 1101, 1011}

可以看到等号右边的集合都是左边的循环，我们只取其中最小的串作为主串（prime word）。

## m=3

当m=3时，情况变得更加复杂。我们可以构造出更多的组合。实际会有18个不同的prime word，这时候就不容易“看出”了，我们按字典序将它们排序列出：{0001, 0002, 0011, 0012, 0021, 0022, 0102, 0111, 0112, 0121, 0122, 0211, 0212, 0221, 0222, 1112, 1122, 1222}。

生成这个序列并不复杂，借助ChatGPT能够很容易完成：

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

简单分析下时间复杂度，候选集alphabet_str长度的n次方，即`len(alphabet_str)^n`，看起来还可以接受是吧。但当我们将问题变成文章开头提到的D时，复杂度就完全不一样了，我将在下篇文章中给出一般解法。
