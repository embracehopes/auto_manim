"""
带相机移动的方框引导演示

演示 focus_guide_with_camera 的用法：
- 方框高亮 + 相机跟随
- 相机自动缩放适应目标大小
- 更强的视觉引导效果

运行方法：
    cd E:\\auto_manim\\new_class\\demo
    manimgl camera_focus_guide_demo.py CameraFocusGuideDemo -w
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
    Text, Tex, Write, FadeIn, FadeOut, ShowCreation, VGroup,
    YELLOW, RED, BLUE, GREEN, WHITE, LEFT, RIGHT, UP, DOWN
)


class CameraFocusGuideDemo(AutoScene):
    """
    带相机移动的方框引导演示
    
    演示 focus_guide_with_camera 的强大视觉引导效果
    """
    
    def construct(self):
        self.enable_debug(True)
        
        # ===== 1. 基本用法：公式引导 =====
        self._demo_formula_guide()
        
        # ===== 2. 文本关键词引导 =====
        self._demo_keyword_guide()
        
        # ===== 3. 多对象引导 =====
        self._demo_multi_object_guide()
        
        self.wait(1)
    
    def _demo_formula_guide(self):
        """公式引导演示"""
        title = Text("相机跟随方框引导 - 公式演示", font="STKaiti", font_size=32, color=YELLOW)
        title.to_edge(UP)
        title.fix_in_frame()  # 固定标题
        self.play(Write(title), run_time=0.5)
        
        # 创建公式
        formula = Tex(
            r"E = mc^2 + \frac{1}{2}mv^2",
            font_size=56,
        )
        self.play(Write(formula), run_time=1)
        
        # 使用带相机移动的方框引导
        # 相机会自动移动到每个公式部分并放大
        self.focus_guide_with_camera(
            [formula["E"], formula["mc^2"], formula[r"\frac{1}{2}mv^2"]],
            zoom_factor=2.5,
            hold_time=1.2,
        )
        
        self.play(FadeOut(formula), FadeOut(title), run_time=0.5)
    
    def _demo_keyword_guide(self):
        """文本关键词引导演示"""
        title = Text("相机跟随方框引导 - 关键词演示", font="STKaiti", font_size=32, color=YELLOW)
        title.to_edge(UP)
        title.fix_in_frame()
        self.play(Write(title), run_time=0.5)
        
        # 创建长句子
        sentence = Text(
            "数学中，向量加法满足交换律和结合律",
            font="STKaiti",
            font_size=36,
        )
        self.play(Write(sentence), run_time=1)
        
        # 使用便捷方法引导关键词
        # 相机会依次移动到每个关键词并放大
        self.focus_guide_with_camera_sequence(
            sentence,
            ["向量", "加法", "交换律", "结合律"],
            zoom_factor=3.0,
            hold_time=1.0,
        )
        
        self.play(FadeOut(sentence), FadeOut(title), run_time=0.5)
    
    def _demo_multi_object_guide(self):
        """多对象引导演示"""
        title = Text("相机跟随方框引导 - 多对象演示", font="STKaiti", font_size=32, color=YELLOW)
        title.to_edge(UP)
        title.fix_in_frame()
        self.play(Write(title), run_time=0.5)
        
        # 创建多个分散的对象
        from manimlib import Square, Circle, Triangle
        
        square = Square(side_length=1.5, color=BLUE).shift(LEFT * 4 + UP * 1.5)
        circle = Circle(radius=0.8, color=RED).shift(RIGHT * 3 + DOWN * 1)
        triangle = Triangle(color=GREEN).scale(1.2).shift(DOWN * 2)
        
        square_label = Text("正方形", font="STKaiti", font_size=24).next_to(square, DOWN)
        circle_label = Text("圆形", font="STKaiti", font_size=24).next_to(circle, DOWN)
        triangle_label = Text("三角形", font="STKaiti", font_size=24).next_to(triangle, DOWN)
        
        self.play(
            ShowCreation(square), ShowCreation(circle), ShowCreation(triangle),
            Write(square_label), Write(circle_label), Write(triangle_label),
            run_time=1
        )
        
        # 相机会自动移动到每个分散的对象
        self.focus_guide_with_camera(
            [square, circle, triangle],
            zoom_factor=3.0,
            hold_time=1.5,
            run_time=1.0,
        )
        
        self.play(
            FadeOut(square), FadeOut(circle), FadeOut(triangle),
            FadeOut(square_label), FadeOut(circle_label), FadeOut(triangle_label),
            FadeOut(title),
            run_time=0.5
        )


if __name__ == "__main__":
    os.system(f"cd {script_dir} && manimgl camera_focus_guide_demo.py CameraFocusGuideDemo")
