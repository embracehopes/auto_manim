from manimlib import *
from numpy import *
from typing import Callable, Iterable, Tuple
from pathlib import Path

# 导入现有的ShaderSurface基类
from .sphere_surface import ShaderSurface

class FixedIonizeSphere(ShaderSurface):
    """
    电离效果球体着色器表面类，shader效果完全基于绝对世界坐标
    不管球体如何移动、旋转、缩放，shader效果都保持在固定的世界位置
    """
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
        self.original_center = np.array(center)  # 保存原始中心点
        self.current_center = np.array(center)   # 当前中心点
        
        # 定义球面UV函数
        def sphere_func(u, v):
            # 球面参数方程
            # u: 经度 (0 到 2π)
            # v: 纬度 (0 到 π)
            x = self.radius * sin(v) * cos(u) + self.current_center[0]
            y = self.radius * sin(v) * sin(u) + self.current_center[1]
            z = self.radius * cos(v) + self.current_center[2]
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
        # 使用原始中心点作为shader效果的固定参考点
        self.set_uniform(sphere_center=np.array(self.original_center, dtype=np.float32))

    def increment_time(self, dt):
        """更新时间uniform（覆盖父类方法）"""
        current_time = self.uniforms.get("time", 0.0)
        self.set_uniform(time=current_time + dt)
        return self
    
    def move_to(self, point):
        """重写 move_to 方法，确保更新球体中心的 uniform 变量"""
        result = super().move_to(point)
        # 更新当前中心位置
        self.current_center = np.array(self.get_center())
        # 更新shader中的球体中心位置
        self.set_uniform(sphere_center=np.array(self.current_center, dtype=np.float32))
        return result
    
    def shift(self, vector):
        """重写 shift 方法，确保更新球体中心的 uniform 变量"""
        result = super().shift(vector)
        # 更新当前中心位置
        self.current_center = np.array(self.get_center())
        # 更新shader中的球体中心位置
        self.set_uniform(sphere_center=np.array(self.current_center, dtype=np.float32))
        return result
    
    def update_center_position(self, new_center):
        """更新当前中心位置并同步到shader"""
        self.current_center = np.array(new_center)
        self.set_uniform(sphere_center=np.array(self.current_center, dtype=np.float32))
    
    def apply_matrix(self, matrix, **kwargs):
        """重写矩阵变换方法，确保shader球心同步更新"""
        # 应用变换
        result = super().apply_matrix(matrix, **kwargs)
        # 更新中心位置
        self.current_center = np.array(self.get_center())
        self.set_uniform(sphere_center=np.array(self.current_center, dtype=np.float32))
        return result


class AnimatedFixedIonizeSphere(FixedIonizeSphere):
    """动画固定位置电离球体"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 时间更新器已经在ShaderSurface基类中添加了


# 便捷创建函数
def create_fixed_ionize_sphere(
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        u_range: tuple[float, float] = (0, TAU),
        v_range: tuple[float, float] = (0, PI),
        resolution: tuple[int, int] = (64, 64),
        brightness: float = 1.5,
        animated: bool = True,
        **kwargs
) -> FixedIonizeSphere:
    """创建固定位置电离球体的便捷函数"""
    if animated:
        return AnimatedFixedIonizeSphere(
            radius=radius,
            center=center,
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            brightness=brightness,
            **kwargs
        )
    else:
        return FixedIonizeSphere(
            radius=radius,
            center=center,
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            brightness=brightness,
            **kwargs
        )


def create_animated_fixed_ionize_sphere(
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        u_range: tuple[float, float] = (0, TAU),
        v_range: tuple[float, float] = (0, PI),
        resolution: tuple[int, int] = (64, 64),
        brightness: float = 1.5,
        **kwargs
) -> AnimatedFixedIonizeSphere:
    """创建动画固定位置电离球体的便捷函数"""
    return AnimatedFixedIonizeSphere(
        radius=radius,
        center=center,
        u_range=u_range,
        v_range=v_range,
        resolution=resolution,
        brightness=brightness,
        **kwargs
    )
