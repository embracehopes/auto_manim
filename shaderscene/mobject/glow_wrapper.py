"""Glow wrapper effect for arbitrary mobjects."""

from __future__ import annotations

import numpy as np
import moderngl
from pathlib import Path

from manimlib import *  # noqa: F401,F403
from manimlib.constants import WHITE
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.point_cloud_mobject import PMobject
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.color import color_to_rgba
from manimlib.utils.space_ops import get_norm

from typing import Sequence, Iterable, Optional, Self

__all__ = [
    "GlowObjectPointCloud",
    "GlowLineStrip",
    "GlowWrapperEffect",
]


DEFAULT_BRIGHT_COLORS = [
    "#FF0080", "#FF4000", "#FF8000", "#FFFF00",
    "#80FF00", "#00FF80", "#0080FF", "#8000FF", "#FF0080"
]

DEFAULT_DARK_COLORS = [
    "#2D1B69", "#4A0E4E", "#8B0000", "#B8860B",
    "#006400", "#191970", "#4B0082", "#2D1B69"
]

DEFAULT_NEON_COLORS = [
    "#FF006E", "#FB5607", "#FFBE0B", "#8338EC",
    "#3A86FF", "#06FFA5", "#FF006E"
]


class GlowObjectPointCloud(PMobject):
    """GPU halo renderer that expands every point into a glowing quad."""

    shader_folder: str = str(Path(Path(__file__).parent.parent, "trueglow_wrapper_shader"))
    render_primitive: int = moderngl.POINTS

    data_dtype = [
        ("point", np.float32, (3,)),
        ("rgba", np.float32, (4,)),
        ("glow_width", np.float32, (1,)),
    ]

    def __init__(
        self,
        points: np.ndarray,
        colors: np.ndarray,
        glow_width: float = 0.35,
        glow_factor: float = 1.0,
        core_width_ratio: float = 0.3,
        white_core_ratio: float = 0.3,
        white_glow_ratio: float = 1,
        outer_color_intensity: float = 0.75,
        anti_alias_width: float = 1.5,
        **kwargs,
    ) -> None:
        self.glow_width = glow_width
        self.glow_factor = glow_factor
        self.core_width_ratio = core_width_ratio
        self.white_core_ratio = white_core_ratio
        self.white_glow_ratio = white_glow_ratio
        self.anti_alias_width = anti_alias_width

        super().__init__(**kwargs)

        self.replace_points(points)
        self.data["rgba"][:] = colors
        self.data["glow_width"][:, 0] = glow_width

    def replace_points(self, points: np.ndarray) -> None:
        if len(points.shape) != 2 or points.shape[1] != 3:
            raise ValueError("GlowObjectPointCloud expects (N,3) points")
        self.set_points(points)

    def init_uniforms(self) -> None:
        super().init_uniforms()
        self.uniforms["glow_factor"] = float(self.glow_factor)
        self.uniforms["core_width_ratio"] = float(self.core_width_ratio)
        self.uniforms["white_core_ratio"] = float(self.white_core_ratio)
        self.uniforms["white_glow_ratio"] = float(self.white_glow_ratio)
        self.uniforms["anti_alias_width"] = float(self.anti_alias_width)

    def set_glow_factor(self, value: float) -> "GlowObjectPointCloud":
        self.glow_factor = value
        self.uniforms["glow_factor"] = float(value)
        return self

    def set_glow_width(self, value: float) -> "GlowObjectPointCloud":
        self.glow_width = value
        if self.has_points():
            self.data["glow_width"][:, 0] = float(value)
        return self

    def set_white_core_ratio(self, value: float) -> "GlowObjectPointCloud":
        self.white_core_ratio = value
        self.uniforms["white_core_ratio"] = float(value)
        return self

    def set_white_glow_ratio(self, value: float) -> "GlowObjectPointCloud":
        self.white_glow_ratio = value
        self.uniforms["white_glow_ratio"] = float(value)
        return self

    def set_colors(self, colors: np.ndarray) -> "GlowObjectPointCloud":
        if colors.shape != self.data["rgba"].shape:
            raise ValueError("Color array shape mismatch")
        self.data["rgba"][:] = colors
        return self


# ============================================================================
# GlowLineStrip - 使用线段渲染连续辉光
# ============================================================================

class GlowLineStrip(PMobject):
    """
    使用连续线段渲染辉光效果的 Mobject
    
    相比 GlowObjectPointCloud（离散点），GlowLineStrip 使用线段连接相邻采样点，
    避免了明显的辉光点痕迹，产生更平滑连续的辉光效果。
    
    适用于：
    - VMobject 轮廓的辉光包裹
    - 曲线/路径的辉光效果
    - 需要连续辉光而非离散辉光点的场景
    """
    
    # 使用与 GlowCurve 相同的着色器
    shader_folder: str = str(Path(Path(__file__).parent.parent, "trueglow_curve_shader"))
    render_primitive: int = moderngl.LINES
    
    data_dtype = [
        ("point", np.float32, (3,)),
        ("rgba", np.float32, (4,)),
        ("glow_width", np.float32, (1,)),
        ("tangent", np.float32, (3,)),
    ]
    
    def __init__(
        self,
        points: np.ndarray,
        colors: np.ndarray,
        glow_width: float = 0.15,
        glow_factor: float = 2.5,
        core_width_ratio: float = 0.35,
        white_core_ratio: float = 0.12,
        anti_alias_width: float = 1.5,
        closed: bool = False,
        **kwargs,
    ) -> None:
        """
        参数：
        - points: (N, 3) 形状的点数组，定义线段路径
        - colors: (N, 4) 形状的 RGBA 颜色数组
        - glow_width: 辉光宽度
        - glow_factor: 辉光衰减因子（越大衰减越快）
        - core_width_ratio: 过渡区域结束位置
        - white_core_ratio: 白色核心区域半径
        - closed: 是否闭合路径（首尾相连）
        """
        self.glow_width = glow_width
        self.glow_factor = glow_factor
        self.core_width_ratio = core_width_ratio
        self.white_core_ratio = white_core_ratio
        self.anti_alias_width = anti_alias_width
        self.closed = closed
        
        super().__init__(**kwargs)
        
        # 设置数据
        self._setup_line_data(points, colors)
    
    def _compute_tangents(self, points: np.ndarray) -> np.ndarray:
        """
        计算每个点的切线方向
        使用中心差分法确保平滑的切线过渡
        """
        n = len(points)
        tangents = np.zeros_like(points)
        
        if n < 2:
            return tangents
        
        # 内部点使用中心差分
        for i in range(1, n - 1):
            tangent = points[i + 1] - points[i - 1]
            norm = get_norm(tangent)
            if norm > 1e-8:
                tangents[i] = tangent / norm
            else:
                tangent = points[i + 1] - points[i]
                norm = get_norm(tangent)
                if norm > 1e-8:
                    tangents[i] = tangent / norm
        
        # 端点处理
        if self.closed and n > 2:
            # 闭合路径：首尾相连
            tangent = points[1] - points[-1]
            norm = get_norm(tangent)
            tangents[0] = tangent / norm if norm > 1e-8 else np.array([1., 0., 0.])
            
            tangent = points[0] - points[-2]
            norm = get_norm(tangent)
            tangents[-1] = tangent / norm if norm > 1e-8 else tangents[-2]
        else:
            # 开放路径：单侧差分
            tangent = points[1] - points[0]
            norm = get_norm(tangent)
            tangents[0] = tangent / norm if norm > 1e-8 else np.array([1., 0., 0.])
            
            tangent = points[-1] - points[-2]
            norm = get_norm(tangent)
            tangents[-1] = tangent / norm if norm > 1e-8 else tangents[-2]
        
        return tangents.astype(np.float32)
    
    def _setup_line_data(self, points: np.ndarray, colors: np.ndarray) -> None:
        """设置线段数据，将点转换为线段格式"""
        n_points = len(points)
        if n_points < 2:
            # 至少需要2个点
            self.set_points(np.zeros((0, 3), dtype=np.float32))
            return
        
        # 计算切线
        tangents = self._compute_tangents(points)
        
        # 构建线段数据
        # 每两个相邻点形成一条线段
        if self.closed:
            n_segments = n_points
        else:
            n_segments = n_points - 1
        
        # 分配数据空间 (每条线段2个顶点)
        n_vertices = n_segments * 2
        self.resize_points(n_vertices)
        
        # 填充数据
        for i in range(n_segments):
            j = (i + 1) % n_points
            base_idx = i * 2
            
            # 起点
            self.data["point"][base_idx] = points[i]
            self.data["rgba"][base_idx] = colors[i]
            self.data["glow_width"][base_idx, 0] = self.glow_width
            self.data["tangent"][base_idx] = tangents[i]
            
            # 终点
            self.data["point"][base_idx + 1] = points[j]
            self.data["rgba"][base_idx + 1] = colors[j]
            self.data["glow_width"][base_idx + 1, 0] = self.glow_width
            self.data["tangent"][base_idx + 1] = tangents[j]
    
    def init_uniforms(self) -> None:
        super().init_uniforms()
        self.uniforms["glow_factor"] = float(self.glow_factor)
        self.uniforms["core_width_ratio"] = float(self.core_width_ratio)
        self.uniforms["white_core_ratio"] = float(self.white_core_ratio)
        self.uniforms["anti_alias_width"] = float(self.anti_alias_width)
    
    def replace_points(self, points: np.ndarray, colors: np.ndarray = None) -> "GlowLineStrip":
        """替换点数据"""
        if colors is None:
            # 保持原有颜色
            n_points = len(points)
            colors = np.tile([1., 1., 1., 1.], (n_points, 1)).astype(np.float32)
        self._setup_line_data(points, colors)
        return self
    
    def set_glow_factor(self, value: float) -> "GlowLineStrip":
        self.glow_factor = value
        self.uniforms["glow_factor"] = float(value)
        return self
    
    def set_glow_width(self, value: float) -> "GlowLineStrip":
        self.glow_width = value
        if self.has_points():
            self.data["glow_width"][:, 0] = float(value)
        return self
    
    def set_white_core_ratio(self, value: float) -> "GlowLineStrip":
        self.white_core_ratio = value
        self.uniforms["white_core_ratio"] = float(value)
        return self
    
    def set_core_width_ratio(self, value: float) -> "GlowLineStrip":
        self.core_width_ratio = value
        self.uniforms["core_width_ratio"] = float(value)
        return self
    
    def set_colors(self, colors: np.ndarray) -> "GlowLineStrip":
        """设置颜色，需要传入完整的线段顶点颜色"""
        if colors.shape != self.data["rgba"].shape:
            raise ValueError(f"Color array shape mismatch: expected {self.data['rgba'].shape}, got {colors.shape}")
        self.data["rgba"][:] = colors
        return self


# ============================================================================
# GlowWrapperEffect - 重构版本
# ============================================================================

def _interpolate(a, b, alpha: float):
    """线性插值"""
    return a + (b - a) * alpha


def _format_rgba(value) -> np.ndarray:
    """将颜色值转换为 RGBA 数组"""
    if isinstance(value, np.ndarray):
        rgba = value.astype(np.float32).flatten()
    elif isinstance(value, (list, tuple)):
        rgba = np.array(value, dtype=np.float32)
    elif isinstance(value, str):
        rgba = np.array(color_to_rgba(value), dtype=np.float32)
    else:
        rgba = np.array(color_to_rgba(value), dtype=np.float32)
    
    if rgba.shape[0] == 3:
        rgba = np.append(rgba, 1.0).astype(np.float32)
    
    return rgba[:4]


def _format_color(color) -> np.ndarray:
    """将颜色值转换为 RGB 数组"""
    if isinstance(color, np.ndarray):
        return color.astype(np.float32)[:3]
    elif isinstance(color, (list, tuple)) and not isinstance(color, str):
        return np.array(color, dtype=np.float32)[:3]
    else:
        return np.array(color_to_rgba(color)[:3], dtype=np.float32)


class GlowWrapperEffect(Group):
    """
    为任意 Mobject 添加 GPU 辉光效果
    
    辉光效果：白色核心 → 柔和过渡 → 原始颜色高斯模糊辉光
    
    渲染模式（render_mode）：
    - "line": 使用连续线段渲染，产生平滑连续的辉光效果（推荐）
    - "point": 使用离散点渲染，适合粒子效果但可能有明显的辉光点痕迹
    
    主要参数：
    - color: 辉光颜色（支持 hex、RGB、RGBA）
    - alpha: 透明度 (0-1)
    - size: 辉光大小（即 glow_width）
    - glow_factor: 辉光衰减因子
    - white_core_ratio: 白色核心强度
    - render_mode: "line" 或 "point"
    
    使用示例：
    >>> glow = GlowWrapperEffect(circle, color=BLUE, size=0.3)
    >>> glow = GlowWrapperEffect(circle, color=BLUE, render_mode="line")  # 连续辉光
    >>> glow.set(color=RED, alpha=0.8, size=0.5)  # 一次设置多个属性
    >>> glow.mix(YELLOW, factor=0.5)  # 混合颜色
    """

    def __init__(
        self,
        mobject: Mobject,
        # === 核心参数 ===
        color: str | Sequence[float] | np.ndarray = WHITE,
        alpha: float = 1.0,
        size: float = 0.3,
        glow_factor: float = 3.0,
        # === 渲染模式 ===
        render_mode: str = "line",  # "line" 或 "point"
        # === 辉光样式参数 ===
        core_width_ratio: float = 0.45,
        white_core_ratio: float = 0.5,
        white_glow_ratio: float = 1.0,
        anti_alias_width: float = 1.5,
        # === 采样参数 ===
        sample_stride: int = 1,
        max_points: int = 2000,
        use_perimeter_sampling: bool = True,
        curve_sample_factor: float = 50.0,
        min_curve_samples: int = 200,
        # === 高级参数 ===
        color_scheme: str | Sequence[str] | None = None,
        jitter: float = 0.0,
        auto_update: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        
        # 目标对象
        self.target = mobject
        
        # 渲染模式
        self._render_mode = render_mode.lower()
        if self._render_mode not in ("line", "point"):
            raise ValueError(f"render_mode must be 'line' or 'point', got '{render_mode}'")
        
        # 核心属性：使用 RGBA 数组存储颜色和透明度
        self._rgba = _format_rgba(color)
        self._rgba[3] = float(alpha)
        self._size = float(size)
        self._glow_factor = float(glow_factor)
        
        # 辉光样式
        self._core_width_ratio = float(core_width_ratio)
        self._white_core_ratio = float(white_core_ratio)
        self._white_glow_ratio = float(white_glow_ratio)
        self._anti_alias_width = float(anti_alias_width)
        
        # 采样参数
        self._sample_stride = max(1, sample_stride)
        self._max_points = max_points
        self._use_perimeter_sampling = use_perimeter_sampling
        self._curve_sample_factor = max(curve_sample_factor, 0.0)
        self._min_curve_samples = max(1, int(min_curve_samples))
        self._jitter = jitter
        
        # 颜色方案（用于渐变效果）
        self._color_scheme = color_scheme
        
        # 创建辉光层
        self._build_glow()
        
        # 自动更新
        if auto_update:
            self.add_updater(lambda m, dt: m.refresh())

    # ========================================================================
    # 核心方法：set / get / mix
    # ========================================================================
    
    def set(
        self,
        color: str | Sequence[float] | np.ndarray | None = None,
        alpha: float | None = None,
        size: float | None = None,
        glow_factor: float | None = None,
        white_core_ratio: float | None = None,
        white_glow_ratio: float | None = None,
        *,
        rebuild: bool = True,
    ) -> Self:
        """
        设置辉光属性（一次设置多个）
        
        参数：
        - color: RGB 或 RGBA 颜色（支持 hex、列表、数组）
        - alpha: 透明度 (0-1)
        - size: 辉光大小
        - glow_factor: 辉光衰减因子
        - white_core_ratio: 白色核心强度
        - white_glow_ratio: 白色辉光比例
        - rebuild: 是否立即重建辉光（默认 True）
        
        特殊：当 color 为 RGBA (4分量) 时，同时设置颜色和透明度
        """
        if color is not None:
            rgba = _format_rgba(color)
            # 如果传入的是 RGBA，同时设置透明度
            if len(rgba) == 4 and alpha is None:
                self._rgba[:] = rgba
            else:
                self._rgba[:3] = rgba[:3]
        
        if alpha is not None:
            self._rgba[3] = float(np.clip(alpha, 0.0, 1.0))
        
        if size is not None:
            self._size = float(size)
        
        if glow_factor is not None:
            self._glow_factor = float(glow_factor)
        
        if white_core_ratio is not None:
            self._white_core_ratio = float(white_core_ratio)
        
        if white_glow_ratio is not None:
            self._white_glow_ratio = float(white_glow_ratio)
        
        if rebuild:
            self._update_glow()
        
        return self

    def get(self) -> np.ndarray:
        """获取当前 RGBA 颜色数组"""
        return self._rgba.copy()

    def get_color(self) -> np.ndarray:
        """获取 RGB 颜色"""
        return self._rgba[:3].copy()

    def get_alpha(self) -> float:
        """获取透明度"""
        return float(self._rgba[3])

    def get_size(self) -> float:
        """获取辉光大小"""
        return self._size

    def mix(
        self,
        color: str | Sequence[float] | np.ndarray,
        factor: float = 0.5,
        *,
        rebuild: bool = True,
    ) -> Self:
        """
        混合颜色
        
        参数：
        - color: 目标颜色
        - factor: 混合因子 (0=保持原色, 1=完全变成目标色)
        """
        factor = float(np.clip(factor, 0.0, 1.0))
        target_rgb = _format_color(color)
        self._rgba[:3] = self._rgba[:3] * (1 - factor) + target_rgb * factor
        
        if rebuild:
            self._update_glow()
        
        return self

    def mix_alpha(
        self,
        alpha: float,
        factor: float = 0.5,
        *,
        rebuild: bool = True,
    ) -> Self:
        """
        混合透明度
        
        参数：
        - alpha: 目标透明度
        - factor: 混合因子
        """
        factor = float(np.clip(factor, 0.0, 1.0))
        self._rgba[3] = self._rgba[3] * (1 - factor) + float(alpha) * factor
        
        if rebuild:
            self._update_glow()
        
        return self

    def mix_size(
        self,
        size: float,
        factor: float = 0.5,
        *,
        rebuild: bool = True,
    ) -> Self:
        """
        混合辉光大小
        
        参数：
        - size: 目标大小
        - factor: 混合因子
        """
        factor = float(np.clip(factor, 0.0, 1.0))
        self._size = self._size * (1 - factor) + float(size) * factor
        
        if rebuild:
            self._update_glow()
        
        return self

    # ========================================================================
    # 动画插值支持
    # ========================================================================
    
    def interpolate_glow(
        self,
        other: "GlowWrapperEffect",
        alpha: float,
    ) -> Self:
        """
        与另一个 GlowWrapperEffect 进行插值（用于动画）
        
        参数：
        - other: 目标状态
        - alpha: 插值因子 (0=当前状态, 1=目标状态)
        """
        self._rgba = _interpolate(self._rgba, other._rgba, alpha)
        self._size = _interpolate(self._size, other._size, alpha)
        self._glow_factor = _interpolate(self._glow_factor, other._glow_factor, alpha)
        self._white_core_ratio = _interpolate(self._white_core_ratio, other._white_core_ratio, alpha)
        self._white_glow_ratio = _interpolate(self._white_glow_ratio, other._white_glow_ratio, alpha)
        
        self._update_glow()
        return self

    # ========================================================================
    # 便捷属性访问器
    # ========================================================================
    
    @property
    def glow_width(self) -> float:
        """辉光宽度（size 的别名）"""
        return self._size

    @glow_width.setter
    def glow_width(self, value: float):
        self._size = float(value)
        self._update_glow()

    @property
    def glow_factor(self) -> float:
        return self._glow_factor

    @glow_factor.setter
    def glow_factor(self, value: float):
        self._glow_factor = float(value)
        self._update_glow()

    @property
    def white_core_ratio(self) -> float:
        return self._white_core_ratio

    @white_core_ratio.setter
    def white_core_ratio(self, value: float):
        self._white_core_ratio = float(value)
        self._update_glow()

    @property
    def white_glow_ratio(self) -> float:
        return self._white_glow_ratio

    @white_glow_ratio.setter
    def white_glow_ratio(self, value: float):
        self._white_glow_ratio = float(value)
        self._update_glow()

    # ========================================================================
    # 内部方法
    # ========================================================================
    
    def _collect_points(self) -> np.ndarray:
        """从目标对象收集采样点"""
        if self.target is None:
            return np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        
        batches = []
        for member in self.target.get_family():
            if not member.has_points():
                continue
            
            # 优先使用周长采样
            if self._use_perimeter_sampling and isinstance(member, VMobject):
                perimeter = self._sample_vmobject_perimeter(member)
                if perimeter is not None and len(perimeter) > 0:
                    batches.append(perimeter)
                    continue
            
            # 回退到原始点
            points = member.get_points()
            if len(points) > 0:
                batches.append(points[::self._sample_stride])
        
        if not batches:
            return np.array([self.target.get_center()], dtype=np.float32)
        
        points = np.concatenate(batches, axis=0)
        
        # 添加抖动
        if self._jitter > 0:
            noise = (np.random.random(points.shape) - 0.5) * 2.0 * self._jitter
            points = points + noise
        
        # 限制点数
        if self._max_points and len(points) > self._max_points:
            idx = np.linspace(0, len(points) - 1, self._max_points, dtype=int)
            points = points[idx]
        
        return points.astype(np.float32)

    def _sample_vmobject_perimeter(self, vmob: VMobject) -> Optional[np.ndarray]:
        """沿 VMobject 周长采样"""
        if vmob.get_num_points() == 0:
            return None
        
        num_curves = max(vmob.get_num_curves(), 1)
        samples = max(int(num_curves * self._curve_sample_factor), self._min_curve_samples)
        
        if samples <= 0:
            return None
        
        alphas = np.linspace(0.0, 1.0, samples, endpoint=False)
        getter = getattr(vmob, "quick_point_from_proportion", vmob.point_from_proportion)
        
        return np.array([getter(float(a)) for a in alphas], dtype=np.float32)

    def _generate_colors(self, count: int) -> np.ndarray:
        """生成颜色数组"""
        if count <= 0:
            return np.zeros((0, 4), dtype=np.float32)
        
        # 如果有颜色方案，使用渐变
        if self._color_scheme is not None:
            return self._generate_gradient_colors(count)
        
        # 单色模式
        return np.tile(self._rgba, (count, 1))

    def _generate_gradient_colors(self, count: int) -> np.ndarray:
        """生成渐变颜色"""
        if isinstance(self._color_scheme, str):
            if self._color_scheme == "bright":
                palette = DEFAULT_BRIGHT_COLORS
            elif self._color_scheme == "dark":
                palette = DEFAULT_DARK_COLORS
            elif self._color_scheme == "neon":
                palette = DEFAULT_NEON_COLORS
            else:
                palette = [self._rgba]
        else:
            palette = list(self._color_scheme)
        
        if len(palette) == 1:
            return np.tile(_format_rgba(palette[0]), (count, 1))
        
        colors = []
        steps = len(palette) - 1
        for i in range(count):
            pos = i / max(count - 1, 1)
            seg = min(int(pos * steps), steps - 1)
            local_t = pos * steps - seg
            c1 = _format_rgba(palette[seg])
            c2 = _format_rgba(palette[seg + 1])
            colors.append(_interpolate(c1, c2, local_t))
        
        return np.stack(colors, axis=0).astype(np.float32)

    def _build_glow(self) -> None:
        """构建辉光层"""
        points = self._collect_points()
        colors = self._generate_colors(len(points))
        
        if self._render_mode == "line":
            # 使用线段渲染连续辉光
            # 检测是否为闭合路径
            closed = self._is_closed_path(points)
            
            self.glow = GlowLineStrip(
                points=points,
                colors=colors,
                glow_width=self._size,
                glow_factor=self._glow_factor,
                core_width_ratio=self._core_width_ratio,
                white_core_ratio=self._white_core_ratio,
                anti_alias_width=self._anti_alias_width,
                closed=closed,
            )
        else:
            # 使用点云渲染（原方式）
            self.glow = GlowObjectPointCloud(
                points=points,
                colors=colors,
                glow_width=self._size,
                glow_factor=self._glow_factor,
                core_width_ratio=self._core_width_ratio,
                white_core_ratio=self._white_core_ratio,
                white_glow_ratio=self._white_glow_ratio,
                anti_alias_width=self._anti_alias_width,
            )
        
        self.add(self.glow)

    def _is_closed_path(self, points: np.ndarray) -> bool:
        """检测点集是否构成闭合路径"""
        if len(points) < 3:
            return False
        # 检查首尾点的距离
        dist = get_norm(points[0] - points[-1])
        # 如果首尾距离小于采样间距的阈值，认为是闭合的
        if len(points) > 1:
            avg_dist = np.mean([get_norm(points[i+1] - points[i]) for i in range(min(10, len(points)-1))])
            return dist < avg_dist * 1.5
        return False

    def _update_glow(self) -> None:
        """更新辉光层属性"""
        if not hasattr(self, 'glow'):
            return
        
        points = self._collect_points()
        colors = self._generate_colors(len(points))
        
        if self._render_mode == "line":
            # 线段模式
            closed = self._is_closed_path(points)
            self.glow.closed = closed
            self.glow.replace_points(points, colors)
            self.glow.set_glow_width(self._size)
            self.glow.set_glow_factor(self._glow_factor)
            self.glow.set_white_core_ratio(self._white_core_ratio)
            self.glow.set_core_width_ratio(self._core_width_ratio)
        else:
            # 点云模式
            self.glow.replace_points(points)
            self.glow.set_colors(colors)
            self.glow.set_glow_width(self._size)
            self.glow.set_glow_factor(self._glow_factor)
            self.glow.set_white_core_ratio(self._white_core_ratio)
            self.glow.set_white_glow_ratio(self._white_glow_ratio)

    # ========================================================================
    # 公共方法
    # ========================================================================
    
    def refresh(self) -> Self:
        """刷新辉光（重新采样目标对象）"""
        self._update_glow()
        return self

    def surround(self, mob: Mobject) -> Self:
        """更换目标对象"""
        self.target = mob
        return self.refresh()

    def copy(self) -> "GlowWrapperEffect":
        """复制"""
        clone = GlowWrapperEffect(
            self.target,
            color=self._rgba[:3].copy(),
            alpha=self._rgba[3],
            size=self._size,
            glow_factor=self._glow_factor,
            render_mode=self._render_mode,
            core_width_ratio=self._core_width_ratio,
            white_core_ratio=self._white_core_ratio,
            white_glow_ratio=self._white_glow_ratio,
            anti_alias_width=self._anti_alias_width,
            sample_stride=self._sample_stride,
            max_points=self._max_points,
            use_perimeter_sampling=self._use_perimeter_sampling,
            curve_sample_factor=self._curve_sample_factor,
            min_curve_samples=self._min_curve_samples,
            color_scheme=self._color_scheme,
            jitter=self._jitter,
        )
        return clone

    # ========================================================================
    # 兼容性方法（保持向后兼容）
    # ========================================================================
    
    def set_glow(
        self,
        color: str | Sequence[float] | np.ndarray | None = None,
        alpha: float | None = None,
        width: float | None = None,
    ) -> Self:
        """兼容旧 API"""
        return self.set(color=color, alpha=alpha, size=width)

    def set_glow_width(self, value: float) -> Self:
        """兼容旧 API"""
        return self.set(size=value)

    def set_glow_factor(self, value: float) -> Self:
        """兼容旧 API"""
        return self.set(glow_factor=value)

    def set_white_core_ratio(self, value: float) -> Self:
        """兼容旧 API"""
        return self.set(white_core_ratio=value)

    def set_white_glow_ratio(self, value: float) -> Self:
        """兼容旧 API"""
        return self.set(white_glow_ratio=value)

    def set_color_scheme(self, scheme: str | Sequence[str]) -> Self:
        """设置颜色方案"""
        self._color_scheme = scheme
        return self.refresh()

    def mix_glow(
        self,
        color: str | Sequence[float] | np.ndarray | None = None,
        alpha: float | None = None,
        factor: float = 0.5,
    ) -> Self:
        """兼容旧 API"""
        if color is not None:
            self.mix(color, factor, rebuild=False)
        if alpha is not None:
            self.mix_alpha(alpha, factor, rebuild=False)
        self._update_glow()
        return self

    def get_glow_rgba(self) -> np.ndarray:
        """兼容旧 API"""
        return self.get()
