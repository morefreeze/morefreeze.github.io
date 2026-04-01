---
title: "用 Dancing Links 解决五格骨牌平铺问题"
categories: algorithm combinatorics
tags: [DLX, 算法, 组合数学, TAOCP, 精确覆盖]
description: "探索 TAOCP 中五格骨牌平铺问题，学习如何用 Dancing Links 算法将平铺问题转化为精确覆盖问题"
math: true
---

## 引言

Donald Knuth 在《The Art of Computer Programming》Volume 4B 中提出了 Dancing Links (DLX) 算法——一种优雅地解决精确覆盖问题的回溯算法。本文将探讨习题 7.2.2.1-31 中提到的经典应用：**五格骨牌平铺问题**。

### 什么是五格骨牌？

五格骨牌（Pentominoes）是由 5 个单位正方形连接而成的多格骨牌。不考虑旋转和翻转，共有 **12 种** 不同的五格骨牌，通常用字母 F, I, L, P, N, T, U, V, W, X, Y, Z 来命名：

<img src="/images/pentominoes.svg" alt="12种五格骨牌形状" style="width:100%; max-width:840px;"/>

### 问题定义

**经典问题**：用全部 12 种五格骨牌各一片，能否精确平铺一个 6×10 的矩形区域？

这个问题可以推广到：
- 5×12 矩形
- 4×15 矩形
- 3×20 矩形

## 转化为精确覆盖问题

Dancing Links 算法解决的是**精确覆盖问题**：

> 给定一个 0-1 矩阵，选择若干行，使得每一列恰好有一个 1。

### 构建矩阵

对于五格骨牌平铺问题，我们构造如下矩阵：

**列的构造**：
- 每个网格位置（6×10 = 60 列）
- 每种五格骨牌（12 列）
- 总共 72 列

**行的构造**：
- 对于每种五格骨牌
- 考虑其在矩形内的所有合法位置和方向
- 每行对应一个"放置选项"
- 该行的 1 标记被占用的网格和使用的骨牌类型

### 举例说明

假设我们要放置 **L 型五格骨牌**在位置 (0,0)：

<img src="/images/pentomino-L-example.svg" alt="L型五格骨牌放置示例" style="width:100%; max-width:300px;"/>

行表示：`[L型, (0,0), (1,0), (2,0), (3,0), (3,1)]`，对应 6 个 1。

## Dancing Links 算法

DLX 的核心思想是用**双向十字链表**表示稀疏矩阵，实现高效的回溯：

### 数据结构

```
ColumnHeader ←→ ColumnHeader ←→ ColumnHeader ←→ ...
       ↓                ↓               ↓
    DataNode ↔ DataNode ↔ DataNode
       ↓
    DataNode
```

### 算法流程

```
Algorithm X(cover):
    if matrix empty:
        solution found!
    choose column c (fewest options)
    cover column c
    for each row r in column c:
        add r to solution
        for each column j in row r:
            cover column j
        X(cover)
        remove r from solution
        for each column j in row r:
            uncover column j
    uncover column c
```

### 优化：选择最少选项的列

这是 DLX 的关键优化——**总是选择约束最紧的列**，这样能最大限度地剪枝。

## 核心实现

DLX 的核心在于 `cover`（覆盖）和 `uncover`（撤销）操作，它们利用双向链表实现高效的回溯：

```python
def cover(self, col):
    """覆盖列 col：从矩阵中移除该列及所有相关行"""
    # 1. 从列链表中移除该列
    self.R[self.L[col]] = self.R[col]
    self.L[self.R[col]] = self.L[col]

    # 2. 移除所有与该列相交的行
    i = self.D[col]
    while i != col:
        j = self.R[i]
        while j != i:
            self.D[self.U[j]] = self.D[j]  # 跳过节点 j
            self.U[self.D[j]] = self.U[j]
            self.S[self.C[j]] -= 1  # 减少列计数
            j = self.R[j]
        i = self.D[i]

def uncover(self, col):
    """撤销覆盖：精确逆向执行 cover 操作"""
    # 1. 恢复所有被移除的行（逆序）
    i = self.U[col]
    while i != col:
        j = self.L[i]
        while j != i:
            self.S[self.C[j]] += 1  # 恢复列计数
            self.D[self.U[j]] = j
            self.U[self.D[j]] = j
            j = self.L[j]
        i = self.U[i]

    # 2. 恢复列到列链表
    self.R[self.L[col]] = col
    self.L[self.R[col]] = col
```

**关键点**：
- `cover` 操作必须是**可逆的**，以便回溯时能精确恢复状态
- 使用 `L` 和 `R` 指针在水平方向跳过节点
- 使用 `U` 和 `D` 指针在垂直方向跳过节点
- `S` 数组跟踪每列的节点数，用于 MRV 启发式

完整代码实现见：[GitHub - pentomino_dlx.py](https://github.com/morefreeze/morefreeze.github.io/blob/master/code/pentomino_dlx.py)

## 运行结果

<img src="/images/pentomino-6x10-solution.svg" alt="6x10五格骨牌平铺解" style="width:100%; max-width:480px;"/>

*用全部 12 种五格骨牌平铺 6×10 矩形的一种解*

## 复杂度分析

### 空间复杂度

- 对于 6×10 矩形，每列最多有 $$O(n)$$ 个节点
- 总节点数约为放置选项的数量
- 空间复杂度：$$O(\text{放置选项})$$

### 时间复杂度

- 最坏情况是指数级：$$O(2^n)$$
- 实际运行中，DLX 的剪枝效果显著
- 对于五格骨牌问题，通常在毫秒级找到解

## 扩展与思考

### 1. 其他多格骨牌

- **三格骨牌**：2 种（直线形、L形）
- **四格骨牌**：5 种
- **六格骨牌**：35 种——有趣的是，全部 35 种六格骨牌**无法**平铺任何矩形。棋盘着色可以证明：24 种"奇"骨牌覆盖 3 黑 3 白，11 种"偶"骨牌覆盖 4 黑 2 白（或 2 黑 4 白），总覆盖黑格数恒为偶数；而 10×21 等矩形有 105 格黑格（奇数），产生矛盾。但它们可以平铺带洞的区域（如 15×15 挖去中央 3×5）。完整代码见 [hexomino_dlx.py](https://github.com/morefreeze/morefreeze.github.io/blob/master/code/hexomino_dlx.py)。

### 2. 计数问题

根据文献记载，五格骨牌平铺 6×10 矩形共有 **9,356** 种不同的解（考虑旋转和翻转）。这个数字是组合数学中的经典结果，由多种不同方法验证得出。

### 3. 变体问题

- 有洞的矩形
- 非矩形区域
- 使用部分骨牌
- 重复使用某些骨牌

## 总结

五格骨牌平铺问题完美展示了 Dancing Links 算法的威力：

1. **建模优雅**：将几何问题转化为精确覆盖问题
2. **算法高效**：双向链表实现快速回溯
3. **扩展性强**：可轻松推广到其他约束满足问题

这正是 Knuth 大师的设计哲学：**找到问题的本质表示，然后用最恰当的数据结构来实现它**。

## 参考资料

- Knuth, D. E. (2022). *The Art of Computer Programming, Volume 4B: Combinatorial Algorithms, Part 2*. Addison-Wesley.
- [Dancing Links - Wikipedia](https://en.wikipedia.org/wiki/Dancing_Links)
- [Exact Cover - Wikipedia](https://en.wikipedia.org/wiki/Exact_cover)

---
