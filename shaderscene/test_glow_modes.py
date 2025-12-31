"""
测试 GlowWrapperEffect 的两种渲染模式

- render_mode="line": 使用连续线段渲染，产生平滑的辉光效果
- render_mode="point": 使用离散点渲染，可能有明显的辉光点痕迹

运行方式:
    manimgl test_glow_modes.py GlowModeComparison
"""

from manimlib import *
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mobject.glow_wrapper import GlowWrapperEffect, GlowLineStrip


class GlowModeComparison(Scene):
    """比较两种渲染模式"""
    
    def construct(self):
        # 创建测试对象
        circle = Circle(radius=1.5).set_stroke(BLUE, 3)
        square = Square(side_length=2.5).set_stroke(RED, 3)
        
        # 左侧：线段模式（推荐）
        circle.move_to(LEFT * 3)
        glow_line = GlowWrapperEffect(
            circle,
            color=BLUE,
            size=0.2,
            glow_factor=2.5,
            render_mode="line",  # 连续线段
        )
        label_line = Text("Line Mode (推荐)", font_size=24).next_to(circle, DOWN, buff=0.5)
        
        # 右侧：点云模式
        square.move_to(RIGHT * 3)
        glow_point = GlowWrapperEffect(
            square,
            color=RED,
            size=0.2,
            glow_factor=2.5,
            render_mode="point",  # 离散点
        )
        label_point = Text("Point Mode", font_size=24).next_to(square, DOWN, buff=0.5)
        
        # 标题
        title = Text("GlowWrapperEffect 渲染模式对比", font_size=36).to_edge(UP)
        
        self.add(title)
        self.add(circle, glow_line, label_line)
        self.add(square, glow_point, label_point)
        
        self.wait(3)


class GlowLineDemo(Scene):
    """演示线段模式的连续辉光效果"""
    
    def construct(self):
        # 创建多种形状
        shapes = VGroup(
            Circle(radius=1),
            Square(side_length=1.8),
            RegularPolygon(n=6, circumscribed_circle_radius=1),
         
        ).arrange_in_grid(rows=2, cols=2, buff=1.5)
        
        colors = [BLUE, RED, GREEN, YELLOW]
        
        # 为每个形状添加辉光
        glows = VGroup()
        for shape, color in zip(shapes, colors):
            shape.set_stroke(color, 2)
            glow = GlowWrapperEffect(
                shape,
                color=color,
                size=0.15,
                glow_factor=2.0,
                render_mode="line",
            )
            glows.add(glow)
        
        title = Text("Line Mode 连续辉光效果", font_size=36).to_edge(UP)
        
        self.add(title, shapes, glows)
        
        # 动画：改变辉光属性
        self.wait(1)
        
        # 改变大小
        for glow in glows:
            glow.set(size=0.3)
        self.wait(1)
        
        # 改变颜色
        for glow in glows:
            glow.mix(WHITE, factor=0.5)
        self.wait(1)


class GlowCurveDemo(Scene):
    """演示曲线的辉光效果"""
    
    def construct(self):
        # 创建一条复杂曲线
        curve = ParametricCurve(
            lambda t: np.array([
                3 * np.cos(t),
                2 * np.sin(2 * t),
                0
            ]),
            t_range=[0, TAU, 0.01],
        ).set_stroke(TEAL, 2)
        
        
        title = Tex(r"曲线辉光效果", font_size=36).to_edge(UP)
        glow = GlowLineStrip(
            title.get_points(),
            colors=TEAL,

        )
        
        self.add(title, curve, glow)
        self.wait(2)
        
        # # 动态改变
        # self.play(
        #     UpdateFromAlphaFunc(
        #         glow,
        #         lambda m, a: m.set(size=0.1 + 0.3 * np.sin(a * TAU) ** 2)
        #     ),
        #     run_time=3,
        # )


class MultiShapeGlow(Scene):
    """多形状辉光组合"""
    
    def construct(self):
        # 创建一组嵌套的形状
        shapes = VGroup()
        for i, r in enumerate([0.5, 1.0, 1.5, 2.0]):
            shape = Circle(radius=r).set_stroke(
                color_gradient([BLUE, PURPLE, RED], i / 3),
                width=2
            )
            shapes.add(shape)
        
        # 为所有形状添加辉光
        glow = GlowWrapperEffect(
            shapes,
            color=BLUE,
            size=0.15,
            glow_factor=2.5,
            render_mode="line",
            color_scheme="neon",  # 使用渐变色
        )
        
        title = Text("多形状辉光", font_size=36).to_edge(UP)
        
        self.add(title, shapes, glow)
        self.wait(3)


if __name__ == "__main__":
    import subprocess
    subprocess.run(["manimgl", __file__, "GlowCurveDemo"])
