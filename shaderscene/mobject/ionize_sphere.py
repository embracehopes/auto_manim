from manimlib import *
from numpy import *
from typing import Callable, Iterable, Tuple
from pathlib import Path

# 导入现有的ShaderSurface基类
from .sphere_surface import ShaderSurface

class IonizeSphere(ShaderSurface):
    """电离效果球体着色器表面类，shader效果基于绝对世界坐标"""
    shader_folder: str = str(Path(Path(__file__).parent.parent / "ionize_sphere_shader"))

    def __init__(
            self,
            radius: float = 1.0,
            center: Iterable[float] = [0, 0, 0],
            u_range: tuple[float, float] = (0, TAU),
            v_range: tuple[float, float] = (0, PI),
            resolution: tuple[int, int] = (64, 64),
            brightness: float = 1.5,
            **kwargs
    ):
        self.radius = radius
        self.center = np.array(center)
        
        # 定义球面UV函数
        def sphere_func(u, v):
            # 球面参数方程
            # u: 经度 (0 到 2π)
            # v: 纬度 (0 到 π)
            x = self.radius * sin(v) * cos(u) + self.center[0]
            y = self.radius * sin(v) * sin(u) + self.center[1]
            z = self.radius * cos(v) + self.center[2]
            return np.array([x, y, z])
        
        super().__init__(
            uv_func=sphere_func,
            u_range=u_range,
            v_range=v_range,
            brightness=brightness,
            resolution=resolution,
            **kwargs
        )

        # 添加电离效果特定的uniforms
        self.set_uniform(resolution=np.array([800.0, 600.0], dtype=np.float32))
        self.set_uniform(sphere_center=np.array(self.center, dtype=np.float32))

    def increment_time(self, dt):
        """更新时间uniform（覆盖父类方法）"""
        current_time = self.uniforms.get("time", 0.0)
        self.set_uniform(time=current_time + dt)
        return self
    
    def move_to(self, point):
        """重写移动方法，确保球心uniform也更新"""
        # 先调用父类的移动方法
        result = super().move_to(point)
        
        # 更新球心uniform，但保持shader效果在绝对坐标中
        # 这样shader效果不会随球体移动而改变
        # self.set_uniform(sphere_center=np.array(self.get_center(), dtype=np.float32))
        
        return result
    
    def shift(self, vector):
        """重写平移方法，确保球心uniform也更新"""
        # 先调用父类的平移方法
        result = super().shift(vector)
        
        # 更新球心uniform，但保持shader效果在绝对坐标中
        # self.set_uniform(sphere_center=np.array(self.get_center(), dtype=np.float32))
        
        return result


class AnimatedIonizeSphere(IonizeSphere):
    """动画电离球体"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 时间更新器已经在ShaderSurface基类中添加了


# 便捷创建函数
def create_ionize_sphere(
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        u_range: tuple[float, float] = (0, TAU),
        v_range: tuple[float, float] = (0, PI),
        resolution: tuple[int, int] = (64, 64),
        brightness: float = 1.5,
        animated: bool = True,
        **kwargs
) -> IonizeSphere:
    """创建电离球体的便捷函数"""
    if animated:
        return AnimatedIonizeSphere(
            radius=radius,
            center=center,
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            brightness=brightness,
            **kwargs
        )
    else:
        return IonizeSphere(
            radius=radius,
            center=center,
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            brightness=brightness,
            **kwargs
        )


def create_animated_ionize_sphere(
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        u_range: tuple[float, float] = (0, TAU),
        v_range: tuple[float, float] = (0, PI),
        resolution: tuple[int, int] = (64, 64),
        brightness: float = 1.5,
        **kwargs
) -> AnimatedIonizeSphere:
    """创建动画电离球体的便捷函数"""
    return AnimatedIonizeSphere(
        radius=radius,
        center=center,
        u_range=u_range,
        v_range=v_range,
        resolution=resolution,
        brightness=brightness,
        **kwargs
    )
