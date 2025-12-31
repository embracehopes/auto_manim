"""
GlowDot 呼吸效果模块
提供多种呼吸效果的工厂函数，可集成到 AutoScene 中使用
"""

from manimlib import *
import numpy as np


class BreathingMode:
    """GlowDot 呼吸模式"""
    BASIC = "basic"           # 基础呼吸 - 正弦 + smooth 缓动
    RAINBOW = "rainbow"       # 七色彩虹 - 彩虹色循环 + 大小变化
    HEARTBEAT = "heartbeat"   # 心跳效果 - 双脉冲模式
    PULSE = "pulse"           # 辉光脉冲 - 快速脉冲
    WAVE = "wave"             # 波浪呼吸 - 三角波 + 相位


# 默认配置
BREATHING_FREQUENCY = 0.8      # 默认呼吸频率 (Hz)
BREATHING_MIN_RADIUS = 0.2     # 最小半径
BREATHING_MAX_RADIUS = 0.5     # 最大半径
BREATHING_GLOW_FACTOR = 1.0    # 辉光强度（固定为1）

# 彩虹色盘（七色循环）
BREATHING_RAINBOW_COLORS = [
    "#FF0000",  # 红
    "#FF7F00",  # 橙
    "#FFFF00",  # 黄
    "#00FF00",  # 绿
    "#00FFFF",  # 青
    "#0000FF",  # 蓝
    "#8B00FF",  # 紫
]


def _heartbeat_pattern(t, rate=1.0):
    """心跳双脉冲模式"""
    cycle_time = 1.0 / rate
    t_in_cycle = t % cycle_time
    normalized_t = t_in_cycle / cycle_time
    
    if normalized_t < 0.15:
        return smooth(normalized_t / 0.15)
    elif normalized_t < 0.25:
        return smooth(1 - (normalized_t - 0.15) / 0.1)
    elif normalized_t < 0.35:
        return smooth((normalized_t - 0.25) / 0.1) * 0.7
    elif normalized_t < 0.45:
        return smooth((1 - (normalized_t - 0.35) / 0.1)) * 0.7
    else:
        return 0.0


def create_breathing_updater(
    mode,
    frequency=BREATHING_FREQUENCY,
    min_radius=BREATHING_MIN_RADIUS,
    max_radius=BREATHING_MAX_RADIUS,
    rainbow_colors=None,
    color_start=BLUE,
    color_end=PURPLE,
):
    """
    创建呼吸效果更新器
    
    Args:
        mode: 呼吸模式 (BreathingMode 常量)
        frequency: 呼吸频率 (Hz)
        min_radius: 最小半径
        max_radius: 最大半径
        rainbow_colors: 彩虹色列表（用于 RAINBOW 模式）
        color_start: 起始颜色（用于非彩虹模式）
        color_end: 结束颜色（用于非彩虹模式）
    
    Returns:
        (updater_func, time_tracker): 更新器函数和时间追踪器
    """
    if rainbow_colors is None:
        rainbow_colors = BREATHING_RAINBOW_COLORS
    
    # 创建时间追踪器
    time_tracker = {"t": 0.0}
    
    if mode == BreathingMode.BASIC:
        def updater(mob, dt):
            time_tracker["t"] += dt
            t = time_tracker["t"]
            phase = (np.sin(t * frequency * TAU) + 1) / 2
            smoothed = smooth(phase)
            mob.set_radius(interpolate(min_radius, max_radius, smoothed))
        return updater, time_tracker
    
    elif mode == BreathingMode.RAINBOW:
        def updater(mob, dt):
            time_tracker["t"] += dt
            t = time_tracker["t"]
            
            # 大小变化
            phase = (np.sin(t * frequency * TAU) + 1) / 2
            smoothed = smooth(phase)
            mob.set_radius(interpolate(min_radius, max_radius, smoothed))
            
            # 七色循环 - 慢速循环，周期约 5 秒
            color_cycle_speed = 0.2  # 颜色循环速度
            color_position = (t * color_cycle_speed) % 1.0
            n_colors = len(rainbow_colors)
            
            # 计算当前颜色索引和插值
            scaled_pos = color_position * n_colors
            idx1 = int(scaled_pos) % n_colors
            idx2 = (idx1 + 1) % n_colors
            local_t = scaled_pos - int(scaled_pos)
            
            current_color = interpolate_color(
                rainbow_colors[idx1], 
                rainbow_colors[idx2], 
                local_t
            )
            mob.set_color(current_color)
        return updater, time_tracker
    
    elif mode == BreathingMode.HEARTBEAT:
        def updater(mob, dt):
            time_tracker["t"] += dt
            t = time_tracker["t"]
            pulse = _heartbeat_pattern(t, rate=1.0)
            mob.set_radius(interpolate(min_radius, max_radius, pulse))
        return updater, time_tracker
    
    elif mode == BreathingMode.PULSE:
        def updater(mob, dt):
            time_tracker["t"] += dt
            t = time_tracker["t"]
            freq = 2.0  # 快速脉冲
            phase = (np.sin(t * freq * TAU) + 1) / 2
            # 使用更尖锐的曲线
            sharp = phase ** 2
            mob.set_radius(interpolate(min_radius, max_radius, sharp))
        return updater, time_tracker
    
    elif mode == BreathingMode.WAVE:
        def updater(mob, dt):
            time_tracker["t"] += dt
            t = time_tracker["t"]
            freq = 0.7
            # 使用三角波而非正弦波
            wave = abs((t * freq) % 2 - 1)  # 三角波 0->1->0
            smoothed = smooth(wave)
            mob.set_radius(interpolate(min_radius, max_radius, smoothed))
        return updater, time_tracker
    
    else:
        raise ValueError(f"Unknown breathing mode: {mode}")


def create_breathing_glow_dot(
    center=ORIGIN,
    mode=BreathingMode.BASIC,
    color=BLUE,
    radius=0.35,
    glow_factor=BREATHING_GLOW_FACTOR,
    frequency=BREATHING_FREQUENCY,
    min_radius=BREATHING_MIN_RADIUS,
    max_radius=BREATHING_MAX_RADIUS,
    rainbow_colors=None,
    auto_start=True,
):
    """
    创建带呼吸效果的 GlowDot
    
    Args:
        center: 中心位置
        mode: 呼吸模式
        color: 初始颜色
        radius: 初始半径
        glow_factor: 辉光强度
        frequency: 呼吸频率
        min_radius: 最小半径
        max_radius: 最大半径
        rainbow_colors: 彩虹色列表（仅用于 RAINBOW 模式）
        auto_start: 是否自动添加更新器
    
    Returns:
        GlowDot: 带呼吸效果的辉光点
    """
    dot = GlowDot(
        center=center,
        radius=radius,
        color=color,
        glow_factor=glow_factor,
    )
    
    if auto_start:
        updater, _ = create_breathing_updater(
            mode=mode,
            frequency=frequency,
            min_radius=min_radius,
            max_radius=max_radius,
            rainbow_colors=rainbow_colors,
        )
        dot.add_updater(updater)
    
    # 存储模式信息以供查询
    dot._breathing_mode = mode
    
    return dot


# 呼吸模式循环管理器
class BreathingModeManager:
    """管理呼吸模式的循环选择"""
    
    def __init__(self):
        self._modes = [
            BreathingMode.BASIC,
            BreathingMode.RAINBOW,
            BreathingMode.HEARTBEAT,
            BreathingMode.PULSE,
            BreathingMode.WAVE,
        ]
        self._index = 0
    
    def next_mode(self):
        """返回下一个呼吸模式（循环）"""
        mode = self._modes[self._index]
        self._index = (self._index + 1) % len(self._modes)
        return mode
    
    def current_mode(self):
        """返回当前呼吸模式"""
        return self._modes[self._index]
    
    def reset(self):
        """重置到第一个模式"""
        self._index = 0
    
    def get_all_modes(self):
        """返回所有模式列表"""
        return self._modes.copy()


# 全局管理器实例
_breathing_manager = BreathingModeManager()


def next_breathing_mode():
    """返回下一个呼吸模式（全局循环）"""
    return _breathing_manager.next_mode()


def reset_breathing_mode():
    """重置呼吸模式循环"""
    _breathing_manager.reset()
