from __future__ import annotations

"""
辉光线条 Mobject 类
基于 true_dot 和 DotCloud 的架构创建的辉光线条效果
"""

__all__ = [
    "GlowLine", 
    "MultiGlowLine", 
    "GlowLineBetween", 
    "GlowPath"
]

import moderngl
import numpy as np
from pathlib import Path
from manimlib.constants import WHITE, GREY_C
from manimlib.constants import ORIGIN, NULL_POINTS
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.point_cloud_mobject import PMobject
from manimlib.utils.iterables import resize_with_interpolation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy.typing as npt
    from typing import Sequence, Tuple
    from manimlib.typing import ManimColor, Vect3, Vect3Array, Self


DEFAULT_GLOW_LINE_WIDTH = 0.02
DEFAULT_GLOW_WIDTH = 0.15
DEFAULT_GLOW_FACTOR = 2.0


class GlowLine(PMobject):
    """
    辉光线条类
    
    使用自定义着色器渲染具有辉光效果的线条。
    类似于 DotCloud 使用 true_dot 着色器，
    但专门为线条渲染优化。
    """
    
    # 指定着色器文件夹
    shader_folder: str = str(Path(Path(__file__).parent.parent, "trueglow_line_shader"))
    
    # 渲染基元类型：线条
    render_primitive: int = moderngl.LINES
    
    # 数据类型定义
    data_dtype: Sequence[Tuple[str, type, Tuple[int]]] = [
        ('point', np.float32, (3,)),      # 线条端点位置
        ('rgba', np.float32, (4,)),       # 颜色和透明度
        ('glow_width', np.float32, (1,)), # 辉光宽度
    ]

    def __init__(
        self,
        start: Vect3 = ORIGIN,
        end: Vect3 = ORIGIN + np.array([1, 0, 0]),
        color: ManimColor = WHITE,
        opacity: float = 1.0,
        line_width: float = DEFAULT_GLOW_LINE_WIDTH,
        glow_width: float = DEFAULT_GLOW_WIDTH,
        glow_factor: float = DEFAULT_GLOW_FACTOR,
        core_width_ratio: float = 0.3,
        anti_alias_width: float = 0.1,
        **kwargs
    ):
        self.line_width = line_width
        self.glow_width = glow_width
        self.glow_factor = glow_factor
        self.core_width_ratio = core_width_ratio
        self.anti_alias_width = anti_alias_width

        super().__init__(
            color=color,
            opacity=opacity,
            **kwargs
        )
        
        # 设置线条端点
        self.set_line_endpoints(start, end)
        
        # 设置辉光参数
        self.set_glow_width(self.glow_width)

    def init_uniforms(self) -> None:
        super().init_uniforms()
        self.uniforms["glow_factor"] = self.glow_factor
        self.uniforms["core_width_ratio"] = self.core_width_ratio
        self.uniforms["anti_alias_width"] = self.anti_alias_width

    @Mobject.affects_data
    def set_line_endpoints(self, start: Vect3, end: Vect3) -> Self:
        """设置线条的起点和终点"""
        points = np.array([start, end])
        self.set_points(points)
        # 确保设置辉光宽度数据
        if self.has_points():
            self.data['glow_width'][:, 0] = self.glow_width
        return self

    def get_start(self) -> Vect3:
        """获取线条起点"""
        if self.has_points():
            return self.get_points()[0]
        return ORIGIN

    def get_end(self) -> Vect3:
        """获取线条终点"""
        if self.has_points():
            return self.get_points()[-1]
        return ORIGIN

    def get_center(self) -> Vect3:
        """获取线条中心点"""
        return (self.get_start() + self.get_end()) / 2

    def get_vector(self) -> Vect3:
        """获取线条方向向量"""
        return self.get_end() - self.get_start()

    def get_length(self) -> float:
        """获取线条长度"""
        return np.linalg.norm(self.get_vector())

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
        """设置核心线条宽度比例"""
        self.uniforms["core_width_ratio"] = core_width_ratio
        self.core_width_ratio = core_width_ratio
        return self

    def get_core_width_ratio(self) -> float:
        """获取核心线条宽度比例"""
        return self.uniforms["core_width_ratio"]

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
        """缩放线条，可选择是否缩放辉光"""
        super().scale(scale_factor, **kwargs)
        if scale_glow:
            if np.isscalar(scale_factor):
                glow_scale = scale_factor
            else:
                # 对于非均匀缩放，使用平均值
                glow_scale = np.mean(scale_factor)
            self.set_glow_widths(glow_scale * self.get_glow_widths())
        return self

    def put_start_and_end_on(self, start: Vect3, end: Vect3) -> Self:
        """将线条的起点和终点放置在指定位置"""
        self.set_line_endpoints(start, end)
        return self

    def move_to(self, point: Vect3) -> Self:
        """移动线条中心到指定点"""
        current_center = self.get_center()
        shift_vector = point - current_center
        self.shift(shift_vector)
        return self


class MultiGlowLine(PMobject):
    """
    多段辉光线条类
    
    可以渲染多条线段，每条线段都有独立的辉光效果
    """
    
    shader_folder: str = "trueglow_line"
    render_primitive: int = moderngl.LINES
    
    data_dtype: Sequence[Tuple[str, type, Tuple[int]]] = [
        ('point', np.float32, (3,)),
        ('rgba', np.float32, (4,)),
        ('glow_width', np.float32, (1,)),
    ]

    def __init__(
        self,
        line_segments: list = None,
        colors: list = None,
        color: ManimColor = WHITE,
        opacity: float = 1.0,
        glow_width: float = DEFAULT_GLOW_WIDTH,
        glow_factor: float = DEFAULT_GLOW_FACTOR,
        **kwargs
    ):
        self.glow_factor = glow_factor
        
        super().__init__(
            color=color,
            opacity=opacity,
            **kwargs
        )
        
        if line_segments:
            self.set_line_segments(line_segments, colors)
        
        self.set_glow_width(glow_width)

    def init_uniforms(self) -> None:
        super().init_uniforms()
        self.uniforms["glow_factor"] = self.glow_factor
        self.uniforms["core_width_ratio"] = 0.3
        self.uniforms["anti_alias_width"] = 0.1

    @Mobject.affects_data
    def set_line_segments(self, line_segments: list, colors: list = None) -> Self:
        """
        设置多条线段
        line_segments: [(start1, end1), (start2, end2), ...]
        colors: [color1, color2, ...] 或单个颜色
        """
        points = []
        rgba_values = []
        
        for i, (start, end) in enumerate(line_segments):
            points.extend([start, end])
            
            # 处理颜色
            if colors and i < len(colors):
                segment_color = colors[i]
            else:
                segment_color = self.color
            
            # 转换为RGBA数组
            if isinstance(segment_color, str):
                # 如果是字符串颜色，转换为RGB
                from manimlib.utils.color import color_to_rgba
                rgba = color_to_rgba(segment_color, self.opacity)
            elif hasattr(segment_color, '__len__') and len(segment_color) >= 3:
                # 如果是RGB/RGBA数组
                if len(segment_color) == 3:
                    rgba = np.array([segment_color[0], segment_color[1], segment_color[2], self.opacity])
                else:
                    rgba = np.array(segment_color)
            else:
                # 默认颜色
                rgba = np.array([1.0, 1.0, 1.0, self.opacity])
            
            # 为线段的两个端点设置相同的颜色
            rgba_values.extend([rgba, rgba])
        
        if points:
            self.set_points(np.array(points))
            # 设置颜色数据
            if rgba_values:
                self.data['rgba'][:] = np.array(rgba_values)
            # 为每条线段设置默认辉光宽度
            self.set_glow_width(DEFAULT_GLOW_WIDTH)
        return self

    def add_line_segment(self, start: Vect3, end: Vect3) -> Self:
        """添加一条线段"""
        current_points = self.get_points() if self.has_points() else np.array([]).reshape(0, 3)
        new_points = np.array([start, end])
        all_points = np.vstack([current_points, new_points]) if len(current_points) > 0 else new_points
        self.set_points(all_points)
        
        # 更新辉光宽度数据
        if self.has_points():
            self.set_glow_width(DEFAULT_GLOW_WIDTH)
        return self

    @Mobject.affects_data  
    def set_glow_width(self, glow_width: float) -> Self:
        """设置所有线段的辉光宽度"""
        if self.has_points():
            self.data['glow_width'][:, 0] = glow_width
        return self

    def set_glow_factor(self, glow_factor: float) -> Self:
        """设置辉光因子"""
        self.uniforms["glow_factor"] = glow_factor
        return self


# 便捷函数
def GlowLineBetween(start: Vect3, end: Vect3, **kwargs) -> GlowLine:
    """创建连接两点的辉光线条"""
    return GlowLine(start=start, end=end, **kwargs)


def GlowPath(points: list, **kwargs) -> MultiGlowLine:
    """创建连接多个点的辉光路径"""
    line_segments = []
    for i in range(len(points) - 1):
        line_segments.append((points[i], points[i + 1]))
    return MultiGlowLine(line_segments=line_segments, **kwargs)
