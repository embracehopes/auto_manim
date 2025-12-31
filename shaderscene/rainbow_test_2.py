"""电影级七彩尾迹测试场景.

此脚本展示如何使用 Taichi + ManimGL + 自定义 Glow TracingTail 实现
GPU 加速的 3D 轨迹系统，同时提供可调试的电影级彩虹调色盘。
"""

import os
import sys
import time
from typing import Iterable, Sequence

import numpy as np
import taichi as ti
from manimlib import *  # noqa: F401,F403 - 按照项目习惯导入全部
from manimlib.utils.color import color_to_rgb

sys.path.insert(0, os.path.dirname(__file__))
from mobject.TracingTailPMobject import *  # noqa: E402,F401


class _BufferTracer:
    __slots__ = ("buffer", "index")

    def __init__(self, buffer: np.ndarray, index: int):
        self.buffer = buffer
        self.index = index

    def __call__(self) -> np.ndarray:
        return self.buffer[self.index]

# ---------------------------------------------------------------------------
# Taichi & 全局参数
# ---------------------------------------------------------------------------

ti.init(arch=ti.gpu)  # GPU 加速

n_curves = 180
n_dots = 5
total_points = n_curves * n_dots

# 单个 Taichi block 的默认线程配置（根据 GPU SM 情况可再调）
BLOCK_DIM = 256

# 外部共享缓冲类型定义
NdArray3f = ti.types.ndarray(dtype=ti.f32, ndim=2)

MAX_PALETTE_COLORS = 16

# Taichi 场数据
positions = ti.Vector.field(3, dtype=ti.f32, shape=total_points)
colors_field = ti.Vector.field(3, dtype=ti.f32, shape=total_points)
cinematic_colors = ti.Vector.field(3, dtype=ti.f32, shape=total_points)
color_metadata = ti.field(dtype=ti.f32, shape=(total_points, 4))
tail_parameters = ti.field(dtype=ti.f32, shape=(total_points, 8))
# 注释：不再需要curve_color_progress，现在直接使用全局点索引i计算颜色
# curve_color_progress = ti.field(dtype=ti.f32, shape=n_curves)

# 三角函数查找表（LUT）优化
LUT_SIZE = 4096  # 查找表大小，越大精度越高
sin_lut = ti.field(dtype=ti.f32, shape=LUT_SIZE)
cos_lut = ti.field(dtype=ti.f32, shape=LUT_SIZE)

film_palette = ti.Vector.field(3, dtype=ti.f32, shape=MAX_PALETTE_COLORS)
film_palette_size = ti.field(dtype=ti.i32, shape=())
film_grade_field = ti.field(dtype=ti.f32, shape=8)

# 心脏环面参数
R1 = 4.0
r = 1.0
R = 7.0
h = -1.0


# ---------------------------------------------------------------------------
# 彩虹调色盘配置与接口
# ---------------------------------------------------------------------------

DEFAULT_FILM_HEX = [
    "#430692",  # 深邃紫
    "#6D28D9",  # 皇家紫
    "#7E3802",  # 玫瑰红
    "#793403",  # 电影级暖橙
    "#846B09",  # 柔和金黄
    "#088A38",  # 翡翠绿
    "#087AAF",  # 天青蓝
    "#043090",  # 深海蓝
]

_palette_buffer = np.zeros((MAX_PALETTE_COLORS, 3), dtype=np.float32)
_current_hex_palette: list[str] = []

film_grade_defaults = {
    "contrast": 0.94,
    "contrast_midpoint": 0.82,
    "base_saturation": 0.88,
    "saturation_wave": 0.06,
    "warm_boost": 0.08,
    "gamma": 1.08,
    "min_clip": 0.045,
    "max_clip": 0.96,
}
film_grade_params = film_grade_defaults.copy()


def _normalize_hex_color(hex_color: str) -> str:
    candidate = hex_color.strip()
    if not candidate:
        raise ValueError("调色盘颜色不能为空字符串")
    if not candidate.startswith("#"):
        candidate = f"#{candidate}"
    if len(candidate) not in (4, 7):
        raise ValueError(f"非法 HEX 颜色: {hex_color}")
    color_to_rgb(candidate)
    return candidate


def set_film_palette(hex_colors: Sequence[str]) -> Sequence[str]:
    """更新电影级彩虹调色盘，支持 2-16 个 HEX 颜色。"""

    colors = [_normalize_hex_color(c) for c in hex_colors]
    if len(colors) < 2:
        raise ValueError("电影级调色盘至少需要 2 个颜色点")
    if len(colors) > MAX_PALETTE_COLORS:
        raise ValueError(
            f"调色盘最多支持 {MAX_PALETTE_COLORS} 个颜色，目前提供了 {len(colors)} 个"
        )

    _palette_buffer.fill(0.0)
    for idx, hex_color in enumerate(colors):
        _palette_buffer[idx] = np.array(color_to_rgb(hex_color), dtype=np.float32)

    film_palette.from_numpy(_palette_buffer)
    film_palette_size[None] = len(colors)

    _current_hex_palette.clear()
    _current_hex_palette.extend(colors)
    return tuple(_current_hex_palette)


def get_film_palette() -> Sequence[str]:
    """返回当前使用的 HEX 调色盘。"""

    return tuple(_current_hex_palette)


def set_film_grade(**kwargs: float) -> dict[str, float]:
    """调整电影级调色参数，如 contrast、warm_boost 等。"""

    for key, value in kwargs.items():
        if key not in film_grade_params:
            valid = ", ".join(film_grade_params.keys())
            raise KeyError(f"未知电影调色参数 '{key}'，可选项: {valid}")
        film_grade_params[key] = float(value)
    _sync_grade_to_device()
    return film_grade_params.copy()


def reset_film_grade() -> dict[str, float]:
    film_grade_params.update(film_grade_defaults)
    _sync_grade_to_device()
    return film_grade_params.copy()


def _apply_palette_from_env() -> None:
    env_value = os.getenv("RAINBOW_HEX_PALETTE")
    if not env_value:
        return
    raw_items = env_value.replace(";", ",").split(",")
    sanitized = [item.strip() for item in raw_items if item.strip()]
    if len(sanitized) >= 2:
        set_film_palette(sanitized)


def _sync_grade_to_device() -> None:
    grade_vector = np.array(
        [
            film_grade_params["base_saturation"],
            film_grade_params["saturation_wave"],
            film_grade_params["warm_boost"],
            film_grade_params["gamma"],
            film_grade_params["contrast"],
            film_grade_params["contrast_midpoint"],
            film_grade_params["min_clip"],
            film_grade_params["max_clip"],
        ],
        dtype=np.float32,
    )
    film_grade_field.from_numpy(grade_vector)


# 注释：不再需要此函数，现在直接在kernel中使用全局点索引i计算颜色
# def _update_curve_color_progress_from_positions(positions_np: np.ndarray) -> None:
#     """
#     根据曲线索引（对应dt值）直接分配颜色进度，确保相邻曲线颜色连续。
#     
#     参考代码中的逻辑：hue = (i / total_points) * 360
#     这里curve_idx对应dt的顺序，dt = 2π * curve_idx / n_curves
#     所以直接用curve_idx来分配颜色最简单直接。
#     """
#
#     if positions_np.shape[0] != total_points:
#         raise ValueError(
#             f"positions_np 期望形状为 ({total_points}, 3)，当前为 {positions_np.shape}"
#         )
#
#     if n_curves <= 0:
#         return
#
#     # 直接基于曲线索引分配颜色进度（与dt的定义完全一致）
#     progress_values = np.zeros(n_curves, dtype=np.float32)
#     for curve_idx in range(n_curves):
#         progress_values[curve_idx] = float(curve_idx) / float(n_curves)
#
#     curve_color_progress.from_numpy(progress_values)


@ti.func
def fast_sin(angle):
    """使用查找表和线性插值的快速 sin 函数"""
    # 将角度归一化到 [0, 2π)
    normalized = angle - ti.floor(angle / (2.0 * ti.math.pi)) * (2.0 * ti.math.pi)
    # 映射到查找表索引
    idx_float = normalized / (2.0 * ti.math.pi) * ti.cast(LUT_SIZE, ti.f32)
    idx = ti.cast(idx_float, ti.i32) % LUT_SIZE
    # 线性插值
    frac = idx_float - ti.cast(idx, ti.f32)
    next_idx = (idx + 1) % LUT_SIZE
    return sin_lut[idx] * (1.0 - frac) + sin_lut[next_idx] * frac


@ti.func
def fast_cos(angle):
    """使用查找表和线性插值的快速 cos 函数"""
    normalized = angle - ti.floor(angle / (2.0 * ti.math.pi)) * (2.0 * ti.math.pi)
    idx_float = normalized / (2.0 * ti.math.pi) * ti.cast(LUT_SIZE, ti.f32)
    idx = ti.cast(idx_float, ti.i32) % LUT_SIZE
    frac = idx_float - ti.cast(idx, ti.f32)
    next_idx = (idx + 1) % LUT_SIZE
    return cos_lut[idx] * (1.0 - frac) + cos_lut[next_idx] * frac


@ti.kernel
def init_trig_lut():
    """初始化三角函数查找表"""
    for i in range(LUT_SIZE):
        angle = 2.0 * ti.math.pi * ti.cast(i, ti.f32) / ti.cast(LUT_SIZE, ti.f32)
        sin_lut[i] = ti.sin(angle)
        cos_lut[i] = ti.cos(angle)


@ti.kernel
def compute_cardioid_torus_positions(time: float):
    """使用Taichi计算所有点的位置"""
    ti.loop_config(block_dim=BLOCK_DIM)
    for i in range(total_points):
        curve_idx = i // n_dots
        dot_idx = i % n_dots
        
        # 计算每条曲线的时间偏移
        dt = 2.0 * ti.math.pi * ti.cast(curve_idx, ti.f32) / ti.cast(n_curves, ti.f32)
        
        # 计算点在曲线上的参数
        phase_offset = ti.cast(curve_idx % 4, ti.f32) / 4.0
        start_positions = ti.Vector([0.0, 4.0, 8.0, 12.0])
        start_t = (start_positions[dot_idx] + phase_offset * 4.0) / 16.0
        
        # 动态时间参数
        t = start_t * 4.0 * ti.math.pi - 2.0 * ti.math.pi + time * 0.8
        
        # 调整 u 和 v 到 [0, 2π] 范围
        u = 2 * t 
        v = t
        
        # 计算3D坐标
        x = (R1 + (R - r) * ti.cos(v) + h * ti.cos(((R - r) / r) * v)) * ti.cos(u+dt)
        y = 1.5 * (R - r) * ti.sin(v) - h * ti.sin(((R - r) / r) * v)
        z = (R1 + (R - r) * ti.cos(v) + h * ti.cos(((R - r) / r) * v)) * ti.sin(u+dt)
        
        positions[i] = ti.Vector([x, y, z])


@ti.func
def rainbow_interpolate(hue):
    """
    基于色相值的6段彩虹颜色插值 (参考原始ManimGL代码)
    hue: [0, 360] 色相角度
    返回: RGB颜色向量
    """
    # 定义6段彩虹颜色 (RED -> YELLOW -> GREEN -> TEAL -> BLUE -> PURPLE -> RED)
    RED = ti.Vector([1.0, 0.0, 0.0])
    YELLOW = ti.Vector([1.0, 1.0, 0.0])
    GREEN = ti.Vector([0.0, 1.0, 0.0])
    TEAL = ti.Vector([0.0, 0.5, 0.5])
    BLUE = ti.Vector([0.0, 0.0, 1.0])
    PURPLE = ti.Vector([0.5, 0.0, 0.5])
    
    # 归一化到 [0, 360)
    h = hue - ti.floor(hue / 360.0) * 360.0
    
    # 6段线性插值
    result = ti.Vector([0.0, 0.0, 0.0])
    
    if h < 60.0:
        # RED -> YELLOW
        t = h / 60.0
        result = RED * (1.0 - t) + YELLOW * t
    elif h < 120.0:
        # YELLOW -> GREEN
        t = (h - 60.0) / 60.0
        result = YELLOW * (1.0 - t) + GREEN * t
    elif h < 180.0:
        # GREEN -> TEAL
        t = (h - 120.0) / 60.0
        result = GREEN * (1.0 - t) + TEAL * t
    elif h < 240.0:
        # TEAL -> BLUE
        t = (h - 180.0) / 60.0
        result = TEAL * (1.0 - t) + BLUE * t
    elif h < 300.0:
        # BLUE -> PURPLE
        t = (h - 240.0) / 60.0
        result = BLUE * (1.0 - t) + PURPLE * t
    else:
        # PURPLE -> RED
        t = (h - 300.0) / 60.0
        result = PURPLE * (1.0 - t) + RED * t
    
    return result


@ti.kernel
def _compute_film_rainbow_kernel():
    palette_size = film_palette_size[None]
    if palette_size >= 2:
        base_saturation = film_grade_field[0]
        saturation_wave = film_grade_field[1]
        warm_boost = film_grade_field[2]
        gamma_value = film_grade_field[3]
        contrast_factor = film_grade_field[4]
        contrast_midpoint = film_grade_field[5]
        min_clip = film_grade_field[6]
        max_clip = film_grade_field[7]

        ti.loop_config(block_dim=BLOCK_DIM)
        for i in range(total_points):
            curve_idx = i // n_dots  # 保留此变量用于后续计算
            
            # 使用全局点索引计算颜色进度(参考rainbow_test.py)
            progress = ti.cast(i, ti.f32) / ti.cast(total_points - 1, ti.f32)
            
            # 计算色相值 [0, 360]
            hue = progress * 360.0
            
            # 使用6段彩虹插值获取基础颜色
            base_rgb = rainbow_interpolate(hue)
            cinematic_colors[i] = base_rgb

            luminance = 0.299 * base_rgb[0] + 0.587 * base_rgb[1] + 0.114 * base_rgb[2]

            rgb = contrast_midpoint + (base_rgb - contrast_midpoint) * contrast_factor
            
            # 使用快速 sin 函数
            depth_factor = fast_sin(
                ti.cast(curve_idx, ti.f32) / ti.cast(n_curves, ti.f32) * ti.math.pi
            )
            saturation_factor = base_saturation + saturation_wave * fast_sin(
                ti.cast(curve_idx, ti.f32) * 0.11
            )

            max_channel = ti.max(rgb[0], ti.max(rgb[1], rgb[2]))
            min_channel = ti.min(rgb[0], ti.min(rgb[1], rgb[2]))
            if max_channel > min_channel:
                center = 0.5 * (max_channel + min_channel)
                rgb = center + (rgb - center) * saturation_factor

            rgb[0] = ti.min(1.0, rgb[0] * (1.0 + warm_boost))
            rgb[1] = ti.min(1.0, rgb[1] * (1.0 + warm_boost * 0.6))
            rgb[2] = ti.min(1.0, rgb[2] * (1.0 + warm_boost * 0.25))

            rgb = ti.pow(rgb, gamma_value)
            lower = ti.Vector([min_clip, min_clip, min_clip])
            upper = ti.Vector([max_clip, max_clip, max_clip])
            rgb = ti.max(lower, ti.min(upper, rgb))

            colors_field[i] = rgb

            color_metadata[i, 0] = hue
            color_metadata[i, 1] = saturation_factor
            color_metadata[i, 2] = luminance
            color_metadata[i, 3] = depth_factor


@ti.kernel
def init_tail_parameters():
    """初始化尾迹参数（冷路径，只在初始化时调用一次）"""
    ti.loop_config(block_dim=BLOCK_DIM)
    for i in range(total_points):
        tail_parameters[i, 0] = 120  # max_tail_length
        tail_parameters[i, 1] = 1.8    # tail_lifetime
        tail_parameters[i, 2] = 1.0    # opacity_start
        tail_parameters[i, 3] = 0.0    # opacity_end
        tail_parameters[i, 4] = 0.032  # width_start
        tail_parameters[i, 5] = 0.008  # width_end
        tail_parameters[i, 6] = 1.2    # glow_factor
        tail_parameters[i, 7] = 0.01   # anti_alias_width


def compute_cinematic_colors() -> None:
    if film_palette_size[None] < 2:
        raise RuntimeError("调色盘颜色不足，至少需要 2 个颜色点")
    _compute_film_rainbow_kernel()


@ti.kernel
def export_positions_to_ndarray(out: NdArray3f):
    ti.loop_config(block_dim=BLOCK_DIM)
    for i in range(total_points):
        for k in ti.static(range(3)):
            out[i, k] = positions[i][k]


@ti.kernel
def export_colors_to_ndarray(out: NdArray3f):
    ti.loop_config(block_dim=BLOCK_DIM)
    for i in range(total_points):
        for k in ti.static(range(3)):
            out[i, k] = colors_field[i][k]


# 初始化查找表和调色盘（支持 ENV 覆盖）
init_trig_lut()
init_tail_parameters()
set_film_palette(DEFAULT_FILM_HEX)
_sync_grade_to_device()
_apply_palette_from_env()


# ---------------------------------------------------------------------------
# 高性能 3D 场景
# ---------------------------------------------------------------------------


class HighPerformanceTracingTailDemo(ThreeDScene):
    color_refresh_interval = 30  # 帧数
    
    # 电影级运镜配置
    CINEMATIC_MOVEMENTS = {
        "epic_opening": {
            "theta": 30, "phi": 70, "height": 18,
            "duration": 5, "rate": lambda t: smooth(t, inflection=8)
        },
        "panoramic_orbit": {
            "theta": 390, "phi": 70, "height": 16,
            "duration": 12, "rate": linear
        },
        "dramatic_dive": {
            "theta": 420, "phi": 50, "height": 10,
            "duration": 4, "rate": lambda t: 1 - (1 - t) ** 3
        },
        "majestic_rise": {
            "theta": 450, "phi": 85, "height": 22,
            "duration": 6, "rate": lambda t: smooth(smooth(t))
        },
        "gods_eye_view": {
            "theta": 480, "phi": 5, "height": 20,
            "duration": 5, "rate": lambda t: there_and_back_with_pause(t, pause_ratio=0.3)
        },
        "spiral_ascent": {
            "theta": 540, "phi": 45, "height": 25,
            "duration": 8, "rate": lambda t: smooth(1 - (1 - t) ** 2)
        },
        "final_settlement": {
            "theta": 45, "phi": 60, "height": 16,
            "duration": 4, "rate": lambda t: smooth(smooth(smooth(t)))
        }
    }

    def construct(self):
        start_time = time.time()
        print("启动 GPU 轨迹演示，加载电影级彩虹调色盘...")

        # 初始镜头：低角度仰视
        self.camera.frame.set_euler_angles(theta=-10 * DEGREES, phi=75 * DEGREES)
        self.camera.frame.set_height(25)

        compute_cardioid_torus_positions(0.0)

        self.positions_buffer = np.empty((total_points, 3), dtype=np.float32)
        self.color_buffer = np.empty((total_points, 3), dtype=np.float32)

        export_positions_to_ndarray(self.positions_buffer)
        # 不再需要更新curve_color_progress，直接在kernel中计算
        # _update_curve_color_progress_from_positions(self.positions_buffer)

        compute_cinematic_colors()
        export_colors_to_ndarray(self.color_buffer)
        self.rgba_buffer = np.ones((total_points, 4), dtype=np.float32)
        self.rgba_buffer[:, :3] = self.color_buffer

        self.dot_cloud = DotCloud(points=self.positions_buffer, radius=0.05, color=WHITE)
        num_points = len(self.positions_buffer)
        self.dot_cloud.data = np.zeros(num_points, dtype=self.dot_cloud.data_dtype)
        self.dot_cloud.data["point"] = self.positions_buffer
        self.dot_cloud.data["radius"] = np.full((num_points, 1), 0.05, dtype=np.float32)
        self.dot_cloud.data["rgba"] = self.rgba_buffer
        self.add(self.dot_cloud)

        tail_params_np = tail_parameters.to_numpy()
        avg_tail_length = int(np.mean(tail_params_np[:, 0]))
        avg_tail_lifetime = float(np.mean(tail_params_np[:, 1]))
        avg_width_start = float(np.mean(tail_params_np[:, 4]))
        avg_width_end = float(np.mean(tail_params_np[:, 5]))
        avg_glow_factor = float(np.mean(tail_params_np[:, 6]))

        tracer_functions = [_BufferTracer(self.positions_buffer, i) for i in range(total_points)]

        self.multi_tails = MultiTracingTails(
            traced_functions=tracer_functions,
            colors=self.color_buffer,
            max_tail_length=avg_tail_length,
            tail_lifetime=avg_tail_lifetime,
            opacity_fade=(1.0, 0.0),
            width_fade=(avg_width_start, avg_width_end),
            glow_factor=avg_glow_factor,
        )
        self.add(self.multi_tails)

        self.current_time = 0.0
        self.frame_count = 0

        print(
            f"初始化完成：{total_points} 粒子，平均尾迹长度 {avg_tail_length}，"
            f"辉光强度 {avg_glow_factor:.2f}"
        )

        def ultra_high_performance_updater(_mob, dt):
            self.current_time += dt
            self.frame_count += 1

            if self.frame_count % 180 == 0:
                elapsed = max(time.time() - start_time, 1e-6)
                fps = self.frame_count / elapsed
                particle_rate = self.frame_count * total_points / elapsed / 1000.0
                print(f"帧 {self.frame_count}: {fps:6.2f} FPS ，粒子吞吐 {particle_rate:7.1f} K/s")

            compute_cardioid_torus_positions(self.current_time)
            export_positions_to_ndarray(self.positions_buffer)
            # 不再需要更新curve_color_progress，直接在kernel中计算
            # _update_curve_color_progress_from_positions(self.positions_buffer)
            self.dot_cloud.set_points(self.positions_buffer)

            if self.frame_count % self.color_refresh_interval == 0:
                compute_cinematic_colors()
                export_colors_to_ndarray(self.color_buffer)
                self.multi_tails.colors = self.color_buffer
                self.rgba_buffer[:, :3] = self.color_buffer
                self.dot_cloud.data["rgba"] = self.rgba_buffer

            self.multi_tails.update_all_tails(dt)

        self.dot_cloud.add_updater(ultra_high_performance_updater)
        self.setup_camera_movement()

        end_time = time.time()
        elapsed = end_time - start_time
        if elapsed > 0:
            print(
                f"\n=== 性能概览 ===\n"
                f"初始化耗时: {elapsed:.2f}s\n"
                f"当前调色盘: {', '.join(get_film_palette())}\n"
                f"调色参数: {film_grade_params}\n"
            )

    def setup_camera_movement(self):
        """电影级多段式运镜设计 - 完整故事化镜头语言"""
        
        print("\n=== 电影级运镜序列启动 ===")
        
        # 【开场】史诗揭幕 - 从黑暗中缓慢升起
        print("第一幕：史诗揭幕...")
        self.play(
            self.camera.frame.animate
            .set_euler_angles(theta=30 * DEGREES, phi=70 * DEGREES)
            .set_height(18),
            run_time=3,
            rate_func=lambda t: smooth(t),  # 超平滑启动
        )
        # self.wait(1)
        
        # 【展示】360度全景环绕 - 展示结构之美
        print("第二幕：全景环绕...")
        self.play(
            self.camera.frame.animate
            .set_euler_angles(theta=390 * DEGREES, phi=70 * DEGREES)
            .set_height(16),
            run_time=3,
            rate_func=linear,  # 匀速旋转
        )
        
        # 【冲击】快速俯冲特写 - 制造紧张感
        print("第三幕：戏剧性俯冲...")
        self.play(
            self.camera.frame.animate
            .set_euler_angles(theta=420 * DEGREES, phi=45 * DEGREES)
            .set_height(10),
            run_time=3,
            rate_func=lambda t: 1 - (1 - t) ** 3,  # 加速俯冲
        )
        # self.wait(0.5)
        
        # 【呼吸】近距离跟随 - 沉浸式体验
        print("第四幕：近距离跟随...")
        self.play(
            self.camera.frame.animate
            .set_euler_angles(theta=435 * DEGREES, phi=55 * DEGREES)
            .set_height(8),
            run_time=3,
            rate_func=lambda t: wiggle(t, wiggles=2),  # 微微晃动跟拍
        )
        
        # 【壮阔】仰视拉远 - 营造宏大感
        print("第五幕：壮阔仰视...")
        self.play(
            self.camera.frame.animate
            .set_euler_angles(theta=460 * DEGREES, phi=85 * DEGREES)
            .set_height(24),
            run_time=3,
            rate_func=lambda t: smooth(smooth(t)),
        )
        # self.wait(1)
        
        # 【上帝】顶视俯瞰 - 揭示全局规律
        print("第六幕：上帝视角...")
        self.play(
            self.camera.frame.animate
            .set_euler_angles(theta=480 * DEGREES, phi=2 * DEGREES)
            .set_height(22),
            run_time=3,
            rate_func=lambda t: there_and_back_with_pause(t),
        )
        # self.wait(1.5)
        
        # 【穿梭】侧面掠过 - 速度与动感
        print("第七幕：侧面掠过...")
        self.play(
            self.camera.frame.animate
            .set_euler_angles(theta=520 * DEGREES, phi=90 * DEGREES)
            .set_height(14),
            run_time=3,
            rate_func=rush_into,  # 快速冲入
        )
        
        # 【升华】螺旋上升 - 渐入永恒
        print("第八幕：螺旋上升...")
        self.play(
            self.camera.frame.animate
            .set_euler_angles(theta=560 * DEGREES, phi=50 * DEGREES)
            .set_height(28),
            run_time=3,
            rate_func=lambda t: smooth(1 - (1 - t) ** 2),  # 渐慢离场
        )
        
        # 【回归】经典视角 - 完美落幕
        print("终幕：回归平衡...")
        self.play(
            self.camera.frame.animate
            .set_euler_angles(theta=45 * DEGREES, phi=60 * DEGREES)
            .set_height(16),
            run_time=3,
            rate_func=lambda t: smooth(smooth(smooth(t))),  # 三重平滑
        )
        
        # 【尾声】静默观察
        print("尾声：静默凝视...\n")
        # self.wait(4)
        
        print("=== 电影级运镜序列完成 ===\n")


# ---------------------------------------------------------------------------
# 命令行入口
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    compute_cinematic_colors()
    os.system(f"cd {script_dir} && manimgl {script_name}.py ")
