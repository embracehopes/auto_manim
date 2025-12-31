#!/usr/bin/env python3
"""调试颜色问题的脚本"""

from manimlib.constants import RED, BLUE, GREEN, YELLOW, WHITE
import numpy as np

def debug_colors():
    print("=== 调试颜色数组 ===")
    colors = [RED, BLUE, GREEN, YELLOW]
    
    for i, color in enumerate(colors):
        print(f"colors[{i}] = {color}")
        print(f"  类型: {type(color)}")
        if hasattr(color, 'shape'):
            print(f"  形状: {color.shape}")
        print(f"  值: {np.array(color)}")
        print()

    print("=== 测试 base_color 设置 ===")
    for i in range(4):
        selected_color = colors[i % len(colors)]
        print(f"i={i}, selected_color = {selected_color}")

if __name__ == "__main__":
    debug_colors()
