"""
TextGlow 效果演示 - 使用 GlowWrapperEffect 实现文字辉光

运行方法：
    cd E:\\auto_manim\\shaderscene
    manimgl demo_text_glow.py TextGlowDemo -w
"""

from manimlib import *
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from mobject.text_glow import create_glow_text, create_glow_tex


class TextGlowDemo(Scene):
    """文字辉光效果演示"""
    
    CONFIG = {
        "camera_config": {
            "background_color": "#1a1a2e",
        }
    }
    
    def construct(self):
        # === 标题 ===
        title = Text("Text Glow Effect", font="Arial", font_size=32, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        # === 演示：白色辉光文字 ===
        line1 = create_glow_text(
            "当电梯有一恒定向上的加速度",
            font="STKaiti",
            font_size=36,
            glow_color=WHITE,
            glow_size=0.15,
            glow_factor=3.0,
            white_core_ratio=0.6,
        ).shift(UP * 1.5)
        
        line2 = create_glow_text(
            "根据牛顿第二定律",
            font="STKaiti",
            font_size=36,
            glow_color=WHITE,
            glow_size=0.12,
        )
        
        # 公式
        formula = create_glow_tex(
            r"\vec{F} = m\vec{a}",
            font_size=42,
            glow_color=WHITE,
            glow_size=0.15,
        ).next_to(line2, RIGHT, buff=0.3)
        
        line3 = create_glow_text(
            "此时你一定受到向上的合外力",
            font="STKaiti",
            font_size=36,
            glow_color=WHITE,
            glow_size=0.12,
        ).shift(DOWN * 1.5)
        
        self.play(FadeIn(line1), run_time=1)
        self.wait(0.5)
        self.play(FadeIn(line2), FadeIn(formula), run_time=1)
        self.wait(0.5)
        self.play(FadeIn(line3), run_time=1)
        self.wait(2)
        
        # === 清理并展示彩色辉光 ===
        self.play(*[FadeOut(m) for m in [line1, line2, formula, line3]], run_time=0.5)
        
        # 彩色辉光
        blue = create_glow_text(
            "能量",
            font="STKaiti",
            font_size=48,
            glow_color=BLUE,
            glow_size=0.18,
        ).shift(LEFT * 3)
        
        gold = create_glow_text(
            "动量",
            font="STKaiti",
            font_size=48,
            glow_color=YELLOW,
            glow_size=0.18,
        )
        
        red = create_glow_text(
            "力学",
            font="STKaiti",
            font_size=48,
            glow_color=RED,
            glow_size=0.18,
        ).shift(RIGHT * 3)
        
        self.play(FadeIn(blue), FadeIn(gold), FadeIn(red), run_time=1)
        self.wait(2)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.system(f'cd "{script_dir}" && manimgl demo_text_glow.py TextGlowDemo -w')
