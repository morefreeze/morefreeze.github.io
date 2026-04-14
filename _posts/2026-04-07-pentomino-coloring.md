---
title: "五格骨牌的三染色问题：2339 种铺法里有多少种能上色？"
categories: algorithm combinatorics
tags: [DLX, 算法, 组合数学, TAOCP, 精确覆盖, 图染色, 五格骨牌]
description: "TAOCP 习题 277：枚举 6×10 五格骨牌铺法，检验强三染色性——相邻骨牌连角都不能碰"
math: true
---

{% include JB/setup %}

## 引言

用 12 块五格骨牌平铺 6×10 矩形共有 2339 种方法——但如果我要求相邻骨牌颜色不同，连角都不能碰，还剩几种？

这是《The Art of Computer Programming》Volume 4B 中的习题 7.2.2.1-277，难度评级 [25]（TAOCP 的评级范围 0–50，数字越大越难）。答案是：**94 种**，仅占约 4%。

<!--more-->

## 问题定义

### 什么是"强"三染色？

普通图染色问题中，两个顶点相邻指的是它们之间有边相连。在五格骨牌的语境下，如果两块骨牌**共享一条边**，它们就是相邻的。

但"强"染色的要求更严格：**两块骨牌不能共享边，也不能共享角点**。用图论的语言来说，这是 8-连通邻接（Chebyshev 距离 ≤ 1，即两个点在 x、y 方向的距离都不超过 1），而不是 4-连通邻接。

<img src="/images/pentomino-adjacency.svg" alt="普通染色与强染色对比" style="width:100%; max-width:520px;"/>

### 目标

用红、白、蓝三种颜色给 12 块五格骨牌着色，使得任何两块相同颜色的骨牌既不共享边，也不共享角。

我们需要枚举所有 2339 种 6×10 的平铺方案，然后逐一检查哪些满足强三染色条件。

## 两阶段算法

### 阶段一：DLX 枚举所有铺法

这个阶段基于[前文](/2026/03/pentomino-tiling.html)实现的 Dancing Links 求解器，封装一个枚举所有铺法的函数：

```python
def get_all_packings(width: int = 6, height: int = 10):
    """枚举所有五格骨牌平铺方案"""
    dlx = DancingLinks(width * height + len(PENTOMINOES))
    # ... 构建精确覆盖矩阵 ...
    packings = []
    for solution in dlx.search():
        packing = {}
        for node in solution:
            # 提取骨牌位置信息
            name, x, y, orientation = row_info[node]
            packing[name] = set_of_cells
        packings.append(packing)
    return packings
```

这个函数会返回所有 9356 种平铺方案（包含板对称性），去重后是 2339 种。

### 阶段二：构建邻接图

对于每一种平铺方案，我们需要构建一个邻接图，图中的顶点代表 12 块骨牌，边代表两块骨牌在 Chebyshev 距离 ≤ 1 的范围内。

```python
def build_adjacency(packing):
    """构建强邻接图：两块骨牌相邻当且仅当它们的任意方格的 Chebyshev 距离 ≤ 1"""
    names = list(packing.keys())
    adjacency = {name: set() for name in names}

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            adjacent = False
            for ax, ay in packing[a]:
                for bx, by in packing[b]:
                    if abs(ax - bx) <= 1 and abs(ay - by) <= 1:
                        adjacent = True
                        break
                if adjacent:
                    break
            if adjacent:
                adjacency[a].add(b)
                adjacency[b].add(a)
    return adjacency
```

这个邻接图是一个**无向图**，最多有 $$\binom{12}{2} = 66$$ 条边（完全图的上界）。实际上由于骨牌形状和空间的限制，边数通常少于这个上界。

### 阶段三：回溯检验三染色性

有了邻接图，我们需要检验它是否可以 3-染色。这又是另一个经典的 NP 完全问题，但由于图很小（只有 12 个顶点），简单的回溯就足够了：

```python
def is_three_colorable(adjacency):
    """通过回溯检验邻接图是否可以 3-染色"""
    names = list(adjacency.keys())
    n = len(names)
    coloring = {}

    def backtrack(idx):
        if idx == n:
            return True
        name = names[idx]
        # 找出所有已染色的邻居的颜色
        used = {coloring[nb] for nb in adjacency[name] if nb in coloring}
        # 尝试三种颜色
        for color in range(3):
            if color not in used:
                coloring[name] = color
                if backtrack(idx + 1):
                    return True
                del coloring[name]
        return False

    if backtrack(0):
        return True, coloring
    return False, None
```

这里的优化在于：我们只考虑已染色邻居的颜色，这样可以尽早剪枝。

## 结果与分析

### 统计结果

运行完整程序后，我们得到：

```
Total packings (with sym):  9356
3-colorable (with sym):     376
Non-3-colorable (with sym): 8980

Distinct packings:          2339
Distinct 3-colorable:       94
Distinct non-3-colorable:   2245
```

只有 **94/2339 ≈ 4.0%** 的平铺方案满足强三染色条件。这个比例之低说明了"强"条件的苛刻性。

### 示例染色

下面是一个满足强三染色条件的平铺方案：

<img src="/images/pentomino-3coloring.svg" alt="强三染色示例" style="width:100%; max-width:480px;"/>

你可以验证：任意两块相同颜色的骨牌既不共享边，也不共享角。

### 为什么这么少？

让我们分析一下为什么强三染色条件如此苛刻：

1. **邻接图密度更高**：在强染色条件下，邻接图的边数大大增加。原本不共享边的两块骨牌可能因为共享角点而变为相邻。

2. **空间约束**：12 块骨牌挤在 60 个格子里，平均每块骨牌有 5 个格子。在 Chebyshev 距离 ≤ 1 的定义下，每块骨牌的"影响范围"更大，更容易与其他骨牌冲突。

3. **颜色的均匀性**：三种颜色要分配给 12 块骨牌，理想情况下每种颜色 4 块。但由于邻接图的稠密性，很难找到这样的完美分配。

## 算法复杂度分析

### 时间复杂度

- **阶段一**：DLX 枚举所有平铺方案。6×10 的情况有 9356 种方案（含对称性），DLX 的实际运行时间在秒级。

- **阶段二**：对于每种方案构建邻接图，需要检查 $$\binom{12}{2} \times 5^2 = 1650$$ 次方格对（上界为 $$12^2 \times 25 = 3600$$）。

- **阶段三**：回溯检验三染色性。最坏情况下是 $$O(3^{12})$$，但由于邻接约束和剪枝，实际运行时间非常快。

总体的实际运行时间在几分钟级别，主要时间花在 DLX 枚举上。

### 空间复杂度

- 存储 9356 种平铺方案，每种方案包含 12 块骨牌的位置信息。
- 邻接图和染色方案的临时存储。

空间需求在百 MB 级别，现代计算机完全可以处理。

## 扩展思考

### 更一般的染色问题

我们可以把这个问题推广：

- **k-染色**：用 k 种颜色给骨牌着色。直觉上，k 越大可行性越高；当 k = 2 时，几乎不可行。

- **不同板形**：5×12、4×15、3×20 等其他矩形板的三染色性如何？

- **不同骨牌集**：如果不用全部 12 种骨牌，或者允许重复使用某些骨牌，情况会如何？

### 与其他问题的联系

这个问题与以下几个领域有深刻联系：

1. **图染色理论**：经典的 NP 完全问题，但在小规模实例上可以通过回溯解决。

2. **精确覆盖问题**：DLX 算法的应用之一，展现了算法设计的优雅性。

3. **组合设计**：如何在有限空间中安排形状，满足特定的约束条件。

## 总结

通过这个问题，我们看到了：

- **DLX 的威力**：不仅解决单个实例，还能枚举所有解，为后续分析提供基础。

- **回溯的适用场景**：对于小规模的 NP 完全问题，回溯配合剪枝完全实用。

- **约束的影响**：从"边相邻"到"边或角相邻"，看似微小的变化，却使得可行解从"几乎所有"变成"极少数"。

完整的代码实现可以在 [GitHub](https://github.com/morefreeze/morefreeze.github.io/blob/master/code/pentomino_coloring.py) 上找到。如果你对 DLX 算法感兴趣，可以参考[前文](/2026/03/pentomino-tiling.html)了解更多细节。

## 参考资料

- Donald Knuth, *The Art of Computer Programming*, Volume 4B, Section 7.2.2.1
- Dancing Links 算法原始论文：[Dancing Links](https://arxiv.org/abs/cs/0011047)
- 五格骨牌平铺问题的 Wikipedia：[Pentomino](https://en.wikipedia.org/wiki/Pentomino)
