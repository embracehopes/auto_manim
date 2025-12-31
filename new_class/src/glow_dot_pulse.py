"""
GlowDot 呼吸效果演示
使用 breathing_effects 模块展示多种呼吸效果
"""

from manimlib import *
import numpy as np
import sys
from pathlib import Path

# 添加 src 目录到路径
_this = Path(__file__).resolve()
if str(_this.parent) not in sys.path:
    sys.path.insert(0, str(_this.parent))

from breathing_effects import (
    BreathingMode,
    create_breathing_glow_dot,
    create_breathing_updater,
    next_breathing_mode,
    reset_breathing_mode,
    BREATHING_RAINBOW_COLORS,
)


class GlowDotBreathingShowcase(Scene):
    """
    GlowDot 呼吸效果综合展示
    在一个场景中同时展示 5 种呼吸效果
    左边放 GlowDot，右边放名称标签
    """
    
    def construct(self):
        # ========== 布局参数 ==========
        LEFT_X = -4.0      # GlowDot 的 x 坐标
        RIGHT_X = -1.5     # 标签的 x 坐标
        START_Y = 2.5      # 起始 y 坐标
        SPACING_Y = 1.3    # 每行间距
        
        # ========== 效果定义 ==========
        effects = [
            {
                "name": "基础呼吸 (Basic)",
                "mode": BreathingMode.BASIC,
                "color": BLUE,
                "desc": "正弦 + smooth 缓动"
            },
            {
                "name": "七色彩虹 (Rainbow)",
                "mode": BreathingMode.RAINBOW,
                "color": BREATHING_RAINBOW_COLORS[0],
                "desc": "彩虹色循环 + 大小变化"
            },
            {
                "name": "心跳效果 (Heartbeat)",
                "mode": BreathingMode.HEARTBEAT,
                "color": RED,
                "desc": "双脉冲模式"
            },
            {
                "name": "辉光脉冲 (Pulse)",
                "mode": BreathingMode.PULSE,
                "color": YELLOW,
                "desc": "快速脉冲"
            },
            {
                "name": "波浪呼吸 (Wave)",
                "mode": BreathingMode.WAVE,
                "color": GREEN,
                "desc": "三角波 + 相位"
            },
        ]
        
        # ========== 创建所有 GlowDot 和标签 ==========
        glow_dots = []
        
        for i, effect in enumerate(effects):
            y_pos = START_Y - i * SPACING_Y
            
            # 使用工厂函数创建带呼吸效果的 GlowDot
            dot = create_breathing_glow_dot(
                center=np.array([LEFT_X, y_pos, 0]),
                mode=effect["mode"],
                color=effect["color"],
                radius=0.35,
                glow_factor=1.0,  # 辉光强度固定为 1
            )
            glow_dots.append(dot)
            self.add(dot)
            
            # 创建名称标签
            label = Text(
                effect["name"],
                font="Microsoft YaHei",
                font_size=24,
                color=WHITE,
            )
            label.move_to(np.array([RIGHT_X + label.get_width() / 2, y_pos, 0]))
            self.add(label)
            
            # 创建描述标签（小字）
            desc = Text(
                effect["desc"],
                font="Microsoft YaHei",
                font_size=16,
                color=GREY_B,
            )
            desc.next_to(label, RIGHT, buff=0.3)
            self.add(desc)
        
        # ========== 添加标题 ==========
        title = Text(
            "GlowDot 呼吸效果展示",
            font="Microsoft YaHei",
            font_size=36,
            color=WHITE,
        )
        title.to_edge(UP, buff=0.3)
        self.add(title)
        
        # ========== 等待动画 ==========
        self.wait(15)


class CyclingBreathingDemo(Scene):
    """
    演示呼吸模式循环使用
    每隔几秒切换到下一个呼吸模式
    """
    
    def construct(self):
        # 重置模式循环
        reset_breathing_mode()
        
        # 创建一个中心辉光点
        center_dot = GlowDot(
            center=ORIGIN,
            radius=0.5,
            color=BLUE,
            glow_factor=1.0,
        )
        self.add(center_dot)
        
        # 模式名称标签
        mode_label = Text(
            "模式: Basic",
            font="Microsoft YaHei",
            font_size=28,
            color=WHITE,
        )
        mode_label.to_edge(UP, buff=0.5)
        self.add(mode_label)
        
        # 循环展示每种模式
        modes_info = [
            (BreathingMode.BASIC, "Basic - 基础呼吸", BLUE),
            (BreathingMode.RAINBOW, "Rainbow - 七色彩虹", "#FF0000"),
            (BreathingMode.HEARTBEAT, "Heartbeat - 心跳效果", RED),
            (BreathingMode.PULSE, "Pulse - 辉光脉冲", YELLOW),
            (BreathingMode.WAVE, "Wave - 波浪呼吸", GREEN),
        ]
        
        for mode, name, color in modes_info:
            # 更新标签
            new_label = Text(
                f"模式: {name}",
                font="Microsoft YaHei",
                font_size=28,
                color=WHITE,
            )
            new_label.to_edge(UP, buff=0.5)
            self.play(Transform(mode_label, new_label), run_time=0.3)
            
            # 设置颜色
            center_dot.set_color(color)
            
            # 清除旧的更新器
            center_dot.clear_updaters()
            
            # 添加新的呼吸更新器
            updater, _ = create_breathing_updater(
                mode=mode,
                min_radius=0.3,
                max_radius=0.7,
            )
            center_dot.add_updater(updater)
            
            # 等待展示
            self.wait(4)
        
        # 清理
        center_dot.clear_updaters()


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    # 运行综合展示
    os.system(f"cd {script_dir} && manimgl {script_name}.py GlowDotBreathingShowcase")
