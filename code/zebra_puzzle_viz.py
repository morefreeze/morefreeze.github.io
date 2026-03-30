#!/usr/bin/env python3
"""Generate SVG visualization for zebra puzzle solution."""

solution = {
    0: {'nationality': 'Norwegian', 'job': 'Diplomat', 'pet': 'Fox', 'drink': 'Water', 'color': 'Yellow', 'highlight': 'drinks WATER'},
    1: {'nationality': 'Ukrainian', 'job': 'Nurse', 'pet': 'Horse', 'drink': 'Tea', 'color': 'Blue', 'highlight': None},
    2: {'nationality': 'English', 'job': 'Sculptor', 'pet': 'Snails', 'drink': 'Milk', 'color': 'Red', 'highlight': None},
    3: {'nationality': 'Spanish', 'job': 'Violinist', 'pet': 'Dog', 'drink': 'Orange Juice', 'color': 'White', 'highlight': None},
    4: {'nationality': 'Japanese', 'job': 'Painter', 'pet': 'ZEBRA', 'drink': 'Coffee', 'color': 'Green', 'highlight': 'owns ZEBRA'},
}

color_map = {
    'Yellow': '#F4D03F',
    'Blue': '#3498DB',
    'Red': '#E74C3C',
    'White': '#ECF0F1',
    'Green': '#2ECC71',
}

svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 320">
<style>
  .title { font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; text-anchor: middle; }
  .house-num { font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; text-anchor: middle; }
  .attr-text { font-family: Arial, sans-serif; font-size: 13px; text-anchor: middle; }
  .attr-text-highlight { font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; text-anchor: middle; }
  .color-text { font-family: Arial, sans-serif; font-size: 11px; font-style: italic; text-anchor: middle; }
  .highlight-label { font-family: Arial, sans-serif; font-size: 12px; font-weight: bold; text-anchor: middle; fill: #E74C3C; }
  .house-box { stroke: #333; stroke-width: 2; rx: 8; ry: 8; }
  .house-box-highlight { stroke: #E74C3C; stroke-width: 4; rx: 8; ry: 8; }
  .attr-box { fill: white; opacity: 0.85; rx: 4; ry: 4; }
  .highlight-box { fill: #E74C3C; opacity: 0.2; rx: 4; ry: 4; stroke: #E74C3C; stroke-width: 2; }
</style>

<!-- Background -->
<rect width="900" height="320" fill="white"/>

<!-- Title -->
<text x="450" y="35" class="title">Who Owns the Zebra? — The Solution</text>

'''

house_width = 160
house_height = 140
start_x = 35
start_y = 60
gap = 15

for i in range(5):
    x = start_x + i * (house_width + gap)
    y = start_y
    house_color = color_map[solution[i]['color']]
    is_highlight = solution[i]['highlight'] is not None
    box_class = 'house-box-highlight' if is_highlight else 'house-box'

    # House body
    svg_content += f'''<!-- House {i+1} -->
<rect x="{x}" y="{y}" width="{house_width}" height="{house_height}" fill="{house_color}" class="{box_class}"/>

<!-- House number -->
<text x="{x + house_width//2}" y="{y - 8}" class="house-num">House {i+1}</text>

'''

    # Attributes
    attrs = [
        ('Nationality', solution[i]['nationality']),
        ('Job', solution[i]['job']),
        ('Pet', solution[i]['pet']),
        ('Drink', solution[i]['drink']),
    ]

    for j, (label, attr) in enumerate(attrs):
        attr_y = y + 25 + j * 32

        # Highlight zebra and water
        is_attr_highlight = (solution[i]['highlight'] == 'owns ZEBRA' and label == 'Pet') or \
                           (solution[i]['highlight'] == 'drinks WATER' and label == 'Drink')

        if is_attr_highlight:
            svg_content += f'''<rect x="{x + 6}" y="{attr_y - 15}" width="{house_width - 12}" height="26" class="highlight-box"/>
<text x="{x + house_width//2}" y="{attr_y + 5}" class="attr-text-highlight">{attr}</text>
'''
        else:
            svg_content += f'''<rect x="{x + 8}" y="{attr_y - 14}" width="{house_width - 16}" height="24" class="attr-box"/>
<text x="{x + house_width//2}" y="{attr_y + 4}" class="attr-text">{attr}</text>
'''

    # Color label
    svg_content += f'<text x="{x + house_width//2}" y="{y + house_height + 12}" class="color-text" fill="#555">{solution[i]["color"]}</text>\n\n'

    # Highlight label below house
    if is_highlight:
        svg_content += f'<text x="{x + house_width//2}" y="{y + house_height + 28}" class="highlight-label">← {solution[i]["highlight"]}</text>\n\n'

svg_content += '</svg>'

output_path = '/Users/bytedance/mygit/morefreeze.github.io/images/zebra-puzzle-solution.svg'
with open(output_path, 'w') as f:
    f.write(svg_content)

print(f"Saved to {output_path}")
