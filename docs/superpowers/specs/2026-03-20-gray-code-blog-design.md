# Blog Post Design: 从九连环到格雷码：最少步数的秘密

## Meta

- **Series**: TAOCP 组合算法系列
- **Position**: 接在 DLX/精确覆盖之后，开启"生成所有 n-tuples"子系列第一篇
- **Source**: TAOCP Pre-Fascicle 2A, Section 7.2.1.1 (Generating All n-Tuples)
- **Language**: 中文，代码用 Python
- **Estimated length**: 3000-3500 字 + 代码 + 图表
- **Approach**: 问题驱动型 — 从九连环的最少步数问题出发，发现格雷码

## Article Structure

### 1. 开篇 — 九连环与问题 (~400字)

介绍九连环：横杆、环、链条约束。配一张简化示意图。

两条规则：
- 最右边的环随时可操作
- 其他环只有"右邻在杆上、右邻之后全部离杆"时才能操作

抛出问题：**n 个环，最少需要多少步才能全部取下？**

### 2. 小规模尝试 — 手动拆解 (~300字)

用 n=3 为主要例子，快速展示完整拆解过程，用表格列出每步状态 (如 `111 → 110 → 100 → 101 → 001 → 000`)。n=1, n=2 一笔带过。

发现递归结构：要拆 n 个环，先拆前 n-2 个，操作第 n 个，再装回前 n-2 个，然后拆前 n-1 个。
递推关系：T(n) = T(n-1) + 1 + T(n-2)

### 3. 从 01 串到格雷码 (~500字)

把"环在杆上"记为 1，"不在"记为 0。用第 2 节的 n=3 状态表格直接观察。

关键发现：**相邻两个状态之间，恰好只有一位不同。** 规则本身要求每步只操作一个环，所以这是必然的。我们得到了一个遍历所有 3-bit 串、每次只改一位的序列。

命名：这就是格雷码！正式定义：2^n 个 n-bit 串的序列，相邻两串恰差一位。

历史简述：
- Frank Gray 1953 年专利（脉冲编码调制）
- Louis Gros 1872 年通过九连环已经发现
- Knuth: Gros is "the true inventor"

点明：九连环的拆解序列就是格雷码的逆序。

### 4. 反射构造法 (~500字)

递归构造（PDF 公式 (5)）：
- Γ₀ = ε
- Γₙ₊₁ = 0Γₙ, 1Γₙᴿ

用 n=1,2,3 展示构造过程。解释"反射"含义：后半部分是前半部分的镜像翻转，首位加 1。

与九连环的对应：递归拆环过程对应反射构造的递归结构。

给出 g(k) 函数：格雷码第 k 个元素 = k XOR (k >> 1)，Python 一行实现。

### 5. Algorithm G — Knuth 的实现 (~600字)

Algorithm G（PDF p.10）核心思想：维护 parity bit，决定翻转哪一位。

逐步讲解 G1-G5：
- parity bit 追踪操作奇偶性
- parity 为偶 → 翻转最低位
- parity 为奇 → 翻转"最低的 1"左边那一位

Python 生成器实现，yield 每个 n-tuple。

用代码跑 n=4，输出 16 个格雷码，与九连环拆解步骤对照验证。

### 6. 回收问题 — 最少步数 (~300字)

格雷码遍历所有 2^n 个状态且不重复 → 最少步数 = 2^n - 1。

递推关系验证：T(1)=1, T(2)=2, T(3)=5, T(4)=10...
闭合公式：T(n) = (2^(n+1) + (-1)^n) / 3 - 1

趣味事实：7 环需要 85 步。

### 7. 预告 (~100字)

下一篇预告：格雷码的变体（balanced, monotonic, complementary）和 Loopless Algorithm L（focus pointers, O(1) per step）。

## Illustrations

1. 九连环示意图（第1节）
2. n=3 拆解状态表格（第2节）
3. n=3 格雷码 hypercube 路径图 — 三维立方体顶点上的哈密顿路径（第3节）
4. 反射构造递归展开图（第4节）
5. Algorithm G 运行 trace 表格（第5节）

## Follow-up Posts (planned)

- 第二篇：Gray code 变体 + Algorithm L (Loopless)
- 第三篇：De Bruijn 序列 + Algorithm S
- 第四篇：非二进制 Gray codes + Algorithm H/K
