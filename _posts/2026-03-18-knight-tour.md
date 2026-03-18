---
layout: post
title: "骑士巡游：把哈密顿回路塞进精准匹配"
description: ""
category: algorithm
comments: true
tags: [knuth, exact-cover, dancing-links, hamilton, TAOCP]
---

{% include JB/setup %}

## 引言

2025 年 12 月，87 岁的 Knuth 在斯坦福做了他的第 29 届圣诞讲座，主题是**骑士巡游（Knight's Tours）**。台下的人估计没想到，这老爷子 1973 年就开始研究这个问题，找了五十多年才把当年的笔记翻出来，在 2025 年做出了新的突破——把 8×8 棋盘上所有满足 180° 旋转对称的封闭巡游数清楚了：**2,432,932 个**，占全部封闭巡游的不到 0.1%。这个数字是怎么来的，后面慢慢说。

这篇文章是 TAOCP 系列的续集。我们已经聊过[精准匹配][exact-cover]、[Dancing Link][dancing-link] 和[回溯算法][backtrack]，骑士巡游是把这些东西串起来的绝佳例子——它是一个**哈密顿路径问题**，但 Knuth 有个漂亮的技巧把它变成精准匹配。

<!--more-->

## 骑士巡游是什么

国际象棋里的马（骑士）走"日"字。骑士巡游的问题是：**能否让马从棋盘某个格子出发，不重复地走遍所有格子？**

- **开放巡游（Open Tour）**：起点和终点不同
- **封闭巡游（Closed Tour / Circuit）**：终点可以直接跳回起点，形成回路

用图论的语言说，把棋盘每个格子当成节点，两个格子之间有边当且仅当马能一步到达，这张图叫**骑士图（Knight's Graph）**。骑士巡游就是骑士图上的哈密顿路径（封闭巡游就是哈密顿回路）。

8×8 棋盘上，封闭巡游的数量大约是 260 亿条。即使在小一点的 6×6 棋盘上，独立封闭巡游（消除对称后）也有几万条。

## 直觉编码行不通

第一反应很自然：把"每个格子恰好被访问一次"写成精准匹配。

用 $$n^2$$ 个 item 代表每个格子，然后……然后就卡住了。因为"访问"是有顺序的，必须保证访问序列是连通的，第 $$k$$ 步必须和第 $$k-1$$ 步之间有一条马步。这个"相邻"约束没法直接写成精准匹配的 01 矩阵。

## 换个视角：从格子到移动

Knuth 的转化思路是**换了观察对象**。

与其追踪"哪些格子被访问了"，不如追踪"选了哪些移动"。对一个封闭巡游（回路），每个格子恰好：

- **出发一次**（out）
- **到达一次**（in）

所以定义：

- **Items**：$$out[cell]$$ 和 $$in[cell]$$，共 $$2n^2$$ 个，每个必须恰好被覆盖一次
- **Options**：棋盘上每一步合法的马步移动 $$(r_1, c_1) \to (r_2, c_2)$$，覆盖 $$out[r_1 \cdot n + c_1]$$ 和 $$in[r_2 \cdot n + c_2]$$

选出一组马步，让所有格子各有一进一出，就是精准匹配。代码实现非常干净：

{% highlight python linenos %}
def build_closed_tour(n):
    num_cells = n * n
    num_items = 2 * num_cells   # out[0..n²-1] 然后 in[0..n²-1]
    options, labels = [], []

    for r1 in range(n):
        for c1 in range(n):
            src = r1 * n + c1
            for (r2, c2) in knight_moves(r1, c1, n):
                dst = r2 * n + c2
                # out[src] 的下标是 src，in[dst] 的下标是 num_cells + dst
                options.append([src, num_cells + dst])
                labels.append(((r1, c1), (r2, c2)))

    return num_items, options, labels
{% endhighlight %}

以 6×6 棋盘为例，这会生成 72 个 items 和 160 个 options（即 160 条合法马步）。

## 一个重要的陷阱

上面的编码正确吗？几乎。

精准匹配保证了每个格子恰好有一个出边和一个入边，也就是说选出的马步形成了一个**置换**——一组不相交的有向环，合起来覆盖所有格子。但这不一定是**一个**哈密顿回路，也可能是若干条短环的组合。

例如在 6×6 棋盘上，DLX 找到的合法精准匹配里，绝大多数（约 99.98%）是多环解，只有少数是真正的哈密顿回路。所以必须在重建路径时做一次检查：

{% highlight python linenos %}
def reconstruct_circuit(solution, labels, n):
    nxt = {labels[i][0]: labels[i][1] for i in solution}
    # 从 (0,0) 出发，看能走多少步
    cur, steps = (0, 0), 0
    while True:
        cur = nxt[cur]
        steps += 1
        if cur == (0, 0):
            break
    # 如果 steps != n²，说明是多环解，丢弃
    if steps != n * n:
        return None
    # 重建有序路径
    path, cur = [], (0, 0)
    for _ in range(n * n):
        path.append(cur)
        cur = nxt[cur]
    return path
{% endhighlight %}

这个检查同时也揭示了一个有趣的问题：精准匹配本身**不能排除多环解**。要找哈密顿回路，要么在编码里加额外约束（Knuth 在 Pre-Fascicle 8a 里有更精妙的方案），要么像这里一样事后过滤。

## 开放巡游：加一个虚拟节点

封闭巡游编码清晰，开放路径怎么办？

技巧是加一个**虚拟节点** $$v$$，它和棋盘上所有真实格子双向相连。于是开放路径 $$s \to \cdots \to e$$ 就变成了封闭回路 $$v \to s \to \cdots \to e \to v$$，直接复用封闭巡游的编码框架。

{% highlight python linenos %}
def build_open_tour(n):
    v = n * n              # 虚拟节点编号
    total = n * n + 1      # 真实格子 + 虚拟节点
    num_items = 2 * total
    options, labels = [], []

    # 真实马步（item 下标在扩展空间里）
    for r1 in range(n):
        for c1 in range(n):
            src = r1 * n + c1
            for (r2, c2) in knight_moves(r1, c1, n):
                dst = r2 * n + c2
                options.append([src, total + dst])
                labels.append(((r1, c1), (r2, c2)))

    # 虚拟边：v → cell（选择起点）
    for r2 in range(n):
        for c2 in range(n):
            dst = r2 * n + c2
            options.append([v, total + dst])
            labels.append(('v', (r2, c2)))

    # 虚拟边：cell → v（选择终点）
    for r1 in range(n):
        for c1 in range(n):
            src = r1 * n + c1
            options.append([src, total + v])
            labels.append(((r1, c1), 'v'))

    return num_items, options, labels
{% endhighlight %}

5×5 棋盘的开放巡游，items 变成 52 个（$$2 \times 26$$），options 是 146 个（100 条真实马步 + 25 条虚拟出边 + 25 条虚拟入边）。

跑出来的一个解长这样：

```
 5 20  9 14  7
10 15  6 19 24
21  4 23  8 13
16 11  2 25 18
 3 22 17 12  1
```

从格子 (4,4) 出发，到格子 (3,3) 结束，走遍全部 25 个格子，每一步都是合法马步。

## 深入：对称性分析

回到 Knuth 的 2,432,932 这个数字。

棋盘有 8 种对称操作，构成**二面体群 $$D_4$$**：

| 编号 | 操作 | 变换 $$(r, c) \to$$ |
|:---:|:---|:---|
| 0 | 恒等 | $$(r, c)$$ |
| 1 | 旋转 90° | $$(c, n{-}1{-}r)$$ |
| 2 | 旋转 180° | $$(n{-}1{-}r,\ n{-}1{-}c)$$ |
| 3 | 旋转 270° | $$(n{-}1{-}c,\ r)$$ |
| 4 | 水平翻转 | $$(r,\ n{-}1{-}c)$$ |
| 5 | 垂直翻转 | $$(n{-}1{-}r,\ c)$$ |
| 6 | 对角线翻转 | $$(c, r)$$ |
| 7 | 反对角线翻转 | $$(n{-}1{-}c,\ n{-}1{-}r)$$ |

**两个封闭巡游算同一个**，当且仅当一个可以通过对称变换 + 改变起点 + 翻转方向变成另一个。要判断某条巡游在 180° 旋转下不变：

{% highlight python linenos %}
def has_sym(path, sym, n):
    transformed = apply_symmetry(path, sym, n)
    m = len(path)
    # 建立原路径所有循环旋转（含反向）的集合
    rotations = set()
    for i in range(m):
        rotations.add(tuple(path[i:] + path[:i]))
    rev = list(reversed(path))
    for i in range(m):
        rotations.add(tuple(rev[i:] + rev[:i]))
    # 检查变换后的路径是否是某个旋转
    for i in range(m):
        if tuple(transformed[i:] + transformed[:i]) in rotations:
            return True
    return False
{% endhighlight %}

在 6×6 棋盘上随机抽取 329 条不同的封闭巡游，检查它们在 8 种对称下的不变性：

```
sym 0 identity           : 329  ← 恒等，全部成立（sanity check）
sym 1 rot90              :   0
sym 2 rot180             :   1  ← 只有 1 条是 180° 对称的
sym 3 rot270             :   0
sym 4 flip_horizontal    :   0
sym 5 flip_vertical      :   0
sym 6 flip_diagonal      :   0
sym 7 flip_antidiagonal  :   0
```

**180° 对称极为罕见。** 这也是为什么这个数字值得专门统计——它是对称性在组合爆炸里留下的一小片有序的痕迹。

Knuth 在讲座里还展示了一条"最少钝角"的骑士巡游——路径方向转折角度的钝角数量最小化，在对称意义下唯一，视觉上极为漂亮。还有一条 18×18 棋盘的巡游，旋转 90° 后和自身完全一样。这些都不只是数学，而是几何上的美。

## 小结

这篇文章展示了把哈密顿回路塞进精准匹配的核心技巧：

1. **从格子到移动**：in/out 两类 item + 每条马步一个 option，编码极简
2. **多环陷阱**：精准匹配不保证单一回路，要额外检查
3. **虚拟节点**：一行改动，开放路径复用封闭巡游框架
4. **对称性**：$$D_4$$ 的 8 种操作，180° 不变的巡游极为稀少

完整代码（含 DLX 实现、对称分析、验证）在[这里][code]。

Knuth 的 Pre-Fascicle 8a 正在写哈密顿路径与回路，还没有正式出版。下一篇我们顺着这条线继续。

[exact-cover]: /2024/07/exact-cover.html
[dancing-link]: /2024/07/dancing-link.html
[backtrack]: /2024/08/backtrack.html
[code]: https://github.com/morefreeze/morefreeze.github.io/blob/master/code/knight_tour.py
