from manimlib import *
from numpy import *
from typing import Callable, Iterable, Tuple
from pathlib import Path

# 导入现有的ShaderSurface基类
from .sphere_surface import ShaderSurface

class IonizeSurface(ShaderSurface):
    """电离效果的着色器表面类，基于ShaderSurface"""
    shader_folder: str = str(Path(Path(__file__).parent.parent / "ionize_shader"))

    def __init__(
            self,
            u_range: tuple[float, float] = (-2, 2),
            v_range: tuple[float, float] = (-2, 2),
            resolution: tuple[int, int] = (64, 64),
            brightness: float = 1.0,
            **kwargs
    ):
        # 定义平面UV函数 - 创建一个平面来显示raymarching效果
        def plane_func(u, v):
            return np.array([u, v, 0])
        
        super().__init__(
            uv_func=plane_func,
            u_range=u_range,
            v_range=v_range,
            brightness=brightness,
            resolution=resolution,
            **kwargs
        )

        # 添加电离效果特定的uniforms
        self.set_uniform(resolution=np.array([800.0, 600.0], dtype=np.float32))

    def increment_time(self, dt):
        """更新时间uniform（覆盖父类方法）"""
        current_time = self.uniforms.get("time", 0.0)
        self.set_uniform(time=current_time + dt)
        return self


class AnimatedIonizeSurface(IonizeSurface):
    """动画电离表面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 时间更新器已经在ShaderSurface基类中添加了


# 便捷创建函数
def create_ionize_surface(
        u_range: tuple[float, float] = (-2, 2),
        v_range: tuple[float, float] = (-2, 2),
        resolution: tuple[int, int] = (64, 64),
        brightness: float = 1.0,
        animated: bool = True,
        **kwargs
) -> IonizeSurface:
    """创建电离表面的便捷函数"""
    if animated:
        return AnimatedIonizeSurface(
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            brightness=brightness,
            **kwargs
        )
    else:
        return IonizeSurface(
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            brightness=brightness,
            **kwargs
        )


def create_animated_ionize_surface(
        u_range: tuple[float, float] = (-2, 2),
        v_range: tuple[float, float] = (-2, 2),
        resolution: tuple[int, int] = (64, 64),
        brightness: float = 1.0,
        **kwargs
) -> AnimatedIonizeSurface:
    """创建动画电离表面的便捷函数"""
    return AnimatedIonizeSurface(
        u_range=u_range,
        v_range=v_range,
        resolution=resolution,
        brightness=brightness,
        **kwargs
    )
