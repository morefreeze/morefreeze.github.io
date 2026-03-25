"""
斑马谜题（Einstein's Riddle）—— 用 XCC (Algorithm C) 求解
=========================================================

参考 Knuth TAOCP 4B §7.2.2.1 Exercise 101。

将经典斑马谜题建模为 XCC 问题：
  - 16 个 primary items：每条线索一个（含两条隐含线索）
  - 25 个 secondary items：Nj, Jj, Pj, Dj, Cj (j=0..4)
    分别表示第 j 号房子的国籍、职业、宠物、饮料、颜色
  - 每个 secondary item 用 color 值表示具体属性

同时实现了 Knuth 提到的 "inverse items" 优化：
额外增加 25 个 secondary items 表示逆映射（如 "England 住在哪号房子"），
使搜索树从 112 个节点减少到 32 个。

第二部分：自动生成新的逻辑谜题。
"""

from __future__ import annotations

import random
import sys
from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple

# 从同目录导入 DLX_C
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dlx_colors import DLX_C


# =====================================================================
# 第一部分：经典斑马谜题
# =====================================================================

# 五个属性类别及其取值
NATIONALITIES = ['England', 'Spain', 'Ukraine', 'Norway', 'Japan']
JOBS          = ['diplomat', 'painter', 'violinist', 'sculptor', 'nurse']
PETS          = ['dog', 'snails', 'fox', 'horse', 'zebra']
DRINKS        = ['coffee', 'tea', 'milk', 'oj', 'water']
COLORS        = ['red', 'green', 'white', 'yellow', 'blue']

# 属性类别前缀
CATEGORIES = ['N', 'J', 'P', 'D', 'C']
ALL_VALUES = [NATIONALITIES, JOBS, PETS, DRINKS, COLORS]

NUM_HOUSES = 5


def build_zebra_xcc(use_inverse: bool = False):
    """
    构建斑马谜题的 XCC 实例。

    Parameters
    ----------
    use_inverse : bool
        是否使用逆映射 secondary items 优化（Knuth 的优化技巧）。

    Returns
    -------
    dlx : DLX_C
        构建好的求解器实例
    options_info : list
        每个 option 的描述信息（用于解读解）
    secondary_names : dict
        secondary item 索引到名称的映射
    """
    # --- item 编号 ---
    # 16 个 primary items: clue #1 ~ #16
    num_primary = 16

    # 25 个 secondary items: N0..N4, J0..J4, P0..P4, D0..D4, C0..C4
    # 编号从 16 开始
    sec_base = num_primary  # = 16
    # sec_idx(cat, house): 返回 secondary item 的全局索引
    # cat: 0=N, 1=J, 2=P, 3=D, 4=C
    def sec_idx(cat: int, house: int) -> int:
        return sec_base + cat * NUM_HOUSES + house

    num_secondary = 25  # 5 categories × 5 houses
    num_items = num_primary + num_secondary

    # 如果使用逆映射优化，再加 25 个 secondary items
    # 逆映射：每个属性值对应一个 item，color 为房子编号
    # 例如 N_England^-1 的 color = j 表示 England 住在第 j 号房子
    inv_base = num_items  # 逆映射 items 的起始索引
    if use_inverse:
        num_inverse = 25  # 5 categories × 5 values
        num_items += num_inverse

        def inv_idx(cat: int, val_idx: int) -> int:
            """逆映射 item 索引: cat 类别中第 val_idx 个值"""
            return inv_base + cat * NUM_HOUSES + val_idx

        # 建立值到索引的映射
        val_to_idx = {}
        for cat_i, values in enumerate(ALL_VALUES):
            for v_i, val in enumerate(values):
                val_to_idx[(cat_i, val)] = v_i

    # --- 构建 secondary item 名称映射（用于调试） ---
    secondary_names = {}
    for cat_i, prefix in enumerate(CATEGORIES):
        for j in range(NUM_HOUSES):
            secondary_names[sec_idx(cat_i, j)] = f"{prefix}{j}"
    if use_inverse:
        for cat_i, values in enumerate(ALL_VALUES):
            for v_i, val in enumerate(values):
                secondary_names[inv_idx(cat_i, v_i)] = f"{CATEGORIES[cat_i]}_{val}^-1"

    # --- 构建 options ---
    options = []
    options_info = []  # 每个 option 的文字描述

    def add_option(clue_id: int, desc: str, sec_items: List[Tuple[int, Any]]):
        """
        添加一个 option。

        clue_id: 线索编号 (0-based，对应 primary item 索引)
        desc: 文字描述
        sec_items: [(secondary_item_idx, color_value), ...]
        """
        opt = [(clue_id, None)]  # primary item
        for idx, color in sec_items:
            opt.append((idx, color))

        # 如果启用逆映射，为每个涉及的 secondary item 添加逆映射项
        if use_inverse:
            for idx, color in sec_items:
                if idx < inv_base:  # 只处理正向 secondary items
                    cat_i = (idx - sec_base) // NUM_HOUSES
                    house = (idx - sec_base) % NUM_HOUSES
                    v_i = val_to_idx.get((cat_i, color))
                    if v_i is not None:
                        opt.append((inv_idx(cat_i, v_i), house))

        options.append(opt)
        options_info.append(desc)

    # === 14 条显式线索 + 2 条隐含线索 ===

    # #1 (clue 0): The Englishman lives in a red house.
    # 英国人住在红色房子里
    for j in range(NUM_HOUSES):
        add_option(0, f"#1 N{j}:England C{j}:red",
                   [(sec_idx(0, j), 'England'), (sec_idx(4, j), 'red')])

    # #2 (clue 1): The yellow house hosts a diplomat.
    # 黄色房子里住着外交官
    for j in range(NUM_HOUSES):
        add_option(1, f"#2 C{j}:yellow J{j}:diplomat",
                   [(sec_idx(4, j), 'yellow'), (sec_idx(1, j), 'diplomat')])

    # #3 (clue 2): The painter comes from Japan.
    # 画家来自日本
    for j in range(NUM_HOUSES):
        add_option(2, f"#3 J{j}:painter N{j}:Japan",
                   [(sec_idx(1, j), 'painter'), (sec_idx(0, j), 'Japan')])

    # #4 (clue 3): The coffee-lover's house is green.
    # 喝咖啡的人住在绿色房子里
    for j in range(NUM_HOUSES):
        add_option(3, f"#4 D{j}:coffee C{j}:green",
                   [(sec_idx(3, j), 'coffee'), (sec_idx(4, j), 'green')])

    # #5 (clue 4): The Norwegian's house is the leftmost.
    # 挪威人住在最左边
    add_option(4, "#5 N0:Norway",
               [(sec_idx(0, 0), 'Norway')])

    # #6 (clue 5): The dog's owner is from Spain.
    # 西班牙人养狗
    for j in range(NUM_HOUSES):
        add_option(5, f"#6 P{j}:dog N{j}:Spain",
                   [(sec_idx(2, j), 'dog'), (sec_idx(0, j), 'Spain')])

    # #7 (clue 6): The milk drinker lives in the middle house.
    # 喝牛奶的人住在中间的房子里
    add_option(6, "#7 D2:milk",
               [(sec_idx(3, 2), 'milk')])

    # #8 (clue 7): The violinist drinks orange juice.
    # 小提琴手喝橙汁
    for j in range(NUM_HOUSES):
        add_option(7, f"#8 J{j}:violinist D{j}:oj",
                   [(sec_idx(1, j), 'violinist'), (sec_idx(3, j), 'oj')])

    # #9 (clue 8): The white house is just left of the green one.
    # 白色房子在绿色房子的左边（紧邻）
    for i in range(NUM_HOUSES - 1):
        add_option(8, f"#9 C{i}:white C{i+1}:green",
                   [(sec_idx(4, i), 'white'), (sec_idx(4, i + 1), 'green')])

    # #10 (clue 9): The Ukrainian drinks tea.
    # 乌克兰人喝茶
    for j in range(NUM_HOUSES):
        add_option(9, f"#10 N{j}:Ukraine D{j}:tea",
                   [(sec_idx(0, j), 'Ukraine'), (sec_idx(3, j), 'tea')])

    # #11 (clue 10): The horse lives next to the diplomat.
    # 马住在外交官隔壁
    for i in range(NUM_HOUSES - 1):
        # 马在左，外交官在右
        add_option(10, f"#11 P{i}:horse J{i+1}:diplomat",
                   [(sec_idx(2, i), 'horse'), (sec_idx(1, i + 1), 'diplomat')])
        # 外交官在左，马在右
        add_option(10, f"#11 J{i}:diplomat P{i+1}:horse",
                   [(sec_idx(1, i), 'diplomat'), (sec_idx(2, i + 1), 'horse')])

    # #12 (clue 11): The sculptor breeds snails.
    # 雕塑家养蜗牛
    for j in range(NUM_HOUSES):
        add_option(11, f"#12 J{j}:sculptor P{j}:snails",
                   [(sec_idx(1, j), 'sculptor'), (sec_idx(2, j), 'snails')])

    # #13 (clue 12): The Norwegian lives next to the blue house.
    # 挪威人住在蓝色房子旁边
    for i in range(NUM_HOUSES - 1):
        # 挪威人在左，蓝色在右
        add_option(12, f"#13 N{i}:Norway C{i+1}:blue",
                   [(sec_idx(0, i), 'Norway'), (sec_idx(4, i + 1), 'blue')])
        # 蓝色在左，挪威人在右
        add_option(12, f"#13 C{i}:blue N{i+1}:Norway",
                   [(sec_idx(4, i), 'blue'), (sec_idx(0, i + 1), 'Norway')])

    # #14 (clue 13): The nurse lives next to the fox.
    # 护士住在狐狸旁边
    for i in range(NUM_HOUSES - 1):
        add_option(13, f"#14 J{i}:nurse P{i+1}:fox",
                   [(sec_idx(1, i), 'nurse'), (sec_idx(2, i + 1), 'fox')])
        add_option(13, f"#14 P{i}:fox J{i+1}:nurse",
                   [(sec_idx(2, i), 'fox'), (sec_idx(1, i + 1), 'nurse')])

    # #15 (clue 14): Somebody trains a zebra.
    # 有人养斑马
    for j in range(NUM_HOUSES):
        add_option(14, f"#15 P{j}:zebra",
                   [(sec_idx(2, j), 'zebra')])

    # #16 (clue 15): Somebody drinks water.
    # 有人喝水
    for j in range(NUM_HOUSES):
        add_option(15, f"#16 D{j}:water",
                   [(sec_idx(3, j), 'water')])

    # --- 构建求解器 ---
    dlx = DLX_C(num_primary, num_items, options)
    return dlx, options_info, secondary_names


def solve_zebra(use_inverse: bool = False, verbose: bool = True):
    """
    求解经典斑马谜题并打印结果。

    Returns
    -------
    solution : dict
        {house_idx: {'N': ..., 'J': ..., 'P': ..., 'D': ..., 'C': ...}}
    """
    dlx, options_info, sec_names = build_zebra_xcc(use_inverse=use_inverse)

    solutions = list(dlx.solve())

    if verbose:
        mode = "with inverse items" if use_inverse else "without inverse items"
        print(f"\n{'='*60}")
        print(f"  Zebra Puzzle (Einstein's Riddle) — XCC ({mode})")
        print(f"{'='*60}")
        print(f"  Options (rows): {len(options_info)}")
        print(f"  Solutions found: {len(solutions)}")

    if not solutions:
        if verbose:
            print("  No solution found!")
        return None

    # 解读第一个解
    sol = solutions[0]
    if verbose:
        print(f"\n  Selected options:")
        for idx in sorted(sol):
            print(f"    [{idx:3d}] {options_info[idx]}")

    # 从 option 描述中提取属性赋值
    # 每个 option 的格式是 "#k SecItem:value ..."
    assignment = {j: {} for j in range(NUM_HOUSES)}
    for idx in sol:
        desc = options_info[idx]
        parts = desc.split()
        for part in parts[1:]:  # 跳过 "#k"
            # 解析 "Nj:value" 格式
            colon = part.index(':')
            item_name = part[:colon]
            value = part[colon + 1:]
            prefix = item_name[0]
            house = int(item_name[1])
            cat_key = prefix  # N, J, P, D, C
            assignment[house][cat_key] = value

    if verbose:
        # 打印结果表格
        cat_labels = {'N': 'Nationality', 'J': 'Job', 'P': 'Pet',
                      'D': 'Drink', 'C': 'Color'}
        print(f"\n  {'House':>12}", end='')
        for j in range(NUM_HOUSES):
            print(f"  {j:>12}", end='')
        print()
        print("  " + "-" * 74)
        for cat in CATEGORIES:
            print(f"  {cat_labels[cat]:>12}", end='')
            for j in range(NUM_HOUSES):
                val = assignment[j].get(cat, '?')
                print(f"  {val:>12}", end='')
            print()

        # 回答经典问题
        zebra_owner = None
        water_drinker = None
        for j in range(NUM_HOUSES):
            if assignment[j].get('P') == 'zebra':
                zebra_owner = assignment[j].get('N', '?')
            if assignment[j].get('D') == 'water':
                water_drinker = assignment[j].get('N', '?')
        print(f"\n  >>> The {zebra_owner} owns the zebra.")
        print(f"  >>> The {water_drinker} drinks water.")

    return assignment


# =====================================================================
# 第二部分：谜题生成器
# =====================================================================

# 生成器使用的属性类别名称（更友好的描述）
GEN_CATEGORIES = ['Nationality', 'Job', 'Pet', 'Drink', 'Color']
GEN_VALUES = [
    ['American', 'British', 'Canadian', 'Dutch', 'French'],
    ['teacher', 'doctor', 'lawyer', 'chef', 'artist'],
    ['cat', 'dog', 'fish', 'bird', 'hamster'],
    ['coffee', 'tea', 'juice', 'soda', 'water'],
    ['red', 'blue', 'green', 'yellow', 'white'],
]


class Clue:
    """表示一条逻辑谜题线索"""

    def __init__(self, clue_type: str, **kwargs):
        """
        clue_type:
          'same'     — 同一房子中两个属性共存
          'adjacent' — 两个属性在相邻房子
          'fixed'    — 某属性在指定位置
        """
        self.clue_type = clue_type
        self.params = kwargs

    def describe(self) -> str:
        """生成自然语言描述"""
        p = self.params
        if self.clue_type == 'fixed':
            pos_name = ['first', 'second', 'third', 'fourth', 'fifth'][p['house']]
            return f"The person with {p['cat_name']}={p['value']} lives in the {pos_name} house."
        elif self.clue_type == 'same':
            return (f"The person with {p['cat_name_a']}={p['value_a']} "
                    f"also has {p['cat_name_b']}={p['value_b']}.")
        elif self.clue_type == 'adjacent':
            return (f"The person with {p['cat_name_a']}={p['value_a']} "
                    f"lives next to the person with {p['cat_name_b']}={p['value_b']}.")
        return str(p)

    def __repr__(self):
        return f"Clue({self.clue_type}, {self.params})"


def _build_xcc_from_clues(clues: List[Clue], categories: List[str],
                           values: List[List[str]], n: int = 5,
                           use_inverse: bool = False):
    """
    将一组线索构建为 XCC 问题。

    除了线索对应的 primary items，还添加 "all-different" 约束：
    每个属性值必须恰好出现在一个房子中。这通过额外的 primary items 实现，
    每个属性值一个 primary item，对应 n 个 options（放在哪个房子）。

    Parameters
    ----------
    clues : list of Clue
    categories : 类别名称列表
    values : 每个类别的取值列表
    n : 房子数量
    use_inverse : 是否使用逆映射优化

    Returns
    -------
    dlx : DLX_C
    options_info : list of str
    options : raw option data
    sec_base : secondary items 起始索引
    num_cats : 类别数量
    n : 房子数量
    """
    num_clues = len(clues)
    num_cats = len(categories)

    # Primary items:
    #   - num_clues 个线索约束 (indices 0 .. num_clues-1)
    #   - num_cats * n 个 "all-different" 约束
    #     每个属性值必须恰好被分配到一个房子
    #     (indices num_clues .. num_clues + num_cats*n - 1)
    ad_base = num_clues  # all-different primary items 起始索引
    num_primary = num_clues + num_cats * n

    def ad_idx(cat: int, val_idx: int) -> int:
        """all-different primary item 索引"""
        return ad_base + cat * n + val_idx

    # Secondary items: Nj, Jj, Pj, Dj, Cj (j=0..n-1)
    sec_base = num_primary
    num_secondary = num_cats * n

    def sec_idx(cat: int, house: int) -> int:
        return sec_base + cat * n + house

    num_items = num_primary + num_secondary

    # 逆映射
    inv_base = num_items
    if use_inverse:
        num_inverse = num_cats * n  # 每个类别 n 个值
        num_items += num_inverse

        def inv_idx(cat: int, val_idx: int) -> int:
            return inv_base + cat * n + val_idx

    # 值到索引的映射
    val_to_idx = {}
    for cat_i, vals in enumerate(values):
        for v_i, val in enumerate(vals):
            val_to_idx[(cat_i, val)] = v_i

    options = []
    options_info = []

    # 类别名到索引
    cat_name_to_idx = {name: i for i, name in enumerate(categories)}

    # === all-different options ===
    # 对于每个类别的每个值，生成 n 个 option（放在哪个房子）
    for cat_i in range(num_cats):
        for v_i, val in enumerate(values[cat_i]):
            for j in range(n):
                opt = [(ad_idx(cat_i, v_i), None),  # primary: 该值必须被分配
                       (sec_idx(cat_i, j), val)]     # secondary: 放在第 j 号房子
                if use_inverse:
                    opt.append((inv_idx(cat_i, v_i), j))
                options.append(opt)
                options_info.append(
                    f"assign {categories[cat_i]}={val} to house {j}")

    # === 线索对应的 options ===
    for clue_i, clue in enumerate(clues):
        p = clue.params

        if clue.clue_type == 'fixed':
            cat_i = cat_name_to_idx[p['cat_name']]
            house = p['house']
            val = p['value']
            opt = [(clue_i, None), (sec_idx(cat_i, house), val)]
            if use_inverse:
                v_i = val_to_idx.get((cat_i, val))
                if v_i is not None:
                    opt.append((inv_idx(cat_i, v_i), house))
            options.append(opt)
            options_info.append(clue.describe())

        elif clue.clue_type == 'same':
            cat_a = cat_name_to_idx[p['cat_name_a']]
            cat_b = cat_name_to_idx[p['cat_name_b']]
            val_a = p['value_a']
            val_b = p['value_b']
            for j in range(n):
                opt = [(clue_i, None),
                       (sec_idx(cat_a, j), val_a),
                       (sec_idx(cat_b, j), val_b)]
                if use_inverse:
                    v_i_a = val_to_idx.get((cat_a, val_a))
                    v_i_b = val_to_idx.get((cat_b, val_b))
                    if v_i_a is not None:
                        opt.append((inv_idx(cat_a, v_i_a), j))
                    if v_i_b is not None:
                        opt.append((inv_idx(cat_b, v_i_b), j))
                options.append(opt)
                options_info.append(f"#{clue_i+1} house {j}: {clue.describe()}")

        elif clue.clue_type == 'adjacent':
            cat_a = cat_name_to_idx[p['cat_name_a']]
            cat_b = cat_name_to_idx[p['cat_name_b']]
            val_a = p['value_a']
            val_b = p['value_b']
            for i in range(n - 1):
                # A 在左，B 在右
                opt1 = [(clue_i, None),
                        (sec_idx(cat_a, i), val_a),
                        (sec_idx(cat_b, i + 1), val_b)]
                if use_inverse:
                    v_i_a = val_to_idx.get((cat_a, val_a))
                    v_i_b = val_to_idx.get((cat_b, val_b))
                    if v_i_a is not None:
                        opt1.append((inv_idx(cat_a, v_i_a), i))
                    if v_i_b is not None:
                        opt1.append((inv_idx(cat_b, v_i_b), i + 1))
                options.append(opt1)
                options_info.append(f"#{clue_i+1} ({i},{i+1}): {clue.describe()}")

                # B 在左，A 在右
                opt2 = [(clue_i, None),
                        (sec_idx(cat_b, i), val_b),
                        (sec_idx(cat_a, i + 1), val_a)]
                if use_inverse:
                    v_i_a = val_to_idx.get((cat_a, val_a))
                    v_i_b = val_to_idx.get((cat_b, val_b))
                    if v_i_b is not None:
                        opt2.append((inv_idx(cat_b, v_i_b), i))
                    if v_i_a is not None:
                        opt2.append((inv_idx(cat_a, v_i_a), i + 1))
                options.append(opt2)
                options_info.append(f"#{clue_i+1} ({i+1},{i}): {clue.describe()}")

    dlx = DLX_C(num_primary, num_items, options)
    return dlx, options_info, options, sec_base, num_cats, n


def count_solutions(clues: List[Clue], categories: List[str],
                    values: List[List[str]], n: int = 5, limit: int = 2) -> int:
    """
    计算给定线索集合的解的数量（最多数到 limit 即停止）。

    用于判断谜题是否有唯一解。
    """
    dlx, *_ = _build_xcc_from_clues(clues, categories, values, n, use_inverse=True)
    count = 0
    for _ in dlx.solve():
        count += 1
        if count >= limit:
            break
    return count


def generate_puzzle(n: int = 5, seed: Optional[int] = None,
                    verbose: bool = True) -> Tuple[List[Clue], List[List[str]]]:
    """
    自动生成一道逻辑谜题。

    算法：
    1. 随机生成一个合法赋值（每个属性类别的值随机排列）
    2. 枚举所有可能的线索（同房、相邻、固定位置）
    3. 打乱线索顺序，逐条尝试移除
    4. 如果移除后仍有唯一解，则移除该线索
    5. 最终得到一个（近似）最小线索集

    Parameters
    ----------
    n : int
        房子数量（默认 5）
    seed : int, optional
        随机种子
    verbose : bool
        是否打印详细信息

    Returns
    -------
    final_clues : list of Clue
    assignment : list of list of str
        真实答案，assignment[cat][house] = value
    """
    if seed is not None:
        random.seed(seed)

    categories = GEN_CATEGORIES
    values = GEN_VALUES

    # 第 1 步：随机生成赋值
    # assignment[cat][house] = 该类别在该房子的值
    assignment = []
    for cat_i in range(len(categories)):
        perm = list(values[cat_i])
        random.shuffle(perm)
        assignment.append(perm)

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Puzzle Generator (seed={seed})")
        print(f"{'='*60}")
        print(f"\n  Secret assignment (answer):")
        print(f"  {'House':>12}", end='')
        for j in range(n):
            print(f"  {j:>10}", end='')
        print()
        print("  " + "-" * (12 + 12 * n))
        for cat_i, cat_name in enumerate(categories):
            print(f"  {cat_name:>12}", end='')
            for j in range(n):
                print(f"  {assignment[cat_i][j]:>10}", end='')
            print()

    # 第 2 步：生成所有可能的线索
    all_clues = []

    # 同房线索：不同类别的属性对在同一房子
    for ca, cb in combinations(range(len(categories)), 2):
        for j in range(n):
            all_clues.append(Clue('same',
                                  cat_name_a=categories[ca], value_a=assignment[ca][j],
                                  cat_name_b=categories[cb], value_b=assignment[cb][j]))

    # 相邻线索：不同类别（或同类别）的属性在相邻房子
    for ca in range(len(categories)):
        for cb in range(ca, len(categories)):
            for j in range(n - 1):
                # 属性 A 在 house j，属性 B 在 house j+1
                val_a = assignment[ca][j]
                val_b = assignment[cb][j + 1]
                all_clues.append(Clue('adjacent',
                                      cat_name_a=categories[ca], value_a=val_a,
                                      cat_name_b=categories[cb], value_b=val_b))
                # 反方向也考虑（如果不同类别）
                if ca != cb:
                    val_a2 = assignment[ca][j + 1]
                    val_b2 = assignment[cb][j]
                    all_clues.append(Clue('adjacent',
                                          cat_name_a=categories[ca], value_a=val_a2,
                                          cat_name_b=categories[cb], value_b=val_b2))

    # 固定位置线索
    for ca in range(len(categories)):
        for j in range(n):
            all_clues.append(Clue('fixed',
                                  cat_name=categories[ca], value=assignment[ca][j],
                                  house=j))

    if verbose:
        print(f"\n  Total candidate clues: {len(all_clues)}")

    # 第 3 步：从全部线索出发，贪心移除
    # 先打乱顺序以获得不同的最小集
    random.shuffle(all_clues)
    remaining = list(all_clues)

    # 验证全部线索确实给出唯一解
    assert count_solutions(remaining, categories, values, n) == 1, \
        "Bug: all clues should give unique solution"

    # 逐条尝试移除
    i = 0
    while i < len(remaining):
        # 尝试移除第 i 条
        candidate = remaining[:i] + remaining[i + 1:]
        if count_solutions(candidate, categories, values, n) == 1:
            remaining = candidate
            # 不递增 i，因为列表缩短了
        else:
            i += 1

    if verbose:
        print(f"  Clues after minimization: {len(remaining)}")
        print(f"\n  Generated puzzle clues:")
        for k, clue in enumerate(remaining):
            print(f"    {k+1}. {clue.describe()}")

    # 验证最终线索集
    final_count = count_solutions(remaining, categories, values, n)
    assert final_count == 1, f"Bug: final clues have {final_count} solutions"

    return remaining, assignment


def solve_generated_puzzle(clues: List[Clue], verbose: bool = True):
    """
    用 XCC 求解生成的谜题并打印结果。

    通过解析 XCC 解中选中 option 的 secondary items 颜色来还原完整赋值。
    """
    categories = GEN_CATEGORIES
    values = GEN_VALUES
    n = 5

    dlx, options_info, raw_options, sec_base, num_cats, _ = \
        _build_xcc_from_clues(clues, categories, values, n, use_inverse=True)

    solutions = list(dlx.solve())
    if verbose:
        print(f"\n  Solving generated puzzle...")
        print(f"  Solutions found: {len(solutions)}")

    if not solutions:
        return None

    sol = solutions[0]

    # 从选中的 options 中提取 secondary items 的颜色赋值
    # secondary item 编号: sec_base + cat * n + house
    result = {j: {} for j in range(n)}
    for idx in sol:
        opt = raw_options[idx]
        for item_idx, color in opt:
            if sec_base <= item_idx < sec_base + num_cats * n:
                offset = item_idx - sec_base
                cat_i = offset // n
                house = offset % n
                result[house][categories[cat_i]] = color

    # 用排除法填充未确定的属性值
    # 每个类别的每个值恰好出现在一个房子里
    for cat_i, cat_name in enumerate(categories):
        assigned = {result[j].get(cat_name) for j in range(n)} - {None}
        remaining_vals = [v for v in values[cat_i] if v not in assigned]
        remaining_houses = [j for j in range(n) if cat_name not in result[j]]
        if len(remaining_vals) == len(remaining_houses) == 1:
            result[remaining_houses[0]][cat_name] = remaining_vals[0]
    # 可能需要多轮排除（当有多个未填值时依次推导）
    for _ in range(n):
        for cat_i, cat_name in enumerate(categories):
            assigned = {result[j].get(cat_name) for j in range(n)} - {None}
            remaining_vals = [v for v in values[cat_i] if v not in assigned]
            remaining_houses = [j for j in range(n) if cat_name not in result[j]]
            if len(remaining_vals) == 1 and len(remaining_houses) == 1:
                result[remaining_houses[0]][cat_name] = remaining_vals[0]

    if verbose:
        print(f"\n  {'House':>12}", end='')
        for j in range(n):
            print(f"  {j:>10}", end='')
        print()
        print("  " + "-" * (12 + 12 * n))
        for cat_name in categories:
            print(f"  {cat_name:>12}", end='')
            for j in range(n):
                print(f"  {result[j].get(cat_name, '?'):>10}", end='')
            print()

    return result


# =====================================================================
# 主程序
# =====================================================================

if __name__ == '__main__':
    # --- 求解经典斑马谜题 ---
    print("=" * 60)
    print("  Part 1: Classic Zebra Puzzle")
    print("=" * 60)

    # 不使用逆映射优化
    print("\n  [Without inverse items optimization]")
    solve_zebra(use_inverse=False, verbose=True)

    # 使用逆映射优化
    print("\n  [With inverse items optimization]")
    solve_zebra(use_inverse=True, verbose=True)

    # --- 生成新谜题 ---
    print("\n\n" + "=" * 60)
    print("  Part 2: Puzzle Generator")
    print("=" * 60)

    clues, assignment = generate_puzzle(seed=42, verbose=True)
    solve_generated_puzzle(clues, verbose=True)
