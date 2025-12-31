#!/usr/bin/env python3
"""
辉光线条 (GlowLine) Demo

演示如何使用辉光线条 Mobject 创建各种辉光效果
"""
#把
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from manimlib import *
from mobject.glow_line import *


class GlowLineDemo(Scene):
    """辉光线条演示场景"""

    def construct(self):
        # 演示1: 基本辉光线条
        self.demo_basic_glow_line()

        # 清除场景
        self.clear()

        # 演示2: 多段辉光线条
        self.demo_multi_glow_line()

        # 清除场景
        

        # 演示3: 辉光路径
        self.demo_glow_path()

        # 清除场景
        self.clear()

        # 演示4: 动画效果
        self.demo_animations()


    def demo_basic_glow_line(self):
        """演示基本辉光线条"""

        # 创建一个简单的辉光线条
        line1 = GlowLine(
            start=LEFT * 2,
            end=RIGHT * 2,
            color=BLUE,
            glow_width=0.2,
            glow_factor=1.5
        )

        # 创建另一个不同颜色的线条
        line2 = GlowLine(
            start=UP * 1.5 + LEFT,
            end=DOWN * 1.5 + RIGHT,
            color=RED,
            glow_width=0.15,
            glow_factor=2.0
        )

        # 创建绿色线条
        line3 = GlowLine(
            start=UP * 1 + RIGHT * 1.5,
            end=DOWN * 1 + LEFT * 1.5,
            color=GREEN,
            glow_width=0.25,
            glow_factor=1.8
        )

        # 动画显示线条
        self.play(ShowCreation(line1), run_time=1.5)
        self.play(ShowCreation(line2), run_time=1.5)
        self.play(ShowCreation(line3), run_time=1.5)

        # 清除演示
        self.clear()


    def demo_multi_glow_line(self):
        """演示多段辉光线条"""

        # 定义线段
        segments = [
            (LEFT * 3 + UP, LEFT + UP),
            (LEFT + UP, ORIGIN + UP * 0.5),
            (ORIGIN + UP * 0.5, RIGHT + UP),
            (RIGHT + UP, RIGHT * 3 + UP),
        ]

        # 定义颜色
        colors = [RED, GREEN, BLUE, YELLOW]

        # 创建多段辉光线条
        multi_line = MultiGlowLine(
            line_segments=segments,
            colors=colors,
            glow_width=0.18,
            glow_factor=1.6
        )

        # 动画显示
        self.play(ShowCreation(multi_line), run_time=2)

        # 清除演示
        self.clear()


    def demo_glow_path(self):
        """演示辉光路径"""

        # 定义路径点
        path_points = [
            LEFT * 2 + UP * 2,
            LEFT + UP * 2.5,
            ORIGIN + UP * 2,
            RIGHT + UP * 2.5,
            RIGHT * 2 + UP * 2,
            RIGHT * 2.5 + UP * 1,
            RIGHT * 2 + ORIGIN,
            RIGHT * 2.5 + DOWN * 1,
            RIGHT * 2 + DOWN * 2,
            RIGHT + DOWN * 2.5,
            ORIGIN + DOWN * 2,
            LEFT + DOWN * 2.5,
            LEFT * 2 + DOWN * 2,
            LEFT * 2.5 + DOWN * 1,
            LEFT * 2 + ORIGIN,
            LEFT * 2.5 + UP * 1,
            LEFT * 2 + UP * 2
        ]

        # 创建辉光路径
        glow_path = GlowPath(
            points=path_points,
            color=PURPLE,
            glow_width=0.12,
            glow_factor=2.2
        )

        # 动画显示路径
        self.play(ShowCreation(glow_path), run_time=3)

        # 清除演示
        self.clear()


    def demo_animations(self):
        """演示动画效果"""

        # 创建一个可动画的辉光线条
        animated_line = GlowLine(
            start=LEFT * 2,
            end=RIGHT * 2,
            color=ORANGE,
            glow_width=0.1,
            glow_factor=1.0
        )

        self.play(ShowCreation(animated_line))

        # 动画1: 改变辉光宽度
        self.play(
            animated_line.animate.set_glow_width(0.3),
            run_time=1.5
        )

        # 动画2: 改变辉光因子
        self.play(
            animated_line.animate.set_glow_factor(3.0),
            run_time=1.5
        )

        # 动画3: 改变颜色
        self.play(
            animated_line.animate.set_color(TEAL),
            run_time=1.5
        )

        # 动画4: 移动线条
        self.play(
            animated_line.animate.put_start_and_end_on(
                UP * 1.5 + LEFT,
                UP * 1.5 + RIGHT
            ),
            run_time=2
        )

        # 清除演示
        self.clear()


# 便捷函数演示
def create_simple_glow_line():
    """创建简单辉光线条的示例函数"""
    return GlowLineBetween(
        start=LEFT,
        end=RIGHT,
        color=YELLOW,
        glow_width=0.2
    )


def create_star_pattern():
    """创建星形图案的示例函数"""
    center = ORIGIN
    radius = 2
    points = []

    # 创建五角星的点
    for i in range(5):
        angle = i * 72 * DEGREES
        point = center + radius * np.array([np.cos(angle), np.sin(angle), 0])
        points.append(point)

    # 连接成路径
    return GlowPath(
        points=points,
        color=GOLD,
        glow_width=0.15,
        glow_factor=2.0
    )


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  -w")