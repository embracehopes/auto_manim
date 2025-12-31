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

# ---------------------------------------------------------------------------
# Taichi & 全局参数
# ---------------------------------------------------------------------------

ti.init(arch=ti.gpu)  # GPU 加速

n_curves = 180
n_dots = 5
total_points = n_curves * n_dots

MAX_PALETTE_COLORS = 16

# Taichi 场数据
positions = ti.Vector.field(3, dtype=ti.f32, shape=total_points)
colors_field = ti.Vector.field(3, dtype=ti.f32, shape=total_points)
cinematic_colors = ti.Vector.field(3, dtype=ti.f32, shape=total_points)
color_metadata = ti.field(dtype=ti.f32, shape=(total_points, 4))
tail_parameters = ti.field(dtype=ti.f32, shape=(total_points, 8))

film_palette = ti.Vector.field(3, dtype=ti.f32, shape=MAX_PALETTE_COLORS)
film_palette_size = ti.field(dtype=ti.i32, shape=())
film_grade_field = ti.field(dtype=ti.f32, shape=8)

# 心脏环面参数
R = 3.0
r = 2.0
k1 = 2.0
k2 = 2.0
k3 = 2.0


# ---------------------------------------------------------------------------
# 彩虹调色盘配置与接口
# ---------------------------------------------------------------------------

DEFAULT_FILM_HEX = [
    "#33135C",  # 深邃紫
    "#6D28D9",  # 皇家紫
    "#E11D48",  # 玫瑰红
    "#F97316",  # 电影级暖橙
    "#FACC15",  # 柔和金黄
    "#22C55E",  # 翡翠绿
    "#0EA5E9",  # 天青蓝
    "#2563EB",  # 深海蓝
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
    # 交给 manim 判断是否可解析
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


# ---------------------------------------------------------------------------
# Taichi 核心函数
# ---------------------------------------------------------------------------


@ti.func
def _smoothstep01(t):
    return t * t * (3.0 - 2.0 * t)


@ti.kernel
def compute_cardioid_torus_positions(time: float):
    for i in range(total_points):
        curve_idx = i // n_dots
        dot_idx = i % n_dots

        dt = (
            2.0
            * ti.math.pi
            * ti.cast(curve_idx, ti.f32)
            / ti.cast(n_curves, ti.f32)
        )

        phase_offset = ti.cast(curve_idx % 4, ti.f32) / 4.0
        start_positions = ti.Vector([0.0, 4.0, 8.0, 12.0])
        start_t = (start_positions[dot_idx] + phase_offset * 4.0) / 16.0

        t = start_t * 4.0 * ti.math.pi - 2.0 * ti.math.pi + time * 0.8

        u = 0.25 * t
        v = t

        x = (R + r * (2.0 * ti.cos(v / 2.0) - ti.cos(k1 * v))) * ti.cos(3.0 * u + dt)
        y = 1.4 * r * (2.0 * ti.sin(v / 2.0) - ti.sin(k2 * v))
        z = (R + r * (2.0 * ti.cos(v / 2.0) - ti.cos(k3 * v))) * ti.sin(3.0 * u + dt)

        positions[i] = ti.Vector([x, y, z])


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

        for i in range(total_points):
            progress = ti.cast(i, ti.f32) / ti.cast(total_points - 1, ti.f32)
            segment_pos = progress * ti.cast(palette_size - 1, ti.f32)

            segment_idx = ti.cast(ti.floor(segment_pos), ti.i32)
            segment_idx = ti.max(0, ti.min(segment_idx, palette_size - 2))
            local_t = segment_pos - ti.cast(segment_idx, ti.f32)
            eased_t = _smoothstep01(local_t)

            c1 = film_palette[segment_idx]
            c2 = film_palette[segment_idx + 1]
            base_rgb = c1 + (c2 - c1) * eased_t
            cinematic_colors[i] = base_rgb

            luminance = 0.299 * base_rgb[0] + 0.587 * base_rgb[1] + 0.114 * base_rgb[2]

            rgb = contrast_midpoint + (base_rgb - contrast_midpoint) * contrast_factor

            curve_idx = i // n_dots
            depth_factor = ti.sin(
                ti.cast(curve_idx, ti.f32) / ti.cast(n_curves, ti.f32) * ti.math.pi
            )
            saturation_factor = base_saturation + saturation_wave * ti.sin(
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

            color_metadata[i, 0] = progress * 360.0
            color_metadata[i, 1] = saturation_factor
            color_metadata[i, 2] = luminance
            color_metadata[i, 3] = depth_factor

            tail_parameters[i, 0] = 120.0
            tail_parameters[i, 1] = 1.8
            tail_parameters[i, 2] = 1.0
            tail_parameters[i, 3] = 0.0
            tail_parameters[i, 4] = 0.032
            tail_parameters[i, 5] = 0.008
            tail_parameters[i, 6] = 1.2
            tail_parameters[i, 7] = 0.01


def compute_cinematic_colors() -> None:
    if film_palette_size[None] < 2:
        raise RuntimeError("调色盘颜色不足，至少需要 2 个颜色点")
    _compute_film_rainbow_kernel()


# 初始化调色盘（支持 ENV 覆盖）
set_film_palette(DEFAULT_FILM_HEX)
_sync_grade_to_device()
_apply_palette_from_env()


# ---------------------------------------------------------------------------
# 高性能 3D 场景
# ---------------------------------------------------------------------------


class HighPerformanceTracingTailDemo(ThreeDScene):
    color_refresh_interval = 30  # 帧数

    def construct(self):
        start_time = time.time()
        print("启动 GPU 轨迹演示，加载电影级彩虹调色盘...")

        self.camera.frame.set_euler_angles(theta=0 * DEGREES, phi=0 * DEGREES)
        self.camera.frame.set_height(20)

        compute_cardioid_torus_positions(0.0)
        compute_cinematic_colors()

        self.positions_buffer = positions.to_numpy()
        self.color_buffer = colors_field.to_numpy()
        self.rgba_buffer = np.ones((total_points, 4), dtype=np.float32)
        self.rgba_buffer[:, :3] = self.color_buffer

        self.dot_cloud = DotCloud(points=self.positions_buffer, radius=0.025, color=WHITE)
        num_points = len(self.positions_buffer)
        self.dot_cloud.data = np.zeros(num_points, dtype=self.dot_cloud.data_dtype)
        self.dot_cloud.data["point"] = self.positions_buffer
        self.dot_cloud.data["radius"] = np.full((num_points, 1), 0.025, dtype=np.float32)
        self.dot_cloud.data["rgba"] = self.rgba_buffer
        self.add(self.dot_cloud)

        tail_params_np = tail_parameters.to_numpy()
        avg_tail_length = int(np.mean(tail_params_np[:, 0]))
        avg_tail_lifetime = float(np.mean(tail_params_np[:, 1]))
        avg_width_start = float(np.mean(tail_params_np[:, 4]))
        avg_width_end = float(np.mean(tail_params_np[:, 5]))
        avg_glow_factor = float(np.mean(tail_params_np[:, 6]))

        tracer_functions = []

        def make_tracer(idx: int):
            def tracer():
                if 0 <= idx < len(self.positions_buffer):
                    return self.positions_buffer[idx]
                return ORIGIN

            return tracer

        for i in range(total_points):
            tracer_functions.append(make_tracer(i))

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
            updated_positions = positions.to_numpy()
            self.positions_buffer[:] = updated_positions
            self.dot_cloud.set_points(updated_positions)

            if self.frame_count % self.color_refresh_interval == 0:
                compute_cinematic_colors()
                self.color_buffer[:] = colors_field.to_numpy()
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
        self.play(
            self.camera.frame.animate.set_euler_angles(theta=45 * DEGREES, phi=60 * DEGREES)
            .set_height(16),
            run_time=4,
            rate_func=lambda t: smooth(smooth(t)),
        )


# ---------------------------------------------------------------------------
# 命令行入口
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    compute_cinematic_colors()
    os.system(f"cd {script_dir} && manimgl.exe {script_name}.py ")
