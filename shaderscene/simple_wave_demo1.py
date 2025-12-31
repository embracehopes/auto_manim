"""
简化的动态波纹效果演示

该文件展示了基于原始 LightWaveSlice 类的动态效果演示，
避免了复杂的自定义 Shader 实现，专注于展示基础的光波干涉效果。
"""

from __future__ import annotations
from manimlib import *
import numpy as np
import sys
import os

# 添加当前目录到 Python 路径以便导入
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 导入衍射模块
from mobject.diffraction import LightWaveSlice


class SimpleDynamicWaveDemo(InteractiveScene):
    """
    简化的动态波纹演示场景
    
    使用原始的 LightWaveSlice 类展示：
    1. 单波源效果
    2. 双波源干涉
    3. 多波源复杂干涉
    4. 动态参数调节
    """
    
    def construct(self):
        # 场景标题
        title = Text("光波干涉效果演示", font_size=48)
        title.to_edge(UP)
        title.set_color_by_gradient(BLUE, GREEN, YELLOW, RED)
        
        # 第一阶段：单波源
        self.add(title)
        
        subtitle1 = Text("单点光源", font_size=32)
        subtitle1.to_edge(UP, buff=1.5)
        
        sources1 = DotCloud([np.array([0.0, 0.0, 0.0])])
        wave1 = LightWaveSlice(
            point_sources=sources1,
            shape=(8.0, 6.0),
            color=BLUE,
            frequency=1.0,
            wave_number=2.0,
            opacity=0.7
        )
        
        self.play(
            Transform(title, subtitle1),
            FadeIn(wave1, run_time=2)
        )
        self.wait(3)
        
        # 第二阶段：双波源干涉
        subtitle2 = Text("双点光源干涉", font_size=32)
        subtitle2.to_edge(UP, buff=1.5)
        
        sources2 = DotCloud([
            np.array([-2.0, 0.0, 0.0]),
            np.array([2.0, 0.0, 0.0]),
        ])
        wave2 = LightWaveSlice(
            point_sources=sources2,
            shape=(8.0, 6.0),
            color=GREEN,
            frequency=1.2,
            wave_number=1.8,
            opacity=0.8
        )
        
        self.play(
            Transform(title, subtitle2),
            Transform(wave1, wave2, run_time=3)
        )
        self.wait(4)
        
        # 第三阶段：三波源复杂干涉
        subtitle3 = Text("三点光源复杂干涉", font_size=32)
        subtitle3.to_edge(UP, buff=1.5)
        
        sources3 = DotCloud([
            np.array([-2.0, -1.0, 0.0]),
            np.array([2.0, -1.0, 0.0]),
            np.array([0.0, 2.0, 0.0]),
        ])
        wave3 = LightWaveSlice(
            point_sources=sources3,
            shape=(10.0, 8.0),
            color=RED,
            frequency=0.8,
            wave_number=1.5,
            opacity=0.9
        )
        
        self.play(
            Transform(title, subtitle3),
            Transform(wave1, wave3, run_time=4)
        )
        self.wait(4)
        
        # 参数说明
        params_text = VGroup(
            Text("物理参数说明:", font_size=24, color=WHITE),
            Text("• 频率: 控制振荡速度", font_size=20, color=GREY_A),
            Text("• 波数: 控制波长密度", font_size=20, color=GREY_A),
            Text("• 颜色: 表示不同波长", font_size=20, color=GREY_A),
            Text("• 干涉: 波的叠加效应", font_size=20, color=GREY_A),
        )
        params_text.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        params_text.to_corner(UL)
        params_text.shift(DOWN + RIGHT * 0.5)
        
        self.play(Write(params_text, lag_ratio=0.3))
        self.wait(3)
        
        # 动态调整演示
        subtitle4 = Text("动态参数调节", font_size=32)
        subtitle4.to_edge(UP, buff=1.5)
        
        self.play(Transform(title, subtitle4))
        
        # 频率变化
        self.play(
            wave1.animate.set_frequency(2.5),
            run_time=3
        )
        self.wait(2)
        
        # 波数变化
        self.play(
            wave1.animate.set_wave_number(3.0),
            run_time=3
        )
        self.wait(2)
        
        # 颜色变化
        self.play(
            wave1.animate.set_color(PURPLE),
            run_time=2
        )
        self.wait(3)
        
        # 结束
        ending = Text("演示结束", font_size=48)
        ending.set_color_by_gradient(GOLD, YELLOW)
        
        self.play(
            *[FadeOut(obj) for obj in [wave1, params_text]],
            Transform(title, ending),
            run_time=2
        )
        self.wait(2)


class QuickWaveTest(Scene):
    """快速波效果测试"""
    def construct(self):
        sources = DotCloud([
            np.array([-1.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
        ])
        wave = LightWaveSlice(
            point_sources=sources,
            shape=(6.0, 4.0),
            color=BLUE,
            frequency=1.5,
            wave_number=2.0,
            opacity=0.8
        )
        
        title = Text("双波源干涉测试", font_size=36)
        title.to_edge(UP)
        
        self.add(title, wave)
        self.wait(8)
if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")