"""
GlowVMobjectTracer 功能演示
展示如何使用发光追踪器围绕各种 VMobject 运动
"""

import sys
from pathlib import Path

# 添加项目路径
_this = Path(__file__).resolve()
for parent in _this.parents:
    if (parent / 'shadersence').exists():
        sys.path.insert(0, str(parent))
        break

from manimlib import *
from shadersence.mobject.GlowFlashRectangle import GlowVMobjectTracer, PresetGlowTracers


class GlowVMobjectTracerDemo(Scene):
    """综合演示：多种形状的发光追踪效果"""
    
    def construct(self):
        # # 标题
        # title = Text("GlowVMobjectTracer 演示", font_size=48)
        # title.to_edge(UP)
        # self.play(Write(title))
        # self.wait(0.5)
        
        # # ===== 演示 1: 基础圆形追踪 =====
        # subtitle1 = Text("1. 基础圆形追踪", font_size=36)
        # subtitle1.next_to(title, DOWN, buff=0.5)
        # self.play(FadeIn(subtitle1))
        
        # circle = Circle(radius=1.5, stroke_color=BLUE, stroke_opacity=0.3)
        # circle.shift(DOWN * 0.5)
        
        # tracer1 = GlowVMobjectTracer(
        #     circle,
        #     num_points=8,
        #     color_scheme="bright",
        #     speed=1.0,
        #     time_per_cycle=4.0,
        #     tail_length=60,
        #     glow_factor=3.5
        # )
        
        # self.play(FadeIn(circle))
        # self.add(tracer1)
        # self.wait(8)  # 运行两个完整循环
        
        # self.play(
        #     FadeOut(circle),
        #     FadeOut(tracer1),
        #     FadeOut(subtitle1)
        # )
        
        # # ===== 演示 2: 多个形状同时追踪 =====
        # subtitle2 = Text("2. 多形状同时追踪", font_size=36)
        # subtitle2.next_to(title, DOWN, buff=0.5)
        # self.play(FadeIn(subtitle2))
        
        # # 创建三个不同的形状
        # shapes = Group(
        #     Circle(radius=0.8).shift(LEFT * 3),
        #     Square(side_length=1.5).shift(ORIGIN),
        #     RegularPolygon(n=6, radius=0.9).shift(RIGHT * 3)
        # )
        
        
        # # 为每个形状创建追踪器（不同颜色方案）
        # tracers = Group(
        #     GlowVMobjectTracer(shapes[0], num_points=6, color_scheme="neon", 
        #                       time_per_cycle=3.0, tail_length=40),
        #     GlowVMobjectTracer(shapes[1], num_points=8, color_scheme="bright", 
        #                       time_per_cycle=4.0, tail_length=50),
        #     GlowVMobjectTracer(shapes[2], num_points=12, color_scheme="dark", 
        #                       time_per_cycle=5.0, tail_length=60)
        # )
        
        # self.play(FadeIn(shapes))
        # self.add(*tracers)
        # self.wait(10)
        
        # self.play(
        #     FadeOut(shapes),
        #     FadeOut(tracers),
        #     FadeOut(subtitle2)
        # )
        
        # # ===== 演示 3: 预设配置对比 =====
        # subtitle3 = Text("3. 预设配置对比", font_size=36)
        # subtitle3.next_to(title, DOWN, buff=0.5)
        # self.play(FadeIn(subtitle3))
        
        # # 创建四个圆形用于演示不同预设
        # circles = Group(
        #     Circle(radius=0.7).shift(UP * 1.5 + LEFT * 3),
        #     Circle(radius=0.7).shift(UP * 1.5 + RIGHT * 3),
        #     Circle(radius=0.7).shift(DOWN * 1.5 + LEFT * 3),
        #     Circle(radius=0.7).shift(DOWN * 1.5 + RIGHT * 3)
        # )
        
        
        # # 使用不同的预设
        # preset_tracers = Group(
        #     PresetGlowTracers.neon_fast(circles[0]),
        #     PresetGlowTracers.bright_smooth(circles[1]),
        #     PresetGlowTracers.dark_slow(circles[2]),
        #     PresetGlowTracers.custom_rainbow(circles[3])
        # )
        
        # # 添加标签
        # labels = Group(
        #     Text("Neon Fast", font_size=20).next_to(circles[0], DOWN, buff=0.3),
        #     Text("Bright Smooth", font_size=20).next_to(circles[1], DOWN, buff=0.3),
        #     Text("Dark Slow", font_size=20).next_to(circles[2], DOWN, buff=0.3),
        #     Text("Custom Rainbow", font_size=20).next_to(circles[3], DOWN, buff=0.3)
        # )
        
        # self.play(FadeIn(circles), FadeIn(labels))
        # self.add(*preset_tracers)
        # self.wait(12)
        
        # self.play(
        #     FadeOut(circles),
        #     FadeOut(preset_tracers),
        #     FadeOut(labels),
        #     FadeOut(subtitle3)
        # )
        
        # # ===== 演示 4: 复杂路径追踪 =====
        # subtitle4 = Text("4. 复杂路径追踪", font_size=36)
        # subtitle4.next_to(title, DOWN, buff=0.5)
        # self.play(FadeIn(subtitle4))
        
        # 创建复杂的自定义路径
        heart = ParametricCurve(
            lambda t: np.array([
                16 * np.sin(t) ** 3,
                13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t),
                0
            ]) * 0.15,
            t_range=[0, TAU,0.01],

        )
        
        tracer4 = GlowVMobjectTracer(
            heart,
            num_points=16,
            color_scheme=[RED, PINK, ORANGE, YELLOW, PINK, RED],
            speed=1.0,
            time_per_cycle=6.0,
            tail_length=80,
            glow_factor=4.0,
            rate_function=smooth
        )
        
        self.play(ShowCreation(heart))
        self.add(tracer4)
        self.wait(12)
        
        self.play(
            FadeOut(heart),
            FadeOut(tracer4),

        )
        

        
        # 创建可变形的正方形
        morphing_square = Square(side_length=2, stroke_color=GREEN, stroke_opacity=0.3)
        
        tracer5 = GlowVMobjectTracer(
            morphing_square,
            num_points=12,
            color_scheme="neon",
            speed=1.5,
            time_per_cycle=4.0,
            tail_length=70,
            glow_factor=3.0
        )
        
        self.play(FadeIn(morphing_square))
        self.add(tracer5)
        self.wait(4)
        
        # 变形为圆形
        circle_morph = Circle(radius=1.4, stroke_color=GREEN, stroke_opacity=0.3)
        self.play(Transform(morphing_square, circle_morph), run_time=3)
        self.wait(4)
        
        # 变形为三角形
        triangle_morph = Triangle(stroke_color=GREEN, stroke_opacity=0.3).scale(2)
        self.play(Transform(morphing_square, triangle_morph), run_time=3)
        self.wait(4)
        
        self.play(
            FadeOut(morphing_square),
            FadeOut(tracer5),

        )
        

    
        hexagon = RegularPolygon(n=6, radius=1.5, stroke_color=YELLOW, stroke_opacity=0.3)
        
        tracer6 = GlowVMobjectTracer(
            hexagon,
            num_points=10,
            color_scheme="bright",
            speed=1.0,
            time_per_cycle=5.0,
            tail_length=60
        )
        
        self.play(FadeIn(hexagon))
        self.add(tracer6)
        self.wait(3)
        
        # 加速
        info1 = Text("加速 x2", font_size=30, color=YELLOW)
        info1.to_edge(DOWN)
        self.play(FadeIn(info1))
        tracer6.update_speed(2.0)
        self.wait(3)
        self.play(FadeOut(info1))
        
        # 改变颜色方案
        info2 = Text("切换到霓虹色", font_size=30, color=YELLOW)
        info2.to_edge(DOWN)
        self.play(FadeIn(info2))
        tracer6.update_colors("neon")
        self.wait(3)
        self.play(FadeOut(info2))
        
        # 增强辉光
        info3 = Text("增强辉光 x2", font_size=30, color=YELLOW)
        info3.to_edge(DOWN)
        self.play(FadeIn(info3))
        tracer6.set_glow_intensity(6.0)
        self.wait(3)
        self.play(FadeOut(info3))
        
        self.play(
            FadeOut(hexagon),
            FadeOut(tracer6),

        )
        


class SimpleGlowDemo(Scene):
    """简化版演示：快速展示基本功能"""
    
    def construct(self):
        # 创建多个形状
        shapes = Group(
            Circle(radius=1).shift(LEFT * 3.5),
            Square(side_length=1.8).shift(LEFT * 1.2),
            RegularPolygon(n=5, radius=1).shift(RIGHT * 1.2),
            RegularPolygon(n=6, radius=1.1).shift(RIGHT * 3.5)
        )
        
        
        # 为每个形状添加不同风格的追踪器
        tracers = [
            GlowVMobjectTracer(shapes[0], num_points=6, color_scheme="neon", 
                              time_per_cycle=3.0, glow_factor=4.0),
            GlowVMobjectTracer(shapes[1], num_points=8, color_scheme="bright", 
                              time_per_cycle=4.0, glow_factor=3.0),
            GlowVMobjectTracer(shapes[2], num_points=10, color_scheme="dark", 
                              time_per_cycle=5.0, glow_factor=3.5),
            PresetGlowTracers.custom_rainbow(shapes[3])
        ]
        
        # 添加所有对象
        self.add(shapes, *tracers)
        
        # 运行动画
        self.wait(15)


class HeartGlowDemo(Scene):
    """心形发光追踪演示"""
    
    def construct(self):
        # 创建心形路径
        heart = ParametricCurve(
            lambda t: np.array([
                16 * np.sin(t) ** 3,
                13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t),
                0
            ]) * 0.2,
            t_range=[0, TAU,0.01],
 
        )
        
        # 创建发光追踪器
        tracer = GlowVMobjectTracer(
            heart,
            num_points=10,
            color_scheme=[RED, PINK, BLUE, YELLOW, PINK, GREEN],
            speed=1.0,
            time_per_cycle=8.0,
            tail_length=100,
            glow_factor=0.5,
            rate_function=smooth
        )
                
        
        # 添加标题
        title = Text("爱心发光追踪", font_size=48, color=RED)
        title.to_edge(UP)
        
        self.play(Write(title))
        self.play(ShowCreation(heart))
        self.add(tracer)
        self.wait(5)
        triangle_morph = Triangle(stroke_color=GREEN, stroke_opacity=0.3).scale(2)
        self.play(Transform(heart, triangle_morph), run_time=3)
        self.wait(4)

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    
    # 运行完整演示
    # os.system(f"cd {script_dir} && manimgl {script_name}.py GlowVMobjectTracerDemo")
    
    # 运行简化演示
    os.system(f"cd {script_dir} && manimgl {script_name}.py HeartGlowDemo")
    
    # 运行心形演示
    # os.system(f"cd {script_dir} && manimgl {script_name}.py HeartGlowDemo")
