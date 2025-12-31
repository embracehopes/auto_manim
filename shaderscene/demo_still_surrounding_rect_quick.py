"""
快速测试 StillSurroundingRect 和 GlowRoundedRectangle
"""

from manimlib import *
import sys
import os

# 添加当前目录到路径，以便导入其他模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from GlowFlashRectangle import GlowRoundedRectangle, StillSurroundingRect


class QuickTest(Scene):
    """快速测试场景"""
    
    def construct(self):
        # 测试 GlowRoundedRectangle
        # rect = GlowRoundedRectangle(
        #     width=5.0,
        #     height=3.0,
        #     corner_radius=0.3,
        #     color_scheme="bright",
        #     stroke_width=0.1,
        #     glow_factor=3.0,
        #     num_segments=1000
        # )
        
        # label = Text("GlowRoundedRectangle", font_size=36)
        # label.next_to(rect, UP, buff=0.5)


        # 测试 StillSurroundingRect
        text = Text("测试文本", font="STKaiti", font_size=48, color=YELLOW).scale(1.5)
        
        glow = StillSurroundingRect(
            text,
            buff=0.25,
            corner_radius=0.15,
            color_scheme="neon",
            stroke_width=0.05,
            glow_factor=3.5,
            num_segments=400
        )
        
        self.play(ShowCreation(text))
        self.wait(0.3)
        self.play(FadeIn(glow))
        self.wait(2.0)


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")