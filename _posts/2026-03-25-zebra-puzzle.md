---
layout: post
title: "谁养斑马？——用算法终结逻辑推理题"
description: "经典的爱因斯坦谜题，手工画表格能把人逼疯。把它翻译成 XCC 问题之后，算法几毫秒就给出唯一解——然后我们反过来，让算法自动出题"
category: algorithm
comments: true
tags: [knuth, exact-cover, dancing-links, CSP, zebra-puzzle, TAOCP]
---

{% include JB/setup %}

我花了一个小时没解出来，然后写了 30 行代码，算法用不到 1 毫秒解完了。

这道题就是著名的"斑马谜题"（又叫爱因斯坦谜题）：五个人住一排房子，每人国籍不同、职业不同、宠物不同、饮料不同、房子颜色不同，给你一堆线索，问——**谁养斑马？**

1962 年发表在 *Life International* 杂志上，据说只有 2% 的人能解出来。

这篇文章介绍一种完全不同的做法：**把谜题翻译成 XCC 问题，让舞蹈链算法自动求解**。不用画表格，不用推理，只需要把"什么是合法答案"描述清楚。

**然后我们反过来——让算法自动出一道新的逻辑推理题。**

<!--more-->

---

## 谜面

完整的 16 条线索（含两条隐含线索）：

1. 英国人住红色房子
2. 黄色房子里住外交官
3. 画家来自日本
4. 喝咖啡的人住绿色房子
5. 挪威人住最左边
6. 西班牙人养狗
7. 中间房子的人喝牛奶
8. 小提琴手喝橙汁
9. 白色房子紧挨在绿色房子左边
10. 乌克兰人喝茶
11. 马住在外交官隔壁
12. 雕塑家养蜗牛
13. 挪威人住蓝色房子隔壁
14. 护士住在狐狸隔壁
15. 有人养斑马（隐含）
16. 有人喝水（隐含）

问：谁养斑马？谁喝水？

---

## 手工解法的痛苦

5 个类别，每个 5 个值，分配到 5 个房子。如果完全没有约束，可能的分配方案有 $$(5!)^5 = 24{,}883{,}200{,}000$$ 种。

手工做法是画一个排除矩阵，逐步收窄范围。但"隔壁"类线索（第 9、11、13、14 条）特别难处理——处理它们时要同时维护多条分支推导链，基本超出人类工作记忆上限。一旦某条分支出错，整张表作废重来。

我们需要一种不怕分支、不怕回溯的方法。

---

## 把线索翻译成 XCC

前两篇（[颜色项与贴纸][dlx-colors]、[拼字谜题][dlx-xcc]）介绍了 XCC 的核心思想及其应用：**主要项必须恰好覆盖一次，颜色项可以被多次覆盖但颜色必须一致**。颜色项用来表示"同一个位置的属性槽"——多条线索可以同时约束它，只要它们给出的颜色（属性值）相同，算法就不会报冲突。

斑马谜题的翻译规则非常直接：

| 概念 | XCC 中的角色 | 说明 |
|:---|:---|:---|
| 每条线索 | **主要项** | 每条线索必须恰好被满足一次 |
| 每个房子的每个属性槽 | **颜色项** | $$N_j, J_j, P_j, D_j, C_j$$（N=国籍, J=职业, P=宠物, D=饮料, C=颜色；$$j=0..4$$） |

颜色项的 color 值就是具体的属性值。比如"$$N_2$$ 的颜色是 England"表示"2 号房子住着英国人"。

通用 CSP 库当然也能解，但 XCC 框架的好处是：颜色项天然支持"多条线索约束同一个槽位"的语义，而且解题和出题使用相同的建模模式，调用同一个求解器——后面会看到这一点。

### 线索怎么变成 option？

以线索 1（"英国人住红色房子"）为例。我们不知道英国人住哪号房子，所以要为每种可能性生成一个 option：

```
#1  N0:England  C0:red     ← 英国人住 0 号房子（红色）
#1  N1:England  C1:red     ← 英国人住 1 号房子（红色）
#1  N2:England  C2:red     ← 英国人住 2 号房子（红色）
#1  N3:England  C3:red     ← 英国人住 3 号房子（红色）
#1  N4:England  C4:red     ← 英国人住 4 号房子（红色）
```

每个 option 包含一个主要项（`#1`，表示"线索 1 被满足"）和若干颜色项（表示"这些属性槽被设置为这些值"）。

算法会从这 5 个 option 里选恰好一个——选中后，对应的颜色项就被"锁定"了。如果后续某条线索试图把同一个 $$N_j$$ 涂成不同颜色，算法自动回溯。

### "隔壁"类线索

线索 11（"马住在外交官隔壁"）稍微复杂。"隔壁"意味着两种可能：马在左外交官在右，或者反过来。对每对相邻位置 $$(i, i+1)$$ 都要列举两种情况：

```
#11  P0:horse  J1:diplomat    ← 马在 0 号，外交官在 1 号
#11  J0:diplomat  P1:horse    ← 外交官在 0 号，马在 1 号
#11  P1:horse  J2:diplomat    ← 马在 1 号，外交官在 2 号
...
```

4 对相邻位置 × 2 种方向 = 8 个 option。

### 固定位置线索

线索 5（"挪威人住最左边"）最简单——只有一个 option：

```
#5  N0:Norway
```

### 总计

16 条线索共生成 **80 个 option**。构建完毕，调用上一篇的 `DLX_C` 求解器，瞬间得到唯一解。

---

## 代码

```python
from dlx_colors import DLX_C

# 16 个 primary items（线索），25 个 secondary items（属性槽）
num_primary = 16
sec_base = 16
def sec_idx(cat, house):  # cat: 0=N,1=J,2=P,3=D,4=C
    return sec_base + cat * 5 + house

# 线索 1: 英国人住红色房子（5 个 option，clue_id=0）
for j in range(5):
    add_option(0, f"#1 N{j}:England C{j}:red",
               [(sec_idx(0, j), 'England'), (sec_idx(4, j), 'red')])

# 线索 9: 白色房子紧挨在绿色房子左边（4 个 option，clue_id=8）
for i in range(4):
    add_option(8, f"#9 C{i}:white C{i+1}:green",
               [(sec_idx(4, i), 'white'), (sec_idx(4, i+1), 'green')])

# 线索 11: 马住在外交官隔壁（8 个 option，clue_id=10）
for i in range(4):
    add_option(10, f"#11 P{i}:horse J{i+1}:diplomat",
               [(sec_idx(2, i), 'horse'), (sec_idx(1, i+1), 'diplomat')])
    add_option(10, f"#11 J{i}:diplomat P{i+1}:horse",
               [(sec_idx(1, i), 'diplomat'), (sec_idx(2, i+1), 'horse')])
```

完整实现见 [zebra_puzzle.py][code_zebra]。运行结果：

```
       House       0       1       2       3       4
  --------------------------------------------------------
 Nationality  Norway Ukraine England   Spain   Japan
         Job diplomat   nurse sculptor violinist painter
         Pet     fox   horse  snails     dog   zebra
       Drink   water     tea    milk      oj  coffee
       Color  yellow    blue     red   white   green
```

**日本人养斑马，挪威人喝水。**

---

## 反过来：自动出题

解题是"给定线索，求分配"。反过来——**给定一个分配，找最少的线索使得解唯一**——就是自动出题。

### 算法

1. **随机生成一个合法分配**：每个类别的 5 个值随机排列到 5 个房子
2. **枚举所有可能的线索**：
   - 同房线索：$$\binom{5}{2} \times 5 = 50$$ 条（"某属性 A 和属性 B 在同一房子"）
   - 相邻线索：$$\binom{5}{2} \times 4 \times 2 + 5 \times 4 = 100$$ 条（"属性 A 和属性 B 在相邻房子"）
   - 固定位置线索：$$5 \times 5 = 25$$ 条（"某属性在第 k 号房子"）
3. **贪心移除**：打乱线索顺序，逐条尝试删除。如果删除后仍有唯一解（用 XCC 验证），就删掉；否则保留

这不保证得到全局最少的线索集（那是 NP-hard 的），但实际效果很好——通常能压缩到 15～20 条线索。

### 一个例子

```python
clues, answer = generate_puzzle(seed=42)
```

输出：

```
 1. The person with Nationality=Canadian also has Color=green.
 2. The person with Drink=coffee also has Color=blue.
 3. The person with Nationality=French lives next to the person with Drink=soda.
 4. The person with Job=lawyer also has Color=yellow.
 5. The person with Job=teacher lives next to the person with Job=artist.
 6. The person with Job=artist also has Pet=cat.
 7. The person with Job=lawyer also has Drink=juice.
 8. The person with Nationality=British lives next to the person with Job=chef.
 9. The person with Pet=hamster also has Drink=coffee.
10. The person with Drink=water lives in the fourth house.
11. The person with Job=lawyer lives next to the person with Color=green.
12. The person with Pet=bird also has Color=white.
13. The person with Nationality=British also has Job=lawyer.
14. The person with Nationality=Dutch lives in the first house.
15. The person with Pet=bird lives next to the person with Pet=dog.
16. The person with Nationality=British lives next to the person with Job=teacher.
17. The person with Drink=juice lives in the second house.
```

17 条线索，唯一解。你可以拿去考朋友。

### 关键代码

出题和解题使用相同的 XCC 建模模式。区别只在于：出题时需要额外的 **all-different** 主要项——因为现在线索不够多，算法需要显式知道"每个属性值恰好出现一次"：

```python
# 每个属性值对应一个 primary item，5 个 option（放在哪个房子）
for cat_i in range(num_cats):
    for v_i, val in enumerate(values[cat_i]):
        for j in range(n):
            options.append([
                (ad_idx(cat_i, v_i), None),   # primary: 该值必须被分配
                (sec_idx(cat_i, j), val)       # secondary: 放在第 j 号房子
            ])
```

这正是 Knuth 在 Exercise 100(c) 里讲的 **CSP → XCC 通用翻译**，斑马谜题（Exercise 101）就是它的经典应用：每个变量的每种取值是一个 option，约束通过颜色项的一致性自动保证。

---

## Knuth 的小优化

Knuth 在 TAOCP 4B 的答案里提到一个技巧：上面的建模**没有**显式约束"每个属性值只能出现在一个房子"。比如，算法并不直接知道"如果 England 在 2 号房子，就不能再出现在别的房子"——它只是碰巧从 16 条线索的交叉约束中推导出这一点。

如果额外加 25 个**逆映射**颜色项（每个属性值一个，颜色 = 房子编号），让算法更早感知到冲突，搜索树就从 **112 个节点**缩减到 **32 个**。代码里加几行就行，但节省的时间"刚好抵消"了这些额外项带来的开销——Knuth 原话。

---

## 回顾

这是本系列第三篇。前两篇分别是[颜色项与贴纸][dlx-colors]和[拼字谜题][dlx-xcc]，建议按顺序阅读。

四篇文章用同一个求解器（`DLX_C`）解了四类完全不同的问题：

| 文章 | 问题 | 主要项 | 颜色项 |
|:---|:---|:---|:---|
| [颜色项与贴纸][dlx-colors] | 颜色项的 bug 与修复 | 每个单词 | 每个格子（颜色=字母） |
| [拼字谜题][dlx-xcc] | 把单词塞进格子 | 每个单词 | 每个格子（颜色=字母） |
| 本篇（解题） | 满足逻辑线索 | 每条线索 | 每个属性槽（颜色=属性值） |
| 本篇（出题） | 找最少线索 | 线索 + all-different | 同上 |

四类问题表面上毫无关联，底层却是同一种结构：描述"什么是合法选择"，让算法找到覆盖全局的那一组。

我们没有写过任何"如何推理"的代码。每次只是换一种方式描述"什么是合法答案"，算法就自动找到了所有答案。

这就是 XCC 最迷人的地方：**你负责描述问题，它负责求解**。

---

## 完整代码

[zebra_puzzle.py][code_zebra] 包含解题和出题两部分，依赖 [dlx_colors.py][code_dlx_colors]，直接运行即可。

换个随机种子就能生成一道新题，拿去考朋友试试。

[dlx-colors]: /2026/03/dlx-colors.html
[dlx-xcc]: /2026/03/dlx-xcc.html
[code_zebra]: https://github.com/morefreeze/morefreeze.github.io/blob/master/code/zebra_puzzle.py
[code_dlx_colors]: https://github.com/morefreeze/morefreeze.github.io/blob/master/code/dlx_colors.py
