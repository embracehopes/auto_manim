"""
AutoScene 增强功能演示

演示内容：
1. highlight_text - 多种随机高亮效果
2. annotate_region - 区域标注覆盖
3. camera_focus - 动态相机聚焦
4. add_fixed_* - 固定方向元素

运行方法：
    cd E:\\auto_manim\\new_class\\demo
    manimgl enhancement_demo.py AutoSceneEnhancementDemo -w
"""

import os
import sys
import random
import numpy as np

# 添加父目录到路径以导入 AutoScene
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from auto_scene import AutoScene
from manimlib import (
    Text, Write, FadeIn, FadeOut, ShowCreation, VGroup,
    YELLOW, RED, BLUE, GREEN, WHITE, DEGREES
)


class AutoSceneEnhancementDemo(AutoScene):
    """
    AutoScene 增强功能演示
    
    演示内容：
    1. highlight_text - 多种随机高亮效果
    2. annotate_region - 区域标注覆盖
    3. camera_focus - 动态相机聚焦
    4. add_fixed_* - 固定方向元素
    """
    
    def construct(self):
        self.enable_debug(True)
        
        # === 1. 测试文本高亮 ===
        self._test_highlight()
        
        # === 2. 测试区域标注 ===
        self._test_annotate()
        
        # === 3. 测试相机聚焦 ===
        self._test_camera_focus()
        
        # === 4. 测试固定方向元素 ===
        self._test_fixed_elements()
        
        self.wait(2)
    
    def _test_highlight(self):
        """测试高亮效果"""
        from manimlib import Tex
        
        title = Text("文本高亮演示", font="STKaiti", font_size=36, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.5)
        
        # 创建测试公式
        formula = Tex(r"E = mc^2 + \frac{1}{2}mv^2", font_size=48)
        self.play(Write(formula), run_time=1)
        
        # 随机高亮效果演示（多次调用展示不同效果）
        for i in range(3):
            decoration = self.highlight_text(formula, effect="random")
            self.wait(0.5)
            if decoration:
                self.remove_highlight(decoration)
        
        self.play(FadeOut(formula), FadeOut(title), run_time=0.5)
    
    def _test_annotate(self):
        """测试区域标注"""
        title = Text("区域标注演示", font="STKaiti", font_size=36, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.5)
        
        # 创建一些图形
        from manimlib import Circle, Square
        circle = Circle(radius=1, color=BLUE).shift(LEFT * 2)
        square = Square(side_length=1.5, color=RED).shift(RIGHT * 2)
        
        self.play(ShowCreation(circle), ShowCreation(square), run_time=1)
        
        # 标注圆形
        ann1 = self.annotate_region(circle, "这是圆形", bg_color=BLUE)
        self.wait(1)
        self.remove_annotation(ann1)
        
        # 标注方形
        ann2 = self.annotate_region(square, "这是方形", bg_color=RED)
        self.wait(1)
        self.remove_annotation(ann2)
        
        self.play(FadeOut(circle), FadeOut(square), FadeOut(title), run_time=0.5)
    
    def _test_camera_focus(self):
        """测试相机聚焦"""
        title = Text("相机聚焦演示", font="STKaiti", font_size=36, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.5)
        
        # 创建多个元素
        from manimlib import Dot
        dots = VGroup(*[
            Dot(color=random.choice([RED, BLUE, GREEN, YELLOW]))
            .move_to(np.array([
                random.uniform(-5, 5),
                random.uniform(-3, 3),
                0
            ]))
            for _ in range(10)
        ])
        
        self.play(FadeIn(dots), run_time=0.5)
        
        # 聚焦到某个点
        target_dot = dots[0]
        target_dot.set_color(WHITE).scale(2)
        
        self.camera_focus(target_dot, zoom_factor=3.0, hold_time=2.0)
        
        self.play(FadeOut(dots), FadeOut(title), run_time=0.5)
    
    def _test_fixed_elements(self):
        """测试固定方向元素"""
        # 添加固定标题
        fixed_title = self.add_fixed_title("固定标题演示", color=YELLOW)
        self.add(fixed_title)
        self.play(Write(fixed_title), run_time=0.5)
        
        # 添加固定字幕
        fixed_sub = self.add_fixed_subtitle("这是固定在屏幕底部的字幕")
        self.add(fixed_sub)
        self.play(Write(fixed_sub), run_time=0.5)
        
        # 创建 3D 场景元素（模拟）
        from manimlib import Sphere, Cube
        
        # 设置相机角度（模拟 3D）
        self.camera.frame.set_euler_angles(theta=-30 * DEGREES, phi=60 * DEGREES)
        
        sphere = Sphere(radius=0.8).shift(LEFT * 2)
        cube = Cube(side_length=1.2).shift(RIGHT * 2)
        
        self.play(ShowCreation(sphere), ShowCreation(cube), run_time=1)
        
        # 为 3D 对象添加固定方向标注
        sphere_label = self.add_fixed_annotation(sphere, "球体", direction=DOWN)
        cube_label = self.add_fixed_annotation(cube, "立方体", direction=DOWN)
        
        self.add(sphere_label, cube_label)
        
        # 旋转相机，观察标签始终朝向观众
        self.play(
            self.camera.frame.animate.set_euler_angles(theta=30 * DEGREES, phi=60 * DEGREES),
            run_time=3
        )
        
        self.wait(1)


if __name__ == "__main__":
    os.system(f"cd {script_dir} && manimgl enhancement_demo.py AutoSceneEnhancementDemo")
