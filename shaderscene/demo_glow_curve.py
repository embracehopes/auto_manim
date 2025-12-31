"""
GlowCurve 演示文件
展示各种辉光曲线的效果和用法
"""

from manimlib import *
import numpy as np
import sys
from pathlib import Path

# 添加 shaderscene 到路径
_this = Path(__file__).resolve()
for parent in _this.parents:
    if (parent / 'shaderscene').exists():
        sys.path.insert(0, str(parent))
        break

from shaderscene.mobject.glow_curve import (
    GlowCurve,
    GlowFunctionGraph,
    GlowCircle,
    GlowSpiral,
    GlowSin,
)


class BasicGlowCurveDemo(Scene):
    """基础辉光曲线演示"""
    
    def construct(self):
        # 标题
        title = Text("辉光曲线演示", font="Microsoft YaHei", font_size=48)
        title.to_edge(UP)
        title.fix_in_frame()
        
        self.add(title)
        self.wait(0.5)
        
        # 1. 正弦曲线
        sin_curve = GlowFunctionGraph(
            function=np.sin,
            x_range=(-TAU, TAU),
            n_samples=200,
            color=BLUE,
            glow_width=0.2,
            glow_factor=2.5,
        )
        sin_curve.shift(UP * 2)
        
        sin_label = Text("y = sin(x)", font_size=24)
        sin_label.next_to(sin_curve, RIGHT)
        sin_label.fix_in_frame()
        
        self.play(ShowCreation(sin_curve), run_time=2)
        self.play(FadeIn(sin_label))
        self.wait()
        
        # 2. 余弦曲线
        cos_curve = GlowFunctionGraph(
            function=np.cos,
            x_range=(-TAU, TAU),
            n_samples=200,
            color=RED,
            glow_width=0.18,
            glow_factor=3.0,
        )
        
        cos_label = Text("y = cos(x)", font_size=24)
        cos_label.next_to(cos_curve, RIGHT)
        cos_label.fix_in_frame()
        
        self.play(ShowCreation(cos_curve), run_time=2)
        self.play(FadeIn(cos_label))
        self.wait()
        
        # 3. 二次函数
        quad_curve = GlowFunctionGraph(
            function=lambda x: 0.3 * x**2,
            x_range=(-3, 3),
            n_samples=150,
            color=GREEN,
            glow_width=0.15,
            glow_factor=2.0,
        )
        quad_curve.shift(DOWN * 2)
        
        quad_label = Text("y = 0.3x²", font_size=24)
        quad_label.next_to(quad_curve, RIGHT)
        quad_label.fix_in_frame()
        
        self.play(ShowCreation(quad_curve), run_time=2)
        self.play(FadeIn(quad_label))
        self.wait(2)
        
        # 清理
        self.play(
            FadeOut(sin_curve),
            FadeOut(cos_curve),
            FadeOut(quad_curve),
            FadeOut(sin_label),
            FadeOut(cos_label),
            FadeOut(quad_label),
        )


class ParametricCurvesDemo(Scene):
    """参数化曲线演示"""
    
    def construct(self):
        title = Text("参数化辉光曲线", font="Microsoft YaHei", font_size=48)
        title.to_edge(UP)
        title.fix_in_frame()
        
        self.add(title)
        self.wait(0.5)
        
        # 1. 圆形
        circle = GlowCircle(
            radius=2.0,
            n_samples=100,
            color=YELLOW,
            glow_width=0.25,
            glow_factor=2.5,
        )
        
        circle_label = Text("圆形", font="Microsoft YaHei", font_size=32)
        circle_label.next_to(circle, DOWN)
        circle_label.fix_in_frame()
        
        self.play(ShowCreation(circle), run_time=2)
        self.play(FadeIn(circle_label))
        self.wait()
        
        # 2. 螺旋线
        spiral = GlowSpiral(
            a=0.3,
            b=0.15,
            n_samples=300,
            color=PURPLE,
            glow_width=0.2,
            glow_factor=3.0,
        )
        
        spiral_label = Text("螺旋线", font="Microsoft YaHei", font_size=32)
        spiral_label.to_edge(DOWN)
        spiral_label.fix_in_frame()
        
        self.play(
            FadeOut(circle),
            FadeOut(circle_label),
        )
        self.play(ShowCreation(spiral), run_time=3)
        self.play(FadeIn(spiral_label))
        self.wait(2)
        
        # 3. 李萨如图形（Lissajous）
        lissajous = GlowCurve(
            function=lambda t: np.array([
                2 * np.sin(3 * t),
                2 * np.sin(2 * t),
                0
            ], dtype=np.float32),
            t_range=(0, TAU),
            n_samples=300,
            color=TEAL,
            glow_width=0.2,
            glow_factor=2.8,
        )
        
        lissa_label = Text("李萨如图形", font="Microsoft YaHei", font_size=32)
        lissa_label.to_edge(DOWN)
        lissa_label.fix_in_frame()
        
        self.play(
            FadeOut(spiral),
            Transform(spiral_label, lissa_label),
        )
        self.play(ShowCreation(lissajous), run_time=3)
        self.wait(2)


class AnimatedGlowCurveDemo(Scene):
    """动画辉光曲线演示"""
    
    def construct(self):
        title = Text("动态辉光曲线", font="Microsoft YaHei", font_size=48)
        title.to_edge(UP)
        title.fix_in_frame()
        
        self.add(title)
        self.wait(0.5)
        
        # 创建一个可以动态变化的曲线
        freq_tracker = ValueTracker(1)
        
        def get_curve():
            freq = freq_tracker.get_value()
            return GlowFunctionGraph(
                function=lambda x: np.sin(freq * x),
                x_range=(-TAU, TAU),
                n_samples=200,
                color=interpolate_color(BLUE, RED, (freq - 1) / 4),
                glow_width=0.2,
                glow_factor=2.5,
            )
        
        curve = always_redraw(get_curve)
        
        freq_label = always_redraw(lambda: Text(
            f"频率: {freq_tracker.get_value():.1f}",
            font="Microsoft YaHei",
            font_size=32
        ).to_edge(DOWN).fix_in_frame())
        
        self.add(curve, freq_label)
        self.wait()
        
        # 动画改变频率
        self.play(
            freq_tracker.animate.set_value(5),
            run_time=4,
            rate_func=smooth
        )
        self.wait()
        
        self.play(
            freq_tracker.animate.set_value(1),
            run_time=3,
            rate_func=smooth
        )
        self.wait(2)


class ColorfulGlowCurvesDemo(Scene):
    """多彩辉光曲线演示"""
    
    def construct(self):
        title = Text("多彩辉光曲线", font="Microsoft YaHei", font_size=48)
        title.to_edge(UP)
        title.fix_in_frame()
        
        self.add(title)
        self.wait(0.5)
        
        # 创建多条不同颜色的曲线
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        curves = Group()
        
        for i, color in enumerate(colors):
            phase = i * TAU / len(colors)
            curve = GlowFunctionGraph(
                function=lambda x, p=phase: 0.5 * np.sin(x + p),
                x_range=(-TAU, TAU),
                n_samples=1000,
                color=color,
                glow_width=0.4,
                glow_factor=5,
            )
            curves.add(curve)
        
        # 依次显示曲线
        for curve in curves:
            self.play(ShowCreation(curve), run_time=0.8)
        
        self.wait()
        
        # 所有曲线一起移动
        self.play(
            curves.animate.shift(UP * 2),
            run_time=1.5
        )
        self.play(
            curves.animate.shift(DOWN * 4),
            run_time=1.5
        )
        self.play(
            curves.animate.shift(UP * 2),
            run_time=1.5
        )
        
        self.wait(2)


class ComplexShapesDemo(Scene):
    """复杂形状演示"""
    
    def construct(self):
        title = Text("复杂辉光曲线", font="Microsoft YaHei", font_size=48)
        title.to_edge(UP)
        title.fix_in_frame()
        
        self.add(title)
        self.wait(0.5)
        
        # 心形曲线
        heart = GlowCurve(
            function=lambda t: np.array([
                2 * (16 * np.sin(t)**3),
                2 * (13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)),
                0
            ], dtype=np.float32) / 20,
            t_range=(0, TAU),
            n_samples=300,
            color=RED,
            glow_width=0.2,
            glow_factor=2.5,
        )
        
        heart_label = Text("心形", font="Microsoft YaHei", font_size=32)
        heart_label.next_to(heart, DOWN, buff=0.5)
        heart_label.fix_in_frame()
        
        self.play(ShowCreation(heart), run_time=3)
        self.play(FadeIn(heart_label))
        self.wait(2)
        
        # 玫瑰线
        rose = GlowCurve(
            function=lambda t: np.array([
                2 * np.cos(4 * t) * np.cos(t),
                2 * np.cos(4 * t) * np.sin(t),
                0
            ], dtype=np.float32),
            t_range=(0, TAU),
            n_samples=400,
            color=PINK,
            glow_width=0.18,
            glow_factor=3.0,
        )
        
        rose_label = Text("玫瑰线", font="Microsoft YaHei", font_size=32)
        rose_label.to_edge(DOWN)
        rose_label.fix_in_frame()
        
        self.play(
            FadeOut(heart),
            Transform(heart_label, rose_label),
        )
        self.play(ShowCreation(rose), run_time=3)
        self.wait(2)


if __name__ == "__main__":
    # 运行演示
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    
    # 可以选择运行不同的场景
    # os.system(f"cd {script_dir} && manimgl {script_name}.py BasicGlowCurveDemo")
    # os.system(f"cd {script_dir} && manimgl {script_name}.py ParametricCurvesDemo")
    # os.system(f"cd {script_dir} && manimgl {script_name}.py AnimatedGlowCurveDemo")
    # os.system(f"cd {script_dir} && manimgl {script_name}.py ColorfulGlowCurvesDemo")
    os.system(f"cd {script_dir} && manimgl {script_name}.py ColorfulGlowCurvesDemo")
