"""
方框引导高亮演示

演示 focus_guide 的用法：
1. 基本用法 - 依次高亮多个目标
2. 关键词查找 - 在文本中查找并高亮
3. 颜色轮询 - 每次变换换颜色
4. 不连续处理 - 自动生成多个方框

运行方法：
    cd E:\\auto_manim\\new_class\\demo
    manimgl focus_guide_demo.py FocusGuideDemo -w
"""

import os
import sys
import numpy as np

# 添加父目录到路径以导入 AutoScene
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from auto_scene import AutoScene
from manimlib import (
    Text, Write, FadeIn, FadeOut, VGroup,
    YELLOW, RED, BLUE, GREEN
)


class FocusGuideDemo(AutoScene):
    """
    方框引导高亮演示
    
    演示 focus_guide 的用法：
    1. 基本用法 - 依次高亮多个目标
    2. 关键词查找 - 在文本中查找并高亮
    3. 颜色轮询 - 每次变换换颜色
    4. 不连续处理 - 自动生成多个方框
    """
    
    def construct(self):
        self.enable_debug(True)
        
        # ===== 1. 基本用法 =====
        self._test_basic_focus()
        
        # ===== 2. 关键词查找 =====
        self._test_keyword_focus()
        
        # ===== 3. 公式引导 =====
        self._test_formula_focus()
        
        self.wait(1)
    
    def _test_basic_focus(self):
        """基本用法演示"""
        title = Text("方框引导 - 基本用法", font="STKaiti", font_size=32, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.5)
        
        # 创建多个图形
        from manimlib import Square, Circle, Triangle, Polygon
        shapes = VGroup(
            Square(side_length=1, color=BLUE),
            Circle(radius=0.5, color=RED),
            Triangle(color=GREEN).scale(0.7),
            Polygon(*[np.array([np.cos(a), np.sin(a), 0]) for a in np.linspace(0, 2*np.pi, 6, endpoint=False)], color=YELLOW).scale(0.5),
        ).arrange(RIGHT, buff=1.5)
        
        self.play(FadeIn(shapes), run_time=0.5)
        
        # 依次高亮每个形状
        self.focus_guide(
            [shapes[0], shapes[1], shapes[2], shapes[3]],
            hold_time=0.8,
            auto_remove=True,
        )
        
        self.play(FadeOut(shapes), FadeOut(title), run_time=0.5)
    
    def _test_keyword_focus(self):
        """关键词查找演示 - 使用自动关键词匹配"""
        title = Text("方框引导 - 自动关键词匹配", font="STKaiti", font_size=32, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.5)
        
        # 创建带关键词的句子
        sentence = Text(
            "数学中，向量加法满足交换律和结合律",
            font="STKaiti",
            font_size=36,
        )
        self.play(Write(sentence), run_time=1)
        
        # 使用 focus_guide_sequence 依次高亮关键词
        # 现在使用自动字符串匹配，无需手动指定索引！
        self.focus_guide_sequence(
            sentence,
            ["向量", "加法", "交换律", "结合律"],  # 直接传关键词字符串
            hold_time=1.0,
            auto_remove=True,
        )
        
        self.play(FadeOut(sentence), FadeOut(title), run_time=0.5)
    
    def _test_formula_focus(self):
        """公式引导演示 - 使用字符串匹配定位公式部分"""
        title = Text("方框引导 - 公式字符串匹配", font="STKaiti", font_size=32, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.5)
        
        # 创建公式（单个字符串，不是分开的）
        from manimlib import Tex
        formula = Tex(
            r"f(x) = x^2 + 2x + 1",
            font_size=48,
        )
        self.play(Write(formula), run_time=1)
        
        # 使用字符串匹配依次高亮公式各部分
        # Tex 对象支持 tex["x^2"] 这样的字符串索引！
        self.focus_guide_sequence(
            formula,
            ["f(x)", "x^2", "2x", "1"],  # 直接用 LaTeX 字符串匹配
            hold_time=1.0,
            auto_remove=True,
        )
        
        self.play(FadeOut(formula), FadeOut(title), run_time=0.5)


if __name__ == "__main__":
    os.system(f"cd {script_dir} && manimgl focus_guide_demo.py FocusGuideDemo")
