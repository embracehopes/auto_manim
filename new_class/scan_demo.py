"""
Scan 效果演示 - 背景扫描矩形从左到右展开

运行命令:
    python scan_demo.py
    或
    manimgl scan_demo.py ScanDemo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auto_scene import AutoScene
from manimlib import Text, Tex, Write, FadeOut, YELLOW, BLUE, GREEN, RED, DOWN


class ScanDemo(AutoScene):
    """演示 scan 高亮效果"""
    
    def construct(self):
        self.enable_debug(True)
        
        # 创建测试文本
        title = Text("Scan 效果演示", font=self.SUBTITLE_FONT, font_size=48)
        title.shift_onto_screen()
        self.play(Write(title))
        self.wait(0.5)
        
        # 演示 scan 效果（自动销毁）
        self.speak("这是 scan 扫描效果")
        self.highlight_text(title, effect="scan", color=YELLOW, run_time=1.5)
        
        # 换一个对象测试
        formula = Tex(r"E = mc^2", font_size=72)
        formula.next_to(title, direction=3*DOWN)
        self.play(Write(formula))
        
        self.speak("公式也可以使用 scan 效果")
        self.highlight_text(formula, effect="scan", color=BLUE, run_time=1.2)
        
        # 测试不同颜色（七色轮询自动切换）
        colors = [RED, GREEN, YELLOW]
        for i, color in enumerate(colors):
            self.speak(f"颜色变体 {i+1}")
            self.highlight_text(formula, effect="scan", color=color, run_time=0.8)
        
        self.play(FadeOut(title), FadeOut(formula))
        self.wait(1)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    os.system(f"cd {script_dir} && manimgl {script_name}.py ScanDemo -w")
