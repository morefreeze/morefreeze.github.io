---
layout: post
title: "再战commafree code——暴力挑选&优化"
description: "介绍如何通过暴力搜索和回溯算法来构建无逗号码集合"
category: algorithm
comments: true
tags: [algorithm, knuth, code]
---

{% include JB/setup %}

## 引言

在[上一篇文章](/2024/10/commafree-code-first.html)中，我们生成了参数 m=3、n=4 时的所有可能 commafree code。本文将介绍如何从这18个码中挑选出一个最大的子集，使其满足 commafree code 的性质：当集合中任意两个码相连接时，不考虑首尾各n个字母后，中间所有长度为n的子串都不在这个集合中。

由于一个码可以和自身连接，比如选择0001后，序列00010001中的所有长度为4的中间子串(0010、0100、1000)都不能出现在最终集合中。这意味着如果我们选择了某个码，它的所有循环移位都不能再加入集合。因此，对每个主码，我们只需要从它的4个循环移位中选择一个加入集合。
<!--more-->

## 暴力搜索方法

最直接的方法是采用暴力搜索。对每个主码，我们尝试从它的4个循环移位中选择一个，然后验证是否满足 commafree code 的条件。如果满足，就将其加入结果集合。

以下是搜索过程的伪代码：

```python
def pick_code(codes):
    if len(codes) == 0:
        if len(result) > max_result:
            max_result = result
        return
        
    for code in codes:
        for shift in get_shifts(code):
            if is_commafree(result + [shift]):
                result.append(shift)
                pick_code(codes - {code})
                result.pop()
```

通过实践发现，如果选择策略得当，搜索过程可以快速收敛。例如，按以下顺序选择：
1. 第一步选择0001
2. 第二步选择0011
3. 接下来只能依次选择0002、0021、0111、0211和2111

## 优化搜索策略

### 稀疏集合数据结构

为了高效地记录和更新搜索过程中的选择，我们引入稀疏集合(Sparse Set)这个数据结构。它包含HEAD和TAIL指针，用于维护一个动态集合，同时使用反向数组记录元素在集合中的位置。
它支持快速的添加和删除元素，以及遍历功能。下面简单描述下它的底层数据结构和操作：

分配两组内存中连续的空间，空间大小取决于集合最大个数和集合元素的范围，比如我们只需要存 0~M-1，
那只需要分配2个M长的内存空间就够了。我们用 `MEM[HEAD]` 表示集合开头，`MEM[TAIL]` 表示
集合结束后的一个位置，
`MEM[IHEAD]` 表示0对应在集合的位置，以此类推 `MEM[IHEAD+M-1]` 是最后的M-1对应的位
置。
![稀疏集合示意图](/images/commafree-sparse_set.png)

#### 核心操作

1. **添加元素**

```python
def add_to_set(mem, head, tail, ihead, x):
    if head <= mem[ihead + x] < tail:
        return
    mem[tail] = x
    mem[ihead + x] = tail
    tail += 1
```

完成的样子就是前面的图。

#### 删除元素
比如现在要删除集合中的9，那么我们要把9交换到`MEM[TAIL-1]`位置，更新`MEM[IHEAD]`，然后`TAIL-=1`就好，

```python
def remove_from_set(mem, head, tail, ihead, x):
    if not (head <= mem[ihead + x] < tail):
        return
    if head == tail:
        return
    p = mem[ihead + x] # 记录即将被删元素的指针
    tail -= 1
    if p != tail:
        y = mem[tail]
        mem[tail], mem[p] = mem[p], y # 交换被删元素和末尾元素
        mem[ihead + x], mem[ihead + y] = tail, p # 交换被删元素和末尾元素反向指针
```

完成的样子如下：
![alt text](/images/commafree-del_sparse.png)

### 红蓝绿
当m=3时，只有18个主串需要考虑，搜索空间还不大（注意复杂度时指数级的，因为常数小所以我们说它不大），
但当m=4时事情就变得完全不一样了，因为有60个主串了，看起来时间不可接受了？接下来我们来看看如何只用少量内存空间来完成搜索的更新和回溯。

首先我们有一个函数alpha，它可以正确地将长度n的词转成十进制，比如 $$(alpha(0102))_3 = 11$$。
然后MEM的0~M-1记录了颜色:
- 红色代表不能选
- 绿色代表选择
- 蓝色代表待定

我们使用7个稀疏集合来维护状态：
- P1(x)、P2(x)、P3(x)：记录蓝色词的前缀匹配 $$x_1\star \star \star$$，$$x_1x_2 \star \star$$，$$x_1x_2x_3 \star$$；
- S1(x)、S2(x)、S3(x)：记录蓝色词的后缀匹配 $$\star \star \star x_4$$，$$\star 
\star x_3x_4$$，$$\star x_2x_3x_4$$；
- CL(x)：记录蓝色词的循环移位集合 $$\{(x_1x_2x_3x_4),(x_2x_3x_4x_1),(x_3x_4x_1x_2),(x_4x_1x_2x_3)\}$$；

每个集合有3个数组，除了上面介绍必备的链表和反向数组外，还有一个数组用来记录TAIL指针。

#### 举个栗子
这么讲有点抽象，还是来看个例子
![alt text](/images/commafree-ex.png)先有个印象，在下篇文章我会详细解释这张图。

## 小结

本文介绍了构建 commafree code 集合的基本思路和关键数据结构。在下一篇文章中，我们将详细讨论具体的搜索算法实现。

## 参考资料

- [A Sparse-Set Representation](https://dl.acm.org/doi/10.1145/176454.176484)
