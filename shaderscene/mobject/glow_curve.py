from __future__ import annotations

"""
辉光曲线 Mobject 类
基于 GlowLine 架构创建的参数化辉光曲线效果
支持自定义函数生成平滑的辉光曲线

辉光效果：
- 白色核心：纯白中心线
- 白色高斯辉光：白色向外衰减
- 彩色高斯辉光：原始颜色的外层辉光
"""

__all__ = [
    "GlowCurve",
    "GlowParametricCurve",
    "GlowFunctionGraph",
]

import moderngl
import numpy as np
from pathlib import Path
from manimlib.constants import WHITE, GREY_C
from manimlib.constants import ORIGIN, TAU
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.point_cloud_mobject import PMobject
from manimlib.utils.iterables import resize_with_interpolation
from manimlib.utils.space_ops import get_norm

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy.typing as npt
    from typing import Sequence, Tuple, Callable
    from manimlib.typing import ManimColor, Vect3, Vect3Array, Self


DEFAULT_GLOW_CURVE_WIDTH = 0.02
DEFAULT_GLOW_WIDTH = 0.15
DEFAULT_GLOW_FACTOR = 2.5


class GlowCurve(PMobject):
    """
    辉光曲线类
    
    使用自定义着色器渲染具有辉光效果的参数化曲线。
    支持传入函数生成曲线点，并通过 GPU 渲染平滑的辉光效果。
    
    辉光效果层次：
    1. 白色核心 (white_core_ratio) - 中心纯白线
    2. 白色辉光 (core_width_ratio) - 白色高斯扩散
    3. 彩色辉光 (glow_width) - 原色高斯扩散
    """
    
    # 指定着色器文件夹
    shader_folder: str = str(Path(Path(__file__).parent.parent, "trueglow_curve_shader"))
    
    # 渲染基元类型：线段
    render_primitive: int = moderngl.LINES
    
    # 数据类型定义
    data_dtype: Sequence[Tuple[str, type, Tuple[int]]] = [
        ('point', np.float32, (3,)),          # 曲线点位置
        ('rgba', np.float32, (4,)),           # 颜色和透明度
        ('glow_width', np.float32, (1,)),     # 辉光宽度
        ('tangent', np.float32, (3,)),        # 切线方向
    ]

    def __init__(
        self,
        function: Callable[[float], Vect3] = None,
        t_range: Tuple[float, float] = (0, 1),
        n_samples: int = 1000,
        color: ManimColor = WHITE,
        opacity: float = 1.0,
        curve_width: float = DEFAULT_GLOW_CURVE_WIDTH,
        glow_width: float = DEFAULT_GLOW_WIDTH,
        glow_factor: float = DEFAULT_GLOW_FACTOR,
        core_width_ratio: float = 0.35,      # 过渡区域结束位置
        white_core_ratio: float = 0.12,      # 白色核心区域半径
        anti_alias_width: float = 1.5,
        **kwargs
    ):
        self.function = function
        self.t_range = t_range
        self.n_samples = n_samples
        self.curve_width = curve_width
        self.glow_width = glow_width
        self.base_glow_width = glow_width
        self.glow_factor = glow_factor
        self.core_width_ratio = core_width_ratio
        self.white_core_ratio = white_core_ratio
        self.anti_alias_width = anti_alias_width

        super().__init__(
            color=color,
            opacity=opacity,
            **kwargs
        )
        
        # 生成曲线点
        if function is not None:
            self.set_points_from_function(function, t_range, n_samples)

    def init_uniforms(self) -> None:
        super().init_uniforms()
        self.uniforms["glow_factor"] = self.glow_factor
        self.uniforms["core_width_ratio"] = self.core_width_ratio
        self.uniforms["white_core_ratio"] = self.white_core_ratio
        self.uniforms["anti_alias_width"] = self.anti_alias_width

    def _compute_tangents(self, points: np.ndarray) -> np.ndarray:
        """
        计算曲线上每个点的切线方向
        
        使用中心差分法计算更平滑的切线，确保曲线宽度一致
        """
        n = len(points)
        tangents = np.zeros_like(points)
        
        if n < 2:
            return tangents
        
        # 中心差分计算内部点的切线
        for i in range(1, n - 1):
            tangent = points[i + 1] - points[i - 1]
            norm = get_norm(tangent)
            if norm > 1e-8:
                tangents[i] = tangent / norm
            else:
                # 如果中心差分失败，使用前向差分
                tangent = points[i + 1] - points[i]
                norm = get_norm(tangent)
                if norm > 1e-8:
                    tangents[i] = tangent / norm
        
        # 端点使用单侧差分
        # 起点
        tangent = points[1] - points[0]
        norm = get_norm(tangent)
        if norm > 1e-8:
            tangents[0] = tangent / norm
        else:
            tangents[0] = np.array([1.0, 0.0, 0.0])
        
        # 终点
        tangent = points[-1] - points[-2]
        norm = get_norm(tangent)
        if norm > 1e-8:
            tangents[-1] = tangent / norm
        else:
            tangents[-1] = tangents[-2] if n > 1 else np.array([1.0, 0.0, 0.0])
        
        return tangents

    @Mobject.affects_data
    def set_points_from_function(
        self,
        function: Callable[[float], Vect3],
        t_range: Tuple[float, float] = None,
        n_samples: int = None
    ) -> Self:
        """从参数函数生成曲线点"""
        if t_range is None:
            t_range = self.t_range
        if n_samples is None:
            n_samples = self.n_samples
        
        # 生成参数值
        t_values = np.linspace(t_range[0], t_range[1], n_samples)
        
        # 计算曲线点
        curve_points = np.array([function(t) for t in t_values], dtype=np.float32)
        
        # 计算切线
        tangents = self._compute_tangents(curve_points)
        
        # 转换为线段端点
        line_points = []
        line_tangents = []
        
        for i in range(len(curve_points) - 1):
            p1 = curve_points[i]
            p2 = curve_points[i + 1]
            t1 = tangents[i]
            t2 = tangents[i + 1]
            
            line_points.append(p1)
            line_points.append(p2)
            line_tangents.append(t1)
            line_tangents.append(t2)
        
        if line_points:
            self.set_points(np.array(line_points, dtype=np.float32))
            
            if self.has_points():
                self.data['tangent'][:] = np.array(line_tangents, dtype=np.float32)
                self.data['glow_width'][:, 0] = self.glow_width
        
        return self

    @Mobject.affects_data
    def set_glow_widths(self, glow_widths: npt.ArrayLike) -> Self:
        """设置辉光宽度数组"""
        glow_widths = np.array(glow_widths, dtype=np.float32)
        if len(glow_widths.shape) == 0:
            glow_widths = np.array([glow_widths])
        
        if self.has_points():
            glow_widths = resize_with_interpolation(glow_widths, self.get_num_points())
            self.data['glow_width'][:, 0] = glow_widths
        return self

    def get_glow_widths(self) -> np.ndarray:
        """获取辉光宽度数组"""
        return self.data['glow_width'][:, 0]

    @Mobject.affects_data
    def set_glow_width(self, glow_width: float) -> Self:
        """设置统一的辉光宽度"""
        self.glow_width = glow_width
        # 如果脉冲未启用，同步更新base_glow_width
        if not getattr(self, 'pulse_enabled', False):
            self.base_glow_width = glow_width
        if self.has_points():
            self.data['glow_width'][:, 0] = glow_width
        return self

    def get_glow_width(self) -> float:
        """获取平均辉光宽度"""
        if self.has_points():
            return np.mean(self.get_glow_widths())
        return self.glow_width

    def set_glow_factor(self, glow_factor: float) -> Self:
        """设置辉光因子"""
        self.uniforms["glow_factor"] = glow_factor
        self.glow_factor = glow_factor
        return self

    def get_glow_factor(self) -> float:
        """获取辉光因子"""
        return self.uniforms["glow_factor"]

    def set_core_width_ratio(self, core_width_ratio: float) -> Self:
        """设置核心曲线宽度比例（过渡区域结束位置）"""
        self.uniforms["core_width_ratio"] = core_width_ratio
        self.core_width_ratio = core_width_ratio
        return self
    
    def get_core_width_ratio(self) -> float:
        """获取核心曲线宽度比例"""
        return self.uniforms.get("core_width_ratio", self.core_width_ratio)
    
    def set_white_core_ratio(self, white_core_ratio: float) -> Self:
        """
        设置白色核心区域半径
        
        Args:
            white_core_ratio: 白色核心区域半径 (推荐范围 0.02-0.25)
                - 较小值 (0.05): 细白线核心
                - 默认值 (0.12): 适中白色核心
                - 较大值 (0.20): 粗白线核心
        """
        self.uniforms["white_core_ratio"] = white_core_ratio
        self.white_core_ratio = white_core_ratio
        return self
    
    def get_white_core_ratio(self) -> float:
        """获取白色核心区域半径"""
        return self.uniforms.get("white_core_ratio", self.white_core_ratio)

    def compute_bounding_box(self) -> Vect3Array:
        """计算包围盒，考虑辉光宽度"""
        bb = super().compute_bounding_box()
        max_glow = self.get_glow_width()
        bb[0] += np.full((3,), -max_glow)
        bb[2] += np.full((3,), max_glow)
        return bb

    def scale(
        self,
        scale_factor: float | npt.ArrayLike,
        scale_glow: bool = True,
        **kwargs
    ) -> Self:
        """缩放曲线，可选择是否缩放辉光"""
        super().scale(scale_factor, **kwargs)
        if scale_glow:
            if np.isscalar(scale_factor):
                glow_scale = scale_factor
            else:
                glow_scale = np.mean(scale_factor)
            self.set_glow_widths(glow_scale * self.get_glow_widths())
            self.base_glow_width *= glow_scale
        return self
    
    def enable_pulse(self, frequency: float = 1.0, amplitude: float = 0.3) -> Self:
        """启用脉冲效果"""
        self.pulse_enabled = True
        self.pulse_frequency = frequency
        self.pulse_amplitude = amplitude
        self._pulse_time = 0.0  # 初始化脉冲时间
        self.pulse_min_width = self.base_glow_width * 0.5  # 设置最小宽度为基础宽度的50%
        if not hasattr(self, '_pulse_updater_added'):
            self.add_updater(self._pulse_updater)
            self._pulse_updater_added = True
        return self
    
    def disable_pulse(self) -> Self:
        """禁用脉冲效果"""
        self.pulse_enabled = False
        self.set_glow_width(self.base_glow_width)
        return self
    
    def _pulse_updater(self, mob, dt: float) -> None:
        """脉冲更新器（内部使用）"""
        if not self.pulse_enabled:
            return
        
        self._pulse_time += dt
        # 使用正弦波生成脉冲
        pulse_value = np.sin(self._pulse_time * self.pulse_frequency * TAU)
        # 映射到 [0, 1] 范围
        pulse_normalized = (pulse_value + 1.0) / 2.0
        # 计算当前辉光宽度
        width_range = self.base_glow_width - self.pulse_min_width
        current_width = self.pulse_min_width + width_range * (1.0 - self.pulse_amplitude + self.pulse_amplitude * pulse_normalized)
        
        self.set_glow_width(current_width)
    
    def set_pulse_frequency(self, frequency: float) -> Self:
        """设置脉冲频率"""
        self.pulse_frequency = frequency
        return self
    
    def set_pulse_amplitude(self, amplitude: float) -> Self:
        """设置脉冲振幅"""
        self.pulse_amplitude = amplitude
        return self


class GlowParametricCurve(GlowCurve):
    """
    参数化辉光曲线（别名，方便使用）
    """
    pass


class GlowFunctionGraph(GlowCurve):
    """
    函数图像辉光曲线
    
    专门用于绘制 y = f(x) 形式的函数图像
    """
    
    def __init__(
        self,
        function: Callable[[float], float],
        x_range: Tuple[float, float] = (-5, 5),
        **kwargs
    ):
        # 将 y=f(x) 转换为参数形式
        def parametric_func(x):
            return np.array([x, function(x), 0], dtype=np.float32)
        
        super().__init__(
            function=parametric_func,
            t_range=x_range,
            **kwargs
        )


# 便捷函数
def GlowSin(**kwargs):
    """创建正弦曲线"""
    return GlowFunctionGraph(
        function=np.sin,
        x_range=(-TAU, TAU),
        **kwargs
    )


def GlowCircle(radius: float = 1.0, **kwargs):
    """创建圆形辉光曲线"""
    def circle_func(t):
        return np.array([
            radius * np.cos(t),
            radius * np.sin(t),
            0
        ], dtype=np.float32)
    
    return GlowCurve(
        function=circle_func,
        t_range=(0, TAU),
        **kwargs
    )


def GlowSpiral(a: float = 0.5, b: float = 0.2, **kwargs):
    """创建螺旋线辉光曲线"""
    def spiral_func(t):
        r = a + b * t
        return np.array([
            r * np.cos(t),
            r * np.sin(t),
            0
        ], dtype=np.float32)
    
    return GlowCurve(
        function=spiral_func,
        t_range=(0, 6 * TAU),
        **kwargs
    )


# 导入常量
from manimlib.constants import TAU
