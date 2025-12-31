from __future__ import annotations

"""
高性能 TracingTail PMobject 类
基于 GlowLine 架构，专门为轨迹追踪优化的辉光尾迹效果
支持 GPU shader 并行渲染，大幅提升多粒子轨迹的性能
"""

__all__ = [
    "TracingTailPMobject", 
    "MultiTracingTails"
]

import math
import moderngl
import numpy as np
from pathlib import Path
from collections import deque

from manimlib.constants import WHITE, ORIGIN
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.point_cloud_mobject import PMobject
from manimlib.utils.iterables import resize_with_interpolation
from manimlib.utils.color import color_to_rgba
from manimlib.utils.bezier import approx_smooth_quadratic_bezier_handles, smooth_quadratic_path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy.typing as npt
    from typing import Sequence, Tuple, Callable, Optional, Deque
    from manimlib.typing import ManimColor, Vect3, Vect3Array, Self


def _compute_neighbor_directions(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """为给定序列的轨迹点计算相邻方向向量。"""
    n_points = len(points)
    prev_dirs = np.zeros((n_points, 3), dtype=np.float32)
    next_dirs = np.zeros((n_points, 3), dtype=np.float32)

    if n_points == 0:
        return prev_dirs, next_dirs
    if n_points == 1:
        return prev_dirs, next_dirs

    last_valid = np.array([1.0, 0.0, 0.0], dtype=np.float32)

    for i in range(n_points):
        if i == 0:
            forward = points[1] - points[0]
            backward = forward
        elif i == n_points - 1:
            backward = points[i] - points[i - 1]
            forward = backward
        else:
            backward = points[i] - points[i - 1]
            forward = points[i + 1] - points[i]

        def _normalize(vec: np.ndarray, fallback: np.ndarray) -> np.ndarray:
            norm = np.linalg.norm(vec)
            if norm < 1e-6:
                return fallback
            return (vec / norm).astype(np.float32)

        prev_dir = _normalize(backward, last_valid)
        next_dir = _normalize(forward, prev_dir)

        if np.linalg.norm(prev_dir) < 1e-6:
            prev_dir = last_valid
        if np.linalg.norm(next_dir) < 1e-6:
            next_dir = prev_dir

        prev_dirs[i] = prev_dir
        next_dirs[i] = next_dir
        last_valid = next_dir

    return prev_dirs, next_dirs


def _prune_large_gaps(points: np.ndarray, times: np.ndarray) -> Tuple[np.ndarray, np.ndarray, bool]:
    """移除首尾处异常大的跳跃，避免首尾牵连。"""
    if len(points) <= 2:
        return points, times, False

    distances = np.linalg.norm(np.diff(points, axis=0), axis=1)
    if len(distances) == 0:
        return points, times, False

    median_dist = float(np.median(distances))
    mad = float(np.median(np.abs(distances - median_dist))) + 1e-6
    high_percentile = float(np.percentile(distances, 95))

    dynamic_threshold = max(
        (median_dist + mad) * 10.0,
        median_dist * 30.0,
        high_percentile * 3.0,
        0.6
    )

    trimmed = False

    if distances[0] > dynamic_threshold:
        points = points[1:]
        times = times[1:]
        trimmed = True

    if len(points) > 2:
        distances_tail = np.linalg.norm(np.diff(points, axis=0), axis=1)
        if len(distances_tail) > 0 and distances_tail[-1] > dynamic_threshold:
            points = points[:-1]
            times = times[:-1]
            trimmed = True

    if len(points) < 2:
        last_point = points[-1] if len(points) else np.zeros(3, dtype=np.float32)
        last_time = times[-1] if len(times) else 0.0
        offset = np.array([1e-4, 0.0, 0.0], dtype=np.float32)
        points = np.vstack([last_point - offset, last_point]).astype(np.float32)
        times = np.array([last_time - 1e-4, last_time], dtype=np.float32)
        trimmed = True

    return points, times, trimmed


def _compute_dynamic_jump_threshold(
    distance_history: deque,
    fallback: float = 3.0,
    min_threshold: float = 0.6,
) -> float:
    """根据历史步长动态计算判定传送的阈值。"""
    if len(distance_history) == 0:
        return max(fallback, min_threshold)

    history_array = np.fromiter(distance_history, dtype=np.float32)
    if history_array.size == 0:
        return max(fallback, min_threshold)

    max_val = float(np.max(history_array))
    median = float(np.median(history_array))
    mad = float(np.median(np.abs(history_array - median))) + 1e-6
    perc90 = float(np.percentile(history_array, 90))
    perc99 = float(np.percentile(history_array, 99)) if history_array.size > 1 else perc90

    dynamic = max(
        min_threshold,
        median + mad * 6.0,
        perc90 * 1.8,
        perc99 * 1.4
    )

    if len(distance_history) <= 3:
        dynamic = max(dynamic, max_val * 4.5 + min_threshold * 0.5)

    return dynamic


class TracingTailPMobject(PMobject):
    """
    高性能轨迹尾迹 PMobject
    
    使用自定义 shader 渲染具有辉光效果的轨迹尾迹。
    优化用于大量粒子的实时轨迹追踪，支持：
    - GPU 并行渲染多条轨迹
    - 动态透明度和宽度渐变
    - 电影级别的辉光效果
    - 高效的轨迹点管理
    - 基于 ManimGL 内置函数的高质量轨迹平滑
      * jagged: 简单快速平滑
      * approx_smooth: 近似贝塞尔平滑（推荐）
      * true_smooth: 完整贝塞尔平滑（最高质量）
    """
    
    # 指定着色器文件夹
    shader_folder: str = str(Path(Path(__file__).parent.parent, "tracing_tail_glow_shader"))
    
    # 渲染基元类型：线段
    render_primitive: int = moderngl.LINES
    
    # 数据类型定义
    data_dtype: Sequence[Tuple[str, type, Tuple[int]]] = [
        ('point', np.float32, (3,)),           # 轨迹点位置
        ('rgba', np.float32, (4,)),            # 颜色和透明度
        ('tail_progress', np.float32, (1,)),   # 尾迹进度 (0=最新, 1=最老)
        ('tail_width', np.float32, (1,)),      # 尾迹宽度
        ('glow_intensity', np.float32, (1,)),  # 辉光强度
        ('prev_dir', np.float32, (3,)),        # 指向当前点的上一段方向
        ('next_dir', np.float32, (3,)),        # 从当前点指向下一段方向
    ]

    def __init__(
        self,
        traced_point_func: Callable[[], Vect3],
        max_tail_length: int = 200,
        tail_lifetime: float = 2.0,
        base_color: ManimColor = WHITE,
        opacity_fade: Tuple[float, float] = (1.0, 0.0),
        width_fade: Tuple[float, float] = (0.06, 0.02),
        glow_factor: float = 2.5,
        anti_alias_width: float = 1,
        smoothing_mode: str = "true_smooth",  # 新增：平滑模式选项
        teleport_fallback: float | None = None,
        teleport_min_threshold: float = 0.6,
        teleport_history: int = 64,
        debug_name: str | None = None,
        debug_logging: bool = False,
        **kwargs
    ):
        self.traced_point_func = traced_point_func
        self.max_tail_length = max_tail_length
        self.tail_lifetime = tail_lifetime
        self.base_color = base_color
        self.opacity_fade = opacity_fade
        self.width_fade = width_fade
        self.glow_factor = glow_factor
        self.anti_alias_width = anti_alias_width
        self.smoothing_mode = smoothing_mode  # 存储平滑模式
        self.debug_name = debug_name or f"TracingTailPMobject@{id(self)}"
        self._debug_logging = debug_logging
        self._teleport_fallback = teleport_fallback if teleport_fallback is not None else 3.0
        self._teleport_min_threshold = max(teleport_min_threshold, 0.1)
        self._distance_history_limit = max(8, int(teleport_history))
        self._recent_distances: Deque[float] = deque(maxlen=self._distance_history_limit)
        self._bootstrap_pending: bool = True
        
        # 轨迹历史存储
        self.tail_points: Deque[Vect3] = deque(maxlen=max_tail_length)
        self.tail_times: Deque[float] = deque(maxlen=max_tail_length)
        self.current_time: float = 0.0
        
        # 预分配缓冲区（避免每次更新都创建新数组）
        self._preallocate_buffers(max_tail_length)
        
        super().__init__(**kwargs)
        
        # 初始化空轨迹
        self._init_empty_tail()

    def _log(self, message: str) -> None:
        if self._debug_logging:
            # 原来这里会直接 print，为避免在非调试模式下输出，将其改为仅记录到内部列表
            # 如果需要外放日志，可以在外部读取 _debug_logs
            if not hasattr(self, '_debug_logs'):
                self._debug_logs = []
            self._debug_logs.append(f"[TracingTail] {self.debug_name}: {message}")

    def _preallocate_buffers(self, max_length: int) -> None:
        """预分配所有缓冲区，避免频繁内存分配"""
        buffer_size = max(max_length * 2, 100)  # 预留足够空间
        self._line_points_cache = np.zeros((buffer_size, 3), dtype=np.float32)
        self._progress_cache = np.zeros(buffer_size, dtype=np.float32)
        self._width_cache = np.zeros(buffer_size, dtype=np.float32)
        self._opacity_cache = np.zeros(buffer_size, dtype=np.float32)
        self._glow_cache = np.zeros(buffer_size, dtype=np.float32)
        self._rgba_cache = np.zeros((buffer_size, 4), dtype=np.float32)
        self._prev_dir_cache = np.zeros((buffer_size, 3), dtype=np.float32)
        self._next_dir_cache = np.zeros((buffer_size, 3), dtype=np.float32)
        self._points_temp = np.zeros((max_length, 3), dtype=np.float32)
        self._times_temp = np.zeros(max_length, dtype=np.float32)

    def _reset_distance_history_from_array(self, points: np.ndarray) -> None:
        """根据当前轨迹点重建步长历史。"""
        self._recent_distances.clear()
        if len(points) < 2:
            return
        diffs = np.linalg.norm(np.diff(points, axis=0), axis=1)
        if diffs.size == 0:
            return
        limit = self._distance_history_limit
        for value in diffs[-limit:]:
            if np.isfinite(value):
                self._recent_distances.append(float(value))

    def _register_step_distance(self, distance: float) -> None:
        if distance >= 1e-6:
            self._recent_distances.append(float(distance))

    def _current_jump_threshold(self) -> float:
        return _compute_dynamic_jump_threshold(
            self._recent_distances,
            fallback=self._teleport_fallback,
            min_threshold=self._teleport_min_threshold,
        )

    def init_uniforms(self) -> None:
        super().init_uniforms()
        self.uniforms["glow_factor"] = self.glow_factor
        self.uniforms["anti_alias_width"] = self.anti_alias_width
        self.uniforms["tail_lifetime"] = self.tail_lifetime

    def _init_empty_tail(self) -> None:
        """初始化空的轨迹数据"""
        # 创建两个几乎相同的点，避免首尾相连问题
        initial_point = self.traced_point_func()
        # 第二个点稍微偏移一点，避免完全重合
        second_point = initial_point + np.array([0.0001, 0.0001, 0])

        self._bootstrap_pending = True
        self._recent_distances.clear()
        self.tail_points.append(initial_point)
        self.tail_points.append(second_point)
        self.tail_times.append(0.0)
        self.tail_times.append(0.001)  # 极小的时间差
        self._register_step_distance(float(np.linalg.norm(second_point - initial_point)))
        self._update_tail_data()
        self._log("init empty tail")

    def update_tail(self, dt: float) -> Self:
        """更新轨迹数据 - 参考TracedPath的逻辑优化"""
        if dt == 0:
            self._log("dt==0 skip")
            return self
            
        self.current_time += dt
        
        # 获取新的追踪点
        try:
            new_point = self.traced_point_func().copy()
        except:
            self._log("traced_point_func failed")
            return self
        
        # 检查新点是否有效（避免 NaN 或 Inf）
        if not np.all(np.isfinite(new_point)):
            self._log("new point invalid")
            return self
        new_point = np.array(new_point, dtype=np.float32)
        
        history_rebuild_required = False

        last_point_before_append = None

        # 检查是否与最后一个点距离过大（防止首尾相连）
        if len(self.tail_points) > 0:
            last_point_before_append = self.tail_points[-1]
            distance = float(np.linalg.norm(new_point - last_point_before_append))
            threshold = self._current_jump_threshold()
            self._log(f"distance={distance:.4f}, threshold={threshold:.4f}, len={len(self.tail_points)}")
            if distance > threshold:
                self._log("distance exceeds threshold, reset tail")
                self.tail_points.clear()
                self.tail_times.clear()
                self._recent_distances.clear()
                self._recent_distances.append(distance)
                self.tail_points.append(new_point)
                self.tail_times.append(self.current_time)
                self._update_tail_data()
                self._bootstrap_pending = False
                return self
            self._register_step_distance(distance)
        
        # 始终添加新点
        self.tail_points.append(new_point)
        self.tail_times.append(self.current_time)

        if self._bootstrap_pending and last_point_before_append is not None:
            direction = new_point - last_point_before_append
            norm = float(np.linalg.norm(direction))
            if norm < 1e-7:
                direction_unit = np.array([1.0, 0.0, 0.0], dtype=np.float32)
                offset_length = 1e-4
            else:
                direction_unit = (direction / norm).astype(np.float32)
                offset_length = np.clip(norm * 0.25, 1e-4, 5e-2)

            prev_point = (new_point - direction_unit * offset_length).astype(np.float32)
            prev_time = max(self.current_time - max(dt, 1e-3), 0.0)

            self.tail_points.clear()
            self.tail_times.clear()
            self.tail_points.append(prev_point)
            self.tail_points.append(new_point)
            self.tail_times.append(prev_time)
            self.tail_times.append(self.current_time)

            self._recent_distances.clear()
            self._register_step_distance(float(np.linalg.norm(new_point - prev_point)))
            self._bootstrap_pending = False
            self._update_tail_data()
            self._log("bootstrap resolved")
            return self
        
        # 基于时间和最大长度管理点的数量
        if self.tail_lifetime < np.inf:
            # 计算相关点的数量
            n_relevant_points = max(2, int(self.tail_lifetime / (dt + 1e-8)))
            n_current_points = len(self.tail_points)
            
            if n_current_points > n_relevant_points:
                # 如果点太多，保留最新的点
                excess_points = n_current_points - n_relevant_points
                for _ in range(excess_points):
                    if len(self.tail_points) > 2:  # 至少保留2个点
                        self.tail_points.popleft()
                        self.tail_times.popleft()
                        history_rebuild_required = True
                if excess_points > 0:
                    self._log(f"trimmed {excess_points} points for lifetime")
            
            # 定期清理
            if n_current_points > 10 * n_relevant_points:
                # 保留最新的相关点
                points_to_keep = list(self.tail_points)[-n_relevant_points:]
                times_to_keep = list(self.tail_times)[-n_relevant_points:]
                self.tail_points.clear()
                self.tail_times.clear()
                self.tail_points.extend(points_to_keep)
                self.tail_times.extend(times_to_keep)
                history_rebuild_required = True
                self._log("mass trim applied")
        
        # 移除过老的点（基于时间的额外清理）
        while (len(self.tail_times) > 2 and 
               self.current_time - self.tail_times[0] > self.tail_lifetime):
            self.tail_points.popleft()
            self.tail_times.popleft()
            history_rebuild_required = True
            self._log("removed expired point")

        if history_rebuild_required:
            if len(self.tail_points) >= 2:
                points_snapshot = np.array(list(self.tail_points), dtype=np.float32)
                self._reset_distance_history_from_array(points_snapshot)
            else:
                self._recent_distances.clear()
            self._log("rebuilt distance history")
        
        # 更新渲染数据
        self._update_tail_data()
        self._log(f"update complete, len={len(self.tail_points)}")
        return self

    def _update_tail_data(self) -> None:
        """更新轨迹的渲染数据 - 完全向量化优化版本"""
        if len(self.tail_points) < 2:
            # 如果点不够，创建最小数据
            points = np.array([self.tail_points[0], self.tail_points[0] + np.array([0.001, 0, 0])]) if len(self.tail_points) == 1 else np.array([ORIGIN, ORIGIN + np.array([0.001, 0, 0])])
            self.set_points(points)
            self._bootstrap_pending = True
            self._recent_distances.clear()
            self._recent_distances.append(1e-4)
            
            if self.has_points():
                n_points = len(points)
                self.data['tail_progress'][:, 0] = np.zeros(n_points)
                self.data['tail_width'][:, 0] = np.full(n_points, 0.001)
                self.data['glow_intensity'][:, 0] = np.zeros(n_points)
                # 批量设置透明颜色
                base_color_rgba = color_to_rgba(self.base_color)
                base_rgba = np.array([base_color_rgba[0], base_color_rgba[1], base_color_rgba[2], 0.0])
                self.data['rgba'][:] = np.tile(base_rgba, (n_points, 1))
                zero_dirs = np.zeros((n_points, 3), dtype=np.float32)
                self.data['prev_dir'][:] = zero_dirs
                self.data['next_dir'][:] = zero_dirs
            return

        # 转换为numpy数组（复用缓冲区）
        n_points = len(self.tail_points)
        points_view = self._points_temp[:n_points]
        times_view = self._times_temp[:n_points]
        
        for i, (pt, tm) in enumerate(zip(self.tail_points, self.tail_times)):
            points_view[i] = pt
            times_view[i] = tm
        
        points = points_view.copy()  # 复制避免引用问题
        times = times_view.copy()
        
        # 检测并修复首尾相连问题（强化版）
        points, times, trimmed = self._detect_and_fix_wraparound(points, times)
        if trimmed:
            self.tail_points = deque(list(points), maxlen=self.max_tail_length)
            self.tail_times = deque(list(times), maxlen=self.max_tail_length)
            self._reset_distance_history_from_array(points)
            if len(points) < 2:
                self._recent_distances.clear()
                return
        
        # 再次检查是否有异常大的跳跃
        if len(points) >= 2:
            distances = np.linalg.norm(np.diff(points, axis=0), axis=1)
            max_dist = np.max(distances)
            median_dist = np.median(distances)
            
            # 如果最大距离是中位数的100倍以上，认为有问题
            if max_dist > median_dist * 100 and max_dist > 10.0:
                # 找到异常跳跃的位置
                anomaly_idx = np.argmax(distances)
                # 只保留异常点之后的部分
                points = points[anomaly_idx + 1:]
                times = times[anomaly_idx + 1:]
                self.tail_points = deque(list(points), maxlen=self.max_tail_length)
                self.tail_times = deque(list(times), maxlen=self.max_tail_length)
                self._reset_distance_history_from_array(points)
                if len(points) < 2:
                    self._recent_distances.clear()
                    return
        
        # 轨迹平滑处理（使用简化的高斯平滑）
        if len(points) >= 3:
            points = self._fast_smooth_trajectory(points)
        
        # 向量化计算年龄和进度
        ages = self.current_time - times
        progress = np.clip(ages / self.tail_lifetime, 0.0, 1.0)
        
        n_segments = len(points) - 1
        if n_segments <= 0:
            return
        
        # 预计算相邻方向（完全向量化）
        prev_dirs_points, next_dirs_points = _compute_neighbor_directions(points)

        # === 完全向量化的线段构建（零 Python 循环）===
        n_verts = n_segments * 2
        
        # 复用缓冲区
        line_points = self._line_points_cache[:n_verts]
        prev_dir_data = self._prev_dir_cache[:n_verts]
        next_dir_data = self._next_dir_cache[:n_verts]
        progress_data = self._progress_cache[:n_verts]
        width_data = self._width_cache[:n_verts]
        opacity_data = self._opacity_cache[:n_verts]
        glow_data = self._glow_cache[:n_verts]
        
        # 使用高级索引一次性构建所有数据（零循环）
        line_points[0::2] = points[:-1]  # 所有起点
        line_points[1::2] = points[1:]   # 所有终点
        
        prev_dir_data[0::2] = prev_dirs_points[:-1]
        prev_dir_data[1::2] = prev_dirs_points[1:]
        next_dir_data[0::2] = next_dirs_points[:-1]
        next_dir_data[1::2] = next_dirs_points[1:]
        
        progress_data[0::2] = progress[:-1]
        progress_data[1::2] = progress[1:]
        
        # 向量化计算属性
        width_start, width_end = self.width_fade
        opacity_start, opacity_end = self.opacity_fade
        
        width_data[0::2] = width_start + (width_end - width_start) * progress[:-1]
        width_data[1::2] = width_start + (width_end - width_start) * progress[1:]
        
        opacity_data[0::2] = opacity_start + (opacity_end - opacity_start) * progress[:-1]
        opacity_data[1::2] = opacity_start + (opacity_end - opacity_start) * progress[1:]
        
        glow_data[0::2] = self.glow_factor * (1.0 - progress[:-1] * 0.7)
        glow_data[1::2] = self.glow_factor * (1.0 - progress[1:] * 0.7)
        
        # 设置点数据
        self.set_points(line_points.copy())
        
        if self.has_points():
            self.data['tail_progress'][:, 0] = progress_data
            self.data['tail_width'][:, 0] = width_data
            self.data['glow_intensity'][:, 0] = glow_data
            self.data['prev_dir'][:] = prev_dir_data
            self.data['next_dir'][:] = next_dir_data
            
            # 向量化设置颜色
            base_color_rgba = color_to_rgba(self.base_color)
            base_rgb = np.array([base_color_rgba[0], base_color_rgba[1], base_color_rgba[2]])
            rgba_colors = self._rgba_cache[:n_verts]
            rgba_colors[:, :3] = base_rgb
            rgba_colors[:, 3] = opacity_data
            self.data['rgba'][:] = rgba_colors

    def _fast_smooth_trajectory(self, points: np.ndarray) -> np.ndarray:
        """
        快速轨迹平滑 - 使用简化的高斯平滑
        性能优化：单次卷积操作，避免复杂的贝塞尔计算
        """
        if len(points) < 3:
            return points
        
        # 简单快速的3点移动平均（等效于高斯核）
        smoothed = points.copy()
        smoothed[1:-1] = 0.25 * points[:-2] + 0.5 * points[1:-1] + 0.25 * points[2:]
        
        # 可选：第二次平滑（更平滑的结果）
        if len(smoothed) >= 3:
            result = smoothed.copy()
            result[1:-1] = 0.25 * smoothed[:-2] + 0.5 * smoothed[1:-1] + 0.25 * smoothed[2:]
            return result
        
        return smoothed

    def _smooth_trajectory_points(self, points: np.ndarray, smoothing_mode: str = "approx_smooth") -> np.ndarray:
        """
        平滑轨迹点 - 已弃用，使用 _fast_smooth_trajectory 替代
        保留此方法以保持向后兼容性
        """
        return self._fast_smooth_trajectory(points)

    def _detect_and_fix_wraparound(self, points: np.ndarray, times: np.ndarray) -> Tuple[np.ndarray, np.ndarray, bool]:
        """检测并切断轨迹中的异常长距离连接。"""
        if len(points) < 3:
            return points, times, False

        pruned_points, pruned_times, trimmed = _prune_large_gaps(points, times)
        return pruned_points, pruned_times, trimmed

    def set_traced_point_func(self, func: Callable[[], Vect3]) -> Self:
        """设置新的追踪点函数"""
        self.traced_point_func = func
        return self

    def clear_tail(self) -> Self:
        """清空轨迹历史"""
        self.tail_points.clear()
        self.tail_times.clear()
        self.current_time = 0.0
        self._recent_distances.clear()
        self._init_empty_tail()
        return self

    def set_tail_lifetime(self, lifetime: float) -> Self:
        """设置轨迹生命周期"""
        self.tail_lifetime = lifetime
        self.uniforms["tail_lifetime"] = lifetime
        return self

    def set_glow_factor(self, factor: float) -> Self:
        """设置辉光强度"""
        self.glow_factor = factor
        self.uniforms["glow_factor"] = factor
        return self

    def set_smoothing_mode(self, mode: str) -> Self:
        """
        设置轨迹平滑模式
        
        参数:
        - mode: "jagged" | "approx_smooth" | "true_smooth"
            - "jagged": 简单快速的中点平滑
            - "approx_smooth": 使用 ManimGL 的近似贝塞尔平滑（推荐）
            - "true_smooth": 使用完整的贝塞尔平滑路径（最高质量）
        """
        valid_modes = ["jagged", "approx_smooth", "true_smooth"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid smoothing mode '{mode}'. Must be one of {valid_modes}")
        
        self.smoothing_mode = mode
        return self


class MultiTracingTails(PMobject):
    """
    多轨迹尾迹管理器
    
    高效管理多个轨迹尾迹，支持批量更新和渲染。
    用于大量粒子系统的轨迹追踪。
    """
    
    shader_folder: str = str(Path(Path(__file__).parent.parent, "tracing_tail_glow_shader"))
    render_primitive: int = moderngl.LINES
    _VALID_SMOOTHING_MODES: Tuple[str, ...] = ("jagged", "approx_smooth", "true_smooth")
    
    # 数据类型定义（与单个轨迹相同）
    data_dtype: Sequence[Tuple[str, type, Tuple[int]]] = [
        ('point', np.float32, (3,)),
        ('rgba', np.float32, (4,)),
        ('tail_progress', np.float32, (1,)),
        ('tail_width', np.float32, (1,)),
        ('glow_intensity', np.float32, (1,)),
        ('prev_dir', np.float32, (3,)),
        ('next_dir', np.float32, (3,)),
    ]

    def __init__(
        self,
        traced_functions: Sequence[Callable[[], Vect3]],
        colors: Optional[Sequence[ManimColor]] = None,
        max_tail_length: int = 100,
        tail_lifetime: float = 2.0,
        opacity_fade: Tuple[float, float] = (1.0, 0.0),
        width_fade: Tuple[float, float] = (0.04, 0.01),
        glow_factor: float = 2.0,
        smoothing_mode: str = "jagged",
        resample_factor: float = 2.0,
        max_resample_points: int = 600,
        anti_alias_width: float = 0.05,
        teleport_fallback: float | None = None,
        teleport_min_threshold: float = 0.6,
        teleport_history: int = 64,
        **kwargs
    ):
        self.traced_functions = traced_functions
        self.n_tails = len(traced_functions)
        self.max_tail_length = max_tail_length
        self._validate_smoothing_mode(smoothing_mode)
        self.smoothing_mode = smoothing_mode
        self.resample_factor = max(1.0, float(resample_factor))
        self.max_resample_points = max(10, int(max_resample_points))
        self.anti_alias_width = float(anti_alias_width)
        self._tail_length_multiplier = 1.5 if self.smoothing_mode != "jagged" else 1.0
        self._history_capacity = max_tail_length if self._tail_length_multiplier == 1.0 else int(max_tail_length * self._tail_length_multiplier)
        self.base_tail_lifetime = tail_lifetime
        self.tail_lifetime = tail_lifetime * self._tail_length_multiplier
        self.opacity_fade = opacity_fade
        self.width_fade = width_fade
        self.glow_factor = glow_factor
        self._teleport_fallback = teleport_fallback if teleport_fallback is not None else 3.0
        self._teleport_min_threshold = max(teleport_min_threshold, 0.1)
        self._distance_history_limit = max(8, int(teleport_history))
        
        # 为每个轨迹分配颜色
        if colors is None:
            # 使用彩虹色
            colors = [np.array([1.0, 0.5, 0.2]) for _ in range(self.n_tails)]
        self.colors = colors
        
        # 轨迹历史存储（每个轨迹独立）
        self.tail_histories = [deque(maxlen=self._history_capacity) for _ in range(self.n_tails)]
        self.tail_time_histories = [deque(maxlen=self._history_capacity) for _ in range(self.n_tails)]
        self._distance_histories = [deque(maxlen=self._distance_history_limit) for _ in range(self.n_tails)]
        self._bootstrap_flags = [True for _ in range(self.n_tails)]
        self.current_time = 0.0

        # 预分配 GPU 侧缓冲区容量
        base_capacity = max(2, self.n_tails * max(2, self._history_capacity - 1) * 2)
        self._allocate_gpu_cache(base_capacity)

        super().__init__(**kwargs)
        self._init_all_tails()

    def _allocate_gpu_cache(self, capacity: int) -> None:
        """预分配并缓存 GPU 顶点及属性缓冲，避免频繁重建。"""
        self._vertex_capacity = max(2, capacity)
        self._line_points_buffer = np.zeros((self._vertex_capacity, 3), dtype=np.float32)
        self._progress_buffer = np.zeros(self._vertex_capacity, dtype=np.float32)
        self._width_buffer = np.zeros(self._vertex_capacity, dtype=np.float32)
        self._opacity_buffer = np.zeros(self._vertex_capacity, dtype=np.float32)
        self._glow_buffer = np.zeros(self._vertex_capacity, dtype=np.float32)
        self._color_buffer = np.zeros((self._vertex_capacity, 3), dtype=np.float32)
        self._prev_dir_buffer = np.zeros((self._vertex_capacity, 3), dtype=np.float32)
        self._next_dir_buffer = np.zeros((self._vertex_capacity, 3), dtype=np.float32)
        self._rgba_cache = np.zeros((self._vertex_capacity, 4), dtype=np.float32)

    def _ensure_gpu_capacity(self, required_vertices: int) -> None:
        if required_vertices <= self._vertex_capacity:
            return
        new_capacity = max(required_vertices, self._vertex_capacity * 2)
        self._allocate_gpu_cache(new_capacity)

    def _validate_smoothing_mode(self, mode: str) -> None:
        if mode not in self._VALID_SMOOTHING_MODES:
            raise ValueError(
                f"Invalid smoothing mode '{mode}'. Must be one of {self._VALID_SMOOTHING_MODES}"
            )

    def _reset_distance_history_for_tail(self, tail_idx: int, points_arr: np.ndarray | None = None) -> None:
        history = self._distance_histories[tail_idx]
        history.clear()

        if points_arr is None:
            if len(self.tail_histories[tail_idx]) < 2:
                return
            points_arr = np.array(list(self.tail_histories[tail_idx]), dtype=np.float32)

        if len(points_arr) < 2:
            return

        diffs = np.linalg.norm(np.diff(points_arr, axis=0), axis=1)
        if diffs.size == 0:
            return

        limit = self._distance_history_limit
        for value in diffs[-limit:]:
            if np.isfinite(value):
                history.append(float(value))

    def _current_jump_threshold_for_tail(self, tail_idx: int) -> float:
        return _compute_dynamic_jump_threshold(
            self._distance_histories[tail_idx],
            fallback=self._teleport_fallback,
            min_threshold=self._teleport_min_threshold,
        )

    def _register_tail_step_distance(self, tail_idx: int, distance: float) -> None:
        if distance >= 1e-6:
            self._distance_histories[tail_idx].append(float(distance))

    def init_uniforms(self) -> None:
        super().init_uniforms()
        self.uniforms["glow_factor"] = self.glow_factor
        self.uniforms["anti_alias_width"] = self.anti_alias_width
        self.uniforms["tail_lifetime"] = self.tail_lifetime

    def _init_all_tails(self) -> None:
        """初始化所有轨迹"""
        for i in range(self.n_tails):
            try:
                initial_point = self.traced_functions[i]()
                self.tail_histories[i].append(initial_point)
                self.tail_time_histories[i].append(0.0)
            except:
                # 如果函数调用失败，使用原点
                self.tail_histories[i].append(ORIGIN)
                self.tail_time_histories[i].append(0.0)
            self._distance_histories[i].clear()
            self._distance_histories[i].append(1e-4)
        
        self._update_all_tail_data()

    def update_all_tails(self, dt: float) -> Self:
        """批量更新所有轨迹 - 优化版本，参考TracedPath逻辑"""
        if dt == 0:
            return self
            
        self.current_time += dt
        history_rebuild_flags = [False] * self.n_tails
        
        # 批量获取所有新点（减少异常处理开销）
        new_points = []
        for i in range(self.n_tails):
            try:
                new_point = self.traced_functions[i]().copy()
                # 检查点是否有效
                if not np.all(np.isfinite(new_point)):
                    new_points.append(None)
                else:
                    new_points.append(np.array(new_point, dtype=np.float32))
            except:
                new_points.append(None)
        
        # 批量更新所有轨迹
        for i, new_point in enumerate(new_points):
            if new_point is None:
                continue
            
            distance_history = self._distance_histories[i]
            last_point_before_append = self.tail_histories[i][-1] if len(self.tail_histories[i]) > 0 else None

            # 检查是否与最后一个点距离过大（防止首尾相连）
            if last_point_before_append is not None:
                distance = float(np.linalg.norm(new_point - last_point_before_append))
                threshold = self._current_jump_threshold_for_tail(i)
                # 如果距离超过阈值，清空历史重新开始
                if distance > threshold:
                    self.tail_histories[i].clear()
                    self.tail_time_histories[i].clear()
                    distance_history.clear()
                    distance_history.append(distance)
                    self.tail_histories[i].append(new_point)
                    self.tail_time_histories[i].append(self.current_time)
                    self._bootstrap_flags[i] = False
                    continue
                self._register_tail_step_distance(i, distance)

            # 始终添加新点（参考TracedPath逻辑）
            self.tail_histories[i].append(new_point)
            self.tail_time_histories[i].append(self.current_time)

            if self._bootstrap_flags[i] and last_point_before_append is not None:
                direction = new_point - last_point_before_append
                norm = float(np.linalg.norm(direction))
                if norm < 1e-7:
                    direction_unit = np.array([1.0, 0.0, 0.0], dtype=np.float32)
                    offset_length = 1e-4
                else:
                    direction_unit = (direction / norm).astype(np.float32)
                    offset_length = np.clip(norm * 0.25, 1e-4, 5e-2)

                prev_point = (new_point - direction_unit * offset_length).astype(np.float32)
                prev_time = max(self.current_time - max(dt, 1e-3), 0.0)

                self.tail_histories[i].clear()
                self.tail_time_histories[i].clear()
                self.tail_histories[i].append(prev_point)
                self.tail_histories[i].append(new_point)
                self.tail_time_histories[i].append(prev_time)
                self.tail_time_histories[i].append(self.current_time)

                distance_history.clear()
                distance_history.append(float(np.linalg.norm(new_point - prev_point)))
                self._bootstrap_flags[i] = False
                continue
            
            # 基于时间和最大长度管理点（参考TracedPath逻辑）
            if self.tail_lifetime < np.inf:
                n_relevant_points = max(2, int(self.tail_lifetime / (dt + 1e-8)))
                n_current_points = len(self.tail_histories[i])
                
                if n_current_points > n_relevant_points:
                    # 移除多余的旧点
                    excess_points = n_current_points - n_relevant_points
                    for _ in range(excess_points):
                        if len(self.tail_histories[i]) > 2:
                            self.tail_histories[i].popleft()
                            self.tail_time_histories[i].popleft()
                            history_rebuild_flags[i] = True
                
                # 定期清理
                if n_current_points > 10 * n_relevant_points:
                    points_to_keep = list(self.tail_histories[i])[-n_relevant_points:]
                    times_to_keep = list(self.tail_time_histories[i])[-n_relevant_points:]
                    self.tail_histories[i].clear()
                    self.tail_time_histories[i].clear()
                    self.tail_histories[i].extend(points_to_keep)
                    self.tail_time_histories[i].extend(times_to_keep)
                    history_rebuild_flags[i] = True
            
            # 额外的时间基础清理
            while (len(self.tail_time_histories[i]) > 2 and 
                   self.current_time - self.tail_time_histories[i][0] > self.tail_lifetime):
                self.tail_histories[i].popleft()
                self.tail_time_histories[i].popleft()
                history_rebuild_flags[i] = True

            if len(self.tail_histories[i]) < 2:
                self._bootstrap_flags[i] = True

        for idx, need_rebuild in enumerate(history_rebuild_flags):
            if need_rebuild:
                self._reset_distance_history_for_tail(idx)
        
        # 批量更新渲染数据
        self._update_all_tail_data()
        return self

    def _update_all_tail_data(self) -> None:
        """批量更新所有轨迹的渲染数据 - 超级优化版本，最小化内存分配和循环"""
        # 第一阶段：快速验证和数据收集（最小化临时对象）
        n_valid = 0
        for tail_idx in range(self.n_tails):
            if len(self.tail_histories[tail_idx]) >= 2:
                n_valid += 1
        
        if n_valid == 0:
            # 创建最小数据
            self.set_points(np.array([ORIGIN, ORIGIN + np.array([0.001, 0, 0])]))
            if self.has_points():
                n_points = 2
                self.data['tail_progress'][:, 0] = np.zeros(n_points)
                self.data['tail_width'][:, 0] = np.full(n_points, 0.001)
                self.data['glow_intensity'][:, 0] = np.zeros(n_points)
                self.data['rgba'][:] = np.tile([1, 1, 1, 0], (n_points, 1))
                zero_dirs = np.zeros((n_points, 3), dtype=np.float32)
                self.data['prev_dir'][:] = zero_dirs
                self.data['next_dir'][:] = zero_dirs
            return
        
        # 第二阶段：预估总顶点数并确保容量
        estimated_verts = n_valid * self._history_capacity * 2
        self._ensure_gpu_capacity(estimated_verts)
        
        # 第三阶段：使用预分配缓冲区直接写入数据（零额外分配）
        point_idx = 0
        width_start, width_end = self.width_fade
        opacity_start, opacity_end = self.opacity_fade
        
        for tail_idx in range(self.n_tails):
            points_deque = self.tail_histories[tail_idx]
            times_deque = self.tail_time_histories[tail_idx]
            
            if len(points_deque) < 2:
                continue
            
            # 转换为数组（直接写入视图，避免临时数组）
            n_pts = len(points_deque)
            points_arr = np.array(list(points_deque), dtype=np.float32)
            times_arr = np.array(list(times_deque), dtype=np.float32)
            
            # 快速异常检测和修复
            points_arr, times_arr, trimmed = _prune_large_gaps(points_arr, times_arr)
            if trimmed:
                self.tail_histories[tail_idx] = deque(list(points_arr), maxlen=self._history_capacity)
                self.tail_time_histories[tail_idx] = deque(list(times_arr), maxlen=self._history_capacity)
                self._reset_distance_history_for_tail(tail_idx, points_arr)
            
            if len(points_arr) < 2:
                self._distance_histories[tail_idx].clear()
                self._distance_histories[tail_idx].append(1e-4)
                self._bootstrap_flags[tail_idx] = True
                continue
            
            # 再次检查异常跳跃
            if len(points_arr) >= 2:
                distances = np.linalg.norm(np.diff(points_arr, axis=0), axis=1)
                if len(distances) > 0:
                    max_dist = np.max(distances)
                    median_dist = np.median(distances) if len(distances) > 1 else max_dist
                    
                    # 如果最大距离异常大，移除异常部分
                    if max_dist > median_dist * 100 and max_dist > 10.0:
                        anomaly_idx = np.argmax(distances)
                        points_arr = points_arr[anomaly_idx + 1:]
                        times_arr = times_arr[anomaly_idx + 1:]
                        self.tail_histories[tail_idx] = deque(list(points_arr), maxlen=self._history_capacity)
                        self.tail_time_histories[tail_idx] = deque(list(times_arr), maxlen=self._history_capacity)
                        self._reset_distance_history_for_tail(tail_idx, points_arr)
                        if len(points_arr) < 2:
                            self._distance_histories[tail_idx].clear()
                            self._bootstrap_flags[tail_idx] = True
                            continue
            
            if len(points_arr) >= 3:
                points_arr = self._apply_smoothing_pipeline(points_arr)
                times_arr = np.linspace(times_arr[0], times_arr[-1], len(points_arr)).astype(np.float32)

            # 向量化计算进度和方向
            ages = self.current_time - times_arr
            progress = np.clip(ages / self.tail_lifetime, 0.0, 1.0)
            prev_dirs, next_dirs = _compute_neighbor_directions(points_arr)
            
            # 获取颜色（处理不同的颜色格式）
            if tail_idx < len(self.colors):
                tail_color = self.colors[tail_idx]
                # 如果已经是 numpy 数组（RGB格式），直接使用
                if isinstance(tail_color, np.ndarray):
                    if len(tail_color) == 3:
                        color_rgb = tail_color.astype(np.float32)
                    elif len(tail_color) == 4:
                        color_rgb = tail_color[:3].astype(np.float32)
                    else:
                        color_rgb = np.array([1.0, 1.0, 1.0], dtype=np.float32)
                else:
                    # 使用 color_to_rgba 转换
                    color_rgba = color_to_rgba(tail_color)
                    color_rgb = np.array([color_rgba[0], color_rgba[1], color_rgba[2]], dtype=np.float32)
            else:
                # 默认白色
                color_rgb = np.array([1.0, 1.0, 1.0], dtype=np.float32)
            
            # 构建线段（完全向量化，直接写入缓冲区）
            n_segments = len(points_arr) - 1
            n_verts = n_segments * 2
            end_idx = point_idx + n_verts
            
            # 直接使用切片和步进索引（零循环）
            self._line_points_buffer[point_idx:end_idx:2] = points_arr[:-1]
            self._line_points_buffer[point_idx+1:end_idx:2] = points_arr[1:]
            
            self._prev_dir_buffer[point_idx:end_idx:2] = prev_dirs[:-1]
            self._prev_dir_buffer[point_idx+1:end_idx:2] = prev_dirs[1:]
            self._next_dir_buffer[point_idx:end_idx:2] = next_dirs[:-1]
            self._next_dir_buffer[point_idx+1:end_idx:2] = next_dirs[1:]
            
            # 向量化属性计算（单次广播操作）
            prog_view = self._progress_buffer[point_idx:end_idx]
            prog_view[0::2] = progress[:-1]
            prog_view[1::2] = progress[1:]
            
            width_view = self._width_buffer[point_idx:end_idx]
            width_view[:] = width_start + (width_end - width_start) * prog_view
            
            opacity_view = self._opacity_buffer[point_idx:end_idx]
            opacity_view[:] = opacity_start + (opacity_end - opacity_start) * prog_view
            
            glow_view = self._glow_buffer[point_idx:end_idx]
            glow_view[:] = self.glow_factor * (1.0 - prog_view * 0.5)
            
            color_view = self._color_buffer[point_idx:end_idx]
            color_view[:] = color_rgb
            
            point_idx = end_idx
        
        # 第四阶段：批量设置所有数据（单次 GPU 上传）
        if point_idx == 0:
            return
        
        active_slice = slice(0, point_idx)
        self.set_points(self._line_points_buffer[active_slice].copy())
        
        if self.has_points():
            self.data['tail_progress'][:, 0] = self._progress_buffer[active_slice]
            self.data['tail_width'][:, 0] = self._width_buffer[active_slice]
            self.data['glow_intensity'][:, 0] = self._glow_buffer[active_slice]
            self.data['prev_dir'][:] = self._prev_dir_buffer[active_slice]
            self.data['next_dir'][:] = self._next_dir_buffer[active_slice]
            
            # 组合 RGBA（原地操作）
            rgba_view = self._rgba_cache[:point_idx]
            rgba_view[:, :3] = self._color_buffer[active_slice]
            rgba_view[:, 3] = self._opacity_buffer[active_slice]
            self.data['rgba'][:] = rgba_view

    def _apply_smoothing_pipeline(self, points: np.ndarray) -> np.ndarray:
        if len(points) < 3:
            return points

        work_points = np.asarray(points, dtype=np.float32)
        if self.smoothing_mode == "jagged":
            return self._fast_average(work_points)

        target_len = int(min(
            self.max_resample_points,
            max(len(work_points), math.ceil(len(work_points) * self.resample_factor))
        ))
        if target_len > len(work_points):
            work_points = self._resample_points_uniform(work_points, target_len)

        work_points = self._fast_average(work_points)

        try:
            handles = approx_smooth_quadratic_bezier_handles(work_points)
            smoothed = smooth_quadratic_path(work_points, handles=handles)
            if self.smoothing_mode == "true_smooth" and len(smoothed) >= 3:
                secondary_handles = approx_smooth_quadratic_bezier_handles(smoothed)
                smoothed = smooth_quadratic_path(smoothed, handles=secondary_handles)
            work_points = np.asarray(smoothed, dtype=np.float32)
        except Exception:
            # 如果贝塞尔平滑失败，回退到快速平滑
            work_points = self._fast_average(work_points)

        return work_points

    def _resample_points_uniform(self, points: np.ndarray, desired_len: int) -> np.ndarray:
        if desired_len <= len(points) or len(points) < 2:
            return points

        diffs = np.linalg.norm(np.diff(points, axis=0), axis=1)
        total = float(np.sum(diffs))
        if total < 1e-6:
            return points

        cumulative = np.concatenate(([0.0], np.cumsum(diffs)))
        targets = np.linspace(0.0, total, desired_len)
        resampled = np.zeros((desired_len, 3), dtype=np.float32)
        for axis in range(3):
            resampled[:, axis] = np.interp(targets, cumulative, points[:, axis])
        return resampled

    def _fast_average(self, points: np.ndarray) -> np.ndarray:
        if len(points) < 3:
            return points
        smoothed = points.copy()
        smoothed[1:-1] = 0.25 * points[:-2] + 0.5 * points[1:-1] + 0.25 * points[2:]
        if len(smoothed) >= 3:
            second = smoothed.copy()
            second[1:-1] = 0.25 * smoothed[:-2] + 0.5 * smoothed[1:-1] + 0.25 * smoothed[2:]
            smoothed = second
        return smoothed

    def _resize_tail_histories(self) -> None:
        for idx in range(self.n_tails):
            points_snapshot = list(self.tail_histories[idx])[-self._history_capacity:]
            times_snapshot = list(self.tail_time_histories[idx])[-self._history_capacity:]
            self.tail_histories[idx] = deque(points_snapshot, maxlen=self._history_capacity)
            self.tail_time_histories[idx] = deque(times_snapshot, maxlen=self._history_capacity)
        new_capacity = max(2, self.n_tails * max(2, self._history_capacity - 1) * 2)
        self._allocate_gpu_cache(new_capacity)

    def set_tail_lifetime(self, lifetime: float) -> Self:
        self.base_tail_lifetime = lifetime
        self.tail_lifetime = lifetime * self._tail_length_multiplier
        self.uniforms["tail_lifetime"] = self.tail_lifetime
        return self

    def set_anti_alias_width(self, width: float) -> Self:
        self.anti_alias_width = float(width)
        self.uniforms["anti_alias_width"] = self.anti_alias_width
        return self

    def set_smoothing_mode(self, mode: str) -> Self:
        self._validate_smoothing_mode(mode)
        if mode == self.smoothing_mode:
            return self
        self.smoothing_mode = mode
        self._tail_length_multiplier = 1.5 if mode != "jagged" else 1.0
        self.tail_lifetime = self.base_tail_lifetime * self._tail_length_multiplier
        self.uniforms["tail_lifetime"] = self.tail_lifetime
        new_capacity = self.max_tail_length if self._tail_length_multiplier == 1.0 else int(self.max_tail_length * self._tail_length_multiplier)
        if new_capacity != self._history_capacity:
            self._history_capacity = new_capacity
            self._resize_tail_histories()
        return self
