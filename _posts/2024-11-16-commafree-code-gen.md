---
layout: post
title: "再战commafree code——暴力挑选"
description: "介绍"
category: algorithm
comments: true
tags: [algorithm, knuth, code]
---

{% include JB/setup %}
## 引言
书接上文，上次我们生成了 m 等于 3， n 等于 4 时，所有可能的 commafree 码，接下来我们要做的就是从这 18 个码中挑选出一批特定的码，来组成一个 commafree 集合，使得这个集合里面任意的两个码相连后，除去前 n 个和末 n 个字母组成的词后，中间所有的长度为 n 的词都不出现在集合里。
因为选出的码自己可以和自己拼接，比如选出 0001，那么 00010001 中间所有的长度为 4 的词（即 0010，0100，1000）都不会出现在集合里，也就是说 0001 的所有移位都不可能再加进集合了，所以我们只需要对于每个主码，从它的 4 个移位中挑选一个出来加入集合。

<!--more-->

## 暴力搜索
我们能想到的最简单的方法就是暴力搜索，对于每个主码，从它的 4 个移位中挑选一个出来，然后检查是否满足条件，如果满足，则加入集合，最后输出最大的集合。
我们用伪码描述一下这个选择过程：

```python
def pick_code(codes):
    if len(codes) == 0:
        if len(result) > max_result:
            max_result = result
        return
    for each code in codes:
        for each shift in shifts:
            if is_commafree(code + shift):
                add shift to result
                pick_code(codes - {code})
```

通过暴力搜索，我们发现如果选得好，可以很快一路确定下去，比如第一步选0001，第二步选0011，接下来我们可以看到分别在第 3 步到 第 7 步只能选0002，0021，0111，0211和2111。

## 回溯
每一步的移位选择是一个很有技术的 trade off, 如果选得好，可以很快一路确定下去，如果选得不好，则需要很多步才能确定。
### 稀疏集合
我们引入一个数据结构来记录每一步做出的选择，一个链表有HEAD和TAIL指针，他们中间记录了一个集合，实际在链表中的位置并不是从小到大，同时还有一个反向数组记录元素对应指针的位置，如下图：
![alt text](/images/commafree-sparse_set.png)

它支持快速的添加和删除元素，以及遍历功能。下面简单描述下它的底层数据结构和操作：

#### 底层数据结构
分配两组内存中连续的空间，空间大小取决于集合最大个数和集合元素的范围，比如我们只需要存 0~M-1，
那只需要分配2个M长的内存空间就够了。我们用 `MEM[HEAD]` 表示集合开头，`MEM[TAIL]` 表示集合结束后的一个位置，
`MEM[IHEAD]` 表示0对应在集合的位置，以此类推 `MEM[IHEAD+M-1]` 是最后的M-1对应的位置。

#### 添加元素进集合
比如现在集合是391，添加进4，那么我们只要把4加到`TAIL`，并让`MEM[IHEAD+4]`指向TAIL，`TAIL+=1`就好，
整理成伪码分为3步：

```python
def add_set(mem, head, tail, ihead, x):
    if head <= mem[ihead+x] < tail:
        return
    mem[tail] = x
    mem[ihead+x] = tail
    tail += 1
```

完成的样子就是前面的图。

#### 删除元素
比如现在要删除集合中的9，那么我们要把9交换到`MEM[TAIL-1]`位置，更新`MEM[IHEAD]`，然后`TAIL-=1`就好，

```python
def del_set(mem, head, tail, ihead, x):
    if not (head <= mem[ihead+x] < tail):
        return
    if head == tail:
        return
    p = mem[ihead+x] # 记录即将被删元素的指针
    tail -= 1
    if p != tail:
        y = mem[tail]
        mem[tail], mem[p] = mem[p], y # 交换被删元素和末尾元素
        mem[ihead+x], mem[ihead+y] = tail, p # 交换被删元素和末尾元素反向指针
```

完成的样子如下：
![alt text](/images/commafree-del_sparse.png)

### 红蓝绿


## 参考

[a sparse-set representation][sparse]

[sparse]: <[a sparse-set representation](https://dl.acm.org/doi/10.1145/176454.176484)>
