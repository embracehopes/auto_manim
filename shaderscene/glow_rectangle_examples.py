"""
GlowFlashRectangle 使用示例
展示智能发光矩形的各种用法
"""

import os
import sys

# 添加路径

sys.path.insert(0,  os.path.dirname(os.path.abspath(__file__)))

from manimlib import *
from mobject.GlowFlashRectangle import GlowFlashRectangle, PresetGlowRectangles


class GlowRectangleDemo(Scene):
    def construct(self):
        # === 示例1: 基础用法 ===
        basic_rect = GlowFlashRectangle(
            width=4, height=4, corner_radius=2,
            num_points=5, color_scheme="dark", rate_function=overshoot
        )
        
        self.add(basic_rect)
        
        # 循环播放动画
        basic_rect.start_animation(self, loop=True)


class MultipleRectanglesDemo(Scene):
    def construct(self):
        # === 示例2: 多个矩形同时显示 ===
        
        # 小型霓虹矩形（左上）
        small_neon = PresetGlowRectangles.neon_small()
        small_neon.shift(UP * 2 + LEFT * 3)
        
        # 中型明亮矩形（右上）
        medium_bright = PresetGlowRectangles.bright_medium() 
        medium_bright.shift(UP * 2 + RIGHT * 2)
        
        # 大型深色矩形（中央下方）
        large_dark = PresetGlowRectangles.dark_large()
        large_dark.shift(DOWN * 1.5)
        large_dark.scale(0.6)  # 缩小以适应屏幕
        
        # 添加到场景
        self.add(small_neon, medium_bright, large_dark)
        
        # 同时播放所有动画
        all_anims = AnimationGroup(
            small_neon.get_animation_group(),
            medium_bright.get_animation_group(), 
            large_dark.get_animation_group()
        )
        
        while True:
            self.play(all_anims)
            self.wait(0.1)


class CustomizedDemo(Scene):
    def construct(self):
        # === 示例3: 高度自定义 ===
        
        # 自定义颜色方案
        custom_colors = [
            "#FF69B4", "#FF1493", "#DC143C", "#B22222",
            "#FF4500", "#FF8C00", "#FFD700", "#FFFF00",
            "#ADFF2F", "#32CD32", "#00FF7F", "#00CED1",
            "#1E90FF", "#0000FF", "#8A2BE2", "#FF69B4"
        ]
        
        custom_rect = GlowFlashRectangle(
            width=10, height=6, corner_radius=1.2,
            num_points=16,  # 更多点
            dot_radius=0.015,  # 更小的点
            color_scheme=custom_colors,
            tail_length=60,  # 更长的轨迹
            tail_lifetime=4.0,  # 更长的生命周期
            glow_factor=4.0,  # 更强的辉光
            speed=10.0,  # 更慢的速度
            rate_function=smooth,  # 平滑动画
            opacity_fade=(1.0, 0.0),
            width_fade=(0.1, 0.01),
            show_dots=True,
            show_rectangle=False
        )
        
        self.add(custom_rect)
        custom_rect.start_animation(self, loop=True, loop_delay=0.05)


class InteractiveDemo(Scene):
    def construct(self):
        # === 示例4: 交互式演示 ===
        
        rect = GlowFlashRectangle(
            width=8, height=5, corner_radius=0.8,
            num_points=10, color_scheme="dark"
        )
        
        self.add(rect)
        
        # 动态改变颜色方案演示
        color_schemes = ["dark", "bright", "neon"]
        
        for scheme in color_schemes:
            # 更新颜色方案
            rect.update_colors(scheme)
            
            # 播放一轮动画
            self.play(rect.get_animation_group())
            self.wait(0.5)
        
        # 最后循环播放
        while True:
            self.play(rect.get_animation_group())
            self.wait(0.1)


class SimpleLoopDemo(Scene):
    """最简单的无限循环示例"""
    def construct(self):
        # 创建发光矩形
        glow_rect = GlowFlashRectangle(width=12, height=8,num_points=4,corner_radius=3.5)
        
        # 添加到场景
        self.add(glow_rect)
        TracingTail
        
        # 开始无限循环动画
        self.play(*glow_rect.animations,run_time=5)
        #add和start_animation的位置不能交换


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py SimpleLoopDemo  ")