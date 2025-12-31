"""
测试 TracingTailPMobject 的 ManimGL 平滑功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import numpy as np
from manimlib import *
from mobject.TracingTailPMobject import TracingTailPMobject

class TestTracingTailSmoothing(InteractiveScene):
    def construct(self):
        # 创建一个简单的圆形轨迹函数
        self.time = 0
        
        def circular_motion():
            # 添加一些噪声来测试平滑效果
            noise = 0.1 * np.random.randn(3)
            base_pos = np.array([
                2 * np.cos(self.time * 2),
                2 * np.sin(self.time * 2),
                0
            ])
            return base_pos + noise
        
        # 创建三个不同平滑模式的轨迹
        tail_jagged = TracingTailPMobject(
            circular_motion,
            max_tail_length=100,
            tail_lifetime=3.0,
            base_color=RED,
            smoothing_mode="jagged"
        ).shift(LEFT * 4)
        
        
        tail_approx = TracingTailPMobject(
            circular_motion,
            max_tail_length=100,
            tail_lifetime=3.0,
            base_color=GREEN,
            smoothing_mode="approx_smooth"
        )
        
        tail_true = TracingTailPMobject(
            circular_motion,
            max_tail_length=100,
            tail_lifetime=3.0,
            base_color=BLUE,
            smoothing_mode="true_smooth"
        ).shift(RIGHT * 4)
        
        # 添加标签
        label_jagged = Text("Jagged", font_size=24, color=RED).next_to(tail_jagged, DOWN, buff=0.5)
        label_approx = Text("Approx Smooth", font_size=24, color=GREEN).next_to(tail_approx, DOWN, buff=0.5)
        label_true = Text("True Smooth", font_size=24, color=BLUE).next_to(tail_true, DOWN, buff=0.5)
        
        self.add(tail_jagged, tail_approx, tail_true)
        self.add(label_jagged, label_approx, label_true)
        
        # 添加更新器
        def update_all(dt):
            self.time += dt
            tail_jagged.update_tail(dt)
            tail_approx.update_tail(dt)
            tail_true.update_tail(dt)
        
        # 创建一个空的mobject来承载updater
        updater_mob = Mobject()
        updater_mob.add_updater(lambda m, dt: update_all(dt))
        self.add(updater_mob)
        
        self.wait(10)  # 观察10秒钟的轨迹
        
        # 演示动态切换平滑模式
        tail_jagged.set_smoothing_mode("true_smooth")
        tail_true.set_smoothing_mode("jagged")
        
        self.wait(5)  # 再观察5秒

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    os.system(f"cd {script_dir} && manimgl {script_name}.py")