"""
弯曲箭头标注演示

演示 add_curved_annotation 的用法：
- 单个标注
- 自动方向选择
- 多标注批量添加

运行方法：
    cd E:\\auto_manim\\new_class\\demo
    manimgl curved_annotation_demo.py CurvedAnnotationDemo -w
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
    Text, Write, FadeOut, ShowCreation,
    YELLOW, RED, BLUE, GREEN
)


class CurvedAnnotationDemo(AutoScene):
    """
    弯曲箭头标注演示
    
    演示 add_curved_annotation 的用法
    """
    
    def construct(self):
        self.enable_debug(True)
        
        # 标题
        title = Text("弯曲箭头标注演示", font="STKaiti", font_size=36, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.5)
        
        # 创建简单图形进行标注
        from manimlib import Square, Circle
        square = Square(side_length=2, color=BLUE)
        self.play(ShowCreation(square), run_time=0.5)
        
        # 标注图形（演示自动方向选择）
        ann1 = self.add_curved_annotation(
            square,
            "这是一个正方形",
            direction="auto",
        )
        self.wait(1.5)
        
        # 移除标注
        self.remove_curved_annotation(ann1)
        
        # 演示不同方向
        ann2 = self.add_curved_annotation(
            square,
            "右上方标注",
            direction="ur",
        )
        self.wait(1)
        self.remove_curved_annotation(ann2)
        
        ann3 = self.add_curved_annotation(
            square,
            "左下方标注",
            direction="dl",
        )
        self.wait(1)
        self.remove_curved_annotation(ann3)
        
        # 清理
        self.play(FadeOut(square), FadeOut(title), run_time=0.5)
        
        # ===== 多标注批量演示 =====
        title2 = Text("多标注批量演示", font="STKaiti", font_size=36, color=YELLOW)
        title2.to_edge(UP)
        self.play(Write(title2), run_time=0.5)
        
        # 创建多个对象
        from manimlib import Triangle
        square2 = Square(side_length=1.2, color=BLUE).shift(LEFT * 3)
        circle = Circle(radius=0.6, color=RED)
        triangle = Triangle(color=GREEN).scale(0.8).shift(RIGHT * 3)
        
        self.play(
            ShowCreation(square2),
            ShowCreation(circle),
            ShowCreation(triangle),
            run_time=1
        )
        
        # 批量添加标注
        annotations = self.add_multi_curved_annotations([
            {"target": square2, "text": "正方形", "direction": "ul"},
            {"target": circle, "text": "圆形", "direction": "up"},
            {"target": triangle, "text": "三角形", "direction": "ur"},
        ])
        
        self.wait(2)
        
        # 批量移除
        for ann in annotations:
            self.remove_curved_annotation(ann)
        
        self.play(
            FadeOut(square2), FadeOut(circle), FadeOut(triangle), FadeOut(title2),
            run_time=0.5
        )
        
        self.wait(1)


if __name__ == "__main__":
    os.system(f"cd {script_dir} && manimgl curved_annotation_demo.py CurvedAnnotationDemo")
