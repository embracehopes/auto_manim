from manimlib import *
from numpy import *
from typing import Callable, Iterable, Tuple
from pathlib import Path
from mobject.sphere_surface import ShaderSurface

class SpecialGeodesicSphere(ShaderSurface):
    """
    使用高级测地线六边形着色器的特殊球面
    基于 Shadertoy 的复杂几何算法
    """
    shader_folder: str = str(Path(Path(__file__).parent.parent / "sphere_special"))

    def __init__(
            self,
            radius: float = 1.0,
            center: Iterable[float] = [0, 0, 0],
            u_range: tuple[float, float] = (0, TAU),
            v_range: tuple[float, float] = (0, PI),
            resolution: tuple[int, int] = (800, 800),
            brightness: float = 1.5,
            **kwargs
    ):
        self.radius = radius
        self.center = np.array(center)
        
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


class AnimatedGeodesicSphere(SpecialGeodesicSphere):
    """
    带有额外动画效果的测地线球面
    """
    
    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        animation_speed: float = 1.0,
        brightness: float = 1.8,
        **kwargs
    ):
        self.animation_speed = animation_speed
        
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            **kwargs
        )
        
        # 添加额外的时间更新器
        self.add_updater(lambda m, dt: m.increment_animation_time(dt))
    
    def increment_animation_time(self, dt):
        if hasattr(self, 'uniforms') and 'time' in self.uniforms:
            self.uniforms["time"] += self.animation_speed * dt
        return self


class MultiScaleGeodesicSphere(SpecialGeodesicSphere):
    """
    多尺度测地线球面，可以动态改变细分级别
    """
    
    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        subdivision_range: tuple[float, float] = (2.0, 4.0),
        subdivision_speed: float = 0.5,
        brightness: float = 1.6,
        **kwargs
    ):
        self.subdivision_range = subdivision_range
        self.subdivision_speed = subdivision_speed
        
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            **kwargs
        )
        
        # 设置细分参数
        self.set_uniform(subdivision_min=subdivision_range[0])
        self.set_uniform(subdivision_max=subdivision_range[1])
        self.set_uniform(subdivision_speed=subdivision_speed)


# 便捷创建函数
def create_special_geodesic_sphere(
    radius: float = 2.0,
    center: Iterable[float] = [0, 0, 0],
    resolution: tuple[int, int] = (100, 100),
    brightness: float = 1.5
) -> SpecialGeodesicSphere:
    """创建一个标准的特殊测地线球面"""
    return SpecialGeodesicSphere(
        radius=radius,
        center=center,
        resolution=resolution,
        brightness=brightness
    )

def create_animated_geodesic_sphere(
    radius: float = 2.0,
    center: Iterable[float] = [0, 0, 0],
    animation_speed: float = 1.2,
    resolution: tuple[int, int] = (100, 100),
    brightness: float = 1.8
) -> AnimatedGeodesicSphere:
    """创建一个动画测地线球面"""
    return AnimatedGeodesicSphere(
        radius=radius,
        center=center,
        animation_speed=animation_speed,
        resolution=resolution,
        brightness=brightness
    )

def create_multiscale_geodesic_sphere(
    radius: float = 2.0,
    center: Iterable[float] = [0, 0, 0],
    subdivision_range: tuple[float, float] = (2.0, 4.0),
    subdivision_speed: float = 0.8,
    resolution: tuple[int, int] = (120, 120),
    brightness: float = 1.6
) -> MultiScaleGeodesicSphere:
    """创建一个多尺度测地线球面"""
    return MultiScaleGeodesicSphere(
        radius=radius,
        center=center,
        subdivision_range=subdivision_range,
        subdivision_speed=subdivision_speed,
        resolution=resolution,
        brightness=brightness
    )
