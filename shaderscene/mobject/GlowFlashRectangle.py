"""
智能发光闪烁矩形 - GlowFlashRectangle
基于 TracingTailPMobject 的高性能GPU渲染辉光边框动画
支持深色彩虹渐变、可调参数和无限循环
支持围绕任意 VMobject 边缘运动
"""

import numpy as np
from typing import Sequence
from manimlib import *
import sys
import os

# 添加当前目录到路径，以便导入其他模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from TracingTailPMobject import TracingTailPMobject
from glow_line import GlowLine

__all__ = ["GlowFlashRectangle", "GlowVMobjectTracer", "GlowSurroundingRect", "GlowRoundedRectangle", "StillSurroundingRect"]


def _refine_vmobject_corners(vmob: VMobject, refinement: int = 6, smooth_passes: int = 2) -> VMobject:
    """Insert extra curves and smoothing rounds to make rounded corners look cleaner."""
    if not isinstance(vmob, VMobject):
        return vmob
    refinement = max(int(refinement), 0)
    smooth_passes = max(int(smooth_passes), 0)
    if refinement > 0:
        vmob.insert_n_curves(refinement)
    if smooth_passes > 0:
        for _ in range(smooth_passes):
            vmob.make_smooth()
    return vmob


def calculate_rainbow_color(index, total_points, color_scheme="bright"):
    """计算彩虹渐变色"""
    progress = index / total_points
    
    if color_scheme == "dark":
        # 深色彩虹色调
        colors = [
            "#2D1B69",  # 深紫色
            "#4A0E4E",  # 深洋红
            "#8B0000",  # 深红色  
            "#B8860B",  # 深金色
            "#006400",  # 深绿色
            "#191970",  # 深蓝色
            "#4B0082",  # 深靛色
            "#2D1B69"   # 回到起始颜色形成循环
        ]
    elif color_scheme == "bright":
        # 明亮彩虹色调
        colors = [
            "#FF0080",  # 亮粉色
            "#FF4000",  # 橙红色
            "#FF8000",  # 橙色
            "#FFFF00",  # 黄色
            "#80FF00",  # 黄绿色
            "#00FF80",  # 青绿色
            "#0080FF",  # 蓝色
            "#8000FF",  # 紫色
            "#FF0080"   # 回到起始颜色
        ]
    elif color_scheme == "neon":
        # 霓虹色调
        colors = [
            "#FF006E",  # 霓虹粉
            "#FB5607",  # 霓虹橙
            "#FFBE0B",  # 霓虹黄
            "#8338EC",  # 霓虹紫
            "#3A86FF",  # 霓虹蓝
            "#06FFA5",  # 霓虹绿
            "#FF006E"   # 循环
        ]
    else:  # 自定义颜色数组
        colors = color_scheme if isinstance(color_scheme, list) else [RED, BLUE, GREEN, YELLOW]
    
    # 计算颜色段和插值
    num_segments = len(colors) - 1
    segment_idx = int(progress * num_segments)
    segment_idx = min(segment_idx, num_segments - 1)
    
    segment_progress = (progress * num_segments) - segment_idx
    
    color1 = colors[segment_idx]
    color2 = colors[segment_idx + 1]
    
    return interpolate_color(color1, color2, segment_progress)


class GlowFlashRectangle(Group):
    """
    智能发光闪烁矩形
    
    特性:
    - 深度可配置的参数
    - 多种颜色方案 (dark/bright/neon/custom)
    - 智能动画控制 (循环/单次/自定义)
    - 高性能GPU渲染
    - 动态轨迹效果
    """
    
    def __init__(
        self,
        width: float = 8,
        height: float = 5,
        corner_radius: float = 0.8,
        corner_refinement: int = 8,
        corner_smooth_passes: int = 2,
        
        # 点和轨迹配置
        num_points: int = 8,
        dot_radius: float = 0.02,
        
        # 颜色配置
        color_scheme: str = "bright",  # "dark", "bright", "neon", 或自定义颜色列表
        
        # 轨迹效果配置
        tail_length: int = 80,
        tail_lifetime: float = 3.0,
        opacity_fade: tuple = (0.9, 0.0),
        width_fade: tuple = (0.08, 0.02),
        glow_factor: float = 3.0,
        tail_debug_logging: bool = False,
        tail_debug_names: Sequence[str] | None = None,
        
        # 动画配置
        speed: float = 6.0,  # 动画时长（秒）
        rate_function = None,  # 动画速率函数
        
        # 显示配置
        show_dots: bool = True,
        show_rectangle: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # 保存配置参数
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.num_points = num_points
        self.dot_radius = dot_radius
        self.color_scheme = color_scheme
        self.tail_length = tail_length
        self.tail_lifetime = tail_lifetime
        self.opacity_fade = opacity_fade
        self.width_fade = width_fade
        self.glow_factor = glow_factor
        self.tail_debug_logging = tail_debug_logging
        self.tail_debug_names = list(tail_debug_names) if tail_debug_names is not None else None
        self.speed = speed
        self.rate_function = rate_function or linear
        self.show_dots = show_dots
        self.show_rectangle = show_rectangle
        self.corner_refinement = corner_refinement
        self.corner_smooth_passes = corner_smooth_passes
        
        # 创建基础路径
        self.path = RoundedRectangle(
            width=width, 
            height=height, 
            corner_radius=corner_radius
        )
        _refine_vmobject_corners(self.path, self.corner_refinement, self.corner_smooth_passes)
        
        # 存储组件
        self.dots = []
        self.traces = []
        self.animations = []
        
        # 初始化组件
        self._create_components()
        
        # 添加到组中
        self._add_to_group()
    
    def _create_components(self):
        """创建所有点、轨迹和动画组件"""
        
        # 使用函数工厂彻底解决闭包问题
        def make_traced_point_func(target_dot):
            """为每个点创建独立的追踪函数"""
            return lambda: target_dot.get_center()
        
        def make_updater_func(target_trace):
            """为每个轨迹创建独立的更新器函数 - 关键修复！"""
            return lambda mob, dt: target_trace.update_tail(dt)
        
        # 创建所有组件
        for i in range(self.num_points):
            # 重要修复：避开首尾连接点，使用 0.5 的偏移确保均匀分布
            start_t = (i + 0.5) / self.num_points
            start_point = self.path.point_from_proportion(start_t)
            
            # 计算颜色
            current_color = calculate_rainbow_color(i, self.num_points, self.color_scheme)
            
            # 创建点
            dot = Dot(radius=self.dot_radius, color=current_color).move_to(start_point)
            
            # 已移除调试输出
            
            # 创建动画 - 支持自定义速率函数
            if hasattr(self.rate_function, '__call__'):
                # 如果是函数，应用偏移
                rate_func = lambda t, st=start_t: (self.rate_function(t) + st) % 1
            else:
                # 默认线性
                rate_func = lambda t, st=start_t: (t + st) % 1
            
            anim = MoveAlongPath(
                dot,
                self.path,
                rate_func=rate_func,
                run_time=self.speed
            )
            
            # 使用工厂函数创建轨迹追踪函数
            traced_func = make_traced_point_func(dot)
            debug_name = None
            if self.tail_debug_names is not None and i < len(self.tail_debug_names):
                debug_name = self.tail_debug_names[i]
            else:
                debug_name = f"trace#{i}"
            
            # 为边界点设置更宽松的传送阈值
            is_boundary = (i == 0 or i == self.num_points - 1)
            teleport_threshold = 10.0 if is_boundary else 0.6
            
            trace = TracingTailPMobject(
                traced_point_func=traced_func,
                base_color=current_color,
                max_tail_length=self.tail_length,
                tail_lifetime=self.tail_lifetime,
                opacity_fade=self.opacity_fade,
                width_fade=self.width_fade,
                glow_factor=self.glow_factor,
                teleport_min_threshold=teleport_threshold,
                debug_name=debug_name,
                debug_logging=self.tail_debug_logging
            )
            
            # 调试信息已移除
            
            # 使用工厂函数创建独立的更新器 - 这是关键！
            updater_func = make_updater_func(trace)
            trace.add_updater(updater_func)
            
            # 更新器已添加（调试信息已移除）
            
            self.dots.append(dot)
            self.animations.append(anim)
            self.traces.append(trace)
            
            # 验证追踪函数（静默）
            _ = traced_func()
        
    # 完成组件创建（调试输出已移除）
    
    def _add_to_group(self):
        """将组件添加到VGroup中"""
        # 总是添加轨迹
        self.add(*self.traces)
        
        # 可选：添加点
        if self.show_dots:
            self.add(*self.dots)
        
        # 可选：添加矩形框架
        if self.show_rectangle:
            self.path.set_stroke(opacity=0.3)
            self.add(self.path)
    
    def start_animation(self, scene, loop=False, loop_delay=0.1):
        """
        开始动画
        
        Args:
            scene: Manim场景对象
            loop: 是否循环播放
            loop_delay: 循环间隔时间
        """
        if loop:
            # 无限循环模式
            while True:
                scene.play(*self.animations)
                if loop_delay > 0:
                    scene.wait(loop_delay)
        else:
            # 单次播放
            scene.play(*self.animations)
    
    def update_colors(self, new_color_scheme):
        """动态更新颜色方案"""
        self.color_scheme = new_color_scheme
        
        for i, (dot, trace) in enumerate(zip(self.dots, self.traces)):
            new_color = calculate_rainbow_color(i, self.num_points, new_color_scheme)
            dot.set_color(new_color)
            trace.base_color = new_color
    
    def update_speed(self, new_speed):
        """动态更新动画速度"""
        self.speed = new_speed
        for anim in self.animations:
            anim.run_time = new_speed
    
    def clear_trails(self):
        """清除所有轨迹"""
        for trace in self.traces:
            trace.tail_points.clear()
            trace.tail_times.clear()
    
    def set_glow_intensity(self, intensity):
        """设置辉光强度"""
        self.glow_factor = intensity
        for trace in self.traces:
            trace.glow_factor = intensity
    
    def get_animation_group(self):
        """获取动画组，用于与其他动画组合"""
        return AnimationGroup(*self.animations)


# 预设配置类
class PresetGlowRectangles:
    """预设的发光矩形配置"""
    
    @staticmethod
    def neon_small():
        """小型霓虹矩形"""
        return GlowFlashRectangle(
            width=4, height=2.5, corner_radius=0.3,
            num_points=6, dot_radius=0.015,
            color_scheme="neon", speed=4.0,
            tail_length=25, glow_factor=4.0
        )
    
    @staticmethod
    def dark_large():
        """大型深色矩形"""
        return GlowFlashRectangle(
            width=10, height=6, corner_radius=1.0,
            num_points=12, dot_radius=0.025,
            color_scheme="dark", speed=8.0,
            tail_length=50, glow_factor=2.5
        )
    
    @staticmethod
    def bright_medium():
        """中型明亮矩形"""
        return GlowFlashRectangle(
            width=6, height=4, corner_radius=0.5,
            num_points=8, dot_radius=0.02,
            color_scheme="bright", speed=5.0,
            tail_length=35, glow_factor=3.5
        )
    
    @staticmethod
    def custom_rainbow():
        """自定义彩虹矩形"""
        custom_colors = [
            "#FF1493", "#FF4500", "#FFD700", "#ADFF2F", 
            "#00CED1", "#1E90FF", "#9932CC", "#FF1493"
        ]
        return GlowFlashRectangle(
            width=8, height=5, corner_radius=0.8,
            num_points=10, dot_radius=0.02,
            color_scheme=custom_colors, speed=6.0,
            rate_function=smooth,  # 使用smooth速率函数
            tail_length=40, glow_factor=3.0
        )


class GlowVMobjectTracer(Group):
    """
    围绕任意 VMobject 边缘运动的发光轨迹追踪器
    
    特性:
    - 支持任意 VMobject 的边缘追踪
    - 动态更新适应 VMobject 的变换
    - 多点同步运动，彩虹渐变色
    - 高性能 GPU 渲染辉光效果
    - 可调参数和动画控制
    """
    
    def __init__(
        self,
        vmobject: VMobject,
        
        # 点和轨迹配置
        num_points: int = 8,
        dot_radius: float = 0.02,
        
        # 颜色配置
        color_scheme: str = "bright",  # "dark", "bright", "neon", 或自定义颜色列表
        
        # 轨迹效果配置
        tail_length: int = 80,
        tail_lifetime: float = 3.0,
        opacity_fade: tuple = (0.9, 0.0),
        width_fade: tuple = (0.08, 0.02),
        glow_factor: float = 3.0,
        tail_debug_logging: bool = False,
        tail_debug_names: Sequence[str] | None = None,
        
        # 动画配置
        speed: float = 1.0,  # 运动速度系数
        time_per_cycle: float = 6.0,  # 完整循环一周的时间
        rate_function = None,  # 动画速率函数
        
        # 显示配置
        show_dots: bool = True,
        auto_update: bool = True,  # 是否自动更新位置
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # 保存配置参数
        self.vmobject = vmobject
        self.num_points = num_points
        self.dot_radius = dot_radius
        self.color_scheme = color_scheme
        self.tail_length = tail_length
        self.tail_lifetime = tail_lifetime
        self.opacity_fade = opacity_fade
        self.width_fade = width_fade
        self.glow_factor = glow_factor
        self.tail_debug_logging = tail_debug_logging
        self.tail_debug_names = list(tail_debug_names) if tail_debug_names is not None else None
        self.speed = speed
        self.time_per_cycle = time_per_cycle
        self.rate_function = rate_function or linear
        self.show_dots = show_dots
        self.auto_update = auto_update
        
        # 内部状态
        self.time = 0.0
        self.dots = []
        self.traces = []
        
        # 初始化组件
        self._create_components()
        
        # 添加到组中
        self._add_to_group()
        
        # 添加自动更新器
        if self.auto_update:
            self.add_updater(lambda mob, dt: mob.update_positions(dt))
    
    def _create_components(self):
        """创建所有点和轨迹组件"""
        
        # 使用函数工厂彻底解决闭包问题
        def make_traced_point_func(target_dot):
            """为每个点创建独立的追踪函数"""
            return lambda: target_dot.get_center()
        
        def make_updater_func(target_trace):
            """为每个轨迹创建独立的更新器函数 - 关键修复！"""
            return lambda mob, dt: target_trace.update_tail(dt)
        
        for i in range(self.num_points):
            # 重要修复：避开首尾连接点，使用 0.5 的偏移
            start_alpha = (i + 0.5) / self.num_points
            start_point = self.vmobject.point_from_proportion(start_alpha)
            
            # 计算颜色
            current_color = calculate_rainbow_color(i, self.num_points, self.color_scheme)
            
            # 创建点
            dot = Dot(radius=self.dot_radius, color=current_color).move_to(start_point)
            
            # 调试输出已移除
            
            # 使用工厂函数创建轨迹追踪函数
            traced_func = make_traced_point_func(dot)
            
            # 为边界点设置更宽松的传送阈值
            is_boundary = (i == 0 or i == self.num_points - 1)
            teleport_threshold = 10.0 if is_boundary else 0.6
            
            trace = TracingTailPMobject(
                traced_point_func=traced_func,
                base_color=current_color,
                max_tail_length=self.tail_length,
                tail_lifetime=self.tail_lifetime,
                opacity_fade=self.opacity_fade,
                width_fade=self.width_fade,
                glow_factor=self.glow_factor,
                teleport_min_threshold=teleport_threshold
            )
            
            # 调试输出已移除
            
            # 使用工厂函数创建独立的更新器 - 这是关键！
            updater_func = make_updater_func(trace)
            trace.add_updater(updater_func)
            
            # 更新器已添加（调试信息已移除）
            
            self.dots.append(dot)
            self.traces.append(trace)
            
            # 验证追踪函数（静默）
            _ = traced_func()
        
    # 完成组件创建（调试输出已移除）
    
    def _add_to_group(self):
        """将组件添加到 Group 中"""
        # 总是添加轨迹
        self.add(*self.traces)
        
        # 可选：添加点
        if self.show_dots:
            self.add(*self.dots)
    
    def update_positions(self, dt: float):
        """更新所有点的位置（主要更新逻辑）"""
        if dt == 0:
            return self
        
        # 更新时间
        self.time += dt * self.speed
        
        # 计算当前周期进度 [0, 1]
        cycle_progress = (self.time / self.time_per_cycle) % 1.0
        
        # 应用速率函数
        if hasattr(self.rate_function, '__call__'):
            cycle_progress = self.rate_function(cycle_progress)
        
        # 更新每个点的位置
        for i, dot in enumerate(self.dots):
            # 计算该点在路径上的位置（带偏移）
            point_offset = i / self.num_points
            alpha = (cycle_progress + point_offset) % 1.0
            
            # 从 VMobject 获取对应位置的点
            new_position = self.vmobject.point_from_proportion(alpha)
            
            # 更新点的位置
            dot.move_to(new_position)
        
        return self
    
    def update_colors(self, new_color_scheme):
        """动态更新颜色方案"""
        self.color_scheme = new_color_scheme
        
        for i, (dot, trace) in enumerate(zip(self.dots, self.traces)):
            new_color = calculate_rainbow_color(i, self.num_points, new_color_scheme)
            dot.set_color(new_color)
            trace.base_color = new_color
    
    def update_speed(self, new_speed):
        """动态更新运动速度"""
        self.speed = new_speed
    
    def update_cycle_time(self, new_time):
        """更新完整循环时间"""
        self.time_per_cycle = new_time
    
    def clear_trails(self):
        """清除所有轨迹"""
        for trace in self.traces:
            trace.tail_points.clear()
            trace.tail_times.clear()
    
    def set_glow_intensity(self, intensity):
        """设置辉光强度"""
        self.glow_factor = intensity
        for trace in self.traces:
            trace.glow_factor = intensity
    
    def reset_time(self):
        """重置时间"""
        self.time = 0.0
    
    def pause(self):
        """暂停动画（移除更新器）"""
        self.clear_updaters()
    
    def resume(self):
        """恢复动画（重新添加更新器）"""
        if self.auto_update:
            self.clear_updaters()
            self.add_updater(lambda mob, dt: mob.update_positions(dt))
    
    def set_vmobject(self, new_vmobject: VMobject, reset_time: bool = True):
        """更换追踪的 VMobject"""
        self.vmobject = new_vmobject
        if reset_time:
            self.reset_time()
        # 立即更新一次位置
        self.update_positions(0)


# 预设配置类 - GlowVMobjectTracer
class PresetGlowTracers:
    """预设的发光追踪器配置"""
    
    @staticmethod
    def neon_fast(vmobject: VMobject):
        """快速霓虹追踪器"""
        return GlowVMobjectTracer(
            vmobject=vmobject,
            num_points=6, dot_radius=0.015,
            color_scheme="neon", speed=1.5,
            time_per_cycle=4.0,
            tail_length=40, glow_factor=4.0
        )
    
    @staticmethod
    def dark_slow(vmobject: VMobject):
        """缓慢深色追踪器"""
        return GlowVMobjectTracer(
            vmobject=vmobject,
            num_points=12, dot_radius=0.025,
            color_scheme="dark", speed=0.5,
            time_per_cycle=10.0,
            tail_length=60, glow_factor=2.5
        )
    
    @staticmethod
    def bright_smooth(vmobject: VMobject):
        """平滑明亮追踪器"""
        return GlowVMobjectTracer(
            vmobject=vmobject,
            num_points=8, dot_radius=0.02,
            color_scheme="bright", speed=1.0,
            time_per_cycle=6.0,
            rate_function=smooth,
            tail_length=50, glow_factor=3.5
        )
    
    @staticmethod
    def custom_rainbow(vmobject: VMobject):
        """自定义彩虹追踪器"""
        custom_colors = [
            "#FF1493", "#FF4500", "#FFD700", "#ADFF2F", 
            "#00CED1", "#1E90FF", "#9932CC", "#FF1493"
        ]
        return GlowVMobjectTracer(
            vmobject=vmobject,
            num_points=10, dot_radius=0.02,
            color_scheme=custom_colors, speed=1.2,
            time_per_cycle=7.0,
            rate_function=lambda t: smooth(smooth(t)),
            tail_length=45, glow_factor=3.0
        )


class GlowSurroundingRect(Group):
    """
    围绕任意 Mobject 的发光闪烁矩形
    
    特性:
    - 自动围绕目标 Mobject，实时跟随其变换
    - 内置 updater，不需要手动添加到 self.play
    - 不会阻塞其他动画的播放
    - 持续发光脉冲效果
    - 支持多种颜色方案和自定义参数
    
    使用示例:
        # 创建并添加到场景，无需 play
        title = Text("标题")
        glow = GlowSurroundingRect(title)
        scene.add(glow)  # 自动开始发光动画
        
        # 继续其他动画，不会被阻塞
        scene.play(...)
        scene.wait()
    """
    
    def __init__(
        self,
        mobject: Mobject,
        
        # 矩形配置
        buff: float = 0.25,
        corner_radius: float = 0.15,
        corner_refinement: int = 6,
        corner_smooth_passes: int = 2,
        
        # 点和轨迹配置
        num_points: int = 8,
        dot_radius: float = 0.02,
        
        # 颜色配置
        color_scheme: str = "bright",  # "dark", "bright", "neon", 或自定义颜色列表
        
        # 轨迹效果配置
        tail_length: int = 80,
        tail_lifetime: float = 3.0,
        opacity_fade: tuple = (0.9, 0.0),
        width_fade: tuple = (0.08, 0.02),
        glow_factor: float = 3.0,
        tail_debug_logging: bool = False,
        tail_debug_names: Sequence[str] | None = None,
        
        # 动画配置
        speed: float = 1.0,  # 运动速度系数
        time_per_cycle: float = 6.0,  # 完整循环一周的时间
        rate_function = None,  # 动画速率函数
        
        # 显示配置
        show_dots: bool = True,
        show_rectangle: bool = False,  # 是否显示边框
        auto_update: bool = True,  # 自动更新（核心特性）
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # 保存配置参数
        self.mobject = mobject
        self.buff = buff
        self.corner_radius = corner_radius
        self.num_points = num_points
        self.dot_radius = dot_radius
        self.color_scheme = color_scheme
        self.tail_length = tail_length
        self.tail_lifetime = tail_lifetime
        self.opacity_fade = opacity_fade
        self.width_fade = width_fade
        self.glow_factor = glow_factor
        self.tail_debug_logging = tail_debug_logging
        self.tail_debug_names = list(tail_debug_names) if tail_debug_names is not None else None
        self.speed = speed
        self.time_per_cycle = time_per_cycle
        self.rate_function = rate_function or linear
        self.show_dots = show_dots
        self.show_rectangle = show_rectangle
        self.auto_update = auto_update
        self.corner_refinement = corner_refinement
        self.corner_smooth_passes = corner_smooth_passes
        
        # 内部状态
        self.time = 0.0
        self.dots = []
        self.traces = []
        self.rect_path = None
    # labels 已移除（调试信息禁用）
        
        # 初始化组件
        self._create_rect_path()
        self._create_components()
        
        # 添加到组中
        self._add_to_group()
        
        # 添加自动更新器（核心特性：不阻塞其他动画）
        if self.auto_update:
            self.add_updater(lambda mob, dt: mob.update_animation(dt))
    
    def _create_rect_path(self):
        """创建围绕 mobject 的矩形路径"""
        # 获取 mobject 的边界
        x_min, y_min = self.mobject.get_corner(DL)[:2]
        x_max, y_max = self.mobject.get_corner(UR)[:2]
        
        # 计算宽度和高度（加上 buff）
        width = x_max - x_min + 2 * self.buff
        height = y_max - y_min + 2 * self.buff
        
        # 创建圆角矩形路径
        self.rect_path = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=self.corner_radius
        )
        _refine_vmobject_corners(self.rect_path, self.corner_refinement, self.corner_smooth_passes)
        
        # 移动到 mobject 的中心
        self.rect_path.move_to(self.mobject.get_center())
        
        # 如果 mobject 固定在帧中，矩形也固定
        if self.mobject.is_fixed_in_frame():
            self.rect_path.fix_in_frame()
    
    def _update_rect_path(self):
        """更新矩形路径以匹配 mobject 的当前位置和大小"""
        # 获取当前边界
        x_min, y_min = self.mobject.get_corner(DL)[:2]
        x_max, y_max = self.mobject.get_corner(UR)[:2]
        
        # 计算新的宽度和高度
        new_width = x_max - x_min + 2 * self.buff
        new_height = y_max - y_min + 2 * self.buff
        
        # 更新矩形路径
        self.rect_path.become(RoundedRectangle(
            width=new_width,
            height=new_height,
            corner_radius=self.corner_radius
        ))
        _refine_vmobject_corners(self.rect_path, self.corner_refinement, self.corner_smooth_passes)
        
        # 移动到新位置
        self.rect_path.move_to(self.mobject.get_center())
        
        # 保持固定状态
        if self.mobject.is_fixed_in_frame():
            self.rect_path.fix_in_frame()
    
    def _create_components(self):
        """创建所有点和轨迹组件"""
        
        # 使用函数工厂彻底解决闭包问题
        def make_traced_point_func(target_dot):
            """为每个点创建独立的追踪函数"""
            return lambda: target_dot.get_center()
        
        def make_updater_func(target_trace):
            """为每个轨迹创建独立的更新器函数 - 关键修复！"""
            return lambda mob, dt: target_trace.update_tail(dt)
        
        # 存储额外的白色备用轨迹（已移除数字标签）
        self.backup_traces = []  # 存储白色备用轨迹
        
        for i in range(self.num_points):
            # 重要修复：避开首尾连接点（0.0 和 1.0），使用更大的偏移
            # 将所有点向中间偏移 0.25，避免边界点触发传送判定
            start_alpha = (i + 0.5) / self.num_points
            start_point = self.rect_path.point_from_proportion(start_alpha)
            
            # 计算颜色
            current_color = calculate_rainbow_color(i, self.num_points, self.color_scheme)
            
            # 创建点
            dot = Dot(radius=self.dot_radius, color=current_color).move_to(start_point)
            
            # 如果 mobject 固定在帧中，点也固定
            if self.mobject.is_fixed_in_frame():
                dot.fix_in_frame()
            
            # 使用工厂函数创建轨迹追踪函数
            traced_func = make_traced_point_func(dot)
            debug_name = None
            if self.tail_debug_names is not None and i < len(self.tail_debug_names):
                debug_name = self.tail_debug_names[i]
            else:
                debug_name = f"GlowSurroundingRect#{i}"
            
            # 为边界点（0 和 num_points-1）设置更宽松的传送阈值
            is_boundary = (i == 0 or i == self.num_points - 1)
            teleport_threshold = 0.6 if is_boundary else 0.6
            
            trace = TracingTailPMobject(
                traced_point_func=traced_func,
                base_color=current_color,
                max_tail_length=self.tail_length,
                tail_lifetime=self.tail_lifetime,
                opacity_fade=self.opacity_fade,
                width_fade=self.width_fade,
                glow_factor=self.glow_factor,
                teleport_min_threshold=teleport_threshold,
                debug_name=debug_name,
                debug_logging=self.tail_debug_logging
            )
            
            # （已移除调试输出）
            
            # 使用工厂函数创建独立的更新器 - 这是关键！
            updater_func = make_updater_func(trace)
            trace.add_updater(updater_func)
            
            # 更新器已添加
            
            self.dots.append(dot)
            self.traces.append(trace)
            
            # 为前3个和后3个点额外创建白色备用轨迹（确保边界点有轨迹）
            if i < 3 or i >= self.num_points - 3:
                backup_trace = TracingTailPMobject(
                    traced_point_func=traced_func,
                    base_color=WHITE,  # 白色备用轨迹
                    max_tail_length=self.tail_length,
                    tail_lifetime=self.tail_lifetime,
                    opacity_fade=self.opacity_fade,  # 稍微透明一些
                    width_fade=(0.065, 0.015),  # 稍微细一些
                    glow_factor=self.glow_factor ,
                    teleport_min_threshold=teleport_threshold,  # 非常宽松的阈值
                    debug_name=f"Backup#{i}",
                    debug_logging=False
                )
                backup_updater = make_updater_func(backup_trace)
                backup_trace.add_updater(backup_updater)
                self.backup_traces.append(backup_trace)
            
            # 不输出调试信息（移除 print）
        
        # 完成组件创建
    
    def _add_to_group(self):
        """将组件添加到 Group 中"""
        # 可选：添加矩形框架
        if self.show_rectangle:
            self.rect_path.set_stroke(opacity=0.3)
            self.add(self.rect_path)
        
        # 总是添加轨迹（包括主轨迹和白色备用轨迹）
        self.add(*self.traces)
        self.add(*self.backup_traces)
        
        # 可选：添加点
        if self.show_dots:
            self.add(*self.dots)
        
    # 数字标签已移除
    
    def update_animation(self, dt: float):
        """
        主更新函数（通过 updater 自动调用）
        这是核心：使动画持续运行而不阻塞其他 play 调用
        """
        if dt == 0:
            return self
        
        # 首先更新矩形路径以跟随 mobject
        self._update_rect_path()
        
        # 更新时间
        self.time += dt * self.speed
        
        # 计算当前周期进度 [0, 1]
        cycle_progress = (self.time / self.time_per_cycle) % 1.0
        
        # 应用速率函数
        if hasattr(self.rate_function, '__call__'):
            cycle_progress = self.rate_function(cycle_progress)
        
        # 更新每个点的位置
        for i, dot in enumerate(self.dots):
            # 计算该点在路径上的位置（带偏移）
            point_offset = i / self.num_points
            alpha = (cycle_progress + point_offset) % 1.0
            
            # 从矩形路径获取对应位置的点
            new_position = self.rect_path.point_from_proportion(alpha)
            
            # 更新点的位置
            dot.move_to(new_position)
            
            # labels 已移除，故不再更新标签位置
        
        return self
    
    def surround(self, mobject: Mobject, buff: float = None):
        """
        更换围绕的目标 mobject
        模仿 SurroundingRectangle 的 API
        """
        self.mobject = mobject
        if buff is not None:
            self.buff = buff
        
        # 立即更新路径
        self._update_rect_path()
        
        # 更新点的位置
        for i, dot in enumerate(self.dots):
            alpha = i / self.num_points
            new_position = self.rect_path.point_from_proportion(alpha)
            dot.move_to(new_position)
        
        return self
    
    def update_colors(self, new_color_scheme):
        """动态更新颜色方案"""
        self.color_scheme = new_color_scheme
        
        for i, (dot, trace) in enumerate(zip(self.dots, self.traces)):
            new_color = calculate_rainbow_color(i, self.num_points, new_color_scheme)
            dot.set_color(new_color)
            trace.base_color = new_color
    
    def update_speed(self, new_speed):
        """动态更新运动速度"""
        self.speed = new_speed
    
    def update_cycle_time(self, new_time):
        """更新完整循环时间"""
        self.time_per_cycle = new_time
    
    def clear_trails(self):
        """清除所有轨迹"""
        for trace in self.traces:
            trace.tail_points.clear()
            trace.tail_times.clear()
    
    def set_glow_intensity(self, intensity):
        """设置辉光强度"""
        self.glow_factor = intensity
        for trace in self.traces:
            trace.glow_factor = intensity
    
    def reset_time(self):
        """重置时间"""
        self.time = 0.0
    
    def pause(self):
        """暂停动画（移除更新器）"""
        self.clear_updaters()
    
    def resume(self):
        """恢复动画（重新添加更新器）"""
        if self.auto_update:
            self.clear_updaters()
            self.add_updater(lambda mob, dt: mob.update_animation(dt))


# 预设配置类 - GlowSurroundingRect
class PresetGlowSurrounding:
    """预设的发光围绕矩形配置"""
    
    @staticmethod
    def neon_tight(mobject: Mobject):
        """紧凑霓虹围绕"""
        return GlowSurroundingRect(
            mobject=mobject,
            buff=0.15, corner_radius=0.1,
            num_points=6, dot_radius=0.015,
            color_scheme="neon", speed=1.5,
            time_per_cycle=4.0,
            tail_length=40, glow_factor=4.0
        )
    
    @staticmethod
    def dark_loose(mobject: Mobject):
        """宽松深色围绕"""
        return GlowSurroundingRect(
            mobject=mobject,
            buff=0.35, corner_radius=0.2,
            num_points=12, dot_radius=0.025,
            color_scheme="dark", speed=0.5,
            time_per_cycle=10.0,
            tail_length=60, glow_factor=2.5
        )
    
    @staticmethod
    def bright_medium(mobject: Mobject):
        """中等明亮围绕"""
        return GlowSurroundingRect(
            mobject=mobject,
            buff=0.25, corner_radius=0.15,
            num_points=8, dot_radius=0.02,
            color_scheme="bright", speed=1.0,
            time_per_cycle=6.0,
            rate_function=smooth,
            tail_length=50, glow_factor=3.5
        )
    
    @staticmethod
    def custom_rainbow(mobject: Mobject):
        """自定义彩虹围绕"""
        custom_colors = [
            "#FF1493", "#FF4500", "#FFD700", "#ADFF2F", 
            "#00CED1", "#1E90FF", "#9932CC", "#FF1493"
        ]
        return GlowSurroundingRect(
            mobject=mobject,
            buff=0.25, corner_radius=0.15,
            num_points=10, dot_radius=0.02,
            color_scheme=custom_colors, speed=1.2,
            time_per_cycle=7.0,
            rate_function=lambda t: smooth(smooth(t)),
            tail_length=45, glow_factor=3.0
        )


class GlowRoundedRectangle(Group):
    """
    静态发光圆角矩形
    使用 GlowLine 构建，不包含动画
    
    特性:
    - 使用 GlowLine 构建静态发光边框
    - 支持彩虹渐变或单色
    - 可调圆角半径、宽度、高度
    - 高性能 GPU 渲染
    """
    
    def __init__(
        self,
        width: float = 4.0,
        height: float = 3.0,
        corner_radius: float = 0.3,
        corner_refinement: int = 8,
        corner_smooth_passes: int = 2,
        corner_sample_boost: float = 1.4,
        
        # 颜色配置
        color_scheme: str = "bright",  # "dark", "bright", "neon", "single", 或自定义颜色列表
        single_color: str = BLUE,  # 当 color_scheme="single" 时使用
        
        # 发光效果配置
        stroke_width: float = 6.0,
        glow_factor: float = 3.0,
        
        # 分段数（影响渐变平滑度）
        num_segments: int = 100,
        
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # 保存参数
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.corner_refinement = corner_refinement
        self.corner_smooth_passes = corner_smooth_passes
        self.corner_sample_boost = corner_sample_boost
        self.color_scheme = color_scheme
        self.single_color = single_color
        self.stroke_width = stroke_width
        self.glow_factor = glow_factor
        self.num_segments = num_segments
        
        # 创建发光线条
        self._create_glow_lines()
    
    def _create_glow_lines(self):
        """创建发光线条组成圆角矩形"""
        # 创建路径
        path = RoundedRectangle(
            width=self.width,
            height=self.height,
            corner_radius=self.corner_radius
        )
        _refine_vmobject_corners(path, self.corner_refinement, self.corner_smooth_passes)
        
        # 获取路径上的点
        points = []
        effective_segments = max(
            self.num_segments,
            int(self.num_segments * self.corner_sample_boost),
            4 * max(1, self.corner_refinement)
        )

        for i in range(effective_segments + 1):
            alpha = i / effective_segments
            point = path.point_from_proportion(alpha)
            points.append(point)
        
        # 根据颜色方案创建线段
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]
            
            # 计算颜色
            if self.color_scheme == "single":
                color = self.single_color
            else:
                color = calculate_rainbow_color(i, len(points) - 1, self.color_scheme)
            
            # 创建 GlowLine
            line = GlowLine(
                start=start,
                end=end,
                color=color,
                glow_width=self.stroke_width,
                glow_factor=self.glow_factor
            )
            
            self.add(line)
    
    def set_color_scheme(self, new_color_scheme):
        """更新颜色方案（需要重新创建）"""
        self.color_scheme = new_color_scheme
        self.remove(*self.submobjects)
        self._create_glow_lines()
        return self
    
    def set_glow_intensity(self, intensity):
        """设置辉光强度"""
        self.glow_factor = intensity
        for line in self.submobjects:
            if isinstance(line, GlowLine):
                line.set_glow_factor(intensity)
        return self


class StillSurroundingRect(Group):
    """
    静态围绕矩形
    使用 GlowRoundedRectangle 围绕任意 Mobject
    
    特性:
    - 自动围绕目标 Mobject
    - 静态发光边框（无动画）
    - 支持多种颜色方案
    - 可调边距、圆角等参数
    
    使用示例:
        title = Text("标题")
        glow_rect = StillSurroundingRect(title, color_scheme="neon")
        scene.add(glow_rect)
    """
    
    def __init__(
        self,
        mobject: Mobject,
        
        # 矩形配置
        buff: float = 0.25,
        corner_radius: float = 0.15,
        corner_refinement: int = 8,
        corner_smooth_passes: int = 2,
        corner_sample_boost: float = 1.4,
        
        # 颜色配置
        color_scheme: str = "bright",  # "dark", "bright", "neon", "single", 或自定义颜色列表
        single_color: str = BLUE,  # 当 color_scheme="single" 时使用
        
        # 发光效果配置
        stroke_width: float = 6.0,
        glow_factor: float = 3.0,
        
        # 分段数（影响渐变平滑度）
        num_segments: int = 100,
        
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # 保存参数
        self.mobject = mobject
        self.buff = buff
        self.corner_radius = corner_radius
        self.corner_refinement = corner_refinement
        self.corner_smooth_passes = corner_smooth_passes
        self.corner_sample_boost = corner_sample_boost
        self.color_scheme = color_scheme
        self.single_color = single_color
        self.stroke_width = stroke_width
        self.glow_factor = glow_factor
        self.num_segments = num_segments
        
        # 创建发光矩形
        self._create_surrounding_rect()
    
    def _create_surrounding_rect(self):
        """创建围绕矩形"""
        # 获取 mobject 的边界
        width = self.mobject.get_width() + 2 * self.buff
        height = self.mobject.get_height() + 2 * self.buff
        
        # 创建 GlowRoundedRectangle
        self.glow_rect = GlowRoundedRectangle(
            width=width,
            height=height,
            corner_radius=self.corner_radius,
            corner_refinement=self.corner_refinement,
            corner_smooth_passes=self.corner_smooth_passes,
            corner_sample_boost=self.corner_sample_boost,
            color_scheme=self.color_scheme,
            single_color=self.single_color,
            stroke_width=self.stroke_width,
            glow_factor=self.glow_factor,
            num_segments=self.num_segments
        )
        
        # 移动到 mobject 的中心
        self.glow_rect.move_to(self.mobject.get_center())
        
        # 如果 mobject 固定在帧中，矩形也固定
        if self.mobject.is_fixed_in_frame():
            self.glow_rect.fix_in_frame()
        
        # 添加到 VGroup
        self.add(self.glow_rect)
    
    def surround(self, mobject: Mobject, buff: float = None):
        """
        更换围绕的目标 mobject
        模仿 SurroundingRectangle 的 API
        """
        self.mobject = mobject
        if buff is not None:
            self.buff = buff
        
        # 重新创建矩形
        self.remove(*self.submobjects)
        self._create_surrounding_rect()
        
        return self
    
    def set_color_scheme(self, new_color_scheme):
        """更新颜色方案"""
        self.color_scheme = new_color_scheme
        self.glow_rect.set_color_scheme(new_color_scheme)
        return self
    
    def set_glow_intensity(self, intensity):
        """设置辉光强度"""
        self.glow_factor = intensity
        self.glow_rect.set_glow_intensity(intensity)
        return self


# 预设配置类 - GlowRoundedRectangle
class PresetGlowRoundedRects:
    """预设的静态发光矩形配置"""
    
    @staticmethod
    def neon_small():
        """小型霓虹矩形"""
        return GlowRoundedRectangle(
            width=3.0, height=2.0, corner_radius=0.2,
            color_scheme="neon", stroke_width=8.0, glow_factor=4.0
        )
    
    @staticmethod
    def bright_large():
        """大型明亮矩形"""
        return GlowRoundedRectangle(
            width=8.0, height=5.0, corner_radius=0.5,
            color_scheme="bright", stroke_width=6.0, glow_factor=3.0
        )
    
    @staticmethod
    def single_blue():
        """单色蓝色矩形"""
        return GlowRoundedRectangle(
            width=5.0, height=3.5, corner_radius=0.3,
            color_scheme="single", single_color=BLUE,
            stroke_width=7.0, glow_factor=3.5
        )


# 预设配置类 - StillSurroundingRect
class PresetStillSurrounding:
    """预设的静态围绕矩形配置"""
    
    @staticmethod
    def neon_tight(mobject: Mobject):
        """紧凑霓虹围绕"""
        return StillSurroundingRect(
            mobject=mobject,
            buff=0.15, corner_radius=0.1,
            color_scheme="neon", stroke_width=8.0, glow_factor=4.0
        )
    
    @staticmethod
    def bright_loose(mobject: Mobject):
        """宽松明亮围绕"""
        return StillSurroundingRect(
            mobject=mobject,
            buff=0.35, corner_radius=0.2,
            color_scheme="bright", stroke_width=6.0, glow_factor=3.0
        )
    
    @staticmethod
    def single_color(mobject: Mobject, color=BLUE):
        """单色围绕"""
        return StillSurroundingRect(
            mobject=mobject,
            buff=0.25, corner_radius=0.15,
            color_scheme="single", single_color=color,
            stroke_width=7.0, glow_factor=3.5
        )


