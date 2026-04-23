"""
生成 Kakuro 博客配图 SVG 文件

生成三个 SVG 文件：
  1. images/kakuro-mini.svg     - 教学示例谜题（左：题目，右：解答）
  2. images/kakuro-sum-table.svg - 和表热图
  3. images/kakuro-pentomino.svg - 五格骨牌形状的 Kakuro 笼示意图
"""

import sys
import os
import xml.etree.ElementTree as ET

sys.path.insert(0, '/Users/bytedance/mygit/morefreeze.github.io/code')

IMAGES_DIR = '/Users/bytedance/mygit/morefreeze.github.io/images'

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def svg_root(width: int, height: int) -> ET.Element:
    """创建 SVG 根元素。"""
    root = ET.Element('svg')
    root.set('xmlns', 'http://www.w3.org/2000/svg')
    root.set('width', str(width))
    root.set('height', str(height))
    root.set('viewBox', f'0 0 {width} {height}')
    return root


def rect(parent: ET.Element, x, y, w, h, fill, stroke='none', sw=1) -> ET.Element:
    el = ET.SubElement(parent, 'rect')
    el.set('x', str(x))
    el.set('y', str(y))
    el.set('width', str(w))
    el.set('height', str(h))
    el.set('fill', fill)
    if stroke != 'none':
        el.set('stroke', stroke)
        el.set('stroke-width', str(sw))
    return el


def text(parent: ET.Element, x, y, content, font_size=12, fill='black',
         anchor='middle', dominant='middle', weight='normal', font_family='monospace') -> ET.Element:
    el = ET.SubElement(parent, 'text')
    el.set('x', str(x))
    el.set('y', str(y))
    el.set('font-size', str(font_size))
    el.set('fill', fill)
    el.set('text-anchor', anchor)
    el.set('dominant-baseline', dominant)
    el.set('font-weight', weight)
    el.set('font-family', font_family)
    el.text = content
    return el


def line(parent: ET.Element, x1, y1, x2, y2, stroke='black', sw=1) -> ET.Element:
    el = ET.SubElement(parent, 'line')
    el.set('x1', str(x1))
    el.set('y1', str(y1))
    el.set('x2', str(x2))
    el.set('y2', str(y2))
    el.set('stroke', stroke)
    el.set('stroke-width', str(sw))
    return el


def save_svg(root: ET.Element, path: str):
    """将 SVG 写入文件。"""
    tree = ET.ElementTree(root)
    ET.indent(tree, space='  ')
    tree.write(path, encoding='unicode', xml_declaration=False)
    print(f'已写入：{path}')


# ---------------------------------------------------------------------------
# SVG 1: kakuro-mini.svg — 教学示例（左：题目，右：解答）
# ---------------------------------------------------------------------------

def gen_kakuro_mini():
    """
    生成教学示例 Kakuro 的 SVG（谜题 + 解答并排）。

    布局：
      - 真实网格行列（含黑格边框）：行 0..5，列 0..3
        - 行 0: 全黑（顶部边框）
        - 行 1: [黑] [纵线索 v0=7] [纵线索 v1=11] [黑]
        - 行 2-4: [黑] [横线索 h0=3/h1=11/h2=4 | 白格 | 白格] [黑]
        - 行 5: 全黑（底部边框）
      - 左：题目（白格空白）
      - 右：解答（白格填入数字）

    教学示例解：
      (2,1)=2, (2,2)=1, (3,1)=4, (3,2)=7, (4,1)=1, (4,2)=3
    """
    CELL = 64          # 格子像素
    MARGIN = 16        # 外边距
    GAP = 32           # 两个视图之间的间距

    # 显示网格：6行×4列（行0..5，列0..3）
    GRID_ROWS = 6
    GRID_COLS = 4

    PANEL_W = GRID_COLS * CELL
    PANEL_H = GRID_ROWS * CELL

    TOTAL_W = 2 * PANEL_W + GAP + 2 * MARGIN
    TOTAL_H = PANEL_H + 2 * MARGIN + 40  # 40px 标题

    svg = svg_root(TOTAL_W, TOTAL_H)

    # 背景
    rect(svg, 0, 0, TOTAL_W, TOTAL_H, '#f8f8f8')

    # 标题
    text(svg, TOTAL_W // 2, 20, '教学示例 Kakuro（3×2 白格）',
         font_size=16, fill='#333', weight='bold', font_family='sans-serif')

    # 谜题数据
    # 线索格位置（display row, display col）
    # 真实白格：(row=2..4, col=1..2) 在显示网格中
    # 横向线索在 col=0（行 2,3,4）；纵向线索在 row=1（col=1,2）
    h_clues = [3, 11, 4]    # H0,H1,H2
    v_clues = [7, 11]       # V0,V1

    solution = {
        (2, 1): 2, (2, 2): 1,
        (3, 1): 4, (3, 2): 7,
        (4, 1): 1, (4, 2): 3,
    }

    def draw_panel(ox: int, oy: int, show_solution: bool):
        """在偏移 (ox, oy) 处绘制一个面板。"""

        def cx(col): return ox + col * CELL
        def cy(row): return oy + row * CELL

        # 绘制所有格子
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x, y = cx(col), cy(row)

                # 判断格子类型
                is_white = (2 <= row <= 4 and 1 <= col <= 2)
                is_h_clue = (2 <= row <= 4 and col == 0)   # 横向线索格
                is_v_clue = (row == 1 and 1 <= col <= 2)   # 纵向线索格

                if is_white:
                    rect(svg, x, y, CELL, CELL, 'white', '#666', 1)
                    if show_solution:
                        d = solution[(row, col)]
                        text(svg, x + CELL // 2, y + CELL // 2, str(d),
                             font_size=22, fill='#1a5fad', weight='bold')
                elif is_h_clue:
                    # 横向线索格（黑底，左下显示数字，对角线分割）
                    rect(svg, x, y, CELL, CELL, '#2c2c2c', '#555', 1)
                    clue_idx = row - 2
                    clue = h_clues[clue_idx]
                    # 对角线
                    line(svg, x + 4, y + 4, x + CELL - 4, y + CELL - 4, '#888', 1)
                    # 数字在左下
                    text(svg, x + CELL // 4, y + CELL * 3 // 4, str(clue),
                         font_size=14, fill='white', weight='bold')
                elif is_v_clue:
                    # 纵向线索格（黑底，右上显示数字，对角线分割）
                    rect(svg, x, y, CELL, CELL, '#2c2c2c', '#555', 1)
                    clue_idx = col - 1
                    clue = v_clues[clue_idx]
                    # 对角线
                    line(svg, x + 4, y + 4, x + CELL - 4, y + CELL - 4, '#888', 1)
                    # 数字在右上
                    text(svg, x + CELL * 3 // 4, y + CELL // 4, str(clue),
                         font_size=14, fill='white', weight='bold')
                else:
                    # 普通黑格
                    rect(svg, x, y, CELL, CELL, '#2c2c2c', '#555', 1)

    # 左面板：题目
    lx = MARGIN
    ly = MARGIN + 30
    draw_panel(lx, ly, show_solution=False)
    text(svg, lx + PANEL_W // 2, ly + PANEL_H + 14, '题目',
         font_size=14, fill='#555', font_family='sans-serif')

    # 右面板：解答
    rx = MARGIN + PANEL_W + GAP
    ry = MARGIN + 30
    draw_panel(rx, ry, show_solution=True)
    text(svg, rx + PANEL_W // 2, ry + PANEL_H + 14, '解答',
         font_size=14, fill='#555', font_family='sans-serif')

    save_svg(svg, os.path.join(IMAGES_DIR, 'kakuro-mini.svg'))


# ---------------------------------------------------------------------------
# SVG 2: kakuro-sum-table.svg — 和表热图
# ---------------------------------------------------------------------------

def gen_sum_table():
    """
    生成 Kakuro 和表热图。

    X 轴：长度 k = 2..9
    Y 轴：和 s = 3..45（仅含有效行）
    颜色：白色（0个组合）→ 深蓝（12个组合，最大值）
    魔法块（唯一组合）：金色背景
    """
    from kakuro import build_sum_table

    C = build_sum_table()

    K_MIN, K_MAX = 2, 9
    S_MIN, S_MAX = 3, 45

    # 只保留至少有一个长度存在组合的 s 值
    valid_s = sorted({s for (s, k) in C.keys() if K_MIN <= k <= K_MAX})

    CELL_W = 44
    CELL_H = 18
    LEFT_MARGIN = 52   # Y 轴标签宽度
    TOP_MARGIN = 50    # X 轴标签高度
    RIGHT_MARGIN = 110  # 图例
    BOTTOM_MARGIN = 20

    n_cols = K_MAX - K_MIN + 1   # 8
    n_rows = len(valid_s)

    W = LEFT_MARGIN + n_cols * CELL_W + RIGHT_MARGIN
    H = TOP_MARGIN + n_rows * CELL_H + BOTTOM_MARGIN

    svg = svg_root(W, H)
    rect(svg, 0, 0, W, H, 'white')

    # 标题
    text(svg, LEFT_MARGIN + n_cols * CELL_W // 2, 18,
         'Kakuro 和表：各 (sum, length) 的组合数',
         font_size=14, fill='#222', weight='bold', font_family='sans-serif')

    # 最大组合数（用于颜色映射）
    MAX_COMBO = 12

    def combo_color(count: int) -> str:
        """将组合数映射为颜色（白→深蓝）。"""
        if count == 0:
            return '#f0f0f0'
        t = count / MAX_COMBO  # 0..1
        # 从浅蓝到深蓝
        r = int(255 * (1 - t * 0.85))
        g = int(255 * (1 - t * 0.75))
        b = 255
        return f'rgb({r},{g},{b})'

    GOLD = '#ffd700'

    # X 轴标签（长度）
    for ki, k in enumerate(range(K_MIN, K_MAX + 1)):
        cx = LEFT_MARGIN + ki * CELL_W + CELL_W // 2
        text(svg, cx, TOP_MARGIN - 8, f'k={k}',
             font_size=11, fill='#444', font_family='sans-serif')

    # X 轴说明
    text(svg, LEFT_MARGIN + n_cols * CELL_W // 2, TOP_MARGIN - 28,
         '长度 k', font_size=12, fill='#333', font_family='sans-serif')

    # Y 轴说明
    label_el = ET.SubElement(svg, 'text')
    label_el.set('transform', f'rotate(-90, 14, {TOP_MARGIN + n_rows * CELL_H // 2})')
    label_el.set('x', '14')
    label_el.set('y', str(TOP_MARGIN + n_rows * CELL_H // 2))
    label_el.set('font-size', '12')
    label_el.set('fill', '#333')
    label_el.set('text-anchor', 'middle')
    label_el.set('dominant-baseline', 'middle')
    label_el.set('font-family', 'sans-serif')
    label_el.text = '和 s'

    # 绘制热图单元格
    for si, s in enumerate(valid_s):
        cy_top = TOP_MARGIN + si * CELL_H

        # Y 轴标签
        text(svg, LEFT_MARGIN - 4, cy_top + CELL_H // 2, str(s),
             font_size=10, fill='#555', anchor='end', font_family='monospace')

        for ki, k in enumerate(range(K_MIN, K_MAX + 1)):
            cx_left = LEFT_MARGIN + ki * CELL_W
            count = len(C.get((s, k), []))

            is_magic = (count == 1)
            bg = GOLD if is_magic else combo_color(count)

            rect(svg, cx_left, cy_top, CELL_W, CELL_H, bg, '#ccc', 0.5)

            if count > 0:
                txt_color = '#222' if count < 8 else 'white'
                text(svg, cx_left + CELL_W // 2, cy_top + CELL_H // 2,
                     str(count), font_size=10, fill=txt_color)

    # 图例
    legend_x = LEFT_MARGIN + n_cols * CELL_W + 12
    legend_y = TOP_MARGIN

    text(svg, legend_x + 30, legend_y - 12, '图例',
         font_size=12, fill='#333', weight='bold', font_family='sans-serif')

    # 魔法块图例
    rect(svg, legend_x, legend_y, 20, 14, GOLD, '#ccc', 0.5)
    text(svg, legend_x + 26, legend_y + 7, '唯一组合',
         font_size=10, fill='#333', anchor='start', font_family='sans-serif')

    # 颜色渐变图例
    for i, count in enumerate([0, 1, 3, 6, 9, 12]):
        ly = legend_y + 22 + i * 18
        bg = combo_color(count)
        if count == 1:
            bg = combo_color(1)  # 普通蓝色，不用金色
        rect(svg, legend_x, ly, 20, 14, bg, '#ccc', 0.5)
        txt_color = '#222' if count < 8 else 'white'
        text(svg, legend_x + 10, ly + 7, str(count) if count > 0 else '0',
             font_size=10, fill=txt_color)
        label = '不可能' if count == 0 else f'{count} 种组合'
        text(svg, legend_x + 26, ly + 7, label,
             font_size=10, fill='#333', anchor='start', font_family='sans-serif')

    save_svg(svg, os.path.join(IMAGES_DIR, 'kakuro-sum-table.svg'))


# ---------------------------------------------------------------------------
# SVG 3: kakuro-pentomino.svg — 五格骨牌笼示意图
# ---------------------------------------------------------------------------

def gen_pentomino():
    """
    生成 12×12 网格中 10 个五格骨牌形状笼的示意图。

    每个笼由 5 个格子组成，形状对应一种五格骨牌（F,I,L,P,T,U,W,X,Y,Z）。
    各笼用不同颜色标注，中心处显示骨牌字母。

    布局设计：在 12×12 网格中铺设 10 个骨牌，共 50 格，其余 94 格为黑格。
    """
    CELL = 48
    MARGIN = 20
    GRID = 12

    # 定义 10 个五格骨牌在网格中的位置（每个骨牌 5 个格子）
    # 坐标 (row, col)，均在 0-indexed 的 12×12 网格内
    pentominoes = {
        'F': [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)],
        'I': [(0, 4), (0, 5), (0, 6), (0, 7), (0, 8)],
        'L': [(0, 10), (1, 10), (2, 10), (3, 10), (3, 11)],
        'P': [(2, 3), (2, 4), (3, 3), (3, 4), (4, 3)],
        'T': [(2, 7), (2, 8), (2, 9), (3, 8), (4, 8)],
        'U': [(5, 1), (5, 3), (6, 1), (6, 2), (6, 3)],
        'W': [(5, 5), (5, 6), (6, 6), (6, 7), (7, 7)],
        'X': [(5, 9), (6, 8), (6, 9), (6, 10), (7, 9)],
        'Y': [(8, 1), (8, 2), (9, 2), (10, 2), (11, 2)],
        'Z': [(8, 5), (8, 6), (9, 6), (10, 6), (10, 7)],
    }

    # 使用 Tableau 风格的配色
    colors = {
        'F': '#e15759',   # 红
        'I': '#4e79a7',   # 蓝
        'L': '#f28e2b',   # 橙
        'P': '#76b7b2',   # 青
        'T': '#59a14f',   # 绿
        'U': '#b07aa1',   # 紫
        'W': '#ff9da7',   # 粉
        'X': '#9c755f',   # 棕
        'Y': '#bab0ac',   # 灰
        'Z': '#edc948',   # 黄
    }

    # 验证：没有重叠
    all_cells = []
    for cells in pentominoes.values():
        all_cells.extend(cells)
    assert len(all_cells) == len(set(all_cells)), "五格骨牌有重叠！"
    assert all(0 <= r < GRID and 0 <= c < GRID for r, c in all_cells), "坐标越界！"

    W = GRID * CELL + 2 * MARGIN
    H = GRID * CELL + 2 * MARGIN + 30  # 30px 标题

    svg = svg_root(W, H)
    rect(svg, 0, 0, W, H, '#1a1a1a')

    # 标题
    text(svg, W // 2, 18, 'Kakuro 五格骨牌笼示意图（10 个骨牌）',
         font_size=14, fill='#ddd', weight='bold', font_family='sans-serif')

    # 反向映射：格子 -> 骨牌名称
    cell_to_piece = {}
    for name, cells in pentominoes.items():
        for cell in cells:
            cell_to_piece[cell] = name

    # 绘制所有格子
    for r in range(GRID):
        for c in range(GRID):
            x = MARGIN + c * CELL
            y = MARGIN + 30 + r * CELL

            if (r, c) in cell_to_piece:
                name = cell_to_piece[(r, c)]
                color = colors[name]
                rect(svg, x, y, CELL, CELL, color, '#1a1a1a', 2)
            else:
                rect(svg, x, y, CELL, CELL, '#2c2c2c', '#444', 1)

    # 在每个骨牌的质心处绘制字母标签
    for name, cells in pentominoes.items():
        avg_r = sum(r for r, c in cells) / 5
        avg_c = sum(c for r, c in cells) / 5
        cx = MARGIN + avg_c * CELL + CELL // 2
        cy = MARGIN + 30 + avg_r * CELL + CELL // 2
        # 深色背景圆形标签
        circle = ET.SubElement(svg, 'circle')
        circle.set('cx', str(int(cx)))
        circle.set('cy', str(int(cy)))
        circle.set('r', '13')
        circle.set('fill', 'rgba(0,0,0,0.55)')
        text(svg, int(cx), int(cy), name,
             font_size=16, fill='white', weight='bold', font_family='sans-serif')

    # 绘制格子边框线（整个网格）
    for r in range(GRID + 1):
        y = MARGIN + 30 + r * CELL
        line(svg, MARGIN, y, MARGIN + GRID * CELL, y, '#444', 0.5)
    for c in range(GRID + 1):
        x = MARGIN + c * CELL
        line(svg, x, MARGIN + 30, x, MARGIN + 30 + GRID * CELL, '#444', 0.5)

    save_svg(svg, os.path.join(IMAGES_DIR, 'kakuro-pentomino.svg'))


# ---------------------------------------------------------------------------
# 主程序
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("生成 Kakuro 博客 SVG 图片...")
    print()

    gen_kakuro_mini()
    gen_sum_table()
    gen_pentomino()

    print()
    print("验证 SVG 文件...")

    import xml.etree.ElementTree as ET2

    for fname in ['kakuro-mini.svg', 'kakuro-sum-table.svg', 'kakuro-pentomino.svg']:
        path = os.path.join(IMAGES_DIR, fname)
        try:
            tree = ET2.parse(path)
            root = tree.getroot()
            w = root.get('width')
            h = root.get('height')
            print(f"  {fname}: OK  ({w} x {h} px)")
        except Exception as e:
            print(f"  {fname}: 错误！{e}")

    print()
    print("完成。")
