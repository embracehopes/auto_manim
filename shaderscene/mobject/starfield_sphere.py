from manimlib import *
from numpy import *
from typing import Callable, Iterable, Tuple
from pathlib import Path
import sys
import os

class StarfieldSphere(Surface):
    """
    星空效果的球面，使用多层星星渲染技术
    基于 Shadertoy 的星空效果，适配到球面坐标系

    特点：
    - 多层星星效果（4层）
    - 彩色星星渲染
    - 位置无关的纹理坐标
    - 时间动画支持
    """

    # 指定新的 shader 文件夹路径
    shader_folder: str = str(Path(__file__).parent.parent / "starfield_sphere_shader")

    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        u_range: tuple[float, float] = (0, TAU),
        v_range: tuple[float, float] = (0, PI),
        resolution: tuple[int, int] = (64, 64),
        brightness: float = 2.0,
        time_scale: float = 1.0,
        star_density: float = 1.0,
        **kwargs
    ):
        self.radius = radius
        self.center = np.array(center)
        self.time_scale = time_scale
        self.star_density = star_density

        def sphere_func(u, v):
            # 球面参数方程
            x = self.radius * sin(v) * cos(u) + self.center[0]
            y = self.radius * sin(v) * sin(u) + self.center[1]
            z = self.radius * cos(v) + self.center[2]
            return np.array([x, y, z])

        self.passed_uv_func = sphere_func
        super().__init__(u_range=u_range, v_range=v_range, resolution=resolution, **kwargs)

        # 初始化shader uniforms
        self.set_uniform(time=0.0)
        self.set_uniform(brightness=float(brightness))
        self.set_uniform(sphere_center=self.center.astype(np.float32))

        # 添加时间更新器
        self.add_updater(lambda m, dt: self.increment_time(dt))

    def uv_func(self, u, v):
        """UV函数定义球面几何"""
        return self.passed_uv_func(u, v)

    def increment_time(self, dt):
        """重写时间增量方法以支持时间缩放"""
        self.uniforms["time"] += self.time_scale * dt
        return self

    def move_to(self, point):
        """重写移动方法，同步更新球体中心"""
        result = super().move_to(point)
        self.center = np.array(self.get_center())
        self.set_uniform(sphere_center=self.center.astype(np.float32))
        return result

    def shift(self, vector):
        """重写位移方法，同步更新球体中心"""
        result = super().shift(vector)
        self.center = np.array(self.get_center())
        self.set_uniform(sphere_center=self.center.astype(np.float32))
        return result

    def set_brightness(self, brightness: float):
        """设置星星亮度"""
        self.set_uniform(brightness=float(brightness))
        return self

    def set_star_density(self, density: float):
        """设置星星密度"""
        self.star_density = density
        self.set_uniform(star_density=float(density))
        return self

    def set_time_scale(self, scale: float):
        """设置时间缩放（动画速度）"""
        self.time_scale = scale
        return self


class AnimatedStarfieldSphere(StarfieldSphere):
    """
    带有额外动画效果的星空球面
    支持自动旋转和缩放动画
    """

    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        brightness: float = 2.0,
        time_scale: float = 1.0,
        auto_rotate: bool = True,
        rotation_speed: float = 0.5,
        **kwargs
    ):
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            time_scale=time_scale,
            **kwargs
        )

        self.auto_rotate = auto_rotate
        self.rotation_speed = rotation_speed

        if auto_rotate:
            # 添加自动旋转
            self.add_updater(self.auto_rotation_updater)

    def auto_rotation_updater(self, mobject, dt):
        """自动旋转更新器"""
        self.rotate(self.rotation_speed * dt, axis=UP)
        self.rotate(self.rotation_speed * dt * 0.7, axis=RIGHT)
        return self

    def stop_auto_rotation(self):
        """停止自动旋转"""
        self.auto_rotate = False
        self.clear_updaters()
        # 重新添加时间更新器
        self.add_updater(lambda m, dt: self.increment_time(dt))
        return self

    def start_auto_rotation(self):
        """开始自动旋转"""
        if not self.auto_rotate:
            self.auto_rotate = True
            self.add_updater(self.auto_rotation_updater)
        return self

    def set_rotation_speed(self, speed: float):
        """设置旋转速度"""
        self.rotation_speed = speed
        return self


class PulsingStarfieldSphere(StarfieldSphere):
    """
    带有脉冲效果的星空球面
    星星亮度会周期性变化
    """

    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        brightness: float = 2.0,
        pulse_frequency: float = 1.0,
        pulse_amplitude: float = 0.5,
        **kwargs
    ):
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            **kwargs
        )

        self.base_brightness = brightness
        self.pulse_frequency = pulse_frequency
        self.pulse_amplitude = pulse_amplitude

        # 添加脉冲更新器
        self.add_updater(self.pulse_updater)

    def pulse_updater(self, mobject, dt):
        """脉冲效果更新器"""
        # 使用正弦波创建脉冲效果
        pulse = sin(self.uniforms["time"] * self.pulse_frequency) * self.pulse_amplitude
        current_brightness = self.base_brightness * (1.0 + pulse)
        self.set_uniform(brightness=float(current_brightness))
        return self

    def set_pulse_frequency(self, frequency: float):
        """设置脉冲频率"""
        self.pulse_frequency = frequency
        return self

    def set_pulse_amplitude(self, amplitude: float):
        """设置脉冲幅度"""
        self.pulse_amplitude = amplitude
        return self


# 便捷的创建函数
def create_starfield_sphere(radius=1.0, **kwargs):
    """创建基础星空球面"""
    return StarfieldSphere(radius=radius, **kwargs)

def create_animated_starfield_sphere(radius=1.0, **kwargs):
    """创建动画星空球面（自动旋转）"""
    return AnimatedStarfieldSphere(radius=radius, **kwargs)

def create_pulsing_starfield_sphere(radius=1.0, **kwargs):
    """创建脉冲星空球面（亮度周期变化）"""
    return PulsingStarfieldSphere(radius=radius, **kwargs)
    """
    星空效果的球面，使用多层星星渲染技术
    基于 Shadertoy 的星空效果，适配到球面坐标系

    特点：
    - 多层星星效果（4层）
    - 彩色星星渲染
    - 位置无关的纹理坐标
    - 时间动画支持
    """

    # 指定新的 shader 文件夹路径
    shader_folder: str = str(Path(__file__).parent / "starfield_sphere_shader")

    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        u_range: tuple[float, float] = (0, TAU),
        v_range: tuple[float, float] = (0, PI),
        resolution: tuple[int, int] = (64, 64),
        brightness: float = 2.0,
        time_scale: float = 1.0,
        star_density: float = 1.0,
        **kwargs
    ):
        self.radius = radius
        self.center = np.array(center)
        self.time_scale = time_scale
        self.star_density = star_density

        def sphere_func(u, v):
            # 球面参数方程
            x = self.radius * sin(v) * cos(u) + self.center[0]
            y = self.radius * sin(v) * sin(u) + self.center[1]
            z = self.radius * cos(v) + self.center[2]
            return np.array([x, y, z])

        super().__init__(
            uv_func=sphere_func,
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            brightness=brightness,
            **kwargs
        )

        # 设置初始 uniforms
        self.uniforms.update({
            "time": 0.0,
            "brightness": float(brightness),
            "sphere_center": self.center.astype(np.float32),
            "star_density": float(star_density)
        })

        # 添加时间更新器
        self.add_updater(lambda m, dt: m.increment_time(dt))

    def increment_time(self, dt):
        """重写时间增量方法以支持时间缩放"""
        self.uniforms["time"] += self.time_scale * dt
        return self

    def move_to(self, point):
        """重写移动方法，同步更新球体中心"""
        result = super().move_to(point)
        self.center = np.array(self.get_center())
        self.uniforms.update({
            "sphere_center": self.center.astype(np.float32)
        })
        return result

    def shift(self, vector):
        """重写位移方法，同步更新球体中心"""
        result = super().shift(vector)
        self.center = np.array(self.get_center())
        self.uniforms.update({
            "sphere_center": self.center.astype(np.float32)
        })
        return result

    def set_brightness(self, brightness: float):
        """设置星星亮度"""
        self.uniforms.update({"brightness": float(brightness)})
        return self

    def set_star_density(self, density: float):
        """设置星星密度"""
        self.star_density = density
        self.uniforms.update({"star_density": float(density)})
        return self

    def set_time_scale(self, scale: float):
        """设置时间缩放（动画速度）"""
        self.time_scale = scale
        return self


class AnimatedStarfieldSphere(StarfieldSphere):
    """
    带有额外动画效果的星空球面
    支持自动旋转和缩放动画
    """

    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        brightness: float = 2.0,
        time_scale: float = 1.0,
        auto_rotate: bool = True,
        rotation_speed: float = 0.5,
        **kwargs
    ):
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            time_scale=time_scale,
            **kwargs
        )

        self.auto_rotate = auto_rotate
        self.rotation_speed = rotation_speed

        if auto_rotate:
            # 添加自动旋转
            self.add_updater(self.auto_rotation_updater)

    def auto_rotation_updater(self, mobject, dt):
        """自动旋转更新器"""
        mobject.rotate(self.rotation_speed * dt, axis=UP)
        mobject.rotate(self.rotation_speed * dt * 0.7, axis=RIGHT)
        return mobject

    def stop_auto_rotation(self):
        """停止自动旋转"""
        self.auto_rotate = False
        self.clear_updaters()
        # 重新添加时间更新器
        self.add_updater(lambda m, dt: m.increment_time(dt))
        return self

    def start_auto_rotation(self):
        """开始自动旋转"""
        if not self.auto_rotate:
            self.auto_rotate = True
            self.add_updater(self.auto_rotation_updater)
        return self

    def set_rotation_speed(self, speed: float):
        """设置旋转速度"""
        self.rotation_speed = speed
        return self


class PulsingStarfieldSphere(StarfieldSphere):
    """
    带有脉冲效果的星空球面
    星星亮度会周期性变化
    """

    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        brightness: float = 2.0,
        pulse_frequency: float = 1.0,
        pulse_amplitude: float = 0.5,
        **kwargs
    ):
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            **kwargs
        )

        self.base_brightness = brightness
        self.pulse_frequency = pulse_frequency
        self.pulse_amplitude = pulse_amplitude

        # 添加脉冲更新器
        self.add_updater(self.pulse_updater)

    def pulse_updater(self, mobject, dt):
        """脉冲效果更新器"""
        # 使用正弦波创建脉冲效果
        pulse = sin(self.uniforms["time"] * self.pulse_frequency) * self.pulse_amplitude
        current_brightness = self.base_brightness * (1.0 + pulse)
        self.uniforms.update({"brightness": float(current_brightness)})
        return mobject

    def set_pulse_frequency(self, frequency: float):
        """设置脉冲频率"""
        self.pulse_frequency = frequency
        return self

    def set_pulse_amplitude(self, amplitude: float):
        """设置脉冲幅度"""
        self.pulse_amplitude = amplitude
        return self


# 便捷的创建函数
def create_starfield_sphere(radius=1.0, **kwargs):
    """创建基础星空球面"""
    return StarfieldSphere(radius=radius, **kwargs)

def create_animated_starfield_sphere(radius=1.0, **kwargs):
    """创建动画星空球面（自动旋转）"""
    return AnimatedStarfieldSphere(radius=radius, **kwargs)

def create_pulsing_starfield_sphere(radius=1.0, **kwargs):
    """创建脉冲星空球面（亮度周期变化）"""
    return PulsingStarfieldSphere(radius=radius, **kwargs)
