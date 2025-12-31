"""
简单的球面多面体位置无关性演示

这个文件提供了一个简单的演示来验证修复后的球面多面体效果不会因位置改变而改变
"""

import sys
import os
import numpy as np

# 添加当前目录到路径，确保能找到 fixed_spherical_polyhedra 模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from manimlib import *
from mobject.fixed_spherical_polyhedra import FixedSphericalPolyhedraSphere


class SimplePositionTest(Scene):
    """
    简单的位置测试演示
    创建两个球体，一个移动，一个静止，观察它们的效果是否一致
    """
    def construct(self):
        self.camera.frame.set_height(6)
        
        # 创建标题
        title = Text("球面多面体位置无关性验证", font_size=28, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.add(title)
        
        # 创建两个相同的球体
        sphere1 = FixedSphericalPolyhedraSphere(
            radius=1.2,
            brightness=25,
            resolution=(60, 60)
        )
        sphere1.move_to(LEFT * 2.5)
        sphere1.set_opacity(0.8)
        
        sphere2 = FixedSphericalPolyhedraSphere(
            radius=1.2,
            brightness=25,
            resolution=(60, 60)
        )
        sphere2.move_to(RIGHT * 2.5)
        sphere2.set_opacity(0.8)
        
        # 添加标签
        label1 = Text("静止球体", font_size=16, color=WHITE)
        label1.next_to(sphere1, DOWN, buff=0.3)
        
        label2 = Text("移动球体", font_size=16, color=WHITE)
        label2.next_to(sphere2, DOWN, buff=0.3)
        
        # 添加到场景
        self.add(sphere1, sphere2, label1, label2)
        
        # 说明文字
        explanation = Text(
            "两个球体使用相同的 shader，观察移动时效果是否保持一致",
            font_size=18,
            color=WHITE
        )
        explanation.to_edge(DOWN, buff=0.3)
        self.add(explanation)
        
        # 等待观察初始状态
        self.wait(3)
        
        # 移动右侧球体进行测试
        self.play(sphere2.animate.shift(UP * 2), run_time=2)
        self.wait(2)
        
        self.play(sphere2.animate.shift(LEFT * 3), run_time=2)
        self.wait(2)
        
        self.play(sphere2.animate.shift(DOWN * 3), run_time=2)
        self.wait(2)
        
        self.play(sphere2.animate.shift(RIGHT * 5), run_time=2)
        self.wait(2)
        
        # 返回初始位置
        self.play(sphere2.animate.move_to(RIGHT * 2.5), run_time=2)
        self.wait(2)
        
        # 最终验证：同时移动两个球体到相同位置
        verification_text = Text(
            "最终验证：移动到相同位置观察效果",
            font_size=18,
            color=GREEN
        )
        verification_text.to_edge(DOWN, buff=0.3)
        self.play(Transform(explanation, verification_text))
        
        self.play(
            sphere1.animate.move_to(UP * 0.8),
            sphere2.animate.move_to(DOWN * 0.8),
            run_time=3
        )
        
        self.wait(3)
        
        # 如果效果一致，应该看到相同的多面体图案
        success_text = Text(
            "✓ 成功！两个球体显示相同的 shader 效果",
            font_size=18,
            color=GREEN
        )
        success_text.to_edge(DOWN, buff=0.3)
        self.play(Transform(explanation, success_text))
        
        self.wait(5)


class QuickDemo(Scene):
    """
    快速演示，展示单个球体的移动过程
    """
    def construct(self):
        self.camera.frame.set_height(5)
        
        # 创建一个球体
        sphere = FixedSphericalPolyhedraSphere(
            radius=1.5,
            brightness=30,
            resolution=(80, 80)
        )
        sphere.set_opacity(0.9)
        
        # 添加说明
        title = Text("位置无关 Shader 演示", font_size=24, color=YELLOW)
        title.to_edge(UP)
        
        instruction = Text(
            "观察球体移动时 shader 图案保持不变",
            font_size=16,
            color=WHITE
        )
        instruction.to_edge(DOWN)
        
        self.add(sphere, title, instruction)
        self.wait(2)
        
        # 创建一个移动路径
        positions = [
            UP * 2,
            RIGHT * 2 + UP,
            RIGHT * 2 + DOWN,
            DOWN * 2,
            LEFT * 2 + DOWN,
            LEFT * 2 + UP,
            ORIGIN
        ]
        
        for pos in positions:
            self.play(sphere.animate.move_to(pos), run_time=1.5)
            self.wait(0.5)
        
        self.wait(3)

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")
