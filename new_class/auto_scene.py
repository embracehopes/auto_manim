"""
AutoScene - 自动化时间轴驱动的 ManimGL 场景类

功能：
- 时间轴同步：sync_to, advance_to, validate_timeline, run_timeline
- 字幕管理：make_subtitle, subtitle, clear_subtitle
- 配音集成：自动生成 TTS 配音并与字幕同步
- 文本高亮：highlight_text（支持多种随机效果）
- 区域标注：annotate_region（纯色背景覆盖+标注）
- 相机聚焦：camera_focus（动态聚焦+恢复）
- 固定方向：add_fixed_subtitle, add_fixed_annotation（3D标签）

使用示例：
    class MyScene(AutoScene):
        def construct(self):
            timeline = [
                {"start": 0.0, "end": 2.5, "text": "欢迎观看"},
                {"start": 2.5, "end": 5.0, "text": "这是自动化字幕演示"},
            ]
            self.run_timeline(timeline)
"""

import os
import asyncio
import sys
import random
import hashlib
import glob
import numpy as np
from manimlib import Scene, Text, Write, Transform, FadeOut, FadeIn, ValueTracker, DecimalNumber,InteractiveScene
from manimlib import VGroup, RoundedRectangle, ShowCreation, Rectangle, Line, Circle
from manimlib import DOWN, UP, LEFT, RIGHT, ORIGIN, WHITE, BLACK, YELLOW, RED, BLUE, GREEN, GREY, UR, UL, DR, DL
from manimlib import Indicate, FocusOn, ApplyWave, Restore
from manimlib import SurroundingRectangle, Underline, ShowPassingFlash
from manimlib import DEGREES
from manimlib import CurvedArrow, Arrow, Group, ReplacementTransform
from manimlib import Arc, TAU, ArcBetweenPoints
from manimlib import VMobject, Axes, get_norm, angle_of_vector
from manimlib import DEFAULT_ARROW_TIP_WIDTH, DEFAULT_ARROW_TIP_LENGTH
from manimlib import GlowDot, interpolate

# ==================== StealthTip 坐标轴 API ====================

class StealthTip(VMobject):
    """
    仿照 LaTeX TikZ 中的 stealth 箭头样式
    这是一个更尖锐的三角形箭头，带有内凹的底边
    """
    def __init__(
        self,
        angle=0,
        width=DEFAULT_ARROW_TIP_WIDTH,
        length=DEFAULT_ARROW_TIP_LENGTH,
        fill_opacity=1.0,
        fill_color=WHITE,
        stroke_width=0.0,
        back_indent=0.3,  # 底边内凹程度 (0-1)，越大越尖锐
        **kwargs
    ):
        super().__init__(
            fill_opacity=fill_opacity,
            fill_color=fill_color,
            stroke_width=stroke_width,
            **kwargs
        )
        
        # 保存参数用于后续计算
        self._tip_length = length
        self._tip_width = width
        self._back_indent = back_indent
        self._init_angle = angle
        
        # 创建 stealth 箭头的路径点
        # 箭头尖端在右侧，底边在左侧
        # 底边中间有一个内凹点
        tip_point = np.array([length / 2, 0, 0])
        top_point = np.array([-length / 2, width / 2, 0])
        bottom_point = np.array([-length / 2, -width / 2, 0])
        # 内凹点：从左边缘向右移动 length * back_indent
        back_point = np.array([-length / 2 + length * back_indent, 0, 0])
        
        # 保存原始内凹点位置（旋转前）
        self._original_back_point = back_point.copy()
        
        # 设置路径: 尖端 -> 上角 -> 内凹点 -> 下角 -> 尖端
        self.set_points_as_corners([
            tip_point,
            top_point,
            back_point,
            bottom_point,
            tip_point,
        ])
        
        self.rotate(angle)

    def get_base(self):
        """返回箭头底部中心点（内凹点）- 通过计算获取"""
        # 内凹点在旋转前位于 (-length/2 + length*back_indent, 0, 0)
        # 旋转后需要重新计算
        length = self._tip_length
        back_indent = self._back_indent
        # 内凹点相对于箭头中心的局部坐标
        local_back = np.array([-length / 2 + length * back_indent, 0, 0])
        # 旋转
        angle = self._init_angle
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        rotated_back = np.array([
            local_back[0] * cos_a - local_back[1] * sin_a,
            local_back[0] * sin_a + local_back[1] * cos_a,
            0
        ])
        # 加上当前中心位置
        return self.get_center() + rotated_back

    def get_tip_point(self):
        """返回箭头尖端点"""
        length = self._tip_length
        local_tip = np.array([length / 2, 0, 0])
        angle = self._init_angle
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        rotated_tip = np.array([
            local_tip[0] * cos_a - local_tip[1] * sin_a,
            local_tip[0] * sin_a + local_tip[1] * cos_a,
            0
        ])
        return self.get_center() + rotated_tip

    def get_vector(self):
        return self.get_tip_point() - self.get_base()

    def get_angle(self):
        return angle_of_vector(self.get_vector())

    def get_length(self):
        return get_norm(self.get_vector())


def add_stealth_tip_to_line(line, tip_length=0.35, tip_width=0.35, 
                            back_indent=0.3, at_start=False):
    """
    为一条线添加 stealth 样式的箭头
    
    Args:
        line: 要添加箭头的线条
        tip_length: 箭头长度
        tip_width: 箭头宽度
        back_indent: 底边内凹程度 (0-1)，越大越尖锐
        at_start: 是否在起点添加箭头（默认在终点）
        
    Returns:
        StealthTip: 箭头对象
    """
    if at_start:
        anchor = line.get_start()
        direction = line.get_start() - line.get_end()
    else:
        anchor = line.get_end()
        direction = line.get_end() - line.get_start()
    
    angle = angle_of_vector(direction)
    
    tip = StealthTip(
        angle=angle,
        width=tip_width,
        length=tip_length,
        fill_color=line.get_color(),
        back_indent=back_indent,
    )
    tip.shift(anchor - tip.get_tip_point())
    
    return tip


def create_stealth_axes(
    x_range=(-6, 6),
    y_range=(-4, 4),
    axis_config=None,
    tip_config=None,
    **kwargs
):
    """
    创建不带刻度、带有 StealthTip 箭头的坐标轴
    
    Args:
        x_range: x轴范围 (min, max) 或 (min, max, step)
        y_range: y轴范围 (min, max) 或 (min, max, step)
        axis_config: 坐标轴配置字典，可覆盖默认设置
        tip_config: 箭头配置字典，可覆盖默认设置
        **kwargs: 传递给 Axes 的其他参数
        
    Returns:
        VGroup: 包含坐标轴和箭头的组，具有以下属性：
            - axes: Axes 对象
            - x_tip: x轴箭头
            - y_tip: y轴箭头
            - x_axis: x轴引用
            - y_axis: y轴引用
    
    示例:
        # 基本用法
        axes = create_stealth_axes()
        
        # 自定义范围
        axes = create_stealth_axes(
            x_range=(-10, 10),
            y_range=(-5, 5)
        )
        
        # 自定义样式
        axes = create_stealth_axes(
            axis_config={"stroke_width": 3, "stroke_color": BLUE},
            tip_config={"tip_length": 0.4, "tip_width": 0.3}
        )
    """
    # 处理范围参数（支持2元组或3元组）
    if len(x_range) == 2:
        x_range = (*x_range, 1)
    if len(y_range) == 2:
        y_range = (*y_range, 1)
    
    # 默认坐标轴配置：不带刻度和箭头
    default_axis_config = dict(
        include_tip=False,      # 不使用默认箭头
        include_ticks=False,    # 不显示刻度
        stroke_width=4,
    )
    
    # 合并用户配置
    if axis_config:
        default_axis_config.update(axis_config)
    
    # 创建坐标轴
    axes = Axes(
        x_range=x_range,
        y_range=y_range,
        axis_config=default_axis_config,
        **kwargs
    )
    
    # 默认箭头配置
    default_tip_config = dict(
        tip_length=0.35,
        tip_width=0.35,
        back_indent=0.3,
    )
    
    # 合并用户配置
    if tip_config:
        default_tip_config.update(tip_config)
    
    # 为 x 轴和 y 轴添加 stealth 箭头
    x_tip = add_stealth_tip_to_line(axes.x_axis, **default_tip_config)
    y_tip = add_stealth_tip_to_line(axes.y_axis, **default_tip_config)
    
    # 创建结果组
    result = VGroup(axes, x_tip, y_tip)
    
    # 添加便捷属性
    result.axes = axes
    result.x_tip = x_tip
    result.y_tip = y_tip
    result.x_axis = axes.x_axis
    result.y_axis = axes.y_axis
    
    # 代理常用方法到 axes
    result.c2p = axes.c2p
    result.p2c = axes.p2c
    result.get_origin = axes.get_origin
    result.get_graph = axes.get_graph  # 普通图像方法
    
    # 添加辉光图像方法
    def get_glow_graph(
        function,
        x_range=None,
        color=WHITE,
        n_samples=500,
        **glow_kwargs
    ):
        """
        创建与坐标系对齐的 GPU 辉光函数图像
        
        Args:
            function: y = f(x) 形式的函数
            x_range: x 范围 [x_min, x_max]，默认使用坐标轴范围
            color: 辉光颜色
            glow_width: 辉光宽度
            glow_factor: 辉光衰减因子
            n_samples: 采样点数
            
        Returns:
            GlowCurve: 与坐标系对齐的辉光曲线
        """
        if not _GPU_GLOW_AVAILABLE:
            # 回退到普通曲线
            return axes.get_graph(function, x_range=x_range, color=color)
        
        # 使用坐标轴范围作为默认值
        if x_range is None:
            x_range = [axes.x_range[0], axes.x_range[1]]
        
        # 创建参数函数，直接使用 axes.c2p 进行坐标转换
        def parametric_func(x):
            y = function(x)
            # 使用 axes.c2p 将数学坐标转换为场景坐标
            point = axes.c2p(x, y)
            return np.array(point, dtype=np.float32)
        
        # 创建辉光曲线，传递额外的辉光参数
        glow_curve = GlowCurve(
            function=parametric_func,
            t_range=tuple(x_range),
            n_samples=n_samples,
            color=color,
            glow_width=0.4,
            white_core_ratio=0.02,  # 白色核心宽度
            core_width_ratio=0.05,   # 过渡区域
            **glow_kwargs
        )
        
        return glow_curve
    
    result.get_glow_graph = get_glow_graph
    
    # 添加辉光点方法
    def get_glow_dot(
        x, y,
        color=YELLOW,
        glow_width=0.3,
        glow_factor=0.5,
        **glow_kwargs
    ):
        """
        在坐标系中创建辉光点
        
        Args:
            x, y: 数学坐标
            color: 辉光颜色
            glow_width: 辉光宽度
            glow_factor: 辉光衰减因子
            
        Returns:
            GlowObjectPointCloud: 辉光点对象
        """
        if not _GPU_GLOW_AVAILABLE:
            # 回退到普通点
            from manimlib import Dot
            return Dot(axes.c2p(x, y), color=color)
        
        # 使用 axes.c2p 获取场景坐标
        point = np.array([axes.c2p(x, y)], dtype=np.float32)
        
        # 创建颜色数组
        from manimlib.utils.color import color_to_rgba
        rgba = np.array([color_to_rgba(color)], dtype=np.float32)
        
        # 创建辉光点
        glow_dot = GlowObjectPointCloud(
            points=point,
            colors=rgba,
            glow_width=glow_width,
            glow_factor=glow_factor,
            **glow_kwargs
        )
        
        return glow_dot
    
    result.get_glow_dot = get_glow_dot
    
    # 添加多个辉光点方法
    def get_glow_dots(
        coords,
        colors=None,
        glow_width=0.15,
        glow_factor=1.5,
        **glow_kwargs
    ):
        """
        在坐标系中创建多个辉光点
        
        Args:
            coords: [(x1, y1), (x2, y2), ...] 坐标列表
            colors: 颜色列表或单一颜色
            glow_width: 辉光宽度
            glow_factor: 辉光衰减因子
            
        Returns:
            GlowObjectPointCloud: 辉光点云对象
        """
        if not _GPU_GLOW_AVAILABLE:
            from manimlib import Dot, VGroup
            dots = VGroup()
            for i, (x, y) in enumerate(coords):
                c = colors[i] if isinstance(colors, list) else (colors or YELLOW)
                dots.add(Dot(axes.c2p(x, y), color=c))
            return dots
        
        # 转换坐标
        points = np.array([axes.c2p(x, y) for x, y in coords], dtype=np.float32)
        
        # 处理颜色
        from manimlib.utils.color import color_to_rgba
        if colors is None:
            colors = [YELLOW] * len(coords)
        elif not isinstance(colors, list):
            colors = [colors] * len(coords)
        
        rgba_array = np.array([color_to_rgba(c) for c in colors], dtype=np.float32)
        
        # 创建辉光点云
        glow_dots = GlowObjectPointCloud(
            points=points,
            colors=rgba_array,
            glow_width=glow_width,
            glow_factor=glow_factor,
            **glow_kwargs
        )
        
        return glow_dots
    
    result.get_glow_dots = get_glow_dots
    
    return result


def create_stealth_axes_with_labels(
    x_range=(-6, 6),
    y_range=(-4, 4),
    x_label="x",
    y_label="y",
    label_config=None,
    axis_config=None,
    tip_config=None,
    **kwargs
):
    """
    创建带标签的 StealthTip 坐标轴
    
    Args:
        x_range: x轴范围
        y_range: y轴范围
        x_label: x轴标签文本
        y_label: y轴标签文本
        label_config: 标签配置字典
        axis_config: 坐标轴配置字典
        tip_config: 箭头配置字典
        **kwargs: 传递给 Axes 的其他参数
        
    Returns:
        VGroup: 包含坐标轴、箭头和标签的组
    """
    # 创建基础坐标轴
    stealth_axes = create_stealth_axes(
        x_range=x_range,
        y_range=y_range,
        axis_config=axis_config,
        tip_config=tip_config,
        **kwargs
    )
    
    # 默认标签配置
    default_label_config = dict(
        font_size=36,
        color=WHITE,
    )
    if label_config:
        default_label_config.update(label_config)
    
    # 创建标签
    x_label_mob = Text(x_label, **default_label_config)
    y_label_mob = Text(y_label, **default_label_config)
    
    # 定位标签（在箭头旁边）
    x_label_mob.next_to(stealth_axes.x_tip, RIGHT, buff=0.1)
    y_label_mob.next_to(stealth_axes.y_tip, UP, buff=0.1)
    
    # 添加到组
    stealth_axes.add(x_label_mob, y_label_mob)
    stealth_axes.x_label = x_label_mob
    stealth_axes.y_label = y_label_mob
    
    return stealth_axes


# ==================== GPU 辉光效果 API (基于着色器) ====================

# 尝试导入 GPU 辉光效果组件
try:
    import sys
    from pathlib import Path
    # 添加 shaderscene 路径
    _shader_path = str(Path(__file__).parent.parent / "shaderscene" / "mobject")
    if _shader_path not in sys.path:
        sys.path.insert(0, _shader_path)
    
    from glow_curve import GlowCurve, GlowFunctionGraph, GlowParametricCurve, GlowCircle, GlowSpiral
    from glow_wrapper import GlowObjectPointCloud, GlowWrapperEffect, GlowLineStrip
    
    _GPU_GLOW_AVAILABLE = True
except ImportError as e:
    _GPU_GLOW_AVAILABLE = False
    GlowCurve = None
    GlowFunctionGraph = None
    GlowParametricCurve = None
    GlowCircle = None
    GlowSpiral = None
    GlowObjectPointCloud = None
    GlowWrapperEffect = None
    GlowLineStrip = None

# 尝试导入 GlowDot 呼吸效果组件
try:
    _src_path = str(Path(__file__).parent / "src")
    if _src_path not in sys.path:
        sys.path.insert(0, _src_path)
    
    from breathing_effects import (
        BreathingMode,
        create_breathing_glow_dot,
        create_breathing_updater,
        next_breathing_mode,
        reset_breathing_mode,
        BreathingModeManager,
        BREATHING_RAINBOW_COLORS,
        BREATHING_GLOW_FACTOR,
    )
    _BREATHING_AVAILABLE = True
except ImportError:
    _BREATHING_AVAILABLE = False
    BreathingMode = None
    create_breathing_glow_dot = None
    create_breathing_updater = None
    next_breathing_mode = None
    reset_breathing_mode = None
    BreathingModeManager = None
    BREATHING_RAINBOW_COLORS = None
    BREATHING_GLOW_FACTOR = 1.0

# 尝试导入 TracingTailPMobject (辉光彗尾效果)
try:
    _tracing_path = str(Path(__file__).parent.parent / "shaderscene" / "mobject")
    if _tracing_path not in sys.path:
        sys.path.insert(0, _tracing_path)
    from TracingTailPMobject import TracingTailPMobject
    _TRACING_TAIL_AVAILABLE = True
except ImportError:
    _TRACING_TAIL_AVAILABLE = False
    TracingTailPMobject = None


def is_gpu_glow_available():
    """检查 GPU 辉光效果是否可用"""
    return _GPU_GLOW_AVAILABLE


def create_glow_curve(
    function,
    t_range=(0, 1),
    n_samples=1000,
    color=WHITE,
    opacity=1.0,
    glow_width=0.15,
    glow_factor=2.5,
    core_width_ratio=0.2,
    white_core_ratio=0.05,
    **kwargs
):
    """
    创建 GPU 辉光曲线
    
    Args:
        function: 参数函数 t -> [x, y, z]
        t_range: 参数范围 (t_min, t_max)
        n_samples: 采样点数
        color: 辉光颜色
        opacity: 透明度
        glow_width: 辉光宽度
        glow_factor: 辉光衰减因子
        core_width_ratio: 过渡区域宽度比
        white_core_ratio: 白色核心比例
        
    Returns:
        GlowCurve: 辉光曲线对象
        
    示例:
        # 创建正弦曲线
        curve = create_glow_curve(
            function=lambda t: np.array([t, np.sin(t), 0]),
            t_range=(-TAU, TAU),
            color=BLUE
        )
    """
    if not _GPU_GLOW_AVAILABLE:
        raise ImportError("GPU 辉光效果不可用，请检查 shaderscene 模块是否正确安装")
    
    return GlowCurve(
        function=function,
        t_range=t_range,
        n_samples=n_samples,
        color=color,
        opacity=opacity,
        glow_width=glow_width,
        glow_factor=glow_factor,
        core_width_ratio=core_width_ratio,
        white_core_ratio=white_core_ratio,
        **kwargs
    )


def create_glow_function_graph(
    function,
    x_range=(-5, 5),
    color=WHITE,
    opacity=1.0,
    glow_width=0.15,
    glow_factor=2.5,
    **kwargs
):
    """
    创建 GPU 辉光函数图像
    
    Args:
        function: y = f(x) 形式的函数
        x_range: x 轴范围 (x_min, x_max)
        color: 辉光颜色
        opacity: 透明度
        glow_width: 辉光宽度
        glow_factor: 辉光衰减因子
        
    Returns:
        GlowFunctionGraph: 辉光函数图像对象
        
    示例:
        # 创建抛物线
        graph = create_glow_function_graph(
            function=lambda x: x**2,
            x_range=(-3, 3),
            color=YELLOW
        )
    """
    if not _GPU_GLOW_AVAILABLE:
        raise ImportError("GPU 辉光效果不可用，请检查 shaderscene 模块是否正确安装")
    
    return GlowFunctionGraph(
        function=function,
        x_range=x_range,
        color=color,
        opacity=opacity,
        glow_width=glow_width,
        glow_factor=glow_factor,
        **kwargs
    )


def create_glow_wrapper(
    mobject,
    color=WHITE,
    alpha=1.0,
    size=0.3,
    glow_factor=3.0,
    render_mode="line",
    white_core_ratio=0.5,
    **kwargs
):
    """
    为任意 Mobject 创建 GPU 辉光包裹效果
    
    Args:
        mobject: 要添加辉光的对象
        color: 辉光颜色
        alpha: 透明度
        size: 辉光大小
        glow_factor: 辉光衰减因子
        render_mode: 渲染模式 ("line" 或 "point")
        white_core_ratio: 白色核心比例
        
    Returns:
        GlowWrapperEffect: 辉光包裹效果对象
        
    示例:
        circle = Circle()
        glow = create_glow_wrapper(circle, color=BLUE, size=0.4)
    """
    if not _GPU_GLOW_AVAILABLE:
        raise ImportError("GPU 辉光效果不可用，请检查 shaderscene 模块是否正确安装")
    
    return GlowWrapperEffect(
        mobject,
        color=color,
        alpha=alpha,
        size=size,
        glow_factor=glow_factor,
        render_mode=render_mode,
        white_core_ratio=white_core_ratio,
        **kwargs
    )


def create_glow_point_cloud(
    points,
    colors,
    glow_width=0.35,
    glow_factor=1.0,
    core_width_ratio=0.3,
    white_core_ratio=0.3,
    **kwargs
):
    """
    创建 GPU 辉光点云
    
    Args:
        points: (N, 3) 形状的点数组
        colors: (N, 4) 形状的 RGBA 颜色数组
        glow_width: 辉光宽度
        glow_factor: 辉光衰减因子
        core_width_ratio: 过渡区域宽度比
        white_core_ratio: 白色核心比例
        
    Returns:
        GlowObjectPointCloud: 辉光点云对象
        
    示例:
        points = np.random.randn(100, 3)
        colors = np.ones((100, 4))  # 白色
        glow = create_glow_point_cloud(points, colors)
    """
    if not _GPU_GLOW_AVAILABLE:
        raise ImportError("GPU 辉光效果不可用，请检查 shaderscene 模块是否正确安装")
    
    return GlowObjectPointCloud(
        points=points,
        colors=colors,
        glow_width=glow_width,
        glow_factor=glow_factor,
        core_width_ratio=core_width_ratio,
        white_core_ratio=white_core_ratio,
        **kwargs
    )


# ==================== 辉光效果 API (软件渲染) ====================

def create_glow_surrounding_rect(
    mobject,
    # 矩形参数
    color=YELLOW,
    buff=0.15,
    stroke_width=3,
    fill_opacity=0,
    # 辉光参数
    glow_color=None,
    n_glow_layers=3,
    max_glow_width=20,
    base_opacity=0.15,
):
    """
    创建带辉光效果的环绕矩形 - 通过宽度和透明度渐变实现
    
    矩形参数:
        mobject: 要环绕的对象
        color: 矩形颜色
        buff: 矩形与对象的间距
        stroke_width: 线条宽度
        fill_opacity: 填充透明度
    
    辉光参数:
        glow_color: 辉光颜色，None则使用color
        n_glow_layers: 辉光层数（2-3层即可）
        max_glow_width: 最外层辉光线条宽度
        base_opacity: 最外层透明度
    
    返回:
        VGroup: 包含辉光层和原始矩形的组
    """
    rect = SurroundingRectangle(
        mobject,
        color=color,
        buff=buff,
        stroke_width=stroke_width,
    )
    rect.set_fill(color=color, opacity=fill_opacity)
    
    glow_col = glow_color if glow_color else color
    glow_layers = VGroup()
    
    for i in range(n_glow_layers, 0, -1):
        glow_copy = rect.copy()
        ratio = i / n_glow_layers
        glow_width = stroke_width + (max_glow_width - stroke_width) * ratio
        opacity = base_opacity + (0.5 - base_opacity) * (1 - ratio)
        glow_copy.set_stroke(color=glow_col, width=glow_width, opacity=opacity)
        glow_copy.set_fill(opacity=0)
        glow_layers.add(glow_copy)
    
    result = VGroup(glow_layers, rect)
    result.rect = rect
    result.glow_layers = glow_layers
    return result


def create_glowing_arc_arrow(
    start_angle=0,
    angle=TAU/2,
    radius=2.5,
    colors=None,
    stroke_width=4,
    glow_color=None,
    n_glow_layers=8,
    arc_scale_factor=1.05,
    tip_scale_factor=1.5,
    glow_stroke_width=None,
    glow_width_mult=2.0,
    base_opacity=0.25,
    add_tip=True,
    tip_at_start=False,
):
    """
    创建辉光弧形箭头 - 封装完整的辉光效果
    """
    if colors is None:
        colors = [WHITE]
    
    arc = Arc(start_angle=start_angle, angle=angle, radius=radius)
    arc.set_stroke(width=stroke_width)
    arc.set_color(colors)
    
    if add_tip:
        arc.add_tip(at_start=tip_at_start)
        arc.get_tips()[0].set_color(colors[-1])
    
    glow_col = glow_color if glow_color else colors[-1]
    
    if glow_stroke_width is None:
        if hasattr(stroke_width, '__iter__') and not isinstance(stroke_width, str):
            glow_width = [w * glow_width_mult for w in stroke_width]
        else:
            glow_width = stroke_width * glow_width_mult
    else:
        glow_width = glow_stroke_width
    
    tips = arc.get_tips() if add_tip else []
    
    arc_glow_layers = VGroup()
    for i in range(n_glow_layers, 0, -1):
        arc_copy = arc.copy()
        if tips:
            for tip in arc_copy.get_tips():
                arc_copy.remove(tip)
        current_scale = 1 + (arc_scale_factor - 1) * (i / n_glow_layers)
        opacity = base_opacity * (1 - (i - 1) / n_glow_layers) * 0.8 + base_opacity * 0.2
        arc_copy.scale(current_scale, about_point=arc_copy.get_center())
        arc_copy.set_stroke(color=glow_col, width=glow_width, opacity=opacity)
        arc_glow_layers.add(arc_copy)
    
    tip_glow_layers = VGroup()
    if tips:
        for original_tip in tips:
            tip_center = original_tip.get_center()
            for i in range(n_glow_layers, 0, -1):
                tip_copy = original_tip.copy()
                current_scale = 1 + (tip_scale_factor - 1) * (i / n_glow_layers)
                opacity = base_opacity * (1 - (i - 1) / n_glow_layers) * 0.8 + base_opacity * 0.2
                tip_copy.scale(current_scale, about_point=tip_center)
                tip_copy.set_fill(color=glow_col, opacity=opacity)
                tip_copy.set_stroke(color=glow_col, opacity=opacity)
                tip_glow_layers.add(tip_copy)
    
    result = VGroup(arc_glow_layers, tip_glow_layers, arc)
    result.arc = arc
    result.arc_glow = arc_glow_layers
    result.tip_glow = tip_glow_layers
    return result


def create_glowing_curved_arrow(
    start_point,
    end_point,
    angle=0.8,
    colors=None,
    stroke_width=None,
    glow_color=None,
    n_glow_layers=8,
    arc_scale_factor=1.03,
    tip_scale_factor=1.5,
    glow_width_mult=2.5,
    base_opacity=0.3,
    tip_length=0.25,
    tip_width=0.2,
    back_indent=0.35,
):
    """
    创建渐变宽度和颜色的辉光弯曲箭头（使用 StealthTip 样式）
    
    Args:
        start_point: 箭头起点
        end_point: 箭头终点（箭头指向处）
        angle: 弯曲角度
        colors: 颜色渐变列表，如 ["#8B0000", "#FF4500", "#FFD700"]
        stroke_width: 线宽列表（渐变宽度），如 [0, 1, 2, 3, 3, 3, 3, 3, 3, 3]
        glow_color: 辉光颜色
        n_glow_layers: 辉光层数
        arc_scale_factor: 弧线辉光缩放
        tip_scale_factor: 箭头尖端辉光缩放
        glow_width_mult: 辉光宽度倍数
        base_opacity: 辉光基础透明度
        tip_length: StealthTip 箭头长度
        tip_width: StealthTip 箭头宽度
        back_indent: StealthTip 内凹程度
        
    Returns:
        VGroup: 包含辉光层和箭头的组
    """
    # 默认渐变颜色（暖色）
    if colors is None:
        colors = ["#8B0000", "#FF4500", "#FFD700"]
    
    # 默认渐变宽度
    if stroke_width is None:
        stroke_width = [0, 1, 2, 3, 3, 3, 3, 3, 3, 3]
    
    # 确保是 numpy 数组
    start_point = np.array(start_point) if not isinstance(start_point, np.ndarray) else start_point
    end_point = np.array(end_point) if not isinstance(end_point, np.ndarray) else end_point
    # 确保是3D点
    if len(start_point) == 2:
        start_point = np.array([start_point[0], start_point[1], 0])
    if len(end_point) == 2:
        end_point = np.array([end_point[0], end_point[1], 0])
    
    # 创建弧线（不带箭头）
    arc = ArcBetweenPoints(
        start_point,
        end_point,
        angle=angle,
    )
    arc.set_stroke(width=stroke_width)
    arc.set_color(colors)
    
    # 计算箭头方向（在弧线终点的切线方向）
    # 获取弧线终点附近的两个点来计算切线
    arc_points = arc.get_points()
    arc_end = arc_points[-1]  # 弧线实际终点
    
    if len(arc_points) >= 4:
        # 使用最后几个点计算切线方向
        tangent = arc_points[-1] - arc_points[-4]
        if get_norm(tangent) < 1e-6:
            tangent = arc_points[-1] - arc_points[-2]
        arrow_angle = angle_of_vector(tangent[:2])
    else:
        # 回退：使用起点到终点的方向
        direction = end_point - start_point
        arrow_angle = angle_of_vector(direction[:2])
        tangent = direction
    
    # 创建 StealthTip 箭头（不旋转，先定位再旋转）
    stealth_tip = StealthTip(
        angle=0,  # 先不旋转
        length=tip_length,
        width=tip_width,
        back_indent=back_indent,
        fill_color=colors[-1],
        fill_opacity=1.0,
    )
    
    # 将箭头的内凹点（base）对齐到弧线实际终点
    # StealthTip 创建时内凹点在 (-length/2 + length*back_indent, 0, 0)
    # 箭头中心在原点
    # 内凹点相对于中心的偏移
    base_offset_x = -tip_length / 2 + tip_length * back_indent
    
    # 先将箭头移动到弧线终点，使内凹点对齐
    # 箭头中心需要在: arc_end - (base相对于中心的向量经过旋转后)
    cos_a, sin_a = np.cos(arrow_angle), np.sin(arrow_angle)
    rotated_base_offset = np.array([
        base_offset_x * cos_a,
        base_offset_x * sin_a,
        0
    ])
    
    # 箭头中心位置 = 弧线终点 - 旋转后的base偏移
    tip_center = arc_end - rotated_base_offset
    stealth_tip.move_to(tip_center)
    stealth_tip.rotate(arrow_angle)
    
    # 辉光颜色
    glow_col = glow_color if glow_color else colors[-1]
    
    # 计算辉光宽度
    if hasattr(stroke_width, '__iter__') and not isinstance(stroke_width, str):
        glow_width = [w * glow_width_mult for w in stroke_width]
    else:
        glow_width = stroke_width * glow_width_mult
    
    # 创建弧线辉光层
    arc_glow_layers = VGroup()
    for i in range(n_glow_layers, 0, -1):
        arc_copy = arc.copy()
        current_scale = 1 + (arc_scale_factor - 1) * (i / n_glow_layers)
        opacity = base_opacity * (1 - (i - 1) / n_glow_layers) * 0.8 + base_opacity * 0.2
        arc_copy.scale(current_scale, about_point=arc_copy.get_center())
        arc_copy.set_stroke(color=glow_col, width=glow_width, opacity=opacity)
        arc_glow_layers.add(arc_copy)
    
    # 创建 StealthTip 辉光层
    tip_glow_layers = VGroup()
    tip_center = stealth_tip.get_center()
    for i in range(n_glow_layers, 0, -1):
        tip_copy = stealth_tip.copy()
        current_scale = 1 + (tip_scale_factor - 1) * (i / n_glow_layers)
        opacity = base_opacity * (1 - (i - 1) / n_glow_layers) * 0.8 + base_opacity * 0.2
        tip_copy.scale(current_scale, about_point=tip_center)
        tip_copy.set_fill(color=glow_col, opacity=opacity)
        tip_copy.set_stroke(color=glow_col, width=1, opacity=opacity * 0.5)
        tip_glow_layers.add(tip_copy)
    
    # 组合：弧线辉光 + 箭头辉光 + 弧线 + 箭头
    result = VGroup(arc_glow_layers, tip_glow_layers, arc, stealth_tip)
    result.arc = arc
    result.stealth_tip = stealth_tip
    result.arc_glow = arc_glow_layers
    result.tip_glow = tip_glow_layers
    return result


class AutoScene(InteractiveScene):
    """
    自动化时间轴驱动的场景类
    
    特性：
    - 精确时间同步
    - 字幕自动 Transform
    - 配音自动生成
    - 调试 HUD 支持
    """
    
    # 字幕配置
    SUBTITLE_FONT = "STKaiti"
    SUBTITLE_FONT_SIZE = 28
    SUBTITLE_MAX_CHARS_PER_LINE = 20  # 中文换行字数
    SUBTITLE_EDGE_BUFF = 0.5  # to_edge 边距
    SUBTITLE_COLOR = BLACK  # 字幕文字颜色（黑色）
    
    # 字幕背景配置
    SUBTITLE_BG_COLOR = WHITE          # 背景颜色
    SUBTITLE_BG_OPACITY = 0.95         # 背景透明度
    SUBTITLE_BG_CORNER_RADIUS = 0.15   # 圆角半径
    SUBTITLE_BG_BUFF = 0.15            # 背景与文字的内边距
    
    DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
    WRITE_DURATION = 0.5
    TRANSFORM_DURATION = 0.3
    FADE_DURATION = 0.3
    
    TIME_TOLERANCE = 0.01  # 10ms 容差
    TIME_WARNING_THRESHOLD = 0.1  # 100ms 报警阈值
    
    # 辉光效果配置
    GLOW_ENABLED = True                 # 是否启用辉光效果
    GLOW_N_LAYERS = 3                   # 辉光层数
    GLOW_MAX_WIDTH_MULT = 4.0           # 最外层辉光宽度倍数
    GLOW_BASE_OPACITY = 0.2             # 辉光透明度
    
    # 辉光弧形箭头默认配置
    GLOW_ARROW_LEFT_COLORS = ["#8B0000", "#FF4500", "#FFD700"]   # 左侧箭头渐变色（暖色）
    GLOW_ARROW_RIGHT_COLORS = ["#2C3E50", "#3498DB", "#E0FFFF"]  # 右侧箭头渐变色（冷色）
    GLOW_ARROW_TAPERED_WIDTH = [0, 1, 2, 3, 3, 3, 3, 3, 3, 3]    # 变宽箭头宽度序列
    GLOW_ARROW_N_LAYERS = 8             # 箭头辉光层数
    GLOW_ARROW_ARC_SCALE = 1.03         # 弧线辉光缩放
    GLOW_ARROW_TIP_SCALE = 1.5          # 箭头尖端辉光缩放
    GLOW_ARROW_WIDTH_MULT = 2.5         # 箭头辉光宽度倍数
    GLOW_ARROW_BASE_OPACITY = 0.3       # 箭头辉光透明度
    
    # 六块布局配置（自适应定位）
    LAYOUT_TITLE_BUFF = 0.2             # 标题到顶部边距
    LAYOUT_DIVIDER_BUFF = 0.1           # 分割线到标题边距
    LAYOUT_CONTENT_BUFF = 0.2           # 内容块最小间距
    LAYOUT_EDGE_BUFF = 0.2              # 左右边距
    LAYOUT_DIVIDER_WIDTH_RATIO = 0.95   # 分割线宽度占屏幕比例
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 时间轴状态
        self._current_time: float = 0.0
        
        # 字幕状态
        self._subtitle = None
        self._subtitle_count: int = 0
        self._subtitle_font_size = self.SUBTITLE_FONT_SIZE
        self._subtitle_edge_buff = self.SUBTITLE_EDGE_BUFF
        
        # 根据屏幕宽度动态计算每行最大字符数
        try:
            frame_width = self.camera.frame.get_width()
            # 竖版视频（9:16）使用更少的字符数
            if frame_width <= 10:
                self._subtitle_max_chars = 18  # 竖版
            else:
                self._subtitle_max_chars = 30  # 横版
        except AttributeError:
            # camera.frame 尚未初始化，使用默认值
            self._subtitle_max_chars = self.SUBTITLE_MAX_CHARS_PER_LINE
        
        # 配音设置
        self._voice = self.DEFAULT_VOICE
        self._enable_voice = True
        self._sounds_dir = self._get_sounds_dir()
        self._voice_count = 0  # 配音文件全局计数器
        
        # 音效库（动画自动播放音效）
        self._sound_library = None
        self._enable_animation_sounds = False  # 默认关闭，需要手动开启
        self._enable_add_sounds = False  # add() 音效开关
        self._sound_gain = 0.6  # 音效音量 (0.0-1.0)
        self._init_sound_library()
        
        # 辉光颜色轮询色盘（电影级彩色，禁止白色）
        self._glow_color_palette = [
            "#FF6B6B",  # 珊瑚红
            "#4ECDC4",  # 蒂芙尼蓝
            "#FFE66D",  # 柠檬黄
            "#95E1D3",  # 薄荷绿
            "#F38181",  # 玫瑰粉
            "#AA96DA",  # 薰衣草紫
            "#FCBAD3",  # 樱花粉
            "#A8D8EA",  # 天空蓝
            "#FF9F43",  # 橘子橙
            "#54E346",  # 荧光绿
            "#C9D6FF",  # 冰蓝紫
            "#EE5A24",  # 烈焰橙
            "#009432",  # 翠绿
            "#1289A7",  # 孔雀蓝
            "#D980FA",  # 霓虹紫
        ]
        self._glow_color_index = 0  # 颜色轮询索引
        
        # 方框引导色盘（高对比度、醒目的颜色）
        self._focus_box_color_palette = [
            "#FF4757",  # 鲜红
            "#2ED573",  # 翠绿
            "#1E90FF",  # 道奇蓝
            "#FFA502",  # 橙黄
            "#A855F7",  # 紫罗兰
            "#00D9FF",  # 青蓝
            "#FF6B9D",  # 玫红
            "#70A1FF",  # 天蓝
            "#FFD93D",  # 金黄
            "#6BCB77",  # 草绿
            "#FF8C42",  # 橘红
            "#9B59B6",  # 紫色
            "#3498DB",  # 蓝色
            "#E74C3C",  # 红色
            "#1ABC9C",  # 青绿
            "#F39C12",  # 橙色
        ]
        self._focus_box_color_index = 0  # 方框颜色轮询索引
        self._focus_boxes = []  # 当前活跃的引导方框列表
        
        # 强调效果轮询列表
        self._highlight_effects = [
            "box",        # 辉光方框
            "underline",  # 下划线
            "indicate",   # 缩放变色
            "flash",      # 颜色渐变闪烁
            "circumscribe",  # 环绕描边
            "focus",      # 聚光灯
            "wave",       # 波浪
            "grow",       # 水波光环
        ]
        self._highlight_effect_index = 0  # 效果轮询索引
        
        # GlowDot 呼吸效果管理器
        if _BREATHING_AVAILABLE:
            self._breathing_manager = BreathingModeManager()
        else:
            self._breathing_manager = None
        
        # 强调装饰自动清理列表 [(decoration, add_time, max_duration)]
        self._highlight_decorations = []
        self._highlight_max_duration = 3.0  # 最大存留时间（秒）
        
        # 跨阶段共享对象（支持独立运行各阶段）
        self.shared_objects = {}
        
        # 调试
        self._time_hud = None
        self._time_tracker = None
        self._markers: list = []
        self._debug_mode = False
    
    def get_shared(self, key: str, default=None, factory=None):
        """
        安全获取共享对象，支持独立运行各阶段
        
        Args:
            key: 对象的键名
            default: 如果对象不存在返回的默认值
            factory: 如果对象不存在，调用此工厂函数创建对象
                    factory 应该是一个无参数函数，返回 Mobject
        
        Returns:
            共享对象或默认值
            
        Example:
            # 简单获取
            title = self.get_shared("title")
            
            # 带默认值
            title = self.get_shared("title", VGroup())
            
            # 带工厂函数（自动创建并缓存）
            final_eq = self.get_shared("final_eq", factory=lambda: Tex(r"T(t)=20+10\cdot0.8^{t/2}"))
        """
        obj = self.shared_objects.get(key)
        if obj is not None:
            return obj
        
        if factory is not None:
            obj = factory()
            self.shared_objects[key] = obj
            return obj
        
        return default if default is not None else VGroup()
    
    def set_shared(self, key: str, obj):
        """设置共享对象"""
        self.shared_objects[key] = obj
        return obj
    
    def safe_fadeout(self, *keys, run_time=0.5):
        """
        安全淡出共享对象，只处理实际存在的对象
        
        Args:
            *keys: 要淡出的对象键名
            run_time: 动画时长
            
        Example:
            self.safe_fadeout("title", "underline", "problem")
        """
        anims = []
        for key in keys:
            obj = self.shared_objects.get(key)
            if obj is not None:
                anims.append(FadeOut(obj))
        if anims:
            self.play(*anims, run_time=run_time)
    
    def _init_sound_library(self) -> None:
        """初始化音效库"""
        try:
            from sound_library import SoundLibrary
            self._sound_library = SoundLibrary()
        except ImportError:
            # 尝试从脚本目录导入
            script_dir = os.path.dirname(os.path.abspath(__file__))
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
            try:
                from sound_library import SoundLibrary
                self._sound_library = SoundLibrary()
            except ImportError:
                # 音效库不可用，禁用相关功能
                self._sound_library = None
                if self._debug_mode:
                    print("ℹ️ SoundLibrary 未安装，音效功能已禁用")
    
    def _get_sounds_dir(self) -> str:
        """获取配音输出目录（按类名存储）"""
        # 使用类名作为文件夹名
        class_name = self.__class__.__name__
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)  # auto_manim 目录
        sounds_dir = os.path.join(parent_dir, "assets", "sounds", "voice", class_name)
        os.makedirs(sounds_dir, exist_ok=True)
        return sounds_dir
    
    # ==================== 音效控制方法 ====================
    
    def play(self, *animations, **kwargs) -> None:
        """
        重写 play() 方法，自动播放动画对应的音效
        
        Args:
            *animations: 动画对象
            **kwargs: 传递给父类 play() 的参数
                _is_subtitle: 内部标记，字幕动画不播放音效
        """
        # 检查是否为字幕动画（字幕不播放音效）
        is_subtitle = kwargs.pop('_is_subtitle', False)
        
        # 自动播放动画音效（字幕动画跳过）
        if self._enable_animation_sounds and self._sound_library and not is_subtitle:
            for anim in animations:
                anim_name = anim.__class__.__name__
                sound_path = self._sound_library.get_sound(anim_name)
                if sound_path:
                    self.add_sound(sound_path, gain=self._sound_gain)
                    if self._debug_mode:
                        print(f"🔊 播放音效: {anim_name} -> {os.path.basename(sound_path)}")
        
        # 调用父类 play
        super().play(*animations, **kwargs)
    
    def add(self, *mobjects, **kwargs) -> None:
        """
        重写 add() 方法，自动播放 add 音效
        
        Args:
            *mobjects: 要添加的对象
            **kwargs: 传递给父类的参数
        """
        # 播放 add 音效
        if self._enable_add_sounds and self._sound_library and mobjects:
            sound_path = self._sound_library.get_add_sound()
            if sound_path:
                self.add_sound(sound_path, gain=self._sound_gain)
                if self._debug_mode:
                    import os
                    print(f"🔊 播放 add 音效: {os.path.basename(sound_path)}")
        
        # 调用父类 add
        super().add(*mobjects, **kwargs)
    
    def set_animation_sounds_enabled(self, enabled: bool) -> None:
        """
        启用/禁用动画音效
        
        Args:
            enabled: True 启用，False 禁用
        """
        self._enable_animation_sounds = enabled
        if self._debug_mode:
            status = "启用" if enabled else "禁用"
            print(f"🔊 动画音效: {status}")
    
    def set_add_sounds_enabled(self, enabled: bool) -> None:
        """
        启用/禁用 add() 音效
        
        Args:
            enabled: True 启用，False 禁用
        """
        self._enable_add_sounds = enabled
        if self._debug_mode:
            status = "启用" if enabled else "禁用"
            print(f"🔊 add() 音效: {status}")
    
    def set_sound_gain(self, gain: float) -> None:
        """
        设置音效音量
        
        Args:
            gain: 音量系数 (0.0-1.0)，默认 0.6
        """
        self._sound_gain = max(0.0, min(1.0, gain))
        if self._debug_mode:
            print(f"🔊 音效音量: {self._sound_gain * 100:.0f}%")
    
    def get_sound_library(self):
        """获取音效库实例"""
        return self._sound_library
    
    # ==================== 布局辅助方法 ====================
    
    def ensure_above_subtitle(self, mobject, viz_bottom_y: float = None, margin: float = 0.3, overlap_buff: float = 0.2) -> None:
        """
        确保物体在字幕区域上方，智能处理布局
        
        逻辑：
        - 如果物体与字幕区域重叠：向上移动，并额外增加 overlap_buff 缓冲
        - 如果没有重叠：将物体放置在可视化区域底部和字幕顶部的中间位置
        
        Args:
            mobject: 要调整位置的物体
            viz_bottom_y: 可视化区域的底部 y 值（用于居中计算，可选）
            margin: 基础安全边距（默认 0.3）
            overlap_buff: 重叠时额外的缓冲距离（默认 0.2）
        """
        # 计算字幕区域的顶部 y 值
        # 字幕位置：to_edge(DOWN, buff=edge_buff)，字幕高度约 1.0
        frame_height = 12  # 默认竖版高度
        try:
            frame_height = self.camera.frame.get_height()
        except AttributeError:
            pass  # camera.frame 尚未初始化，使用默认值
        
        subtitle_height = 1.0  # 字幕大致高度
        subtitle_top_y = -frame_height / 2 + self._subtitle_edge_buff + subtitle_height + margin
        
        # 获取物体底部 y 值
        bottom_y = mobject.get_bottom()[1]
        
        # 检查是否重叠
        if bottom_y < subtitle_top_y:
            # 重叠情况：向上移动，并添加额外缓冲
            offset = subtitle_top_y - bottom_y + overlap_buff
            mobject.shift(UP * offset)
            if self._debug_mode:
                print(f"📐 ensure_above_subtitle: 重叠，向上移动 {offset:.2f} (含 {overlap_buff} 缓冲)")
        elif viz_bottom_y is not None:
            # 没有重叠且提供了可视化区域底部：居中放置
            # 计算可视化底部和字幕顶部的中间位置
            middle_y = (viz_bottom_y + subtitle_top_y) / 2
            
            # 将物体中心移动到中间位置
            current_center_y = mobject.get_center()[1]
            offset = middle_y - current_center_y
            mobject.shift(UP * offset)
            if self._debug_mode:
                print(f"📐 ensure_above_subtitle: 无重叠，居中到 y={middle_y:.2f}")
    
    # ==================== 时间轴方法 ====================
    
    def sync_to(self, target_time: float) -> None:
        """
        同步到目标时间
        
        如果当前时间落后于目标，使用 wait 补齐；
        如果当前时间超前，打印警告。
        
        Args:
            target_time: 目标时间（秒）
        """
        delta = target_time - self._current_time
        
        if delta > self.TIME_TOLERANCE:
            # 落后：补齐等待时间
            self.wait(delta)
            self._current_time = target_time
            if self._debug_mode:
                print(f"⏱️ sync_to({target_time:.2f}s) - waited {delta:.2f}s")
        elif delta < -self.TIME_WARNING_THRESHOLD:
            # 超前：打印警告
            print(f"⚠️ 时间超前: 当前 {self._current_time:.2f}s > 目标 {target_time:.2f}s (差 {-delta:.2f}s)")
        else:
            # 在容差范围内：更新时间
            self._current_time = target_time
    
    def advance_to(self, t_end: float) -> None:
        """
        线性推进到 t_end
        
        与 sync_to 类似，但语义上用于"推进到结束时间"。
        
        Args:
            t_end: 结束时间（秒）
        """
        delta = t_end - self._current_time
        
        if delta > self.TIME_TOLERANCE:
            self.wait(delta)
            self._current_time = t_end
            if self._debug_mode:
                print(f"⏩ advance_to({t_end:.2f}s) - advanced {delta:.2f}s")
        elif delta < -self.TIME_TOLERANCE:
            if self._debug_mode:
                print(f"⚠️ advance_to 跳过: 已在 {self._current_time:.2f}s，目标 {t_end:.2f}s")
    
    def validate_timeline(self, events: list) -> bool:
        """
        验证时间轴有效性
        
        检查：
        - 单调递增（start 按顺序递增）
        - 无时间重叠
        - 无负时长
        
        Args:
            events: 事件列表 [{"start": float, "end": float, "text": str}, ...]
            
        Returns:
            True 如果有效，否则打印错误并返回 False
        """
        if not events:
            return True
        
        valid = True
        prev_end = 0.0
        
        for i, event in enumerate(events):
            start = event.get("start", 0)
            end = event.get("end", 0)
            text = event.get("text", "")[:20]  # 截取前20字符用于日志
            
            # 检查负时长
            if end < start:
                print(f"❌ 事件 {i}: 负时长 (start={start:.2f}, end={end:.2f}) - \"{text}...\"")
                valid = False
            
            # 检查单调性（start 应该 >= 前一个的 end）
            if start < prev_end - self.TIME_TOLERANCE:
                print(f"❌ 事件 {i}: 时间重叠 (start={start:.2f} < prev_end={prev_end:.2f}) - \"{text}...\"")
                valid = False
            
            prev_end = end
        
        if valid and self._debug_mode:
            print(f"✅ 时间轴验证通过: {len(events)} 个事件")
        
        return valid
    
    # 句间气口时长（秒）
    VOICE_GAP_DURATION = 0.5
    
    def run_timeline(self, events: list, generate_voice: bool = None) -> None:
        """
        执行完整时间轴
        
        注意：为避免语音重叠，事件会按顺序执行，实际开始时间使用当前 _current_time，
        而不是预先定义的 start 时间。事件中的 "end - start" 用于计算最小持续时间。
        
        Args:
            events: 事件列表 [{"start": float, "end": float, "text": str}, ...]
            generate_voice: 是否生成配音（默认使用 self._enable_voice）
        """
        # 跳过时间轴验证，因为我们使用实时时间
        should_voice = generate_voice if generate_voice is not None else self._enable_voice
        
        for i, event in enumerate(events):
            # 使用当前实时时间作为开始时间（避免重叠）
            actual_start = self._current_time
            
            # 事件中定义的持续时间
            original_start = event.get("start", 0)
            original_end = event.get("end", original_start + 1)
            event_duration = original_end - original_start
            
            text = event.get("text", "")
            color_map = event.get("color_map", None)
            
            # 生成配音（使用全局计数器）
            audio_duration = 0
            voice_path = None
            if should_voice and text:
                voice_path = self._generate_voice(text, self._voice_count)
                self._voice_count += 1
                if voice_path and os.path.exists(voice_path):
                    audio_duration = self._get_audio_duration(voice_path)
                    # 播放音频
                    self.add_sound(voice_path)
            
            # 计算实际需要的持续时间
            actual_duration = max(event_duration, audio_duration) + self.VOICE_GAP_DURATION
            actual_end = actual_start + actual_duration
            
            # 显示字幕（使用实际时间）
            self.subtitle(actual_start, actual_end, text, color_map)
            
            if self._debug_mode:
                print(f"🎙️ 事件 {i}: \"{text[:15]}...\" @ {actual_start:.2f}s -> {actual_end:.2f}s (音频:{audio_duration:.2f}s)")
        
        # 清除最后的字幕
        if self._subtitle is not None:
            self.clear_subtitle()
    
    def speak(self, text: str, targets: list = None, 
                              subtitle: str = None, color_map: dict = None, 
                              min_duration: float = 2.0) -> float:
        """
        播放语音 + 字幕动画 + 高亮动画
        
        流程：播放语音 + 字幕动画 + 高亮动画 (同时) -> 等待音频结束 -> 气口
        
        Args:
            text: 配音文稿（TTS 朗读的文字，应为口语化中文）
            targets: 要高亮的对象列表（可选）
            subtitle: 字幕文本（屏幕显示的文字），如果为 None 则使用 text
            color_map: 字幕着色映射
            min_duration: 最小持续时间
            
        Returns:
            实际使用的时长（秒）
            
        示例:
            # 简单用法（配音和字幕相同）
            self.speak("由 f 2 等于 4")
            
            # 配音和字幕分离
            self.speak(
                text="由 f 2 等于 4",           # TTS 读这个
                subtitle="由 f(2) = 4",          # 屏幕显示这个
            )
            
            # 带高亮的用法
            self.speak(
                text="f 负 2 等于 负 4",       # TTS 读这个
                subtitle="f(-2) = -4",          # 屏幕显示这个
                targets=[formula],
            )
        """
        if not text:
            return 0
        
        # 如果没有指定字幕，使用配音文稿作为字幕
        display_text = subtitle if subtitle is not None else text
        
        start_time = self._current_time
        
        if self._debug_mode:
            print(f"\n{'='*50}")
            print(f"🎬 speak 开始 @ {start_time:.2f}s")
            print(f"   配音: \"{text[:30]}...\"")
            if subtitle:
                print(f"   字幕: \"{subtitle[:30]}...\"")
            print(f"   高亮目标数: {len(targets) if targets else 0}")
        
        # 生成配音（使用 text）
        voice_path = None
        audio_duration = min_duration
        if self._enable_voice:
            voice_path = self._generate_voice(text, self._voice_count)
            self._voice_count += 1
            if voice_path and os.path.exists(voice_path):
                audio_duration = max(self._get_audio_duration(voice_path), min_duration)
                if self._debug_mode:
                    print(f"   音频时长: {audio_duration:.2f}s")
        
        # 创建字幕（使用 display_text）
        new_sub = self.make_subtitle(display_text, color_map)
        
        # 准备动画
        # new_sub 是 VGroup: [0]=圆角矩形背景, [1]=文字
        anims = []
        if self._subtitle is None:
            # 第一次显示：背景用 ShowCreation，文字用 Write
            anims.append(ShowCreation(new_sub[0]))  # 圆角矩形背景
            anims.append(Write(new_sub[1]))          # 文字
        else:
            # 后续变换：一对一变换
            anims.append(Transform(self._subtitle[0], new_sub[0]))  # 背景→背景
            anims.append(Transform(self._subtitle[1], new_sub[1]))  # 文字→文字
        
        # 添加高亮动画（依次循环使用不同效果）
        highlight_decorations = []
        if targets:
            for target in targets:
                if target is not None:
                    # 获取当前效果
                    effect = self._highlight_effects[self._highlight_effect_index]
                    self._highlight_effect_index = (self._highlight_effect_index + 1) % len(self._highlight_effects)
                    
                    # 获取当前颜色
                    color = self._get_next_focus_box_color()
                    
                    if effect == "box":
                        # 辉光方框效果
                        decoration = create_glow_surrounding_rect(
                            target, 
                            color=color, 
                            buff=0.1,
                            stroke_width=2,
                            fill_opacity=0.2,
                            n_glow_layers=4,
                            max_glow_width=10,
                            base_opacity=0.25,
                        )
                        anims.append(FadeIn(decoration))
                        highlight_decorations.append(decoration)
                        
                    elif effect == "underline":
                        # 辉光扫描下划线效果 (GlowDot + 彗尾) - 单程扫描1次
                        left_point = target.get_corner(DL) + DOWN * 0.08
                        right_point = target.get_corner(DR) + DOWN * 0.08
                        
                        # 创建下划线参考线（半透明）
                        underline_ref = Line(left_point, right_point, color=color, stroke_width=2)
                        underline_ref.set_stroke(opacity=0.4)
                        
                        # 创建增强辉光点
                        glow_dot = GlowDot(
                            center=left_point,
                            radius=0.35,           # 更大的辉光点
                            color=color,
                            glow_factor=2.5,       # 更强的辉光
                        )
                        
                        # 位置追踪器
                        sweep_tracker = ValueTracker(0)
                        n_sweeps = 1  # 来回次数（1次=单程）
                        
                        def make_sweep_position_func(lp, rp, trk, n_sweeps):
                            def get_pos():
                                # t从0到1，映射为来回n_sweeps次的运动
                                # 使用正弦函数实现平滑来回
                                raw_t = trk.get_value()
                                # 正弦来回：sin(π * n_sweeps * t) 的绝对值，但我们需要平滑来回
                                # 使用 (1 - cos(2π * n_sweeps * t)) / 2 实现平滑来回
                                # 或者简单地：t * n_sweeps % 1，然后三角波
                                cycle_t = raw_t * n_sweeps * 2  # 每个来回是2个单程
                                cycle_t = cycle_t % 2  # 0~2 范围
                                if cycle_t > 1:
                                    t = 2 - cycle_t  # 返程
                                else:
                                    t = cycle_t  # 去程
                                x = interpolate(lp[0], rp[0], t)
                                return np.array([x, lp[1], 0])
                            return get_pos
                        
                        get_sweep_pos = make_sweep_position_func(left_point, right_point, sweep_tracker, n_sweeps)
                        
                        def make_dot_sweep_updater(pos_func):
                            def updater(dot):
                                dot.move_to(pos_func())
                            return updater
                        
                        glow_dot.add_updater(make_dot_sweep_updater(get_sweep_pos))
                        
                        # 创建增强彗尾效果
                        if _TRACING_TAIL_AVAILABLE:
                            sweep_tail = TracingTailPMobject(
                                traced_point_func=get_sweep_pos,
                                max_tail_length=60,        # 更长的尾巴
                                tail_lifetime=0.6,         # 更长的尾巴寿命
                                base_color=color,
                                opacity_fade=(1, 0.0),   # 更亮的起始
                                width_fade=(0.2, 0.01),   # 更粗的尾巴
                                glow_factor=2.5,           # 更强的辉光
                            )
                            
                            def make_tail_sweep_updater():
                                def updater(mob, dt):
                                    mob.update_tail(dt)
                                return updater
                            
                            sweep_tail.add_updater(make_tail_sweep_updater())
                            decoration = Group(underline_ref, sweep_tail, glow_dot)
                        else:
                            decoration = Group(underline_ref, glow_dot)
                        
                        # 扫描动画：tracker从0到1，内部会自动来回3次
                        anims.append(FadeIn(underline_ref))
                        anims.append(FadeIn(glow_dot))
                        anims.append(sweep_tracker.animate.set_value(1))
                        highlight_decorations.append(decoration)
                        
                    elif effect == "indicate":
                        # Indicate 缩放+变色效果
                        anims.append(Indicate(target, color=RED, scale_factor=1.5))
                        
                    elif effect == "focus":
                        # 聚光灯效果
                        anims.append(FocusOn(target, color=color, opacity=0.2))
                        
                    elif effect == "wave":
                        # 波浪效果
                        anims.append(ApplyWave(target, direction=UP, amplitude=0.15))
                        
                    elif effect == "flash":
                        # 颜色渐变闪烁效果：白->红->紫->白
                        anims.append(self._create_flash_animation(target, n_cycles=1, duration=1.5))
                        
                    elif effect == "circumscribe":
                        # 环绕描边效果 - 使用 ShowPassingFlash 替代不存在的 Circumscribe
                        from manimlib import ShowPassingFlash, Rectangle
                        rect = SurroundingRectangle(target, color=color, stroke_width=3, buff=0.1)
                        anims.append(ShowPassingFlash(rect, run_time=1.0))
                        
                    elif effect == "grow":
                        # 水波扩散光环效果（1.5秒）
                        wave_anim, wave_rings = self._create_growing_halo(target, color=color, duration=1.5)
                        anims.append(wave_anim)
                        highlight_decorations.append(wave_rings)  # 记录以便清理
        
        # 动画时长（取音频时长的一部分，但不超过1.2秒）
        anim_duration = min(1.2, audio_duration * 0.5)
        
        # 先添加音频（在动画开始的同时播放）
        if voice_path:
            self.add_sound(voice_path)
            if self._debug_mode:
                print(f"   🔊 音频添加 @ {self._current_time:.2f}s")
        
        # 播放所有动画（字幕 + 高亮同时进行）
        self.play(*anims, run_time=anim_duration, _is_subtitle=True)
        
        # 将高亮装饰物添加到场景（如果有的话）
        for decoration in highlight_decorations:
            self.add(decoration)
        
        # 更新字幕引用
        if self._subtitle is not None:
            self.remove(self._subtitle)
        self.add(new_sub)
        self._subtitle = new_sub
        self._subtitle_count += 1
        self._current_time += anim_duration
        
        if self._debug_mode:
            print(f"   📝 字幕+高亮动画完成 @ {self._current_time:.2f}s")
        
        # 等待音频剩余时间
        remaining = audio_duration - anim_duration
        if remaining > 0:
            self.wait(remaining)
            self._current_time += remaining
            if self._debug_mode:
                print(f"   ⏳ 等待音频结束 @ {self._current_time:.2f}s")
        
        # 清理高亮装饰物
        for decoration in highlight_decorations:
            self.play(FadeOut(decoration), run_time=0.3)
        
        # 气口
        self.wait(self.VOICE_GAP_DURATION)
        self._current_time += self.VOICE_GAP_DURATION
        
        if self._debug_mode:
            total_duration = self._current_time - start_time
            print(f"   ✅ speak 结束 @ {self._current_time:.2f}s (总时长: {total_duration:.2f}s)")
            print(f"{'='*50}\n")
        
        return audio_duration
    
    def speak_sequence(self, texts: list, min_duration: float = 2.0) -> None:
        """
        顺序播放多条语音 - 自动链式计算时间
        
        AI 工作流推荐使用此方法，只需提供文本列表。
        
        Args:
            texts: 文本列表 ["第一句", "第二句", ...]
                   或字典列表 [{"text": "第一句", "color_map": {...}}, ...]
            min_duration: 每句最小时长
            
        示例:
            self.speak_sequence([
                "欢迎观看本期视频",
                "今天我们来学习向量",
                {"text": "重点是向量加法", "color_map": {"重点": YELLOW}}
            ])
        """
        for item in texts:
            if isinstance(item, str):
                self.speak(item, min_duration=min_duration)
            elif isinstance(item, dict):
                text = item.get("text", "")
                color_map = item.get("color_map", None)
                duration = item.get("min_duration", min_duration)
                self.speak(text, color_map=color_map, min_duration=duration)
    
    # ==================== 字幕方法 ====================
    
    def make_subtitle(self, text: str, color_map: dict = None) -> VGroup:
        """
        创建统一样式的字幕（带圆角矩形背景）
        
        自动处理中文换行，支持文字着色。
        字幕和背景自动固定在屏幕上（fix_in_frame）。
        
        Args:
            text: 字幕文本
            color_map: 着色映射 {"关键词": RED, "重点": YELLOW}
            
        Returns:
            VGroup: [0]=圆角矩形背景, [1]=文字
        """
        # 中文自动换行
        wrapped_text = self._wrap_chinese_text(text, self._subtitle_max_chars)
        
        # 构建 t2c (text to color) 映射
        # 默认整个文本为黑色，再叠加用户指定的着色
        t2c = {wrapped_text: self.SUBTITLE_COLOR}  # 先设置整体为黑色
        if color_map:
            for keyword, color in color_map.items():
                t2c[keyword] = color
        
        # 创建字幕文字
        subtitle_text = Text(
            wrapped_text,
            font=self.SUBTITLE_FONT,
            font_size=self._subtitle_font_size,
            t2c=t2c
        )
        
        # 创建自适应圆角矩形背景
        bg = RoundedRectangle(
            width=subtitle_text.get_width() + 2 * self.SUBTITLE_BG_BUFF,
            height=subtitle_text.get_height() + 2 * self.SUBTITLE_BG_BUFF,
            corner_radius=self.SUBTITLE_BG_CORNER_RADIUS,
            fill_color=self.SUBTITLE_BG_COLOR,
            fill_opacity=self.SUBTITLE_BG_OPACITY,
            stroke_width=0
        )
        
        # 组合：先背景后文字（文字在上层）
        subtitle_group = VGroup(bg, subtitle_text)
        subtitle_group.to_edge(DOWN, buff=self._subtitle_edge_buff)
        
        # 固定在屏幕上（相机移动时不受影响）
        subtitle_group.fix_in_frame()
        
        return subtitle_group
    
    def set_subtitle_style(self, font_size: float = None, edge_buff: float = None, max_chars: int = None) -> None:
        """
        设置字幕样式参数
        
        Args:
            font_size: 字号（默认 28）
            edge_buff: 底部边距（默认 0.5）
            max_chars: 每行最大字符数（默认根据屏幕宽度自动计算）
        """
        if font_size is not None:
            self._subtitle_font_size = font_size
        if edge_buff is not None:
            self._subtitle_edge_buff = edge_buff
        if max_chars is not None:
            self._subtitle_max_chars = max_chars
    
    def _wrap_chinese_text(self, text: str, max_chars: int) -> str:
        """
        中文文本换行（按显示宽度）
        
        中文字符宽度计算为2，英文/数字/空格/标点计算为1。
        这样可以确保每行的视觉宽度大致相同。
        
        Args:
            text: 原始文本
            max_chars: 每行最大显示宽度（以半角字符为单位）
            
        Returns:
            换行后的文本
        """
        def char_width(c: str) -> int:
            """计算单个字符的显示宽度"""
            # 中文字符宽度为2
            if '\u4e00' <= c <= '\u9fff':  # 中文字符
                return 2
            elif '\u3000' <= c <= '\u303f':  # 中文标点（等效一个中文字）
                return 1
            elif '\uff00' <= c <= '\uffef':  # 全角字符
                return 1
            elif c in '，。！？、；：""''（）【】《》—…':  # 常用中文标点（等效一个中文字）
                return 1
            else:  # 英文、数字、空格、半角标点等
                return 1
        
        def text_width(s: str) -> int:
            """计算字符串的总显示宽度"""
            return sum(char_width(c) for c in s)
        
        # 如果总宽度不超过限制，直接返回
        if text_width(text) <= max_chars * 2:  # max_chars 是字符数，转换为显示宽度
            return text
        
        lines = []
        current_line = ""
        current_width = 0
        max_width = max_chars * 2  # 18个中文字符 = 36个显示单位
        
        for char in text:
            w = char_width(char)
            if current_width + w > max_width:
                lines.append(current_line)
                current_line = char
                current_width = w
            else:
                current_line += char
                current_width += w
        
        if current_line:
            lines.append(current_line)
        
        return "\n".join(lines)
    
    def subtitle(self, t0: float, t1: float, text: str, color_map: dict = None) -> None:
        """
        显示字幕并同步时间
        
        第一句使用 Write 动画，之后使用 Transform。
        
        Args:
            t0: 开始时间
            t1: 结束时间
            text: 字幕文本
            color_map: 着色映射 {"关键词": RED, "重点": YELLOW}
        """
        if not text:
            return
        
        # 同步到开始时间
        self.sync_to(t0)
        
        # 创建新字幕（支持着色）
        new_sub = self.make_subtitle(text, color_map)
        
        if self._subtitle is None:
            # 第一句：使用 Write（标记为字幕，不播放音效）
            self.play(Write(new_sub), run_time=self.WRITE_DURATION, _is_subtitle=True)
            self._subtitle = new_sub
            self._current_time += self.WRITE_DURATION
            if self._debug_mode:
                print(f"📝 Write 字幕: \"{text[:20]}...\" @ {t0:.2f}s")
        else:
            # 之后：使用 Transform（标记为字幕，不播放音效）
            self.play(Transform(self._subtitle, new_sub), run_time=self.TRANSFORM_DURATION, _is_subtitle=True)
            # 关键：更新引用为新对象
            self.remove(self._subtitle)
            self.add(new_sub)
            self._subtitle = new_sub
            self._current_time += self.TRANSFORM_DURATION
            if self._debug_mode:
                print(f"🔄 Transform 字幕: \"{text[:20]}...\" @ {t0:.2f}s")
        
        self._subtitle_count += 1
        
        # 推进到结束时间
        self.advance_to(t1)
    
    def clear_subtitle(self, t: float = None) -> None:
        """
        淡出清除字幕
        
        Args:
            t: 清除时间（可选，默认立即清除）
        """
        if self._subtitle is None:
            return
        
        if t is not None:
            self.sync_to(t)
        
        self.play(FadeOut(self._subtitle), run_time=self.FADE_DURATION)
        self._current_time += self.FADE_DURATION
        self._subtitle = None
        
        if self._debug_mode:
            print(f"🗑️ 清除字幕 @ {self._current_time:.2f}s")
    
    # ==================== 配音集成 ====================
    
    def set_voice(self, voice: str) -> None:
        """
        设置 TTS 语音
        
        Args:
            voice: 语音名称（如 "zh-CN-XiaoxiaoNeural"）
        """
        self._voice = voice
    
    def set_voice_enabled(self, enabled: bool) -> None:
        """
        启用/禁用配音
        
        Args:
            enabled: 是否启用
        """
        self._enable_voice = enabled
    
    def clear_voice_cache(self) -> int:
        """
        清理当前场景的配音缓存
        
        用于脚本修改后强制重新生成所有配音
        
        Returns:
            删除的文件数量
        """
        import glob
        pattern = os.path.join(self._sounds_dir, "line_*.mp3")
        files = glob.glob(pattern)
        deleted_count = 0
        for f in files:
            try:
                os.remove(f)
                deleted_count += 1
            except OSError as e:
                if self._debug_mode:
                    print(f"⚠️ 无法删除文件 {os.path.basename(f)}: {e}")
        if self._debug_mode:
            print(f"🗑️ 已清理 {deleted_count}/{len(files)} 个配音缓存文件")
        return deleted_count
    
    def _get_text_hash(self, text: str) -> str:
        """
        获取文本的短哈希值（用于文件命名）
        
        Args:
            text: 文本内容
            
        Returns:
            6位哈希字符串
        """
        import hashlib
        return hashlib.md5(text.encode('utf-8')).hexdigest()[:6]
    
    def _generate_voice(self, text: str, event_id: int) -> str:
        """
        生成配音文件
        
        使用文本哈希确保缓存有效性：
        - 文件名格式: line_001_a3f8c1.mp3
        - 文本变化时哈希变化，自动生成新文件
        
        Args:
            text: 配音文本
            event_id: 事件 ID（用于文件命名）
            
        Returns:
            生成的音频文件路径
        """
        try:
            # 动态导入 TTSGenerator
            from utils.tts_generator import TTSGenerator
        except ImportError:
            try:
                # 尝试从父目录导入 (auto_manim/utils/)
                import sys
                script_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(script_dir)  # auto_manim 目录
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                from utils.tts_generator import TTSGenerator
            except ImportError as e:
                print(f"⚠️ 无法导入 TTSGenerator，跳过配音生成: {e}")
                return None
        
        # 使用文本哈希确保缓存有效性
        text_hash = self._get_text_hash(text)
        output = os.path.join(self._sounds_dir, f"line_{event_id:03d}_{text_hash}.mp3")
        
        # 如果相同哈希的文件已存在，可以安全复用
        if os.path.exists(output):
            if self._debug_mode:
                print(f"♻️ 复用配音: {output}")
            return output
        
        # 清理同索引的旧文件（不同哈希的旧版本）
        import glob
        old_files = glob.glob(os.path.join(self._sounds_dir, f"line_{event_id:03d}_*.mp3"))
        for old_file in old_files:
            if old_file != output:
                try:
                    os.remove(old_file)
                    if self._debug_mode:
                        print(f"🗑️ 删除旧配音: {os.path.basename(old_file)}")
                except OSError as e:
                    if self._debug_mode:
                        print(f"⚠️ 无法删除旧文件 {os.path.basename(old_file)}: {e}")
        
        try:
            tts = TTSGenerator(voice=self._voice)
            asyncio.run(tts.generate(text, output))
            if self._debug_mode:
                print(f"🎤 生成配音: {output}")
            return output
        except Exception as e:
            print(f"❌ 配音生成失败: {e}")
            return None
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """
        获取音频文件时长
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            音频时长（秒），如果无法获取返回 0
        """
        # 方法1: 使用 pydub (推荐)
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_mp3(audio_path)
            duration = len(audio) / 1000.0  # 毫秒转秒
            if self._debug_mode:
                print(f"   📊 pydub 获取时长: {duration:.2f}s")
            return duration
        except ImportError:
            pass  # pydub 未安装，尝试其他方法
        except Exception as e:
            if self._debug_mode:
                print(f"   ⚠️ pydub 解析失败: {e}")
        
        # 方法2: 使用文件大小估算 (edge-tts 约 48kbps = 6KB/s)
        try:
            file_size = os.path.getsize(audio_path)
            estimated_duration = file_size / 6000.0
            if self._debug_mode:
                print(f"   📊 估算时长: {estimated_duration:.2f}s (文件大小: {file_size} bytes)")
            return estimated_duration
        except OSError as e:
            if self._debug_mode:
                print(f"   ❌ 无法获取文件大小: {e}")
            return 0
    
    # ==================== 调试与导出 ====================
    
    def enable_debug(self, enabled: bool = True) -> None:
        """
        启用/禁用调试模式
        
        Args:
            enabled: 是否启用
        """
        self._debug_mode = enabled
    
    def enable_time_hud(self) -> None:
        """
        在画面角落显示当前时间
        """
        self._time_tracker = ValueTracker(0)
        
        self._time_hud = DecimalNumber(
            0,
            num_decimal_places=2,
            font_size=24,
            color=GREY
        )
        self._time_hud.to_corner(UP + RIGHT, buff=0.3)
        
        # 添加更新器
        def update_hud(hud):
            hud.set_value(self._current_time)
        
        self._time_hud.add_updater(update_hud)
        self.add(self._time_hud)
    
    def mark(self, label: str, t: float = None) -> None:
        """
        记录关键节点
        
        Args:
            label: 标记名称
            t: 时间（默认当前时间）
        """
        time = t if t is not None else self._current_time
        self._markers.append({"label": label, "time": time})
        if self._debug_mode:
            print(f"📍 标记: {label} @ {time:.2f}s")
    
    def export_srt(self, events: list, path: str) -> None:
        """
        导出 SRT 字幕文件
        
        Args:
            events: 事件列表
            path: 输出文件路径
        """
        with open(path, "w", encoding="utf-8") as f:
            for i, event in enumerate(events):
                start = event.get("start", 0)
                end = event.get("end", 0)
                text = event.get("text", "")
                
                # SRT 时间格式: HH:MM:SS,mmm
                start_str = self._seconds_to_srt_time(start)
                end_str = self._seconds_to_srt_time(end)
                
                f.write(f"{i + 1}\n")
                f.write(f"{start_str} --> {end_str}\n")
                f.write(f"{text}\n\n")
        
        print(f"📄 SRT 导出: {path}")
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """
        秒转换为 SRT 时间格式
        
        Args:
            seconds: 秒数
            
        Returns:
            SRT 时间字符串 (HH:MM:SS,mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def get_current_time(self) -> float:
        """
        获取当前场景时间
        
        Returns:
            当前时间（秒）
        """
        return self._current_time
    
    def get_markers(self) -> list:
        """
        获取所有标记
        
        Returns:
            标记列表 [{"label": str, "time": float}, ...]
        """
        return self._markers.copy()
    
    # ==================== 文本高亮方法 ====================
    
    def highlight_text(self, target: "Mobject", effect: str = "random", 
                       color=YELLOW, run_time: float = 1.0,
                       max_duration: float = None) -> "Mobject":
        """
        高亮显示指定内容，支持多种随机效果
        
        装饰物会自动在 max_duration 秒后移除（默认 3 秒）
        
        Args:
            target: 要高亮的目标对象 (Text/Tex 的子对象或任意 Mobject)
            effect: 高亮效果，可选:
                - "random": 随机选择一种效果
                - "box": 辉光方框 (GlowSurroundingRect)
                - "underline": 下划线
                - "indicate": Indicate 缩放+变色
                - "focus": FocusOn 聚光灯
                - "wave": 波浪效果
            color: 高亮颜色
            run_time: 动画时长
            max_duration: 装饰最大存留时间（默认使用 _highlight_max_duration）
            
        Returns:
            创建的高亮装饰对象（如方框），便于后续移除；若为动画效果则返回 None
            
        示例:
            # 高亮 Tex 中的特定部分
            formula = Tex("E = mc^2")
            self.highlight_text(formula[0][2:5], effect="box")
        """
        # 先清理过期的高亮装饰
        self._cleanup_expired_highlights()
        
        effects = ["box", "underline", "indicate", "focus", "wave"]
        
        if effect == "random":
            effect = random.choice(effects)
        
        if self._debug_mode:
            print(f"🎨 highlight_text: 使用效果 '{effect}'")
        
        decoration = None
        
        # 换行检测：如果目标宽度超过高度的 5 倍，可能是多行文本
        width = target.get_width()
        height = target.get_height()
        is_multiline = height > 0 and width / height < 2  # 宽高比小于2可能是多行
        
        if effect == "box":
            # 辉光方框效果
            decoration = create_glow_surrounding_rect(
                target, 
                color=color, 
                buff=0.1,
                stroke_width=2,
                fill_opacity=0.2,
                n_glow_layers=4,
                max_glow_width=10,
                base_opacity=0.25,
            )
            self.play(FadeIn(decoration), run_time=run_time)
            
        elif effect == "underline":
            # 下划线效果
            decoration = Underline(target, color=color, stroke_width=3)
            self.play(ShowCreation(decoration), run_time=run_time)
            
        elif effect == "indicate":
            # Indicate 缩放+变色效果
            self.play(Indicate(target, color=color, scale_factor=1.2), run_time=run_time)
            
        elif effect == "focus":
            # 聚光灯效果
            self.play(FocusOn(target, color=color, opacity=0.2), run_time=run_time)
            
        elif effect == "wave":
            # 波浪效果
            self.play(ApplyWave(target, direction=UP, amplitude=0.15), run_time=run_time)
        
        # 将装饰物加入自动清理追踪列表
        if decoration is not None:
            duration = max_duration if max_duration is not None else self._highlight_max_duration
            self._highlight_decorations.append({
                "decoration": decoration,
                "add_time": self._current_time,
                "max_duration": duration
            })
        
        return decoration
    
    # ==================== 强调效果辅助方法 ====================
    
    def _create_flash_animation(self, target, color=YELLOW, n_cycles=1, duration=1.5):
        """
        创建颜色渐变闪烁动画：物体颜色平滑过渡 白->红->紫->白
        
        Args:
            target: 目标对象
            color: 未使用，保留兼容性
            n_cycles: 颜色循环次数
            duration: 动画时长
        """
        from manimlib import Animation, interpolate_color
        
        # 颜色渐变：白 -> 红 -> 紫 -> 白
        GRADIENT_COLORS = [
            "#FFFFFF",  # 白
            "#FF4444",  # 红
            "#AA44FF",  # 紫
            "#FFFFFF",  # 白（回到原点）
        ]
        
        class ColorGradientAnimation(Animation):
            def __init__(self, mobject, n_cycles=1, **kwargs):
                self.n_cycles = n_cycles
                self.colors = GRADIENT_COLORS
                self.original_color = mobject.get_color() if hasattr(mobject, 'get_color') else WHITE
                super().__init__(mobject, **kwargs)
            
            def interpolate_mobject(self, alpha):
                # 在4色之间平滑过渡（白->红->紫->白）
                # alpha从0到1，映射到颜色序列
                n_segments = len(self.colors) - 1  # 3段
                total_progress = alpha * n_segments * self.n_cycles
                segment = int(total_progress) % n_segments
                blend = total_progress - int(total_progress)
                
                # 平滑插值到下一个颜色
                current_color = self.colors[segment]
                next_color = self.colors[segment + 1]
                
                try:
                    blended_color = interpolate_color(current_color, next_color, blend)
                    self.mobject.set_color(blended_color)
                except:
                    pass
            
            def finish(self):
                # 动画结束时恢复原色
                try:
                    self.mobject.set_color(self.original_color)
                except:
                    pass
                super().finish()
        
        return ColorGradientAnimation(target, n_cycles=n_cycles, run_time=duration)
    
    def _create_growing_halo(self, target, color=YELLOW, n_rings=4, duration=1.5):
        """
        创建水波扩散动画：从目标向外扩散的波纹，带有宽度波动效果
        
        Args:
            target: 目标对象
            color: 光环颜色
            n_rings: 光环层数
            duration: 动画时长（默认1.5秒）
        
        Returns:
            (animation, rings): 动画对象和圆环VGroup（用于后续清理）
        """
        from manimlib import Animation, UpdateFromAlphaFunc
        
        center = target.get_center()
        width = target.get_width()
        height = target.get_height()
        base_radius = max(width, height) / 2 + 0.15
        
        # 创建多个同心圆环
        rings = VGroup()
        for i in range(n_rings):
            ring = Circle(
                radius=base_radius,
                stroke_color=color,
                stroke_width=3,
                stroke_opacity=0.7,
                fill_opacity=0,
            ).move_to(center)
            rings.add(ring)
        
        # 水波动画更新器
        def wave_updater(mob, alpha):
            for i, ring in enumerate(mob):
                # 每个环有不同的相位偏移，产生波浪传播效果
                phase_offset = i * 0.25  # 相位差
                wave_alpha = (alpha + phase_offset) % 1.0
                
                # 半径从内向外扩散
                expansion = 0.8 * wave_alpha  # 最大扩展0.8
                current_radius = base_radius * (1 + expansion)
                
                # 宽度正弦波动：模拟水波的粗细变化
                # 使用正弦让宽度在2~5之间波动
                width_phase = np.sin(2 * np.pi * 2 * wave_alpha)  # 2个周期
                stroke_w = 3.5 + 1.5 * width_phase  # 2~5范围
                
                # 透明度：越外越淡，同时有波动
                base_opacity = 0.8 * (1 - wave_alpha * 0.7)
                opacity_wave = 0.15 * np.sin(2 * np.pi * 3 * wave_alpha)
                opacity = max(0.1, base_opacity + opacity_wave)
                
                # 应用更新
                ring.set_width(current_radius * 2)
                ring.set_stroke(width=stroke_w, opacity=opacity)
                ring.move_to(center)
        
        anim = UpdateFromAlphaFunc(rings, wave_updater, run_time=duration)
        return anim, rings  # 返回动画和圆环（用于清理）
    
    def _cleanup_expired_highlights(self) -> None:
        """清理过期的高亮装饰（超过 max_duration 的）"""
        if not self._highlight_decorations:
            return
        
        current = self._current_time
        expired = []
        remaining = []
        
        for item in self._highlight_decorations:
            elapsed = current - item["add_time"]
            if elapsed >= item["max_duration"]:
                expired.append(item["decoration"])
            else:
                remaining.append(item)
        
        # 更新列表
        self._highlight_decorations = remaining
        
        # 批量移除过期装饰
        if expired:
            for dec in expired:
                if dec in self.mobjects:
                    self.remove(dec)
            if self._debug_mode:
                print(f"🗑️ 自动清理 {len(expired)} 个过期高亮装饰")
    
    def remove_highlight(self, decoration: "Mobject", run_time: float = 0.3) -> None:
        """
        移除高亮装饰
        
        Args:
            decoration: highlight_text 返回的装饰对象
            run_time: 淡出时长
        """
        if decoration is not None:
            self.play(FadeOut(decoration), run_time=run_time)
    
    # ==================== GlowDot 呼吸效果 API ====================
    
    def create_breathing_glow_dot(
        self,
        center=None,
        mode=None,
        color=None,
        radius: float = 0.35,
        glow_factor: float = 1.0,
        frequency: float = 0.8,
        min_radius: float = 0.2,
        max_radius: float = 0.5,
        auto_add: bool = True,
    ):
        """
        创建带呼吸效果的 GlowDot（统一 API）
        
        Args:
            center: 中心位置 (默认 ORIGIN)
            mode: 呼吸模式 (默认自动循环选择下一个模式)
                  可选: "basic", "rainbow", "heartbeat", "pulse", "wave"
            color: 初始颜色 (默认 BLUE，rainbow 模式会自动循环)
            radius: 初始半径
            glow_factor: 辉光强度 (固定为 1)
            frequency: 呼吸频率 (Hz)
            min_radius: 最小半径
            max_radius: 最大半径
            auto_add: 是否自动添加到场景
            
        Returns:
            GlowDot: 带呼吸效果的辉光点
            
        示例:
            # 自动选择下一个模式
            dot = self.create_breathing_glow_dot(center=ORIGIN)
            
            # 指定模式
            dot = self.create_breathing_glow_dot(
                center=LEFT * 2,
                mode="rainbow",
            )
        """
        if not _BREATHING_AVAILABLE:
            # 回退到普通 GlowDot
            from manimlib import GlowDot as _GlowDot
            if center is None:
                center = ORIGIN
            dot = _GlowDot(
                center=center,
                radius=radius,
                color=color or BLUE,
                glow_factor=glow_factor,
            )
            if auto_add:
                self.add(dot)
            return dot
        
        if center is None:
            center = ORIGIN
        
        # 自动选择下一个模式
        if mode is None:
            mode = self._breathing_manager.next_mode() if self._breathing_manager else BreathingMode.BASIC
        elif isinstance(mode, str):
            # 支持字符串模式名称
            mode_map = {
                "basic": BreathingMode.BASIC,
                "rainbow": BreathingMode.RAINBOW,
                "heartbeat": BreathingMode.HEARTBEAT,
                "pulse": BreathingMode.PULSE,
                "wave": BreathingMode.WAVE,
            }
            mode = mode_map.get(mode.lower(), BreathingMode.BASIC)
        
        # 默认颜色
        if color is None:
            color = BLUE
        
        # 创建呼吸辉光点
        dot = create_breathing_glow_dot(
            center=center,
            mode=mode,
            color=color,
            radius=radius,
            glow_factor=glow_factor,
            frequency=frequency,
            min_radius=min_radius,
            max_radius=max_radius,
            auto_start=True,
        )
        
        if auto_add:
            self.add(dot)
        
        return dot
    
    def next_breathing_mode(self):
        """
        获取下一个呼吸模式（循环）
        
        Returns:
            BreathingMode: 下一个呼吸模式
        """
        if self._breathing_manager:
            return self._breathing_manager.next_mode()
        return None
    
    def reset_breathing_modes(self):
        """重置呼吸模式循环到第一个"""
        if self._breathing_manager:
            self._breathing_manager.reset()
    
    def get_breathing_modes(self):
        """
        获取所有可用的呼吸模式
        
        Returns:
            list: 模式列表 ["basic", "rainbow", "heartbeat", "pulse", "wave"]
        """
        if self._breathing_manager:
            return [m for m in self._breathing_manager.get_all_modes()]
        return []
    
    # ==================== 区域标注方法 ====================
    
    def annotate_region(self, region: "Mobject", annotation: str,
                        bg_color=BLUE, bg_opacity: float = 0.85,
                        text_color=WHITE, text_font_size: int = 24,
                        position=None) -> VGroup:
        """
        使用纯色背景覆盖指定区域，显示标注信息
        
        目的：覆盖住图像，让标注信息突出显示
        
        Args:
            region: 要覆盖的目标区域
            annotation: 标注文本
            bg_color: 背景颜色
            bg_opacity: 背景透明度（0.85 接近不透明）
            text_color: 文本颜色
            text_font_size: 文本字号
            position: 文本位置，None 表示居中
            
        Returns:
            VGroup: [背景矩形, 标注文本]，便于后续移除
        """
        # 创建覆盖背景
        bg = Rectangle(
            width=region.get_width() + 0.4,
            height=region.get_height() + 0.4,
            fill_color=bg_color,
            fill_opacity=bg_opacity,
            stroke_width=0
        ).move_to(region)
        
        # 创建标注文本
        label = Text(
            annotation,
            font=self.SUBTITLE_FONT,
            font_size=text_font_size,
            color=text_color
        )
        
        if position is None:
            label.move_to(bg)
        else:
            label.next_to(bg, position, buff=0.1)
        
        # 组合
        annotation_group = VGroup(bg, label)
        
        # 动画显示
        self.play(
            FadeIn(bg),
            Write(label),
            run_time=0.5
        )
        
        if self._debug_mode:
            print(f"📌 annotate_region: '{annotation}'")
        
        return annotation_group
    
    def remove_annotation(self, annotation_group: VGroup, run_time: float = 0.3) -> None:
        """
        移除区域标注
        
        Args:
            annotation_group: annotate_region 返回的 VGroup
            run_time: 淡出时长
        """
        self.play(FadeOut(annotation_group), run_time=run_time)
    
    # ==================== 弯曲箭头标注方法 ====================
    
    def add_curved_annotation(
        self, 
        target: "Mobject", 
        annotation: str,
        direction: str = "auto",
        curve_angle: float = None,
        arrow_color=None,
        text_color=WHITE,
        text_font_size: int = 24,
        text_buff: float = 0.2,
        arrow_buff: float = 0.1,
        stroke_width=None,
        use_glow: bool = True,
        fix_in_frame: bool = False,
        run_time: float = 0.8,
    ) -> VGroup:
        """
        使用渐变辉光弯曲箭头标注目标对象，将标注文字引到空白处
        
        避免遮挡问题，使用弧形箭头将标注信息引出到空白区域
        箭头默认使用渐变宽度和渐变颜色，带辉光效果
        
        Args:
            target: 要标注的目标对象
            annotation: 标注文本
            direction: 箭头引出方向
                - "auto": 自动选择最佳空白方向
                - "up", "down", "left", "right": 指定方向
                - "ur", "ul", "dr", "dl": 对角方向
            curve_angle: 箭头弯曲角度（弧度），None 自动计算
            arrow_color: 箭头主色调（用于生成渐变），默认使用色盘轮询
            text_color: 文字颜色
            text_font_size: 文字字号
            text_buff: 文字与箭头末端的距离
            arrow_buff: 箭头与目标的距离
            stroke_width: 箭头线宽序列，None则使用默认渐变宽度
            use_glow: 是否使用辉光效果
            fix_in_frame: 是否固定在屏幕（3D场景使用）
            run_time: 动画时长
            
        Returns:
            VGroup: [箭头组, 背景, 文字]，便于后续移除
            
        示例:
            formula = Tex("E = mc^2")
            # 标注 "mc^2" 部分，箭头引到右上方
            self.add_curved_annotation(formula[0][2:], "质能方程", direction="ur")
        """
        # 获取目标中心和边界
        target_center = target.get_center()
        target_width = target.get_width()
        target_height = target.get_height()
        
        # 获取屏幕边界用于自动选择方向
        try:
            frame = self.camera.frame
            frame_width = frame.get_width()
            frame_height = frame.get_height()
        except AttributeError:
            frame_width = 14  # 默认横版宽度
            frame_height = 8  # 默认横版高度
        
        # 方向映射
        direction_map = {
            "up": UP, "down": DOWN, "left": LEFT, "right": RIGHT,
            "ur": UR, "ul": UL, "dr": DR, "dl": DL,
        }
        
        # 自动选择最佳方向（选择离屏幕边缘最远的方向）
        if direction == "auto":
            # 计算目标在屏幕中的位置
            x_ratio = target_center[0] / (frame_width / 2)  # -1 到 1
            y_ratio = target_center[1] / (frame_height / 2)  # -1 到 1
            
            # 选择相对空旷的方向
            if x_ratio < -0.3:  # 目标偏左
                direction = "ur" if y_ratio < 0 else "dr"
            elif x_ratio > 0.3:  # 目标偏右
                direction = "ul" if y_ratio < 0 else "dl"
            elif y_ratio < -0.3:  # 目标偏下
                direction = "up"
            elif y_ratio > 0.3:  # 目标偏上
                direction = "down"
            else:  # 目标居中，默认右上
                direction = "ur"
        
        # 获取方向向量
        dir_vector = direction_map.get(direction, UR)
        
        # 计算箭头距离（根据方向调整）- 缩短箭头长度
        if direction in ["ur", "ul", "dr", "dl"]:
            arrow_length = 1.2  # 对角方向
        else:
            arrow_length = 1.0  # 正交方向
        
        # 箭头起点（目标边缘）
        start_point = target.get_edge_center(dir_vector) + dir_vector * arrow_buff
        
        # 箭头终点（空白区域）
        end_point = start_point + dir_vector * arrow_length
        
        # 自动计算弯曲角度 - 增大曲率
        if curve_angle is None:
            # 根据方向选择弯曲方向，使箭头看起来自然
            if direction in ["ur", "dl"]:
                curve_angle = 0.8  # 向外弯曲，曲率更大
            elif direction in ["ul", "dr"]:
                curve_angle = -0.8
            elif direction in ["up", "down"]:
                curve_angle = 0.7 if target_center[0] < 0 else -0.7
            else:
                curve_angle = 0.7 if target_center[1] < 0 else -0.7
        
        # 获取箭头主色调（轮询色盘）
        if arrow_color is None:
            arrow_color = self._get_next_focus_box_color()
        
        # 根据主色调生成渐变色
        # 从深色到主色再到亮色
        from manimlib import color_to_rgb, rgb_to_color
        try:
            main_rgb = color_to_rgb(arrow_color)
            dark_rgb = main_rgb * 0.4  # 深色
            light_rgb = np.clip(main_rgb * 1.3 + 0.2, 0, 1)  # 亮色
            colors = [rgb_to_color(dark_rgb), arrow_color, rgb_to_color(light_rgb)]
        except:
            colors = [arrow_color]
        
        # 默认渐变宽度
        if stroke_width is None:
            stroke_width = self.GLOW_ARROW_TAPERED_WIDTH
        
        if use_glow:
            # 使用渐变辉光弯曲箭头
            arrow_group = create_glowing_curved_arrow(
                start_point,
                end_point,
                angle=curve_angle,
                colors=colors,
                stroke_width=stroke_width,
                glow_color=arrow_color,
                n_glow_layers=self.GLOW_ARROW_N_LAYERS,
                arc_scale_factor=self.GLOW_ARROW_ARC_SCALE,
                tip_scale_factor=self.GLOW_ARROW_TIP_SCALE,
                glow_width_mult=self.GLOW_ARROW_WIDTH_MULT,
                base_opacity=self.GLOW_ARROW_BASE_OPACITY,
            )
        else:
            # 不使用辉光，但仍使用渐变颜色和宽度
            arrow_group = CurvedArrow(
                start_point,
                end_point,
                angle=curve_angle,
            )
            arrow_group.set_stroke(width=stroke_width)
            arrow_group.set_color(colors)
        
        # 创建标注文字
        label = Text(
            annotation,
            font=self.SUBTITLE_FONT,
            font_size=text_font_size,
            color=text_color,
        )
        
        # 文字位置：在箭头末端，根据方向微调
        label.next_to(end_point, dir_vector, buff=text_buff)
        
        # 创建背景（可选，增加可读性）
        label_bg = RoundedRectangle(
            width=label.get_width() + 0.2,
            height=label.get_height() + 0.15,
            corner_radius=0.1,
            fill_color=BLACK,
            fill_opacity=0.7,
            stroke_width=0,
        ).move_to(label)
        
        # 组合：背景 + 文字 + 箭头组
        annotation_group = VGroup(arrow_group, label_bg, label)
        
        # 固定在屏幕（3D场景）
        if fix_in_frame:
            annotation_group.fix_in_frame()
        
        # 动画：先画箭头，再显示文字
        self.play(ShowCreation(arrow_group), run_time=run_time * 0.6)
        self.play(FadeIn(label_bg), Write(label), run_time=run_time * 0.4)
        
        if self._debug_mode:
            print(f"🏹 add_curved_annotation: '{annotation}' -> {direction}")
        
        return annotation_group
    
    def add_multi_curved_annotations(
        self,
        annotations: list,
        stagger: float = 0.3,
        **kwargs,
    ) -> list:
        """
        批量添加多个弯曲箭头标注
        
        Args:
            annotations: 标注列表 [
                {"target": mobject, "text": "标注1", "direction": "ur"},
                {"target": mobject, "text": "标注2"},  # direction 可选
            ]
            stagger: 动画错开时间
            **kwargs: 传递给 add_curved_annotation 的其他参数
            
        Returns:
            list: 所有标注组的列表
        """
        results = []
        for i, ann in enumerate(annotations):
            target = ann["target"]
            text = ann["text"]
            direction = ann.get("direction", "auto")
            
            result = self.add_curved_annotation(
                target, text, direction=direction, **kwargs
            )
            results.append(result)
            
            if i < len(annotations) - 1:
                self.wait(stagger)
        
        return results
    
    def remove_curved_annotation(
        self, 
        annotation_group: VGroup, 
        run_time: float = 0.3
    ) -> None:
        """
        移除弯曲箭头标注
        
        Args:
            annotation_group: add_curved_annotation 返回的 VGroup
            run_time: 淡出时长
        """
        self.play(FadeOut(annotation_group), run_time=run_time)
    
    # ==================== 方框引导高亮方法 ====================
    
    def _get_next_focus_box_color(self) -> str:
        """获取下一个方框颜色（轮询色盘）"""
        color = self._focus_box_color_palette[self._focus_box_color_index]
        self._focus_box_color_index = (self._focus_box_color_index + 1) % len(self._focus_box_color_palette)
        return color
    
    def _find_text_submobjects(
        self, 
        text_mobject: "Mobject", 
        keywords: list
    ) -> list:
        """
        在 Text/Tex 对象中查找关键词对应的子对象
        
        使用类似 TransformMatchingStrings 的方法匹配子对象：
        1. 首先尝试使用 StringMobject 的字符串索引 text["关键词"]
        2. 其次尝试使用 get_symbol_substrings + SequenceMatcher 匹配
        3. 最后尝试字符位置映射
        
        Args:
            text_mobject: Text 或 Tex 对象
            keywords: 要查找的关键词列表
            
        Returns:
            list: 找到的子对象列表，每个元素是一个 VGroup（可能包含多个不连续片段）
        """
        from difflib import SequenceMatcher
        
        results = []
        
        for keyword in keywords:
            found = False
            
            # === 方法1: 使用 StringMobject 的字符串索引（最可靠）===
            try:
                # Text 和 Tex 都支持字符串索引
                submob = text_mobject[keyword]
                if submob is not None and len(submob.family_members_with_points()) > 0:
                    results.append(submob)
                    found = True
                    if self._debug_mode:
                        print(f"✓ 方法1成功: text['{keyword}'] 找到子对象")
                    continue
            except (KeyError, TypeError, IndexError) as e:
                if self._debug_mode:
                    print(f"⚠️ 方法1失败: text['{keyword}'] -> {e}")
            
            # === 方法2: 使用 get_symbol_substrings + SequenceMatcher（类似 TransformMatchingStrings）===
            if not found:
                try:
                    if hasattr(text_mobject, 'get_symbol_substrings') and hasattr(text_mobject, 'substr_to_path_count'):
                        syms = text_mobject.get_symbol_substrings()
                        counts = list(map(text_mobject.substr_to_path_count, syms))
                        
                        # 将符号列表转换为字符串用于匹配
                        sym_str = ''.join(syms)
                        
                        # 查找关键词在符号字符串中的位置
                        matcher = SequenceMatcher(None, sym_str, keyword)
                        match = matcher.find_longest_match(0, len(sym_str), 0, len(keyword))
                        
                        if match.size == len(keyword):
                            # 找到完整匹配
                            # 计算起始和结束的路径索引
                            start_path_idx = sum(counts[:match.a])
                            end_path_idx = start_path_idx + sum(counts[match.a:match.a + match.size])
                            
                            submob = text_mobject[start_path_idx:end_path_idx]
                            if len(submob.family_members_with_points()) > 0:
                                results.append(submob)
                                found = True
                                if self._debug_mode:
                                    print(f"✓ 方法2成功: SequenceMatcher 找到 '{keyword}' 在索引 [{start_path_idx}:{end_path_idx}]")
                                continue
                except Exception as e:
                    if self._debug_mode:
                        print(f"⚠️ 方法2失败: SequenceMatcher -> {e}")
            
            # === 方法3: 使用文本属性直接查找（适用于简单 Text 对象）===
            if not found:
                try:
                    if hasattr(text_mobject, 'text'):
                        text_str = text_mobject.text
                        start_idx = text_str.find(keyword)
                        
                        if start_idx >= 0:
                            end_idx = start_idx + len(keyword)
                            
                            # 对于中文 Text，每个字符对应一个子对象
                            if start_idx < len(text_mobject) and end_idx <= len(text_mobject):
                                submob = text_mobject[start_idx:end_idx]
                                if len(submob.family_members_with_points()) > 0:
                                    results.append(submob)
                                    found = True
                                    if self._debug_mode:
                                        print(f"✓ 方法3成功: text.find('{keyword}') -> [{start_idx}:{end_idx}]")
                                    continue
                except Exception as e:
                    if self._debug_mode:
                        print(f"⚠️ 方法3失败: text.find -> {e}")
            
            # === 方法4: 遍历所有子对象，通过位置聚类查找（兜底方案）===
            if not found:
                if self._debug_mode:
                    print(f"⚠️ 所有方法都未找到 '{keyword}'")
        
        return results
    
    def get_text_part(
        self,
        text_mobject: "Mobject",
        keyword: str,
    ) -> "Mobject":
        """
        获取 Text/Tex 对象中指定关键词对应的子对象
        
        便捷方法，用于获取单个关键词的子对象
        
        Args:
            text_mobject: Text 或 Tex 对象
            keyword: 要查找的关键词
            
        Returns:
            Mobject: 找到的子对象，未找到则返回 None
            
        示例:
            sentence = Text("向量加法满足交换律")
            vec_part = self.get_text_part(sentence, "向量")
            self.play(Indicate(vec_part))
        """
        results = self._find_text_submobjects(text_mobject, [keyword])
        return results[0] if results else None
    
    def get_text_parts(
        self,
        text_mobject: "Mobject",
        keywords: list,
    ) -> list:
        """
        获取 Text/Tex 对象中多个关键词对应的子对象
        
        Args:
            text_mobject: Text 或 Tex 对象
            keywords: 要查找的关键词列表
            
        Returns:
            list: 找到的子对象列表
            
        示例:
            sentence = Text("向量加法满足交换律和结合律")
            parts = self.get_text_parts(sentence, ["向量", "加法", "交换律"])
            for part in parts:
                self.play(Indicate(part))
        """
        return self._find_text_submobjects(text_mobject, keywords)
    
    def _get_discontinuous_groups(
        self, 
        submobject: "Mobject"
    ) -> list:
        """
        检测子对象是否包含不连续的部分，并返回分组
        
        用于处理关键词在文本中不连续出现的情况（如 "a+b" 中的两个变量）
        
        Args:
            submobject: 要检测的子对象
            
        Returns:
            list: 连续区域的列表，每个元素是包含连续子对象的 VGroup
        """
        parts = submobject.family_members_with_points()
        if len(parts) <= 1:
            return [submobject]
        
        # 按 x 坐标排序（假设是水平文本）
        sorted_parts = sorted(parts, key=lambda p: p.get_center()[0])
        
        groups = []
        current_group = [sorted_parts[0]]
        
        for i in range(1, len(sorted_parts)):
            prev_part = sorted_parts[i-1]
            curr_part = sorted_parts[i]
            
            # 检查间距（如果间距过大，视为不连续）
            gap = curr_part.get_left()[0] - prev_part.get_right()[0]
            avg_width = (prev_part.get_width() + curr_part.get_width()) / 2
            
            # 间距超过平均宽度的 1.5 倍视为不连续
            if gap > avg_width * 1.5:
                groups.append(VGroup(*current_group))
                current_group = [curr_part]
            else:
                current_group.append(curr_part)
        
        # 添加最后一组
        if current_group:
            groups.append(VGroup(*current_group))
        
        return groups
    
    def focus_guide(
        self,
        targets: list,
        keywords: list = None,
        box_buff: float = 0.1,
        stroke_width: float = 3,
        run_time: float = 0.6,
        hold_time: float = 0.5,
        auto_remove: bool = True,
    ) -> list:
        """
        方框引导高亮 - 引导读者视线依次关注重点内容
        
        1. ShowCreation 创建第一个方框
        2. Transform 变换到下一个重点位置
        3. 每次变换使用不同颜色
        4. 自动处理不连续的重点（生成多个方框）
        
        Args:
            targets: 目标列表，支持多种格式:
                - [mobject1, mobject2, ...]: 直接指定 mobject
                - [(text_mobject, "关键词"), ...]: 在文本中查找关键词
                - [{"text": text_mobject, "keyword": "关键词"}, ...]: 字典格式
            keywords: 全局关键词列表（与 targets 配合使用）
            box_buff: 方框与目标的边距
            stroke_width: 方框线宽
            run_time: 每次变换动画时长
            hold_time: 每个目标停留时间
            auto_remove: 结束后是否自动移除方框
            
        Returns:
            list: 当前活跃的方框列表
            
        示例:
            # 方式1: 直接指定目标
            formula = Tex("E = mc^2")
            self.focus_guide([formula[0][0], formula[0][2:]])  # 依次高亮 E 和 mc^2
            
            # 方式2: 使用关键词查找
            text = Text("重点是向量加法")
            self.focus_guide([(text, "重点"), (text, "向量加法")])
            
            # 方式3: 混合使用
            self.focus_guide([
                some_mobject,
                (text, "关键词"),
                {"text": formula, "keyword": "x^2"},
            ])
        """
        # 解析目标列表
        parsed_targets = []
        for item in targets:
            if isinstance(item, tuple) and len(item) == 2:
                # (text_mobject, "关键词") 格式
                text_mob, keyword = item
                submobs = self._find_text_submobjects(text_mob, [keyword])
                if submobs:
                    parsed_targets.extend(submobs)
            elif isinstance(item, dict):
                # {"text": text_mobject, "keyword": "关键词"} 格式
                text_mob = item.get("text")
                keyword = item.get("keyword")
                if text_mob and keyword:
                    submobs = self._find_text_submobjects(text_mob, [keyword])
                    if submobs:
                        parsed_targets.extend(submobs)
            else:
                # 直接是 mobject
                parsed_targets.append(item)
        
        if not parsed_targets:
            if self._debug_mode:
                print("⚠️ focus_guide: 没有找到有效目标")
            return []
        
        # 处理每个目标，检测不连续部分
        all_regions = []
        for target in parsed_targets:
            groups = self._get_discontinuous_groups(target)
            all_regions.extend(groups)
        
        if not all_regions:
            return []
        
        # 创建初始方框（可能有多个，用于不连续区域）
        active_boxes = []
        first_region = all_regions[0]
        first_groups = self._get_discontinuous_groups(first_region) if len(all_regions) == 1 else [first_region]
        
        # 为第一个目标创建方框
        first_color = self._get_next_focus_box_color()
        first_anims = []
        
        for group in first_groups:
            if self.GLOW_ENABLED:
                box = create_glow_surrounding_rect(
                    group,
                    color=first_color,
                    buff=box_buff,
                    stroke_width=stroke_width,
                    glow_color=first_color,
                    n_glow_layers=self.GLOW_N_LAYERS,
                    max_glow_width=stroke_width * self.GLOW_MAX_WIDTH_MULT,
                    base_opacity=self.GLOW_BASE_OPACITY,
                )
            else:
                box = SurroundingRectangle(
                    group,
                    color=first_color,
                    buff=box_buff,
                    stroke_width=stroke_width,
                )
            active_boxes.append(box)
            first_anims.append(ShowCreation(box))
        
        # 显示第一组方框
        self.play(*first_anims, run_time=run_time)
        self.wait(hold_time)
        
        # Transform 到后续目标
        for i, region in enumerate(all_regions[1:], start=1):
            new_groups = self._get_discontinuous_groups(region)
            new_color = self._get_next_focus_box_color()
            
            # 计算需要的方框数量
            needed_boxes = len(new_groups)
            current_boxes = len(active_boxes)
            
            transform_anims = []
            
            # 创建新方框
            new_boxes = []
            for j, group in enumerate(new_groups):
                if self.GLOW_ENABLED:
                    new_box = create_glow_surrounding_rect(
                        group,
                        color=new_color,
                        buff=box_buff,
                        stroke_width=stroke_width,
                        glow_color=new_color,
                        n_glow_layers=self.GLOW_N_LAYERS,
                        max_glow_width=stroke_width * self.GLOW_MAX_WIDTH_MULT,
                        base_opacity=self.GLOW_BASE_OPACITY,
                    )
                else:
                    new_box = SurroundingRectangle(
                        group,
                        color=new_color,
                        buff=box_buff,
                        stroke_width=stroke_width,
                    )
                new_boxes.append(new_box)
            
            # 处理方框数量变化
            if needed_boxes <= current_boxes:
                # 方框数量减少或不变：Transform 现有方框
                for j in range(needed_boxes):
                    transform_anims.append(
                        Transform(active_boxes[j], new_boxes[j])
                    )
                # 多余的方框淡出
                for j in range(needed_boxes, current_boxes):
                    transform_anims.append(FadeOut(active_boxes[j]))
                
                # 更新活跃方框列表
                active_boxes = active_boxes[:needed_boxes]
            else:
                # 方框数量增加：Transform 现有方框 + 创建新方框
                for j in range(current_boxes):
                    transform_anims.append(
                        Transform(active_boxes[j], new_boxes[j])
                    )
                # 新增方框
                for j in range(current_boxes, needed_boxes):
                    transform_anims.append(ShowCreation(new_boxes[j]))
                    active_boxes.append(new_boxes[j])
            
            # 播放变换动画
            self.play(*transform_anims, run_time=run_time)
            self.wait(hold_time)
        
        # 保存活跃方框引用
        self._focus_boxes = active_boxes
        
        # 自动移除
        if auto_remove:
            self.play(*[FadeOut(box) for box in active_boxes], run_time=run_time * 0.5)
            self._focus_boxes = []
        
        if self._debug_mode:
            print(f"📦 focus_guide: 完成 {len(all_regions)} 个目标的引导")
        
        return active_boxes
    
    def focus_guide_sequence(
        self,
        text_mobject: "Mobject",
        keywords: list,
        **kwargs,
    ) -> list:
        """
        在文本对象中按顺序引导高亮多个关键词
        
        便捷方法，自动将关键词转换为 (text_mobject, keyword) 格式
        
        Args:
            text_mobject: 包含关键词的文本对象
            keywords: 关键词列表 ["关键词1", "关键词2", ...]
            **kwargs: 传递给 focus_guide 的其他参数
            
        Returns:
            list: 活跃方框列表
            
        示例:
            sentence = Text("数学中，向量加法满足交换律")
            self.focus_guide_sequence(sentence, ["向量", "加法", "交换律"])
        """
        targets = [(text_mobject, kw) for kw in keywords]
        return self.focus_guide(targets, **kwargs)
    
    def remove_focus_boxes(self, run_time: float = 0.3) -> None:
        """
        移除当前所有活跃的引导方框
        
        Args:
            run_time: 淡出时长
        """
        if self._focus_boxes:
            self.play(*[FadeOut(box) for box in self._focus_boxes], run_time=run_time)
            self._focus_boxes = []
    
    def focus_guide_with_camera(
        self,
        targets: list,
        zoom_factor: float = 1.5,
        camera_buff: float = 0.5,
        box_buff: float = 0.1,
        stroke_width: float = 3,
        run_time: float = 0.8,
        hold_time: float = 1.0,
        auto_remove: bool = True,
        restore_after: bool = True,
        fix_box_in_frame: bool = False,
    ) -> list:
        """
        带相机移动和缩放的方框引导 - 更强的视觉引导效果
        
        功能：
        1. 方框高亮目标（使用轮询色盘）
        2. 相机平滑移动到目标位置
        3. 相机自动缩放以适应目标大小
        4. 方框固定在屏幕上（相机移动时不变形）
        
        Args:
            targets: 目标列表，支持多种格式:
                - [mobject1, mobject2, ...]: 直接指定 mobject
                - [(text_mobject, "关键词"), ...]: 在文本中查找关键词
                - [{"text": text_mobject, "keyword": "关键词"}, ...]: 字典格式
            zoom_factor: 缩放因子（1.5 = 视野缩小，目标放大1.5倍）
            camera_buff: 相机视野与目标的边距系数
            box_buff: 方框与目标的边距
            stroke_width: 方框线宽
            run_time: 每次移动动画时长
            hold_time: 每个目标停留时间
            auto_remove: 结束后是否自动移除方框
            restore_after: 结束后是否恢复相机原始状态
            fix_box_in_frame: 方框是否固定在屏幕上（避免相机移动时变形）
            
        Returns:
            list: 当前活跃的方框列表
            
        示例:
            # 带相机跟随的公式引导
            formula = Tex("E = mc^2")
            self.focus_guide_with_camera([formula[0][0], formula[0][2:]], zoom_factor=2.0)
            
            # 关键词引导（自动移动相机到每个关键词）
            text = Text("数学中，向量加法满足交换律")
            self.focus_guide_with_camera(
                [(text, "向量"), (text, "加法"), (text, "交换律")],
                hold_time=1.5,
            )
        """
        # 解析目标列表
        parsed_targets = []
        for item in targets:
            if isinstance(item, tuple) and len(item) == 2:
                text_mob, keyword = item
                submobs = self._find_text_submobjects(text_mob, [keyword])
                if submobs:
                    parsed_targets.extend(submobs)
            elif isinstance(item, dict):
                text_mob = item.get("text")
                keyword = item.get("keyword")
                if text_mob and keyword:
                    submobs = self._find_text_submobjects(text_mob, [keyword])
                    if submobs:
                        parsed_targets.extend(submobs)
            else:
                parsed_targets.append(item)
        
        if not parsed_targets:
            if self._debug_mode:
                print("⚠️ focus_guide_with_camera: 没有找到有效目标")
            return []
        
        # 保存相机初始状态
        camera_frame = self.camera.frame
        camera_frame.save_state()
        original_width = camera_frame.get_width()
        
        # 处理每个目标，检测不连续部分
        all_regions = []
        for target in parsed_targets:
            groups = self._get_discontinuous_groups(target)
            all_regions.extend(groups)
        
        if not all_regions:
            return []
        
        active_boxes = []
        
        # 处理第一个目标
        first_region = all_regions[0]
        first_groups = self._get_discontinuous_groups(first_region) if len(all_regions) == 1 else [first_region]
        first_color = self._get_next_focus_box_color()
        
        # 计算第一个目标的相机参数（限制缩放范围 0.8-1.2）
        first_center = first_region.get_center()
        # 将 zoom_factor 限制在 0.8-1.2 范围内
        clamped_zoom = max(0.8, min(1.2, zoom_factor))
        first_camera_width = original_width / clamped_zoom
        
        # 创建第一个方框
        first_anims = []
        for group in first_groups:
            if self.GLOW_ENABLED:
                box = create_glow_surrounding_rect(
                    group,
                    color=first_color,
                    buff=box_buff,
                    stroke_width=stroke_width,
                    glow_color=first_color,
                    n_glow_layers=self.GLOW_N_LAYERS,
                    max_glow_width=stroke_width * self.GLOW_MAX_WIDTH_MULT,
                    base_opacity=self.GLOW_BASE_OPACITY,
                )
            else:
                box = SurroundingRectangle(
                    group,
                    color=first_color,
                    buff=box_buff,
                    stroke_width=stroke_width,
                )
            if fix_box_in_frame:
                box.fix_in_frame()
            active_boxes.append(box)
            first_anims.append(ShowCreation(box))
        
        # 随机选择贝塞尔曲线缓动函数
        import random
        from manimlib import smooth, rush_into, rush_from, there_and_back
        bezier_funcs = [smooth, rush_into, rush_from, 
                        lambda t: smooth(t) * 0.9 + t * 0.1,  # 略带线性
                        lambda t: t**0.8,  # 快起慢落
                        lambda t: 1 - (1-t)**1.2]  # 慢起快落
        rate_func = random.choice(bezier_funcs)
        
        # 同时播放：方框创建 + 相机移动
        first_anims.append(
            camera_frame.animate.move_to(first_center).set_width(first_camera_width)
        )
        self.play(*first_anims, run_time=run_time, rate_func=rate_func)
        self.wait(hold_time)
        
        if self._debug_mode:
            print(f"📷🎯 focus_guide_with_camera: 目标 1/{len(all_regions)} @ {first_center[:2]}")
        
        # Transform 到后续目标
        for i, region in enumerate(all_regions[1:], start=1):
            new_groups = self._get_discontinuous_groups(region)
            new_color = self._get_next_focus_box_color()
            
            # 计算新目标的相机参数（使用相同的缩放限制）
            new_center = region.get_center()
            new_camera_width = original_width / clamped_zoom
            
            # 计算需要的方框数量
            needed_boxes = len(new_groups)
            current_boxes = len(active_boxes)
            
            transform_anims = []
            
            # 创建新方框
            new_boxes = []
            for j, group in enumerate(new_groups):
                if self.GLOW_ENABLED:
                    new_box = create_glow_surrounding_rect(
                        group,
                        color=new_color,
                        buff=box_buff,
                        stroke_width=stroke_width,
                        glow_color=new_color,
                        n_glow_layers=self.GLOW_N_LAYERS,
                        max_glow_width=stroke_width * self.GLOW_MAX_WIDTH_MULT,
                        base_opacity=self.GLOW_BASE_OPACITY,
                    )
                else:
                    new_box = SurroundingRectangle(
                        group,
                        color=new_color,
                        buff=box_buff,
                        stroke_width=stroke_width,
                    )
                if fix_box_in_frame:
                    new_box.fix_in_frame()
                new_boxes.append(new_box)
            
            # 处理方框数量变化
            if needed_boxes <= current_boxes:
                for j in range(needed_boxes):
                    transform_anims.append(Transform(active_boxes[j], new_boxes[j]))
                for j in range(needed_boxes, current_boxes):
                    transform_anims.append(FadeOut(active_boxes[j]))
                active_boxes = active_boxes[:needed_boxes]
            else:
                for j in range(current_boxes):
                    transform_anims.append(Transform(active_boxes[j], new_boxes[j]))
                for j in range(current_boxes, needed_boxes):
                    transform_anims.append(ShowCreation(new_boxes[j]))
                    active_boxes.append(new_boxes[j])
            
            # 添加相机移动动画
            transform_anims.append(
                camera_frame.animate.move_to(new_center).set_width(new_camera_width)
            )
            
            # 每次随机选择一个新的缓动函数
            rate_func = random.choice(bezier_funcs)
            
            # 播放变换动画
            self.play(*transform_anims, run_time=run_time, rate_func=rate_func)
            self.wait(hold_time)
            
            if self._debug_mode:
                print(f"📷🎯 focus_guide_with_camera: 目标 {i+1}/{len(all_regions)} @ {new_center[:2]}")
        
        # 保存活跃方框引用
        self._focus_boxes = active_boxes
        
        # 恢复相机
        if restore_after:
            restore_anims = [Restore(camera_frame)]
            if auto_remove:
                restore_anims.extend([FadeOut(box) for box in active_boxes])
                self._focus_boxes = []
            self.play(*restore_anims, run_time=run_time)
        elif auto_remove:
            self.play(*[FadeOut(box) for box in active_boxes], run_time=run_time * 0.5)
            self._focus_boxes = []
        
        if self._debug_mode:
            print(f"📷📦 focus_guide_with_camera: 完成 {len(all_regions)} 个目标的引导")
        
        return active_boxes
    
    def focus_guide_with_camera_sequence(
        self,
        text_mobject: "Mobject",
        keywords: list,
        **kwargs,
    ) -> list:
        """
        带相机移动的关键词序列引导（便捷方法）
        
        Args:
            text_mobject: 包含关键词的文本对象
            keywords: 关键词列表 ["关键词1", "关键词2", ...]
            **kwargs: 传递给 focus_guide_with_camera 的其他参数
            
        Returns:
            list: 活跃方框列表
            
        示例:
            sentence = Text("数学中，向量加法满足交换律")
            self.focus_guide_with_camera_sequence(
                sentence, 
                ["向量", "加法", "交换律"],
                zoom_factor=2.0,
                hold_time=1.5,
            )
        """
        targets = [(text_mobject, kw) for kw in keywords]
        return self.focus_guide_with_camera(targets, **kwargs)
    
    # ==================== 六块布局方法 ====================
    
    def get_subtitle_top_y(self) -> float:
        """
        动态获取字幕顶部 Y 坐标
        
        自适应换行高度：当字幕换行时，返回实际的顶部坐标
        
        Returns:
            float: 字幕顶部的 Y 坐标
        """
        if self._subtitle is not None:
            return self._subtitle.get_top()[1]
        # 无字幕时估算：屏幕底部 + 边距 + 预估字幕高度
        frame_bottom = -self.camera.frame.get_height() / 2
        return frame_bottom + self._subtitle_edge_buff + 0.5
    
    def create_title_divider(
        self,
        title_text: str,
        title_font: str = "STKaiti",
        title_font_size: int = 24,
        title_color = None,
        divider_width: float = None,
        divider_color = None,
        use_glow_divider: bool = True,
    ) -> tuple:
        """
        创建标题和分割线（自适应定位）
        
        布局方式：
        - title: .to_edge(UP, buff=LAYOUT_TITLE_BUFF)
        - divider: .next_to(title, DOWN, buff=LAYOUT_DIVIDER_BUFF)
        
        Args:
            title_text: 标题文本，如 "【高考真题·概率】"
            title_font: 标题字体
            title_font_size: 标题字号
            title_color: 标题颜色，默认 GREY
            divider_width: 分割线宽度，默认 frame_width * 0.95
            divider_color: 分割线颜色，默认 YELLOW
            use_glow_divider: 是否使用辉光分割线
            
        Returns:
            (title, divider) 元组，都已 fix_in_frame
        """
        from manimlib import Text, Line, GREY, YELLOW, LEFT, RIGHT, UP, DOWN
        
        # 默认颜色
        if title_color is None:
            title_color = GREY
        if divider_color is None:
            divider_color = YELLOW
        
        # 创建标题
        title = Text(
            title_text, 
            font=title_font,
            font_size=title_font_size, 
            color=title_color
        )
        title.to_edge(UP, buff=self.LAYOUT_TITLE_BUFF)
        title.fix_in_frame()
        
        # 计算自适应宽度
        if divider_width is None:
            divider_width = self.camera.frame.get_width() * self.LAYOUT_DIVIDER_WIDTH_RATIO
        
        # 创建分割线（尝试使用辉光版本）
        if use_glow_divider:
            try:
                from shaderscene.mobject.glow_line import GlowLine
                divider = GlowLine(
                    start=LEFT * divider_width / 2,
                    end=RIGHT * divider_width / 2,
                    color=divider_color,
                    glow_width=0.08,
                    glow_factor=2.0,
                )
            except ImportError:
                use_glow_divider = False
        
        if not use_glow_divider:
            divider = Line(
                LEFT * divider_width / 2, 
                RIGHT * divider_width / 2,
                color=divider_color, 
                stroke_width=2
            )
        
        # 相对定位
        divider.next_to(title, DOWN, buff=self.LAYOUT_DIVIDER_BUFF)
        divider.fix_in_frame()
        
        if self._debug_mode:
            print(f"📐 create_title_divider: title_y={title.get_center()[1]:.2f}, divider_y={divider.get_center()[1]:.2f}")
        
        return title, divider
    
    def layout_content_blocks(
        self,
        problem: "Mobject",
        viz: "Mobject",
        derivation: "Mobject",
        divider: "Mobject" = None,
        subtitle_top_y: float = None,
        align_left: bool = True,
    ) -> dict:
        """
        均匀布局三个内容块（Problem/Viz/Derivation）
        
        算法：
        1. top_y = divider.get_bottom()[1] - CONTENT_BUFF
        2. bottom_y = subtitle_top_y + CONTENT_BUFF
        3. 可用高度 H = top_y - bottom_y - 三块总高度
        4. 间距 gap = H / 2（两个间隙）
        5. 三块中心从上到下依次排列
        
        Args:
            problem: 题目区域 Mobject
            viz: 可视化区域 Mobject
            derivation: 推导区域 Mobject
            divider: 分割线对象，用于获取顶部边界
            subtitle_top_y: 字幕顶部 Y 坐标，默认自动获取
            align_left: 是否左对齐
            
        Returns:
            dict: {"top_y", "bottom_y", "gap", "centers": [problem_y, viz_y, derivation_y]}
        """
        from manimlib import LEFT
        
        # 获取上边界
        if divider is not None:
            top_y = divider.get_bottom()[1] - self.LAYOUT_CONTENT_BUFF
        else:
            # 无 divider 时从屏幕顶部计算
            frame_top = self.camera.frame.get_height() / 2
            top_y = frame_top - 1.5  # 预留标题空间
        
        # 获取下边界
        if subtitle_top_y is None:
            subtitle_top_y = self.get_subtitle_top_y()
        bottom_y = subtitle_top_y + self.LAYOUT_CONTENT_BUFF
        
        # 计算总高度和间距
        blocks = [problem, viz, derivation]
        total_h = sum(b.get_height() for b in blocks)
        available_h = top_y - bottom_y - total_h
        raw_gap = available_h / 2  # 两个间隙
        
        centers = []
        
        if raw_gap >= 0:
            # ===== 正常布局：等间距分布 =====
            gap = max(self.LAYOUT_CONTENT_BUFF, raw_gap)
            current_y = top_y - problem.get_height() / 2
            
            for i, block in enumerate(blocks):
                # 设置垂直位置（中心）
                block.move_to([0, current_y, 0])
                
                # 左对齐
                if align_left:
                    block.to_edge(LEFT, buff=self.LAYOUT_EDGE_BUFF)
                
                centers.append(current_y)
                
                # 计算下一个块的位置
                if i < len(blocks) - 1:
                    next_block = blocks[i + 1]
                    current_y -= block.get_height() / 2 + gap + next_block.get_height() / 2
            
            if self._debug_mode:
                print(f"📐 layout_content_blocks [正常模式]: top_y={top_y:.2f}, bottom_y={bottom_y:.2f}, gap={gap:.2f}")
                print(f"   centers: problem={centers[0]:.2f}, viz={centers[1]:.2f}, derivation={centers[2]:.2f}")
        else:
            # ===== 备用布局：间距不足时允许 viz 超出 =====
            # problem: next_to divider (紧贴分割线下方)
            # derivation: next_to subtitle (紧贴字幕上方)
            # viz: 居中于 problem 和 derivation 之间
            gap = 0  # 无间距
            
            from manimlib import DOWN, UP
            
            # Problem 紧贴 divider 下方
            if divider is not None:
                problem.next_to(divider, DOWN, buff=self.LAYOUT_CONTENT_BUFF)
            else:
                problem.move_to([0, top_y - problem.get_height() / 2, 0])
            if align_left:
                problem.to_edge(LEFT, buff=self.LAYOUT_EDGE_BUFF)
            problem_center_y = problem.get_center()[1]
            centers.append(problem_center_y)
            
            # Derivation 紧贴 subtitle 上方
            derivation.move_to([0, bottom_y + derivation.get_height() / 2, 0])
            if align_left:
                derivation.to_edge(LEFT, buff=self.LAYOUT_EDGE_BUFF)
            derivation_center_y = derivation.get_center()[1]
            
            # Viz 居中于 problem 底部和 derivation 顶部之间
            problem_bottom = problem.get_bottom()[1]
            derivation_top = derivation.get_top()[1]
            viz_center_y = (problem_bottom + derivation_top) / 2
            viz.move_to([0, viz_center_y, 0])
            # viz 通常不左对齐，保持居中
            centers.append(viz_center_y)
            centers.append(derivation_center_y)
            
            if self._debug_mode:
                print(f"📐 layout_content_blocks [备用模式]: 空间不足，viz 可能超出")
                print(f"   problem_y={problem_center_y:.2f}, viz_y={viz_center_y:.2f}, derivation_y={derivation_center_y:.2f}")
        
        return {
            "top_y": top_y,
            "bottom_y": bottom_y,
            "gap": gap,
            "centers": centers,
            "mode": "normal" if raw_gap >= 0 else "fallback",
        }
    
    def get_content_center_y(
        self,
        block_index: int,
        divider: "Mobject" = None,
        subtitle_top_y: float = None,
        block_heights: list = None,
    ) -> float:
        """
        获取第 n 个内容块的中心 Y 坐标
        
        Args:
            block_index: 块索引 (0=Problem, 1=Viz, 2=Derivation)
            divider: 分割线对象
            subtitle_top_y: 字幕顶部 Y 坐标
            block_heights: 三个块的高度列表，默认 [1.0, 2.0, 1.0]
            
        Returns:
            float: 该块中心的 Y 坐标
        """
        if block_heights is None:
            block_heights = [1.0, 2.0, 1.0]  # 默认高度估算
        
        # 获取边界
        if divider is not None:
            top_y = divider.get_bottom()[1] - self.LAYOUT_CONTENT_BUFF
        else:
            frame_top = self.camera.frame.get_height() / 2
            top_y = frame_top - 1.5
        
        if subtitle_top_y is None:
            subtitle_top_y = self.get_subtitle_top_y()
        bottom_y = subtitle_top_y + self.LAYOUT_CONTENT_BUFF
        
        # 计算间距
        total_h = sum(block_heights)
        available_h = top_y - bottom_y - total_h
        gap = max(self.LAYOUT_CONTENT_BUFF, available_h / 2)
        
        # 计算目标块的中心 Y
        current_y = top_y - block_heights[0] / 2
        for i in range(block_index):
            current_y -= block_heights[i] / 2 + gap + block_heights[i + 1] / 2
        
        return current_y
    
    # ==================== 相机聚焦方法 ====================

    
    def camera_focus(self, target: "Mobject", zoom_factor: float = 2.0,
                     focus_time: float = 1.0, hold_time: float = 2.0,
                     restore_time: float = 1.0) -> None:
        """
        动态相机聚焦到目标内容，保持一段时间后恢复
        
        使用 save_state + Restore 实现平滑的聚焦和恢复动画
        
        Args:
            target: 聚焦目标
            zoom_factor: 放大倍数（2.0 = 视野缩小到原来的一半，看起来放大2倍）
            focus_time: 聚焦动画时长
            hold_time: 聚焦后保持时长（默认 2 秒）
            restore_time: 恢复动画时长
        """
        camera_frame = self.camera.frame
        
        # 保存当前相机状态
        camera_frame.save_state()
        
        if self._debug_mode:
            print(f"📷 camera_focus: 聚焦到 {target.__class__.__name__}, zoom={zoom_factor}x")
        
        # 计算目标宽度（确保目标完全可见）
        target_width = max(target.get_width() * zoom_factor, target.get_height() * zoom_factor * 16/9)
        
        # 聚焦动画：移动到目标并缩小视野
        self.play(
            camera_frame.animate.move_to(target.get_center()).set_width(
                camera_frame.get_width() / zoom_factor
            ),
            run_time=focus_time
        )
        
        # 保持聚焦
        self.wait(hold_time)
        self._current_time += hold_time
        
        # 恢复原始视角
        self.play(Restore(camera_frame), run_time=restore_time)
        
        if self._debug_mode:
            print(f"📷 camera_focus: 已恢复原始视角")
    
    # ==================== 固定方向元素方法 ====================
    
    def add_fixed_subtitle(self, text: str, color_map: dict = None, 
                           position=DOWN, edge_buff: float = None) -> VGroup:
        """
        添加固定在屏幕上的字幕（使用 fix_in_frame）
        
        适用于：标题、题目、推导过程、字幕、字幕背景
        这些元素不随相机移动，始终固定在屏幕位置
        
        Args:
            text: 字幕文本
            color_map: 着色映射
            position: 位置 (DOWN/UP/LEFT/RIGHT)
            edge_buff: 边距，None 使用默认值
            
        Returns:
            VGroup: 固定的字幕组 [背景, 文字]
        """
        # 使用现有的 make_subtitle 创建字幕
        subtitle_group = self.make_subtitle(text, color_map)
        
        # 调整位置
        buff = edge_buff if edge_buff is not None else self._subtitle_edge_buff
        subtitle_group.to_edge(position, buff=buff)
        
        # 固定在屏幕上
        subtitle_group.fix_in_frame()
        
        if self._debug_mode:
            print(f"📌 add_fixed_subtitle: '{text[:20]}...' 已固定")
        
        return subtitle_group
    
    def add_fixed_title(self, text: str, font_size: int = 36, 
                        color=WHITE, position=UP, edge_buff: float = 0.5) -> Text:
        """
        添加固定在屏幕上的标题（使用 fix_in_frame）
        
        Args:
            text: 标题文本
            font_size: 字号
            color: 颜色
            position: 位置
            edge_buff: 边距
            
        Returns:
            Text: 固定的标题
        """
        title = Text(
            text,
            font=self.SUBTITLE_FONT,
            font_size=font_size,
            color=color
        )
        title.to_edge(position, buff=edge_buff)
        title.fix_in_frame()
        
        if self._debug_mode:
            print(f"📌 add_fixed_title: '{text}' 已固定")
        
        return title
    
    def add_grid_background(
        self,
        x_range: tuple = None,
        y_range: tuple = None,
        step: float = 1.0,
        color=WHITE,
        stroke_opacity: float = 0.1,
        stroke_width: float = 1.0,
        fix_in_frame: bool = True,
    ) -> VGroup:
        """
        添加低透明度方格背景
        
        Args:
            x_range: x 轴范围 (min, max)，默认使用屏幕宽度
            y_range: y 轴范围 (min, max)，默认使用屏幕高度
            step: 方格间距
            color: 线条颜色
            stroke_opacity: 线条透明度（默认 0.1）
            stroke_width: 线条宽度
            fix_in_frame: 是否固定在屏幕上
            
        Returns:
            VGroup: 包含所有网格线的组
        """
        # 获取屏幕尺寸
        try:
            frame = self.camera.frame
            frame_width = frame.get_width()
            frame_height = frame.get_height()
        except AttributeError:
            frame_width = 14.2  # 默认横版宽度
            frame_height = 8.0  # 默认横版高度
        
        # 默认范围
        if x_range is None:
            x_min, x_max = -frame_width / 2, frame_width / 2
        else:
            x_min, x_max = x_range
            
        if y_range is None:
            y_min, y_max = -frame_height / 2, frame_height / 2
        else:
            y_min, y_max = y_range
        
        grid_lines = VGroup()
        
        # 垂直线
        x = x_min
        while x <= x_max:
            line = Line(
                start=np.array([x, y_min, 0]),
                end=np.array([x, y_max, 0]),
                stroke_color=color,
                stroke_opacity=stroke_opacity,
                stroke_width=stroke_width,
            )
            grid_lines.add(line)
            x += step
        
        # 水平线
        y = y_min
        while y <= y_max:
            line = Line(
                start=np.array([x_min, y, 0]),
                end=np.array([x_max, y, 0]),
                stroke_color=color,
                stroke_opacity=stroke_opacity,
                stroke_width=stroke_width,
            )
            grid_lines.add(line)
            y += step
        
        # 固定在屏幕上
        if fix_in_frame:
            grid_lines.fix_in_frame()
        
        if self._debug_mode:
            print(f"🔲 add_grid_background: {len(grid_lines)} 条线，透明度={stroke_opacity}")
        
        return grid_lines
    
    def add_traffic_lights(
        self,
        radius: float = 0.12,
        spacing: float = 0.35,
        buff: float = 0.3,
        fix_in_frame: bool = True,
    ) -> VGroup:
        """
        添加右上角的红黄绿三色圆点（类似 macOS 窗口控制按钮）
        
        Args:
            radius: 圆点半径（默认 0.12，约 0.7 个字符大小）
            spacing: 圆点间距（默认 0.35，约 1 个字符大小）
            buff: 距离屏幕边缘的距离
            fix_in_frame: 是否固定在屏幕上
            
        Returns:
            VGroup: 包含三个圆点的组
        """
        # 创建三个填充圆
        red_circle = Circle(
            radius=radius,
            fill_color="#FF5F56",
            fill_opacity=1.0,
            stroke_width=0,
        )
        yellow_circle = Circle(
            radius=radius,
            fill_color="#FFBD2E",
            fill_opacity=1.0,
            stroke_width=0,
        )
        green_circle = Circle(
            radius=radius,
            fill_color="#27C93F",
            fill_opacity=1.0,
            stroke_width=0,
        )
        
        # 水平排列（从左到右：红、黄、绿）
        lights = VGroup(red_circle, yellow_circle, green_circle)
        lights.arrange(RIGHT, buff=spacing - 2 * radius)
        
        # 放置到右上角
        lights.to_corner(UL, buff=buff)
        
        # 固定在屏幕上
        if fix_in_frame:
            lights.fix_in_frame()
        
        if self._debug_mode:
            print(f"🚦 add_traffic_lights: 已添加右上角红黄绿圆点")
        
        return lights
    
    def add_fixed_formula(self, tex_string: str, font_size: int = 32,
                          position=None, coords: tuple = None) -> "Tex":
        """
        添加固定在屏幕上的公式（使用 fix_in_frame）
        
        Args:
            tex_string: LaTeX 公式字符串
            font_size: 字号
            position: 边缘位置 (UP/DOWN/LEFT/RIGHT)，与 coords 二选一
            coords: 具体坐标 (x, y)，与 position 二选一
            
        Returns:
            Tex: 固定的公式
        """
        from manimlib import Tex
        
        formula = Tex(tex_string, font_size=font_size)
        
        if coords is not None:
            formula.move_to(np.array([coords[0], coords[1], 0]))
        elif position is not None:
            formula.to_edge(position, buff=0.5)
        
        formula.fix_in_frame()
        
        if self._debug_mode:
            print(f"📌 add_fixed_formula: 已固定")
        
        return formula
    
    # ========================================================================
    # 辉光弧形箭头
    # ========================================================================
    
    def create_glow_arc_arrow(
        self,
        start_angle=0,
        angle=TAU/2,
        radius=2.5,
        colors=None,
        stroke_width=None,
        glow_color=None,
        n_glow_layers=None,
        arc_scale_factor=None,
        tip_scale_factor=None,
        glow_width_mult=None,
        base_opacity=None,
        add_tip=True,
        tip_at_start=False,
        side="left",
    ):
        """
        创建辉光弧形箭头 - 使用类配置的默认值
        
        Args:
            start_angle: 起始角度
            angle: 弧线角度
            radius: 半径
            colors: 颜色列表，None则使用 side 对应的默认色
            stroke_width: 线条宽度列表，None则使用默认变宽配置
            glow_color: 辉光颜色
            n_glow_layers: 辉光层数
            arc_scale_factor: 弧线辉光缩放
            tip_scale_factor: 箭头尖端辉光缩放
            glow_width_mult: 辉光宽度倍数
            base_opacity: 辉光透明度
            add_tip: 是否添加箭头尖端
            tip_at_start: 箭头尖端是否在起始位置
            side: "left" 或 "right"，使用对应颜色配置
            
        Returns:
            VGroup: 辉光弧形箭头组
        """
        # 使用类配置作为默认值
        if colors is None:
            colors = self.GLOW_ARROW_LEFT_COLORS if side == "left" else self.GLOW_ARROW_RIGHT_COLORS
        if stroke_width is None:
            stroke_width = self.GLOW_ARROW_TAPERED_WIDTH
        if n_glow_layers is None:
            n_glow_layers = self.GLOW_ARROW_N_LAYERS
        if arc_scale_factor is None:
            arc_scale_factor = self.GLOW_ARROW_ARC_SCALE
        if tip_scale_factor is None:
            tip_scale_factor = self.GLOW_ARROW_TIP_SCALE
        if glow_width_mult is None:
            glow_width_mult = self.GLOW_ARROW_WIDTH_MULT
        if base_opacity is None:
            base_opacity = self.GLOW_ARROW_BASE_OPACITY
        if glow_color is None:
            glow_color = colors[-1]
        
        return create_glowing_arc_arrow(
            start_angle=start_angle,
            angle=angle,
            radius=radius,
            colors=colors,
            stroke_width=stroke_width,
            glow_color=glow_color,
            n_glow_layers=n_glow_layers,
            arc_scale_factor=arc_scale_factor,
            tip_scale_factor=tip_scale_factor,
            glow_width_mult=glow_width_mult,
            base_opacity=base_opacity,
            add_tip=add_tip,
            tip_at_start=tip_at_start,
        )
    
    def create_glow_box(
        self,
        mobject,
        color=YELLOW,
        buff=0.15,
        stroke_width=3,
        glow_color=None,
        n_glow_layers=None,
        max_glow_width=None,
        base_opacity=None,
    ):
        """
        创建辉光环绕框 - 便捷方法，使用类配置的默认值
        
        Args:
            mobject: 要环绕的对象
            color: 边框颜色
            buff: 边距
            stroke_width: 线条宽度
            glow_color: 辉光颜色
            n_glow_layers: 辉光层数
            max_glow_width: 最外层辉光宽度
            base_opacity: 辉光透明度
            
        Returns:
            VGroup: 辉光环绕框组
        """
        if n_glow_layers is None:
            n_glow_layers = self.GLOW_N_LAYERS
        if max_glow_width is None:
            max_glow_width = stroke_width * self.GLOW_MAX_WIDTH_MULT
        if base_opacity is None:
            base_opacity = self.GLOW_BASE_OPACITY
        if glow_color is None:
            glow_color = color
        
        return create_glow_surrounding_rect(
            mobject,
            color=color,
            buff=buff,
            stroke_width=stroke_width,
            glow_color=glow_color,
            n_glow_layers=n_glow_layers,
            max_glow_width=max_glow_width,
            base_opacity=base_opacity,
        )
    
    # ========================================================================
    # 辉光下划线
    # ========================================================================
    
    def create_glow_underline(
        self,
        mobject: "Mobject",
        color=None,
        offset_ratio: float = 0.55,
        width_ratio: float = 1.0,
        glow_width: float = 0.06,
        glow_factor: float = 2.0,
        fix_in_frame: bool = False,
    ) -> "GlowLine":
        """
        为任意对象创建自适应辉光下划线
        
        自动计算对象高度，将下划线定位在对象下方适当位置。
        
        Args:
            mobject: 要添加下划线的对象（Text, Tex, VGroup 等）
            color: 下划线颜色（默认使用轮询色盘）
            offset_ratio: 下划线距离对象底部的偏移量（以对象高度的比例计算，默认 0.55）
            width_ratio: 下划线宽度相对于对象宽度的比例（默认 1.0）
            glow_width: 辉光宽度
            glow_factor: 辉光衰减因子
            fix_in_frame: 是否固定在屏幕上
            
        Returns:
            GlowLine: 辉光下划线对象
            
        示例:
            title = Text("标题", font="STKaiti", font_size=32)
            underline = self.create_glow_underline(title, color=YELLOW)
            # 下划线自动定位在 title 下方
        """
        try:
            shaderscene_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "shaderscene")
            if shaderscene_path not in sys.path:
                sys.path.insert(0, shaderscene_path)
            from mobject.glow_line import GlowLine
        except ImportError:
            if self._debug_mode:
                print("⚠️ GlowLine 导入失败，返回普通 Line")
            # 回退到普通 Line
            from manimlib import Line
            obj_height = mobject.get_height()
            offset = obj_height * offset_ratio
            start = mobject.get_left() + DOWN * offset
            end = mobject.get_right() + DOWN * offset
            line = Line(start, end, color=color or YELLOW, stroke_width=2)
            if fix_in_frame:
                line.fix_in_frame()
            return line
        
        # 默认颜色：使用轮询色盘
        if color is None:
            color = self._get_next_glow_color()
        
        # 计算对象尺寸
        obj_height = mobject.get_height()
        obj_width = mobject.get_width()
        
        # 计算下划线位置
        offset = obj_height * offset_ratio
        center_x = mobject.get_center()[0]
        bottom_y = mobject.get_bottom()[1]
        line_y = bottom_y - offset * 0.5  # 适当调整到底部下方
        
        # 计算下划线宽度
        half_width = (obj_width * width_ratio) / 2
        start = np.array([center_x - half_width, line_y, 0])
        end = np.array([center_x + half_width, line_y, 0])
        
        # 创建辉光下划线
        underline = GlowLine(
            start=start,
            end=end,
            color=color,
            glow_width=glow_width,
            glow_factor=glow_factor,
        )
        
        # 固定在屏幕上
        if fix_in_frame:
            try:
                underline.fix_in_frame()
            except AttributeError:
                pass
        
        if self._debug_mode:
            print(f"✨ create_glow_underline: offset_ratio={offset_ratio}, width_ratio={width_ratio}")
        
        return underline
    
    # ========================================================================
    # 辉光文字
    # ========================================================================
    
    def create_glow_text(
        self,
        text: str,
        font: str = None,
        font_size: int = 36,
        color=None,
        glow_color=None,
        glow_size: float = 0.4,
        glow_factor: float = 2.5,
        alpha: float = 0.35,
        fix_in_frame: bool = False,
    ) -> "Group":
        """
        创建带辉光效果的文字
        
        使用 GPU shader 渲染柔和的辉光效果，无棱刺
        自动使用电影级彩色轮询色盘（禁止白色）
        
        Args:
            text: 文字内容
            font: 字体 (默认使用 SUBTITLE_FONT)
            font_size: 字号
            color: 文字颜色 (默认使用轮询色盘)
            glow_color: 辉光颜色 (默认使用轮询色盘)
            glow_size: 辉光半径，越大范围越广
            glow_factor: 辉光衰减因子
            alpha: 辉光透明度 (低透明度避免模糊)
            fix_in_frame: 是否固定在屏幕上（相机移动时不受影响）
            
        Returns:
            Group: 包含辉光层和文字的组合
        """
        # 延迟导入 GlowWrapperEffect
        try:
            shaderscene_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "shaderscene")
            if shaderscene_path not in sys.path:
                sys.path.insert(0, shaderscene_path)
            from mobject.glow_wrapper import GlowWrapperEffect
        except ImportError:
            # 如果导入失败，返回普通文字
            if self._debug_mode:
                print("⚠️ GlowWrapperEffect 导入失败，返回普通文字")
            fallback = Text(text, font=font or self.SUBTITLE_FONT, font_size=font_size, color=color or WHITE)
            if fix_in_frame:
                fallback.fix_in_frame()
            return fallback
        
        from manimlib import Group
        
        # 如果未指定颜色，使用轮询色盘
        if color is None:
            color = self._get_next_glow_color()
        
        # 创建文字
        text_font = font or self.SUBTITLE_FONT
        text_obj = Text(text, font=text_font, font_size=font_size, color=color)
        
        # 辉光颜色：如果未指定，使用轮询色盘（非白色）
        if glow_color is None:
            actual_glow_color = color  # 与文字颜色相同
        else:
            actual_glow_color = glow_color
        
        # 创建辉光
        glow = GlowWrapperEffect(
            text_obj,
            color=actual_glow_color,
            alpha=alpha,
            size=glow_size,
            glow_factor=glow_factor,
            white_core_ratio=0.08,
            white_glow_ratio=0.15,
            render_mode="point",
            curve_sample_factor=30,
            min_curve_samples=150,
            core_width_ratio=0.15,
        )
        
        # 关闭深度测试避免棱刺
        glow.deactivate_depth_test()
        
        # 组合：先辉光后文字
        result = Group(glow, text_obj)
        
        # 固定在屏幕上：递归对所有子对象调用 fix_in_frame
        if fix_in_frame:
            self._fix_in_frame_recursive(result)
        
        if self._debug_mode:
            print(f"✨ create_glow_text: '{text}' (glow_color={actual_glow_color})")
        
        return result
    
    def _fix_in_frame_recursive(self, mob: "Mobject") -> None:
        """递归对 mobject 及其所有子对象调用 fix_in_frame"""
        try:
            mob.fix_in_frame()
        except AttributeError:
            pass  # 某些对象（如 ShaderMobject）不支持 fix_in_frame
        
        # 递归处理所有子对象
        if hasattr(mob, 'submobjects'):
            for submob in mob.submobjects:
                self._fix_in_frame_recursive(submob)
    
    def _get_next_glow_color(self) -> str:
        """获取下一个辉光颜色（轮询色盘）"""
        color = self._glow_color_palette[self._glow_color_index]
        self._glow_color_index = (self._glow_color_index + 1) % len(self._glow_color_palette)
        return color
    
    def create_glow_tex(
        self,
        tex_string: str,
        font_size: int = 36,
        color=None,
        glow_color=None,
        glow_size: float = 0.4,
        glow_factor: float = 2.5,
        alpha: float = 0.35,
    ) -> "Group":
        """
        创建带辉光效果的 LaTeX 公式
        
        自动使用电影级彩色轮询色盘（禁止白色）
        
        Args:
            tex_string: LaTeX 公式
            font_size: 字号
            color: 公式颜色 (默认使用轮询色盘)
            glow_color: 辉光颜色 (默认使用轮询色盘)
            
        Returns:
            Group: 包含辉光层和公式的组合
        """
        try:
            shaderscene_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "shaderscene")
            if shaderscene_path not in sys.path:
                sys.path.insert(0, shaderscene_path)
            from mobject.glow_wrapper import GlowWrapperEffect
        except ImportError:
            from manimlib import Tex
            return Tex(tex_string, font_size=font_size, color=color or WHITE)
        
        from manimlib import Tex, Group
        
        # 如果未指定颜色，使用轮询色盘
        if color is None:
            color = self._get_next_glow_color()
        
        tex_obj = Tex(tex_string, font_size=font_size, color=color)
        
        # 辉光颜色：如果未指定，使用与公式相同的颜色
        if glow_color is None:
            actual_glow_color = color
        else:
            actual_glow_color = glow_color
        
        glow = GlowWrapperEffect(
            tex_obj,
            color=actual_glow_color,
            alpha=alpha,
            size=glow_size,
            glow_factor=glow_factor,
            white_core_ratio=0.08,
            white_glow_ratio=0.15,
            render_mode="point",
            curve_sample_factor=30,
            min_curve_samples=150,
        )
        glow.deactivate_depth_test()
        
        result = Group(glow, tex_obj)
        
        if self._debug_mode:
            print(f"✨ create_glow_tex: '{tex_string[:20]}...' (glow_color={actual_glow_color})")
        
        return result
    
    # ========================================================================
    # 脉冲辉光曲线 - 强调线条和方程曲线
    # ========================================================================
    
    def create_pulse_glow_curve(
        self,
        function,
        t_range: tuple = (0, 1),
        color=YELLOW,
        glow_width: float = 0.15,
        pulse_frequency: float = 1.0,
        pulse_amplitude: float = 0.5,
        n_samples: int = 500,
        **kwargs,
    ):
        """
        创建脉冲辉光参数曲线
        
        用于强调线条、轨迹等，带有呼吸灯式的脉动效果
        
        Args:
            function: 参数函数 f(t) -> [x, y, z]
            t_range: 参数范围 (t_start, t_end)
            color: 辉光颜色
            glow_width: 辉光宽度
            pulse_frequency: 脉冲频率 (Hz)
            pulse_amplitude: 脉冲振幅 (0-1)
            n_samples: 采样点数
            
        Returns:
            GlowCurve: 带脉冲效果的辉光曲线
            
        示例:
            # 正弦曲线（呼吸灯效果）
            curve = self.create_pulse_glow_curve(
                lambda t: np.array([t, np.sin(t), 0]),
                t_range=(-np.pi, np.pi),
                color=BLUE,
                pulse_frequency=1.5,
            )
        """
        try:
            shaderscene_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "shaderscene")
            if shaderscene_path not in sys.path:
                sys.path.insert(0, shaderscene_path)
            from mobject.glow_curve import GlowCurve
        except ImportError:
            if self._debug_mode:
                print("⚠️ GlowCurve 导入失败")
            return None
        
        curve = GlowCurve(
            function=function,
            t_range=t_range,
            color=color,
            glow_width=glow_width,
            n_samples=n_samples,
            **kwargs,
        )
        curve.enable_pulse(frequency=pulse_frequency, amplitude=pulse_amplitude)
        
        if self._debug_mode:
            print(f"🌊 create_pulse_glow_curve: {pulse_frequency}Hz, amplitude={pulse_amplitude}")
        
        return curve
    
    def create_pulse_glow_function(
        self,
        f,
        x_range: tuple = (-5, 5),
        color=YELLOW,
        glow_width: float = 0.15,
        pulse_frequency: float = 1.0,
        pulse_amplitude: float = 0.5,
        n_samples: int = 500,
        **kwargs,
    ):
        """
        创建脉冲辉光函数图像 y = f(x)
        
        用于强调数学函数曲线，带有呼吸灯效果
        
        Args:
            f: 函数 f(x) -> y
            x_range: x轴范围 (x_min, x_max)
            color: 辉光颜色
            glow_width: 辉光宽度
            pulse_frequency: 脉冲频率
            pulse_amplitude: 脉冲振幅
            
        Returns:
            GlowFunctionGraph: 带脉冲效果的函数曲线
            
        示例:
            # 正弦函数（脉动高亮）
            curve = self.create_pulse_glow_function(
                lambda x: np.sin(x),
                x_range=(-np.pi, np.pi),
                color=BLUE,
            )
        """
        try:
            shaderscene_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "shaderscene")
            if shaderscene_path not in sys.path:
                sys.path.insert(0, shaderscene_path)
            from mobject.glow_curve import GlowFunctionGraph
        except ImportError:
            if self._debug_mode:
                print("⚠️ GlowFunctionGraph 导入失败")
            return None
        
        curve = GlowFunctionGraph(
            function=f,
            x_range=x_range,
            color=color,
            glow_width=glow_width,
            n_samples=n_samples,
            **kwargs,
        )
        curve.enable_pulse(frequency=pulse_frequency, amplitude=pulse_amplitude)
        
        if self._debug_mode:
            print(f"📈 create_pulse_glow_function: {pulse_frequency}Hz")
        
        return curve
    
    def create_pulse_glow_circle(
        self,
        radius: float = 1.0,
        color=YELLOW,
        glow_width: float = 0.12,
        pulse_frequency: float = 1.0,
        pulse_amplitude: float = 0.5,
        n_samples: int = 200,
        **kwargs,
    ):
        """
        创建脉冲辉光圆形
        
        Args:
            radius: 圆的半径
            color: 辉光颜色
            glow_width: 辉光宽度
            pulse_frequency: 脉冲频率
            pulse_amplitude: 脉冲振幅
            
        Returns:
            GlowCurve: 圆形辉光曲线
        """
        try:
            shaderscene_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "shaderscene")
            if shaderscene_path not in sys.path:
                sys.path.insert(0, shaderscene_path)
            from mobject.glow_curve import GlowCircle
        except ImportError:
            if self._debug_mode:
                print("⚠️ GlowCircle 导入失败")
            return None
        
        circle = GlowCircle(
            radius=radius,
            color=color,
            glow_width=glow_width,
            n_samples=n_samples,
            **kwargs,
        )
        circle.enable_pulse(frequency=pulse_frequency, amplitude=pulse_amplitude)
        
        if self._debug_mode:
            print(f"⭕ create_pulse_glow_circle: r={radius}, {pulse_frequency}Hz")
        
        return circle
    
    def add_glow_to_curve(
        self,
        vmobject,
        color=None,
        glow_width: float = 0.1,
        pulse: bool = False,
        pulse_frequency: float = 1.0,
        pulse_amplitude: float = 0.4,
    ):
        """
        为现有 VMobject (Line, Circle, FunctionGraph等) 添加辉光效果
        
        通过采样 VMobject 的轮廓创建辉光覆盖层
        
        Args:
            vmobject: 要添加辉光的曲线对象
            color: 辉光颜色 (默认使用曲线自身颜色)
            glow_width: 辉光宽度
            pulse: 是否启用脉冲
            pulse_frequency: 脉冲频率
            pulse_amplitude: 脉冲振幅
            
        Returns:
            Group: 包含辉光和原曲线的组合
        """
        try:
            shaderscene_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "shaderscene")
            if shaderscene_path not in sys.path:
                sys.path.insert(0, shaderscene_path)
            from mobject.glow_wrapper import GlowWrapperEffect
        except ImportError:
            if self._debug_mode:
                print("⚠️ GlowWrapperEffect 导入失败")
            return vmobject
        
        from manimlib import Group
        
        # 使用曲线自身颜色
        glow_color = color if color is not None else vmobject.get_color()
        
        glow = GlowWrapperEffect(
            vmobject,
            color=glow_color,
            size=glow_width,
            glow_factor=2.5,
            alpha=0.5,
            render_mode="line",
            curve_sample_factor=50,
        )
        glow.deactivate_depth_test()
        
        result = Group(glow, vmobject)
        
        if self._debug_mode:
            print(f"✨ add_glow_to_curve: pulse={pulse}")
        
        return result

def make_fixed_orientation_updater(original_pos, camera_frame):
    """
    创建 updater 函数，使对象始终面向相机（用于 3D 场景中的标签）
    
    适用于：可视化图中的标记，在 3D 图形中需要标签始终朝向观众且位置正确
    
    Args:
        original_pos: 原始位置 (numpy array 或 list)
        camera_frame: 相机框架对象 (self.camera.frame)
        
    Returns:
        updater 函数，可通过 mobject.add_updater() 添加
        
    示例:
        label = Text("标签").move_to(sphere.get_center())
        label.add_updater(make_fixed_orientation_updater(
            sphere.get_center(), self.camera.frame
        ))
    """
    original_pos = np.array(original_pos)
    
    def updater(obj, dt):
        # 将原始 3D 位置转换为屏幕固定坐标
        new_pos = camera_frame.to_fixed_frame_point(original_pos)
        # 固定在屏幕平面
        obj.fix_in_frame()
        new_pos[2] = 0  # 保持在屏幕平面上
        obj.move_to(new_pos)
        return obj
    
    return updater


class AutoSceneEnhancementMixin:
    """
    增强功能混入类，用于 3D 场景中的固定方向标注
    
    可以单独混入到任何 Scene 子类中使用
    """
    
    def add_fixed_annotation(self, target: "Mobject", label_text: str,
                             direction=UP, buff: float = 0.2,
                             font_size: int = 20, color=WHITE) -> Text:
        """
        为 3D 可视化中的对象添加始终面向相机的标注
        
        标注会跟随 target 的位置，但始终面向观众
        
        Args:
            target: 目标对象（通常是 3D 图形中的元素）
            label_text: 标注文本
            direction: 标注相对于目标的方向
            buff: 标注与目标的距离
            font_size: 字号
            color: 颜色
            
        Returns:
            Text: 带有 updater 的标注文本
        """
        # 计算标注位置
        offset = direction * buff
        original_pos = target.get_center() + offset
        
        # 创建标注
        label = Text(
            label_text,
            font="STKaiti",
            font_size=font_size,
            color=color
        ).move_to(original_pos)
        
        # 添加固定方向 updater
        label.add_updater(
            make_fixed_orientation_updater(original_pos, self.camera.frame)
        )
        
        return label
    
    def add_fixed_annotation_dynamic(self, target: "Mobject", label_text: str,
                                      direction=UP, buff: float = 0.2,
                                      font_size: int = 20, color=WHITE) -> Text:
        """
        为移动中的 3D 对象添加动态跟随的固定方向标注
        
        与 add_fixed_annotation 不同，此方法的标注会实时跟随 target 移动
        
        Args:
            target: 目标对象
            label_text: 标注文本
            direction: 标注方向
            buff: 距离
            font_size: 字号
            color: 颜色
            
        Returns:
            Text: 带有动态 updater 的标注
        """
        label = Text(
            label_text,
            font="STKaiti",
            font_size=font_size,
            color=color
        )
        
        camera_frame = self.camera.frame
        
        def dynamic_updater(obj, dt):
            # 实时计算目标位置
            current_pos = target.get_center() + direction * buff
            new_pos = camera_frame.to_fixed_frame_point(current_pos)
            obj.fix_in_frame()
            new_pos[2] = 0
            obj.move_to(new_pos)
            return obj
        
        label.add_updater(dynamic_updater)
        
        return label




# 将 Mixin 方法添加到 AutoScene
AutoScene.add_fixed_annotation = AutoSceneEnhancementMixin.add_fixed_annotation
AutoScene.add_fixed_annotation_dynamic = AutoSceneEnhancementMixin.add_fixed_annotation_dynamic
