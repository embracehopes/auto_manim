"""
Tex 公式字符串匹配演示

展示如何通过字符串自动定位 Tex 公式中的部分

运行方法：
    cd E:\\auto_manim\\new_class\\demo
    manimgl tex_matching_demo.py TexMatchingDemo -w
"""

import os
import sys

# 添加父目录到路径以导入 AutoScene
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from auto_scene import AutoScene
from manimlib import (
    Text, Tex, Write, FadeOut,
    YELLOW
)


class TexMatchingDemo(AutoScene):
    """
    Tex 公式字符串匹配演示
    
    展示如何通过字符串自动定位 Tex 公式中的部分
    """
    
    def construct(self):
        self.enable_debug(True)
        
        # 标题
        title = Text("Tex 公式字符串匹配", font="STKaiti", font_size=36, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.5)
        
        # ===== 演示1: 基本字符串匹配 =====
        formula1 = Tex(r"E = mc^2", font_size=56)
        self.play(Write(formula1), run_time=1)
        
        # 使用字符串直接获取公式部分
        # Tex 对象支持 tex["E"], tex["mc^2"] 等字符串索引
        self.focus_guide_sequence(
            formula1,
            ["E", "mc^2"],  # 直接用字符串匹配！
            hold_time=1.2,
            auto_remove=True,
        )
        
        self.play(FadeOut(formula1), run_time=0.3)
        
        # ===== 演示2: 复杂公式匹配 =====
        formula2 = Tex(
            r"\int_0^1 x^2 \, dx = \frac{1}{3}",
            font_size=48,
        )
        self.play(Write(formula2), run_time=1)
        
        # 匹配积分符号、被积函数、结果
        self.focus_guide_sequence(
            formula2,
            [r"\int_0^1", "x^2", r"\frac{1}{3}"],
            hold_time=1.2,
            auto_remove=True,
        )
        
        self.play(FadeOut(formula2), run_time=0.3)
        
        # ===== 演示3: 带弯曲箭头标注 =====
        formula3 = Tex(
            r"a^2 + b^2 = c^2",
            font_size=56,
        )
        self.play(Write(formula3), run_time=1)
        
        # 获取公式部分并添加弯曲箭头标注
        a2_part = self.get_text_part(formula3, "a^2")
        b2_part = self.get_text_part(formula3, "b^2")
        c2_part = self.get_text_part(formula3, "c^2")
        
        ann1, ann2, ann3 = None, None, None
        if a2_part:
            ann1 = self.add_curved_annotation(a2_part, "直角边a的平方", direction="ul")
        if b2_part:
            ann2 = self.add_curved_annotation(b2_part, "直角边b的平方", direction="up")
        if c2_part:
            ann3 = self.add_curved_annotation(c2_part, "斜边c的平方", direction="ur")
        
        self.wait(2)
        
        # 清理
        if ann1: self.remove_curved_annotation(ann1)
        if ann2: self.remove_curved_annotation(ann2)
        if ann3: self.remove_curved_annotation(ann3)
        
        self.play(FadeOut(formula3), FadeOut(title), run_time=0.5)
        self.wait(1)


if __name__ == "__main__":
    os.system(f"cd {script_dir} && manimgl tex_matching_demo.py TexMatchingDemo")
