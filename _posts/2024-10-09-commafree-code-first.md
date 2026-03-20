---
layout: post
title: "commafree code初次见面——生成"
description: ""
category: algorithm
comments: true
tags: [algorithm, knuth, code]
---

{% include JB/setup %}

## 引言

commafree code 是一种**自同步**定长编码，和 Huffman 编码那种变长压缩码完全不同。给定 m 个字母构成的长度为 n 的码字集合 D，若任意两个码字 $$x_1x_2x_3x_4$$ 与 $$x_5x_6x_7x_8$$ 相邻时，中间的偏移子串 $$x_2x_3x_4x_5$$、$$x_3x_4x_5x_6$$、$$x_4x_5x_6x_7$$ 均不在 D 中，则称 D 为 commafree code（又称自同步块码）。这一性质保证接收方无需分隔符即可正确分段解码。

以 n=4 为例："likethis"中 "like" 和 "this" 是码字，而中间的偏移串 "iket"、"keth"、"ethi" 均不是码字。另外，自身循环串（如 dodo、gaga）不能成为码字，因为两个相同码字相邻后中间的偏移子串就是自身。

<!--more-->

## m=2

为了便于表达和研究，我们不关心单词是否是真实的单词，只用0到m-1来表示单词。

首先来看上界：由于周期串（如 dodo）不能入选，非周期串共 $$m^4 - m^2$$ 个；又因为选入某个码字后，它的 4 个循环移位都必须排除，所以最多选 $$\frac{m^4 - m^2}{4}$$ 个码字。

当 m=2 时，上界 = $$\frac{16-4}{4} = 3$$，恰好有如下 3 个循环类：

1. [0001] = {0001, 0010, 0100, 1000}
2. [0011] = {0011, 0110, 1100, 1001}
3. [0111] = {0111, 1110, 1101, 1011}

可以看到等号右边的集合都是左边的循环，我们只取其中最小的串作为主串（prime word）。

m=2 有个特殊性质：直接取每个循环类中字典序最小的元素（即 0001、0011、0111），就已经构成合法的 commafree code，达到上界 3。但这个"取最小"的策略在 m≥3 时不再成立。

## m=3

当 m=3 时，上界 = $$\frac{81-9}{4} = 18$$，即有 18 个循环类（prime word）。按字典序排列：{0001, 0002, 0011, 0012, 0021, 0022, 0102, 0111, 0112, 0121, 0122, 0211, 0212, 0221, 0222, 1112, 1122, 1222}。

这时候能否真正选出 18 个码字（达到上界）？不能——比如选了 0001 和 0011 之后，就无法再选 1112 了（因为 0001 ∘ 1112 的内部包含 0011）。实际最大是多少，需要搜索来确定，这将是下篇文章的内容。

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

简单分析下时间复杂度，候选集alphabet_str长度的n次方，即`len(alphabet_str)^n`，看起来还可以接受是吧。但当我们将问题变成文章开头提到的从候选集D中选取一批词使它们满足commafree时，复杂度就完全不一样了，我将在下篇文章中给出一般解法。
