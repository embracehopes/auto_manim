"""
辉光效果集成测试 - 验证 focus_guide 辉光效果
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auto_scene import AutoScene, create_glow_surrounding_rect, create_glowing_arc_arrow
from manimlib import *


class GlowIntegrationDemo(AutoScene):
    """测试辉光效果集成到 AutoScene 的效果"""
    
    def construct(self):
        # 标题
        title = Text("辉光效果集成测试", font="STKaiti", font_size=42)
        title.to_edge(UP)
        self.play(Write(title))
        
        # 创建一些测试对象
        formula = Tex(r"E = mc^2", font_size=56)
        text = Text("向量加法满足交换律", font="STKaiti", font_size=32)
        text.shift(DOWN * 1.5)
        
        self.play(Write(formula), Write(text))
        self.wait(0.5)
        
        # 测试 focus_guide 辉光效果
        self.focus_guide(
            [formula],
            hold_time=1.0,
            stroke_width=4,
        )
        
        # 测试关键词引导
        self.focus_guide_sequence(
            text,
            ["向量", "加法", "交换律"],
            hold_time=0.8,
            stroke_width=3,
        )
        
        # 清除公式和文本
        self.play(FadeOut(formula), FadeOut(text))
        
        # 测试辉光弧形箭头 - 使用类配置的便捷方法
        left_arrow = self.create_glow_arc_arrow(
            start_angle=-TAU/4 - 0.6,
            angle=TAU/2,
            radius=2.5,
            side="left",  # 使用暖色渐变
        )
        
        right_arrow = self.create_glow_arc_arrow(
            start_angle=TAU/4 - 0.6,
            angle=TAU/2,
            radius=2.5,
            side="right",  # 使用冷色渐变
        )
        
        # 布局
        left_arrow.shift(LEFT * 0.8)
        right_arrow.shift(RIGHT * 0.8)
        
        self.play(
            ShowCreation(left_arrow),
            ShowCreation(right_arrow),
            run_time=2
        )
        self.wait(1)
        
        # 测试辉光环绕框便捷方法
        box_text = Text("辉光框测试", font="STKaiti", font_size=36)
        box_text.shift(DOWN * 2)
        self.play(Write(box_text))
        
        glow_box = self.create_glow_box(
            box_text,
            color=BLUE,
            buff=0.3,
            stroke_width=4,
        )
        self.play(ShowCreation(glow_box), run_time=1)
        self.wait(1)
        
        # 结束
        self.play(FadeOut(VGroup(title, left_arrow, right_arrow, box_text, glow_box)))
        
        end_text = Text("辉光效果集成完成!", font="STKaiti", font_size=48, color=YELLOW)
        self.play(Write(end_text))
        self.wait(1)


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    os.system(f"cd {script_dir} && manimgl {script_name}.py GlowIntegrationDemo")
