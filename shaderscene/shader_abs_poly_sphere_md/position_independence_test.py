"""
球面多面体位置无关性测试场景

本文件包含多个测试场景来验证修复后的球面多面体 shader 不会因位置改变而改变效果
"""

import sys
import os
import numpy as np

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from manimlib import *
from shadersence.mobject.fixed_spherical_polyhedra import *
# 尝试导入原版（如果存在）
try:
    sys.path.insert(0, os.path.join(current_dir, "manim_project_V1-master_2", "manimgl"))
    from mobject.spherical_polyhedra_sphere import SphericalPolyhedraSphere
except ImportError:
    # 如果原版不存在，创建一个占位符类
    class SphericalPolyhedraSphere:
        def __init__(self, *args, **kwargs):
            pass


class PositionIndependenceTest(Scene):
    """
    测试球面多面体在不同位置时效果的一致性
    """
    def construct(self):
        self.camera.frame.set_height(8)
        
        # 创建标题
        title = Text("位置无关性测试", font_size=32, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.add(title)
        
        # 创建多个修复版本的球体在不同位置
        positions = [
            UP * 2 + LEFT * 3,
            UP * 2 + RIGHT * 3,
            DOWN * 1.5 + LEFT * 3,
            DOWN * 1.5 + RIGHT * 3,
            ORIGIN + LEFT * 0.5,
            ORIGIN + RIGHT * 0.5
        ]
        
        spheres = []
        for i, pos in enumerate(positions):
            sphere = FixedSphericalPolyhedraSphere(
                radius=1.0,
                brightness=20,
                resolution=(60, 60)
            )
            sphere.move_to(pos)
            sphere.set_opacity(0.8)
            spheres.append(sphere)
        
        # 添加所有球体
        self.add(*spheres)
        
        # 添加说明文字
        explanation = Text(
            "这些球体在不同位置，但 shader 效果应该保持一致",
            font_size=20,
            color=WHITE
        )
        explanation.to_edge(DOWN, buff=0.3)
        self.add(explanation)
        
        # 等待观察
        self.wait(10)
        
        # 添加移动动画来进一步测试
        move_text = Text("测试移动时效果的稳定性", font_size=24, color=GREEN)
        move_text.to_edge(DOWN, buff=0.3)
        self.play(Transform(explanation, move_text))
        
        # 创建复杂的移动模式
        self.play(
            spheres[0].animate.move_to(UP * 3 + RIGHT * 2),
            spheres[1].animate.move_to(DOWN * 2 + LEFT * 4),
            spheres[2].animate.move_to(UP * 1 + LEFT * 1),
            spheres[3].animate.move_to(DOWN * 3 + RIGHT * 1),
            spheres[4].animate.move_to(UP * 2),
            spheres[5].animate.move_to(DOWN * 1),
            run_time=3
        )
        
        self.wait(5)
        
        # 测试大范围移动
        self.play(
            *[sphere.animate.move_to(
                np.array([
                    np.random.uniform(-4, 4),
                    np.random.uniform(-3, 3),
                    0
                ])
            ) for sphere in spheres],
            run_time=4
        )
        
        self.wait(5)


class ComparisonTest(Scene):
    """
    对比修复前后的效果
    """
    def construct(self):
        self.camera.frame.set_height(6)
        
        # 添加标题
        title = Text("修复前后对比测试", font_size=36, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.add(title)
        
        # 左侧标签：修复前
        old_label = Text("原版 (位置相关)", font_size=24, color=RED)
        old_label.move_to(LEFT * 3 + UP * 2)
        
        # 右侧标签：修复后
        new_label = Text("修复版 (位置无关)", font_size=24, color=GREEN)
        new_label.move_to(RIGHT * 3 + UP * 2)
        
        self.add(old_label, new_label)
        
        # 创建原版球体（如果可用）
        try:
            original_sphere = SphericalPolyhedraSphere(
                radius=1.2,
                brightness=20,
                resolution=(50, 50)
            )
            original_sphere.move_to(LEFT * 3)
        except Exception as e:
            # 如果原版不可用，创建一个占位符
            original_sphere = Sphere(radius=1.2, color=RED)
            original_sphere.move_to(LEFT * 3)
            warning = Text("原版不可用", font_size=16, color=RED)
            warning.next_to(original_sphere, DOWN)
            self.add(warning)
        
        # 创建修复版球体
        fixed_sphere = FixedSphericalPolyhedraSphere(
            radius=1.2,
            brightness=20,
            resolution=(50, 50)
        )
        fixed_sphere.move_to(RIGHT * 3)
        
        self.add(original_sphere, fixed_sphere)
        
        # 说明文字
        instruction = Text(
            "观察两个球体在移动时 shader 效果的差异",
            font_size=20,
            color=WHITE
        )
        instruction.to_edge(DOWN, buff=0.3)
        self.add(instruction)
        
        self.wait(3)
        
        # 同步移动测试
        movements = [
            UP * 1.5,
            RIGHT * 1.5,
            DOWN * 2,
            LEFT * 2,
            UP * 0.5,
            ORIGIN + DOWN * 0.5
        ]
        
        for i, movement in enumerate(movements):
            self.play(
                original_sphere.animate.shift(movement),
                fixed_sphere.animate.shift(movement),
                run_time=2
            )
            self.wait(1.5)
        
        self.wait(3)


class MultipleInstanceTest(Scene):
    """
    多实例测试，验证大量球体的性能和一致性
    """
    def construct(self):
        self.camera.frame.set_height(10)
        
        # 标题
        title = Text("多实例一致性测试", font_size=32, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.add(title)
        
        # 创建网格排列的球体
        rows, cols = 4, 5
        spacing = 1.8
        spheres = []
        
        for i in range(rows):
            for j in range(cols):
                x = (j - cols//2) * spacing
                y = (i - rows//2) * spacing
                
                sphere = FixedSphericalPolyhedraSphere(
                    radius=0.6,
                    brightness=15,
                    resolution=(40, 40)
                )
                sphere.move_to([x, y, 0])
                sphere.set_opacity(0.8)
                spheres.append(sphere)
        
        # 逐个添加球体
        for sphere in spheres:
            self.add(sphere)
        
        # 说明文字
        explanation = Text(
            f"创建了 {len(spheres)} 个球体，每个都应显示相同的 shader 效果",
            font_size=18,
            color=WHITE
        )
        explanation.to_edge(DOWN, buff=0.3)
        self.add(explanation)
        
        self.wait(8)
        
        # 随机移动测试
        move_text = Text("随机移动测试", font_size=20, color=GREEN)
        move_text.to_edge(DOWN, buff=0.3)
        self.play(Transform(explanation, move_text))
        
        # 第一轮：随机小幅移动
        self.play(
            *[sphere.animate.shift(
                np.random.uniform(-0.5, 0.5, 3)
            ) for sphere in spheres],
            run_time=3
        )
        
        self.wait(3)
        
        # 第二轮：更大范围的随机移动
        self.play(
            *[sphere.animate.move_to(
                np.array([
                    np.random.uniform(-6, 6),
                    np.random.uniform(-4, 4),
                    np.random.uniform(-1, 1)
                ])
            ) for sphere in spheres],
            run_time=5
        )
        
        self.wait(5)


class AnimationStabilityTest(Scene):
    """
    测试动画过程中效果的稳定性
    """
    def construct(self):
        self.camera.frame.set_height(6)
        
        # 标题
        title = Text("动画稳定性测试", font_size=32, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.add(title)
        
        # 创建一个球体进行各种动画测试
        sphere = FixedSphericalPolyhedraSphere(
            radius=1.5,
            brightness=25,
            resolution=(80, 80)
        )
        sphere.set_opacity(0.9)
        self.add(sphere)
        
        # 说明文字
        explanation = Text(
            "测试各种动画过程中 shader 效果的稳定性",
            font_size=20,
            color=WHITE
        )
        explanation.to_edge(DOWN, buff=0.3)
        self.add(explanation)
        
        self.wait(2)
        
        # 测试1：圆周运动
        test1_text = Text("测试1: 圆周运动", font_size=18, color=BLUE)
        test1_text.to_edge(DOWN, buff=0.3)
        self.play(Transform(explanation, test1_text))
        
        self.play(
            Rotate(sphere, 2*PI, about_point=ORIGIN + UP*2, rate_func=linear),
            run_time=4
        )
        
        self.wait(1)
        
        # 测试2：复杂路径移动
        test2_text = Text("测试2: 复杂路径移动", font_size=18, color=BLUE)
        test2_text.to_edge(DOWN, buff=0.3)
        self.play(Transform(explanation, test2_text))
        
        # 创建8字形路径 - 使用简单的圆形路径替代
        circle_path = Circle(radius=2, color=WHITE, stroke_opacity=0.5)
        self.add(circle_path)
        
        # 沿路径移动 - 使用简单的圆周运动
        self.play(
            Rotate(sphere, 2*PI, about_point=ORIGIN, rate_func=linear),
            run_time=6
        )
        
        self.remove(circle_path)
        self.wait(1)
        
        # 测试3：缩放和旋转组合
        test3_text = Text("测试3: 缩放旋转组合", font_size=18, color=BLUE)
        test3_text.to_edge(DOWN, buff=0.3)
        self.play(Transform(explanation, test3_text))
        
        self.play(
            sphere.animate.scale(1.5).rotate(PI, axis=UP).shift(LEFT*2),
            run_time=3
        )
        
        self.play(
            sphere.animate.scale(0.8).rotate(PI, axis=RIGHT).shift(RIGHT*4),
            run_time=3
        )
        
        self.play(
            sphere.animate.scale(1.2).move_to(ORIGIN),
            run_time=2
        )
        
        self.wait(3)


class StaticPolyhedraShowcase(Scene):
    """
    展示不同类型的静态多面体效果
    """
    def construct(self):
        self.camera.frame.set_height(8)
        
        # 标题
        title = Text("静态多面体效果展示", font_size=32, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.add(title)
        
        # 创建四种不同的多面体
        polyhedra_types = ["dodecahedron", "icosahedron", "cube", "octahedron"]
        polyhedra_names = ["十二面体", "二十面体", "立方体", "八面体"]
        positions = [
            UP + LEFT * 3,
            UP + RIGHT * 3,
            DOWN + LEFT * 3,
            DOWN + RIGHT * 3
        ]
        
        spheres = []
        labels = []
        
        for poly_type, name, pos in zip(polyhedra_types, polyhedra_names, positions):
            # 创建静态多面体
            sphere = FixedStaticPolyhedraSphere(
                polyhedron_type=poly_type,
                radius=1.2,
                brightness=20,
                resolution=(60, 60)
            )
            sphere.move_to(pos)
            sphere.set_opacity(0.9)
            spheres.append(sphere)
            
            # 添加标签
            label = Text(name, font_size=18, color=WHITE)
            label.next_to(sphere, DOWN, buff=0.3)
            labels.append(label)
        
        # 添加所有元素
        for sphere, label in zip(spheres, labels):
            self.add(sphere, label)
        
        # 说明文字
        explanation = Text(
            "四种不同的多面体效果，每种都保持位置无关性",
            font_size=18,
            color=WHITE
        )
        explanation.to_edge(DOWN, buff=0.3)
        self.add(explanation)
        
        self.wait(8)
        
        # 测试移动
        move_text = Text("测试移动时效果保持", font_size=18, color=GREEN)
        move_text.to_edge(DOWN, buff=0.3)
        self.play(Transform(explanation, move_text))
        
        # 交换位置
        self.play(
            spheres[0].animate.move_to(positions[2]),
            spheres[1].animate.move_to(positions[3]),
            spheres[2].animate.move_to(positions[0]),
            spheres[3].animate.move_to(positions[1]),
            labels[0].animate.next_to(spheres[0].get_center() + DOWN*1.5, DOWN, buff=0),
            labels[1].animate.next_to(spheres[1].get_center() + DOWN*1.5, DOWN, buff=0),
            labels[2].animate.next_to(spheres[2].get_center() + UP*1.5, UP, buff=0),
            labels[3].animate.next_to(spheres[3].get_center() + UP*1.5, UP, buff=0),
            run_time=4
        )
        
        self.wait(5)


if __name__ == "__main__":
    # 运行测试场景
    print("开始运行球面多面体位置无关性测试...")
    print("\\n可用的测试场景：")
    print("1. PositionIndependenceTest - 基本位置无关性测试")
    print("2. ComparisonTest - 修复前后对比测试")
    print("3. MultipleInstanceTest - 多实例一致性测试")
    print("4. AnimationStabilityTest - 动画稳定性测试")
    print("5. StaticPolyhedraShowcase - 静态多面体展示")
    print("\\n运行示例：")
    print("manimgl position_independence_test.py PositionIndependenceTest")
