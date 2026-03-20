---
layout: post
title: "舞蹈链进阶：次要项与颜色项"
description: ""
category: algorithm
comments: true
tags: [knuth, exact-cover, dancing-links, sudoku, TAOCP]
---

{% include JB/setup %}

## 引言

[精准匹配][exact-cover]和 [Dancing Link][dancing-link] 里我们用的都是**标准精准匹配**：每一项（item）必须被恰好覆盖一次。这个约束很整洁，但现实问题经常不那么整齐。

智慧珠那类问题天然吻合——每块形状用且仅用一次，每个坐标被填满恰好一次。但换一个问题就卡住了：N 皇后要求每一行、每一列恰好放一个皇后——这还是精准匹配；但对角线上**最多**一个皇后，而不是"恰好一个"。棋盘边缘有很多对角线根本不需要被占据。

标准 DLX 对"最多一次"没有干净的表达方式，只能靠手工预处理凑合——远不够优雅。

Knuth 在 TAOCP 4B 里给出了解决方案：**次要项（secondary items）**和**颜色（colors）**。这两个扩展一起构成了 **Algorithm C**，把精准匹配的适用范围大幅拓宽。

<!--more-->

## 标准精准匹配的局限

回顾一下标准精准匹配的语义：给定一组项和一组选项，每个选项覆盖若干项，要求选出若干选项，使每一项**恰好被覆盖一次**。

"恰好一次"分解为两个约束：
- **至少一次**：每项必须被覆盖
- **至多一次**：每项最多被覆盖一次

很多问题只需要其中一个方向的约束：

| 场景 | 约束 |
|:---|:---|
| N 皇后：对角线 | 至多一次（可以没有皇后占据）|
| 数独：某格已给定数字 | 某格的值必须是指定数字 |
| 填字游戏：横竖单词共享格子 | 横竖两个方向填入的字母必须相同 |

这三种场景都无法直接用标准精准匹配表达。

## 次要项：把"恰好"改成"至多"

**定义**：次要项不强制被覆盖，但如果被某个选项覆盖，就**至多覆盖一次**。

在矩阵表示里，把项分成两类：
- **主要项（primary items）**：必须恰好覆盖一次，排在前面
- **次要项（secondary items）**：至多覆盖一次，排在后面，用 `|` 分隔

Algorithm X 的终止条件从"所有项都被覆盖"改成"所有**主要项**都被覆盖"。

### N 皇后：对角线是次要项

在 $$n \times n$$ 的棋盘上放 $$n$$ 个皇后，互不攻击。

经典编码：
- **主要项**：$$n$$ 行（`r0`..`rn-1`）和 $$n$$ 列（`c0`..`cn-1`），各恰好一个皇后
- **次要项**：$$(2n-1)$$ 条正对角线（`d0`..`d2n-2`）和 $$(2n-1)$$ 条反对角线（`a0`..`a2n-2`），每条至多一个皇后
- **每个选项**：在格子 $$(r, c)$$ 放皇后，覆盖 `rr`、`cc`、`d(r+c)`、`a(r-c+n-1)`

以 4 皇后为例，矩阵片段（省略大量列）：

```
选项           r0 r1 r2 r3 | c0 c1 c2 c3 | d0 d1 d2 d3 d4 d5 d6 | a0 a1 ...
(0,1) 皇后      1  .  .  .    .  1  .  .    .  1  .  .  .  .  .    .  .  ...
(1,3) 皇后      .  1  .  .    .  .  .  1    .  .  .  .  1  .  .    .  1  ...
```

对角线列（次要项部分）在选中选项后会被"锁定"，但搜索结束条件只检查行列（主要项）是否全部覆盖。

DLX 实现层面，次要项的"覆盖"操作和主要项完全相同——一旦某选项覆盖了它，它就被移出链表，其他包含它的选项也被删去。区别只在于：**找解时不要求次要项一定被覆盖过**。

```python
def solve_nqueens(n):
    """
    主要项：行 0..n-1，列 n..2n-1
    次要项：正对角线 2n..4n-2，反对角线 4n-1..6n-3
    """
    num_primary = 2 * n
    num_secondary = 2 * (2 * n - 1)
    num_items = num_primary + num_secondary

    options = []
    for r in range(n):
        for c in range(n):
            diag  = 2 * n + (r + c)          # 正对角线，共 2n-1 条
            adiag = 2 * n + (2*n-1) + (r - c + n - 1)  # 反对角线
            options.append([r, n + c, diag, adiag])

    dlx = DLX(num_items, options, num_primary=num_primary)
    return list(dlx.solve())
```

8 皇后有 92 个解，这个编码跑出来和经典结果一致。

## 颜色项：把"至多一次"改成"同色可多次"

次要项解决了"可以不覆盖"的问题，但还不够。

考虑填字游戏：横向单词和纵向单词在某个格子相交，两个单词必须在这个格子填入**相同的字母**。这个格子会被两个选项（横向某单词、纵向某单词）同时覆盖，但只要字母一样就合法——这是"同色可多次"的语义。

**定义**：颜色项是次要项的加强版。每个选项覆盖某个颜色项时，可以指定一个**颜色值**。规则是：

> 同一个颜色项可以被多个选项覆盖，当且仅当所有覆盖它的选项指定了**相同的颜色**。

颜色可以是任意标签——数独里是数字，填字游戏里是字母，图着色里是颜色名称。

### 净化操作（Purify）

标准 DLX 对主要项做"覆盖"（cover）：移除该列，删掉所有包含该列的行。

颜色项对应的操作叫**净化（purify）**：

1. 找到被选中的颜色项 $$i$$，其颜色为 $$c$$
2. 在 $$i$$ 的列中，**删掉所有颜色不是 $$c$$ 的行**（它们和当前选择冲突）
3. **保留颜色是 $$c$$ 的行**（它们和当前选择相容）
4. $$i$$ 本身**不从链表头移除**（因为后续还可能有同色覆盖）

回溯时做**反净化（unpurify）**：把被删掉的不同色行恢复回来。

用伪代码表示：

```
purify(i, color):
    x ← i.D
    while x ≠ i:
        if color(x) ≠ color:
            hide(x)   # 删掉这一行（同 cover 里的行删除）
        x ← x.D

unpurify(i, color):  # 逆序
    x ← i.U
    while x ≠ i:
        if color(x) ≠ color:
            unhide(x)
        x ← x.U
```

与 cover 的核心区别：
- cover：移除列头 + 删除所有行
- purify：**不移除列头** + 只删除异色行

### 数独：格子是颜色项

数独是颜色项最经典的应用。

**主要项**（必须恰好满足一次）：
- `row-r-d`：第 $$r$$ 行有数字 $$d$$（$$9 \times 9 = 81$$ 个）
- `col-c-d`：第 $$c$$ 列有数字 $$d$$（81 个）
- `box-b-d`：第 $$b$$ 个 3×3 宫有数字 $$d$$（81 个）

**次要颜色项**（可被多个选项覆盖，但颜色必须一致）：
- `cell-(r,c)`：第 $$r$$ 行第 $$c$$ 列的格子，颜色 = 填入的数字

**选项**：在格子 $$(r, c)$$ 填数字 $$d$$，覆盖：
- 主要项：`row-r-d`、`col-c-d`、`box-b-d`
- 颜色项：`cell-(r,c)` 染色为 $$d$$

颜色项的精妙之处在于处理**已给定数字的格子**：

如果格子 $$(r, c)$$ 已经是数字 5，那么在建模时，所有覆盖 `cell-(r,c)` 但颜色不是 5 的选项，会在净化操作里被删掉。已知格子自然地排除了冲突，不需要任何预处理。

对比传统做法：标准精准匹配处理已知格子，需要手动预先选定对应选项，然后把冲突行手动删掉，再开始搜索。颜色项让这一切自动化了。

## Algorithm C 实现

`DLX_C` 在标准 DLX 的四向链表基础上（完整实现见 [knight_tour.py][code_dlx]）扩展了两点：`_Node` 增加了 `.color` 字段，搜索循环里对次要项的处理分支用 purify/unpurify 替换了 cover/uncover。其余结构——链表头、cover/uncover 本身、min-S 启发式——完全相同。

与标准 DLX 的差异集中在三点：

1. 链表头把主要项和次要项分开记录
2. "选取下一项"只在主要项里找
3. 处理次要项时用 purify/unpurify 代替 cover/uncover

{% highlight python linenos %}
class DLX_C:
    """Algorithm C: Exact cover with secondary items and colors."""

    def __init__(self, num_primary: int, num_items: int, options):
        """
        num_primary: 前 num_primary 个项是主要项（必须覆盖）
        num_items:   总项数（主要项 + 次要项）
        options:     每个选项是 [(item_index, color), ...] 的列表
                     主要项的 color 忽略（用 None 即可）
                     次要项的 color 为 None 表示"无颜色"（至多覆盖一次）
        """
        self.num_primary = num_primary
        self._build(num_items, options)

    def _build(self, num_items, options):
        root = _Node(); root.name = 'root'
        self._root = root

        cols = []
        prev = root
        for i in range(num_items):
            h = _Node(); h.name = i; h.S = 0; h.C = h
            h.L = prev; h.R = root
            prev.R = h; root.L = h
            prev = h
            cols.append(h)
        # 次要项的末尾不连回 root 的左侧（便于只遍历主要项）
        # 这里简化实现：通过 num_primary 在 _choose_column 里控制范围
        self._cols = cols

        for row_id, option in enumerate(options):
            first = prev_node = None
            for item, color in option:
                node = _Node()
                node.row_id = row_id
                node.color = color   # 新增：颜色
                col = cols[item]; node.C = col
                node.U = col.U; node.D = col
                col.U.D = node; col.U = node
                col.S += 1
                if first is None:
                    first = node; node.L = node; node.R = node
                else:
                    node.L = prev_node; node.R = first
                    prev_node.R = node; first.L = node
                prev_node = node

    def _choose_column(self):
        """只在主要项里选（前 num_primary 列）。"""
        best = None
        j = self._root.R
        while j is not self._root:
            if j.name >= self.num_primary:
                break   # 次要项开始了，停止
            if best is None or j.S < best.S:
                best = j
            j = j.R
        return best

    @staticmethod
    def _cover(col):
        col.R.L = col.L; col.L.R = col.R
        i = col.D
        while i is not col:
            j = i.R
            while j is not i:
                j.D.U = j.U; j.U.D = j.D; j.C.S -= 1
                j = j.R
            i = i.D

    @staticmethod
    def _uncover(col):
        i = col.U
        while i is not col:
            j = i.L
            while j is not i:
                j.C.S += 1; j.D.U = j; j.U.D = j
                j = j.L
            i = i.U
        col.R.L = col; col.L.R = col

    @staticmethod
    def _purify(node):
        """
        净化：对列中颜色不同的行，只隐藏它们的行兄弟（其他列的节点），
        但行节点本身保留在列链中，以便 _unpurify 时能找回。
        """
        col = node.C
        color = node.color
        i = col.D
        while i is not col:
            if i.color != color:
                j = i.R
                while j is not i:
                    j.D.U = j.U; j.U.D = j.D; j.C.S -= 1
                    j = j.R
            i = i.D

    @staticmethod
    def _unpurify(node):
        """反净化（逆序恢复）：恢复不同色行的行兄弟。"""
        col = node.C
        color = node.color
        i = col.U
        while i is not col:
            if i.color != color:
                j = i.L
                while j is not i:
                    j.C.S += 1; j.D.U = j; j.U.D = j
                    j = j.L
            i = i.U

    def solve(self):
        yield from self._search([])

    def _search(self, solution):
        col = self._choose_column()
        if col is None:
            yield list(solution)
            return
        if col.S == 0:
            return

        self._cover(col)
        r = col.D
        while r is not col:
            solution.append(r.row_id)
            # 处理这一行里其他的项
            j = r.R
            while j is not r:
                if j.C.name < self.num_primary:
                    self._cover(j.C)          # 主要项：正常覆盖
                else:
                    if j.color is not None:
                        self._purify(j)        # 颜色次要项：净化
                    else:
                        self._cover(j.C)       # 无色次要项：正常覆盖（至多一次）
                j = j.R
            yield from self._search(solution)
            # 回溯
            j = r.L
            while j is not r:
                if j.C.name < self.num_primary:
                    self._uncover(j.C)
                else:
                    if j.color is not None:
                        self._unpurify(j)
                    else:
                        self._uncover(j.C)
                j = j.L
            solution.pop()
            r = r.D
        self._uncover(col)
{% endhighlight %}

## 代码验证

### N 皇后（次要项）

{% highlight python linenos %}
def solve_nqueens(n):
    num_primary = 2 * n
    diag_base  = num_primary
    adiag_base = diag_base + (2 * n - 1)
    num_items  = adiag_base + (2 * n - 1)

    options = []
    for r in range(n):
        for c in range(n):
            options.append([
                (r,         None),  # 行：主要项
                (n + c,     None),  # 列：主要项
                (diag_base  + r + c,         None),  # 正对角线：次要项，无色
                (adiag_base + r - c + n - 1, None),  # 反对角线：次要项，无色
            ])

    dlx = DLX_C(num_primary, num_items, options)
    return list(dlx.solve())

solutions = solve_nqueens(8)
print(f"8 皇后解的个数：{len(solutions)}")  # → 92
{% endhighlight %}

### 数独（颜色项）

{% highlight python linenos %}
def solve_sudoku(grid):
    """
    grid: 9x9 列表，0 表示待填，1-9 表示已知
    返回填好的 9x9 列表，或 None
    """
    # 主要项：行-数、列-数、宫-数（各 81 个，共 243 个）
    ROW_D  = lambda r, d: r * 9 + (d - 1)
    COL_D  = lambda c, d: 81 + c * 9 + (d - 1)
    BOX_D  = lambda b, d: 162 + b * 9 + (d - 1)
    # 次要颜色项：格子（81 个，颜色 = 数字）
    CELL   = lambda r, c: 243 + r * 9 + c

    num_primary = 243
    num_items   = 243 + 81

    options = []
    option_labels = []  # (r, c, d)

    for r in range(9):
        for c in range(9):
            b = (r // 3) * 3 + (c // 3)
            digits = [grid[r][c]] if grid[r][c] != 0 else range(1, 10)
            for d in digits:
                options.append([
                    (ROW_D(r, d), None),  # 主要项
                    (COL_D(c, d), None),
                    (BOX_D(b, d), None),
                    (CELL(r, c),  d),     # 颜色次要项，颜色 = 数字
                ])
                option_labels.append((r, c, d))

    dlx = DLX_C(num_primary, num_items, options)
    for sol in dlx.solve():
        result = [row[:] for row in grid]
        for idx in sol:
            r, c, d = option_labels[idx]
            result[r][c] = d
        return result
    return None

# 一道标准数独
puzzle = [
    [5,3,0, 0,7,0, 0,0,0],
    [6,0,0, 1,9,5, 0,0,0],
    [0,9,8, 0,0,0, 0,6,0],

    [8,0,0, 0,6,0, 0,0,3],
    [4,0,0, 8,0,3, 0,0,1],
    [7,0,0, 0,2,0, 0,0,6],

    [0,6,0, 0,0,0, 2,8,0],
    [0,0,0, 4,1,9, 0,0,5],
    [0,0,0, 0,8,0, 0,7,9],
]

answer = solve_sudoku(puzzle)
for row in answer:
    print(row)
{% endhighlight %}

运行结果：

```
[5, 3, 4, 6, 7, 8, 9, 1, 2]
[6, 7, 2, 1, 9, 5, 3, 4, 8]
[1, 9, 8, 3, 4, 2, 5, 6, 7]
[8, 5, 9, 7, 6, 1, 4, 2, 3]
[4, 2, 6, 8, 5, 3, 7, 9, 1]
[7, 1, 3, 9, 2, 4, 8, 5, 6]
[9, 6, 1, 5, 3, 7, 2, 8, 4]
[2, 8, 7, 4, 1, 9, 6, 3, 5]
[3, 4, 5, 2, 8, 6, 1, 7, 9]
```

## 三种约束的对比

| 类型 | 覆盖次数 | DLX 操作 | 典型场景 |
|:---|:---|:---|:---|
| 主要项 | 恰好一次 | cover / uncover | 棋盘格子、数独行列宫 |
| 无色次要项 | 至多一次 | cover / uncover（不要求被覆盖）| N 皇后对角线 |
| 颜色次要项 | 任意次，颜色相同 | purify / unpurify | 数独格子、填字交叉格 |

Algorithm C = Algorithm X + 次要项 + 颜色净化。

三者共用同一套链表结构，差别只在于：主要项决定搜索是否终止，次要项和颜色项决定冲突如何检测。

## 小结

1. **次要项**：把"恰好一次"放宽为"至多一次"，让 N 皇后、图着色等约束松弛问题能直接建模
2. **颜色项**：允许同一个次要项被多次覆盖，只要所有覆盖颜色一致，让共享约束（数独格子、填字交叉）自然表达
3. **净化操作**：和覆盖操作对称，但不移除列头——是实现颜色约束的核心机制

骑士巡游那篇提到，精准匹配无法排除多环解。这其实也是一个"缺少额外约束"的问题。Knuth Pre-Fascicle 8a 里用带颜色的次要项来追踪路径的连通性，从而在精准匹配层面直接排除多环——有空我们再细看那个方案。

完整代码在 [Github][code]。

[exact-cover]: /2024/07/exact-cover.html
[dancing-link]: /2024/07/dancing-link.html
[backtrack]: /2024/08/backtrack.html
[knight-tour]: /2026/03/knight-tour.html
[code]: https://github.com/morefreeze/morefreeze.github.io/blob/master/code/dlx_colors.py
[code_dlx]: https://github.com/morefreeze/morefreeze.github.io/blob/master/code/knight_tour.py
