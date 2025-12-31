"""
Shader-Based Text Glow Demo - 基于 GLSL Shader 的文字辉光演示

使用真正的 GPU shader 实现高斯模糊辉光效果

运行方法：
    cd E:\\auto_manim\\shaderscene
    manimgl demo_shader_text_glow.py ShaderGlowDemo -w
"""

from manimlib import *
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from mobject.shader_text_glow import (
    ShaderTextGlow,
    create_glowing_text,
    create_glowing_tex,
)


class ShaderGlowDemo(Scene):
    """
    基于 Shader 的文字辉光效果演示
    """
    
    CONFIG = {
        "camera_config": {
            "background_color": "#1a1a2e",
        }
    }
    
    def construct(self):
        # === 标题 ===
        title = Text("Shader-Based Text Glow", font="Arial", font_size=32, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(0.5)
        
        # === 演示1: 基础辉光效果 ===
        subtitle = Text("基础白色辉光", font="STKaiti", font_size=24, color=GREY)
        subtitle.next_to(title, DOWN, buff=0.3)
        self.play(Write(subtitle))
        
        # 创建辉光文字
        line1 = create_glowing_text(
            "当电梯有一恒定向上的加速度",
            font="STKaiti",
            font_size=36,
            glow_radius=0.1,
            glow_intensity=1.5,
            glow_softness=0.5,
        ).shift(UP * 1)
        
        line2 = create_glowing_text(
            "根据牛顿第二定律",
            font="STKaiti",
            font_size=36,
            glow_radius=0.08,
            glow_intensity=1.3,
        )
        
        # 公式
        formula = create_glowing_tex(
            r"\vec{F} = m\vec{a}",
            font_size=42,
            glow_radius=0.12,
            glow_intensity=1.6,
        ).next_to(line2, RIGHT, buff=0.3)
        
        line3 = create_glowing_text(
            "此时你一定受到向上的合外力",
            font="STKaiti",
            font_size=36,
            glow_radius=0.08,
            glow_intensity=1.3,
        ).shift(DOWN * 1)
        
        self.play(FadeIn(line1), run_time=1)
        self.wait(0.3)
        self.play(FadeIn(line2), FadeIn(formula), run_time=1)
        self.wait(0.3)
        self.play(FadeIn(line3), run_time=1)
        self.wait(2)
        
        # === 演示2: 不同强度对比 ===
        self.play(
            FadeOut(line1), FadeOut(line2), FadeOut(formula), 
            FadeOut(line3), FadeOut(subtitle),
            run_time=0.5
        )
        
        subtitle2 = Text("辉光强度对比", font="STKaiti", font_size=24, color=GREY)
        subtitle2.next_to(title, DOWN, buff=0.3)
        self.play(Write(subtitle2))
        
        # 弱辉光
        weak = create_glowing_text(
            "弱辉光",
            font="STKaiti",
            font_size=32,
            glow_radius=0.05,
            glow_intensity=0.8,
        ).shift(LEFT * 4 + UP * 0.5)
        
        # 中等辉光
        medium = create_glowing_text(
            "中等辉光",
            font="STKaiti",
            font_size=32,
            glow_radius=0.08,
            glow_intensity=1.3,
        ).shift(UP * 0.5)
        
        # 强辉光
        strong = create_glowing_text(
            "强辉光",
            font="STKaiti",
            font_size=32,
            glow_radius=0.15,
            glow_intensity=2.0,
        ).shift(RIGHT * 4 + UP * 0.5)
        
        self.play(
            FadeIn(weak),
            FadeIn(medium),
            FadeIn(strong),
            run_time=1
        )
        self.wait(2)
        
        # === 演示3: 彩色辉光 ===
        self.play(
            FadeOut(weak), FadeOut(medium), FadeOut(strong), FadeOut(subtitle2),
            run_time=0.5
        )
        
        subtitle3 = Text("彩色辉光", font="STKaiti", font_size=24, color=GREY)
        subtitle3.next_to(title, DOWN, buff=0.3)
        self.play(Write(subtitle3))
        
        # 蓝色辉光
        blue = create_glowing_text(
            "能量",
            font="STKaiti",
            font_size=42,
            glow_color=BLUE,
            glow_radius=0.12,
            glow_intensity=1.5,
        ).shift(LEFT * 3 + UP * 0.5)
        
        # 金色辉光
        gold = create_glowing_text(
            "动量",
            font="STKaiti",
            font_size=42,
            glow_color=YELLOW,
            glow_radius=0.12,
            glow_intensity=1.5,
        ).shift(UP * 0.5)
        
        # 红色辉光
        red = create_glowing_text(
            "力学",
            font="STKaiti",
            font_size=42,
            glow_color=RED,
            glow_radius=0.12,
            glow_intensity=1.5,
        ).shift(RIGHT * 3 + UP * 0.5)
        
        self.play(
            FadeIn(blue),
            FadeIn(gold),
            FadeIn(red),
            run_time=1
        )
        self.wait(2)
        
        # === 结束 ===
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)
        
        final = create_glowing_text(
            "Shader 辉光效果",
            font="STKaiti",
            font_size=48,
            glow_radius=0.15,
            glow_intensity=1.8,
            white_core_strength=0.4,
        )
        self.play(FadeIn(final), run_time=1)
        self.wait(2)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.system(f'cd "{script_dir}" && manimgl demo_shader_text_glow.py ShaderGlowDemo -w')
