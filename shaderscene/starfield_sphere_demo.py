#!/usr/bin/env python3
"""
星空球面演示脚本
展示新创建的 StarfieldSphere 的各种效果
"""

import sys
import os

# 添加当前目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from manimlib import *
from mobject.starfield_sphere import *

class StarfieldSphereDemo(Scene):
    """星空球面基础演示"""

    def construct(self):
        # 创建基础星空球面
        sphere = StarfieldSphere(
            radius=1.5,
            brightness=2.0,
            star_density=1000
        )

        # 添加标题
        title = Text("星空球面效果", font_size=48, color=WHITE)
        title.to_edge(UP)

        self.add(title)
        self.play(FadeIn(sphere))

        # 等待一段时间欣赏静态效果
        self.wait(3)

        # 移动球体，展示位置无关性
        self.play(sphere.animate.move_to(LEFT * 2), run_time=2)
        self.wait(1)
        self.play(sphere.animate.move_to(RIGHT * 2), run_time=2)
        self.wait(1)
        self.play(sphere.animate.move_to(ORIGIN), run_time=2)

        # 调整亮度
        self.play(sphere.animate.set_brightness(3.0), run_time=2)
        self.wait(2)
        self.play(sphere.animate.set_brightness(1.0), run_time=2)
        self.wait(2)

        self.play(FadeOut(sphere), FadeOut(title))


class AnimatedStarfieldDemo(Scene):
    """动画星空球面演示"""

    def construct(self):
        # 创建动画星空球面
        sphere = AnimatedStarfieldSphere(
            radius=1.2,
            brightness=2.5,
            rotation_speed=0.8
        )

        title = Text("动画星空球面", font_size=48, color=WHITE)
        title.to_edge(UP)

        self.add(title)
        self.play(FadeIn(sphere))

        # 让动画运行一段时间
        self.wait(8)

        # 停止旋转
        sphere.stop_auto_rotation()
        self.wait(2)

        # 重新开始旋转
        sphere.start_auto_rotation()
        self.wait(4)

        self.play(FadeOut(sphere), FadeOut(title))
        a =ImplicitFunction


class PulsingStarfieldDemo(Scene):
    """脉冲星空球面演示"""

    def construct(self):
        # 创建脉冲星空球面
        sphere = PulsingStarfieldSphere(
            radius=1.3,
            brightness=2.0,
            pulse_frequency=2.0,
            pulse_amplitude=0.8
        )

        title = Text("脉冲星空球面", font_size=48, color=WHITE)
        title.to_edge(UP)

        self.add(title)
        self.play(FadeIn(sphere))

        # 让脉冲效果运行
        self.wait(10)

        self.play(FadeOut(sphere), FadeOut(title))


class ComparisonDemo(Scene):
    """三种星空球面对比演示"""

    def construct(self):
        title = Text("星空球面效果对比", font_size=48, color=WHITE)
        title.to_edge(UP)

        # 创建三种不同的星空球面
        basic_sphere = StarfieldSphere(radius=0.8, center=LEFT*3, brightness=1.5)
        animated_sphere = AnimatedStarfieldSphere(radius=10.1, center=ORIGIN, brightness=2.0)
        pulsing_sphere = PulsingStarfieldSphere(radius=0.8, center=RIGHT*3, brightness=2.5)
        normalsphere = Sphere(radius=10)
        normalsphere = TexturedSurface(normalsphere, image_file="星云.jpg")
        normalsphere.set_opacity(0.4)
        def normal_rota(mob, dt):
            mob.rotate(PI/20*dt, axis=UP)
        normalsphere.add_updater(normal_rota)
        

        # 添加标签
        labels = VGroup(
            Text("基础", font_size=24).next_to(basic_sphere, DOWN),
            Text("动画", font_size=24).next_to(animated_sphere, DOWN),
            Text("脉冲", font_size=24).next_to(pulsing_sphere, DOWN)
        )


        self.add(title)
        self.play(
            FadeIn(basic_sphere),
            FadeIn(animated_sphere),
            FadeIn(pulsing_sphere),
            FadeIn(labels)
        )
        # self.add(normalsphere)

        # 同时运行所有效果
        self.wait(12)



class TwinklingDemo(Scene):
    """星星闪烁效果演示"""

    def construct(self):
        # 创建带有闪烁效果的星空球面
        sphere = StarfieldSphere(
            radius=1.8,
            brightness=3.0,
            time_scale=1.5  # 控制闪烁速度
        )

        title = Text("星星闪烁效果", font_size=48, color=WHITE)
        title.to_edge(UP)

        subtitle = Text("每颗星星都有独特的闪烁模式", font_size=24, color="#888888")
        subtitle.next_to(title, DOWN)

        self.add(title, subtitle)
        self.play(FadeIn(sphere))

        # 让闪烁效果运行
        self.wait(10)

        # 调整闪烁速度
        sphere.time_scale = 3.0  # 加快闪烁
        self.wait(5)

        sphere.time_scale = 0.5  # 减慢闪烁
        self.wait(5)

        # 增加亮度
        self.play(sphere.animate.set_brightness(5.0), run_time=2)
        self.wait(5)

        self.play(FadeOut(sphere), FadeOut(title), FadeOut(subtitle))


class MovementTestDemo(Scene):
    """位置无关性测试演示"""

    def construct(self):
        title = Text("位置无关性测试", font_size=48, color=WHITE)
        title.to_edge(UP)

        subtitle = Text("移动球体时，星星图案保持相对位置不变", font_size=24, color="#888888")
        subtitle.next_to(title, DOWN)

        # 创建星空球面
        sphere = StarfieldSphere(radius=1.0, brightness=2.0)

        self.add(title, subtitle)
        self.play(FadeIn(sphere))

        # 测试不同的移动路径
        positions = [
            LEFT * 3,
            RIGHT * 3,
            UP * 2,
            DOWN * 2,
            LEFT * 2 + UP * 1,
            RIGHT * 2 + DOWN * 1,
            ORIGIN
        ]

        for pos in positions:
            self.play(sphere.animate.move_to(pos), run_time=1.5)
            self.wait(0.5)

        self.play(FadeOut(sphere), FadeOut(title), FadeOut(subtitle))

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py ComparisonDemo ")