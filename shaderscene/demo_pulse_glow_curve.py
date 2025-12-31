"""
脉冲辉光曲线演示
展示GlowCurve的脉冲效果功能
"""

from manimlib import *
import numpy as np
import sys
from pathlib import Path

# 添加 shaderscene 到路径
_this = Path(__file__).resolve()
for parent in _this.parents:
    if (parent / 'shaderscene').exists():
        sys.path.insert(0, str(parent))
        break

from shaderscene.mobject.glow_curve import (
    GlowCurve,
    GlowFunctionGraph,
    GlowCircle,
    GlowSpiral,
)


class BasicPulseDemo(Scene):
    """基础脉冲效果演示"""
    def construct(self):
        # 创建一个正弦曲线
        curve = GlowFunctionGraph(
            lambda x: 1.5 * np.sin(x),
            x_range=[-PI, PI],
            color=BLUE,
            glow_width=0.4,
        )
        
        # 启用脉冲
        curve.enable_pulse(frequency=1.0, amplitude=5.0)
        
        self.add(curve)
        self.wait(5)


class MultiFrequencyPulseDemo(Scene):
    """多频率脉冲演示"""
    def construct(self):
        # 创建多个不同频率的曲线
        colors = [RED, YELLOW, GREEN, BLUE, PURPLE]
        frequencies = [0.5, 1.0, 1.5, 2.0, 2.5]
        
        curves = VGroup()
        for i, (color, freq) in enumerate(zip(colors, frequencies)):
            curve = GlowFunctionGraph(
                lambda x, i=i: 2.0 * np.sin(x) + (i - 2) * 0.8,
                x_range=[-PI, PI],
                color=color,
                glow_width=0.1,
            )
            curve.enable_pulse(frequency=freq, amplitude=0.4)
            curves.add(curve)
        
        # 添加标签说明频率
        labels = VGroup()
        for i, freq in enumerate(frequencies):
            label = Text(f"{freq}Hz", font_size=24, color=colors[i])
            label.next_to(curves[i], LEFT)
            labels.add(label)
        
        self.add(curves, labels)
        self.wait(8)


class CircularPulseDemo(Scene):
    """圆形脉冲演示"""
    def construct(self):
        # 创建多个同心圆，不同脉冲参数
        circles = VGroup()
        radii = [0.5, 1.0, 1.5, 2.0, 2.5]
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE]
        
        for radius, color in zip(radii, colors):
            circle = GlowCircle(
                radius=radius,
                color=color,
                glow_width=0.12,
                n_samples=200,
            )
            circle.enable_pulse(frequency=1.0, amplitude=0.6)
            circles.add(circle)
        
        self.add(circles)
        self.wait(6)


class SpiralPulseDemo(Scene):
    """螺旋脉冲演示"""
    def construct(self):
        # 创建螺旋线并应用脉冲
        spiral = GlowSpiral(
            max_radius=3.0,
            n_loops=4,
            color=TEAL,
            glow_width=0.15,
            n_samples=800,
        )
        spiral.enable_pulse(frequency=1.5, amplitude=0.5)
        
        self.add(spiral)
        self.wait(8)


class ParametricPulseDemo(Scene):
    """参数曲线脉冲演示"""
    def construct(self):
        # 利萨茹曲线
        lissajous = GlowCurve(
            function=lambda t: np.array([
                2.5 * np.sin(3 * t),
                2.5 * np.sin(4 * t),
                0
            ]),
            t_range=[0, TAU],
            color=PINK,
            glow_width=0.12,
            n_samples=600,
        )
        lissajous.enable_pulse(frequency=2.0, amplitude=0.5)
        
        self.add(lissajous)
        self.wait(6)


class SynchronizedPulseDemo(Scene):
    """同步脉冲演示"""
    def construct(self):
        # 创建多条曲线，同步脉冲
        curves = VGroup()
        
        for i in range(5):
            curve = GlowFunctionGraph(
                lambda x, i=i: 1.5 * np.sin(x + i * PI / 5),
                x_range=[-PI, PI],
                color=interpolate_color(RED, BLUE, i / 4),
                glow_width=0.1,
            )
            curve.shift(UP * (2 - i))
            curve.enable_pulse(frequency=1.5, amplitude=0.6)
            curves.add(curve)
        
        self.add(curves)
        self.wait(6)


class AmplitudeVariationDemo(Scene):
    """不同振幅脉冲演示"""
    def construct(self):
        # 创建多个圆，不同脉冲振幅
        amplitudes = [0.2, 0.4, 0.6, 0.8]
        colors = [RED, YELLOW, GREEN, BLUE]
        
        circles = VGroup()
        for i, (amp, color) in enumerate(zip(amplitudes, colors)):
            circle = GlowCircle(
                radius=1.5,
                color=color,
                glow_width=0.15,
                n_samples=200,
            )
            circle.shift(LEFT * 4.5 + RIGHT * i * 3)
            circle.enable_pulse(frequency=1.0, amplitude=amp)
            circles.add(circle)
            
            # 添加振幅标签
            label = Text(f"A={amp}", font_size=24, color=color)
            label.next_to(circle, DOWN, buff=0.3)
            self.add(label)
        
        self.add(circles)
        self.wait(6)


class HeartPulseDemo(Scene):
    """心形脉冲演示（模拟心跳）"""
    def construct(self):
        # 心形曲线
        def heart_function(t):
            x = 16 * np.sin(t) ** 3
            y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
            return np.array([x * 0.15, y * 0.15, 0])
        
        heart = GlowCurve(
            function=heart_function,
            t_range=[0, TAU],
            color=RED,
            glow_width=0.15,
            n_samples=500,
        )
        
        # 模拟心跳：快速脉冲
        heart.enable_pulse(frequency=1.2, amplitude=0.7)
        
        self.add(heart)
        self.wait(8)


class PhaseShiftedPulseDemo(Scene):
    """相位偏移脉冲演示"""
    def construct(self):
        # 创建三个圆，使用不同的初始相位模拟相位偏移
        circles = VGroup()
        colors = [RED, GREEN, BLUE]
        
        for i, color in enumerate(colors):
            circle = GlowCircle(
                radius=1.2,
                color=color,
                glow_width=0.12,
                n_samples=200,
            )
            # 通过调整初始pulse_time模拟相位偏移
            circle._pulse_time = i * TAU / 3  # 120度相位差
            circle.enable_pulse(frequency=1.0, amplitude=0.6)
            
            # 排列成三角形
            angle = i * TAU / 3
            circle.shift(1.8 * np.array([np.cos(angle), np.sin(angle), 0]))
            circles.add(circle)
        
        self.add(circles)
        self.wait(6)


class DynamicPulseControlDemo(Scene):
    """动态脉冲控制演示"""
    def construct(self):
        # 创建一个可以动态改变脉冲参数的曲线
        curve = GlowCircle(
            radius=2.0,
            color=TEAL,
            glow_width=0.15,
            n_samples=300,
        )
        curve.enable_pulse(frequency=1.0, amplitude=0.5)
        
        # 频率标签
        freq_label = DecimalNumber(
            1.0,
            num_decimal_places=1,
            unit="Hz",
            font_size=36,
        )
        freq_label.to_corner(UL)
        freq_text = Text("频率: ", font_size=36)
        freq_text.next_to(freq_label, LEFT)
        
        self.add(curve, freq_text, freq_label)
        
        # 动态改变频率
        for target_freq in [1.0, 2.0, 3.0, 1.5, 0.5, 1.0]:
            self.play(
                curve.animate.set_pulse_frequency(target_freq),
                ChangeDecimalToValue(freq_label, target_freq),
                run_time=2,
            )
            self.wait(1)


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  BasicPulseDemo")