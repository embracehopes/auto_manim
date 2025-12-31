from manimlib import *
from numpy import *
from typing import Callable, Iterable, Tuple
from pathlib import Path
from mobject.sphere_surface import ShaderSurface

class SphericalPolyhedraSphere(ShaderSurface):
    """
    使用球面多面体着色器的特殊球面
    基于 nimitz 的 Shadertoy 作品 "Spherical polyhedra"
    
    该球面可以在十二面体、二十面体、立方体和八面体之间自动循环切换
    """
    shader_folder: str = str(Path(Path(__file__).parent.parent / "spherical_polyhedra"))

    def __init__(
            self,
            radius: float = 1.0,
            center: Iterable[float] = [0, 0, 0],
            u_range: tuple[float, float] = (0, TAU),
            v_range: tuple[float, float] = (0, PI),
            resolution: tuple[int, int] = (64, 64),
            brightness: float = 1.5,
            time_scale: float = 1.0,
            **kwargs
    ):
        self.radius = radius
        self.center = np.array(center)
        self.time_scale = time_scale
        
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
        self.set_uniform(time=0.0)
        self.set_uniform(brightness=brightness)
        self.set_uniform(resolution=np.array([1920.0, 1080.0], dtype=np.float32))
        
        # 添加时间更新器
        self.add_updater(lambda m, dt: m.increment_time(dt))
    
    def increment_time(self, dt):
        """重写时间增量方法以支持时间缩放"""
        self.uniforms["time"] += self.time_scale * dt
        return self
    
    def set_polyhedron_type(self, poly_type: int):
        """
        手动设置多面体类型 (0-3)
        0: 十二面体 (Dodecahedron)
        1: 二十面体 (Icosahedron) 
        2: 立方体 (Cube)
        3: 八面体 (Octahedron)
        """
        # 通过修改时间来控制显示的多面体类型
        # 由于 shader 中是基于 floor((time+10.)*0.2) 来选择类型
        target_time = (poly_type / 0.2) - 10.0
        self.set_uniform(time=target_time)
        return self
    
    def set_animation_speed(self, speed: float):
        """设置动画速度"""
        self.time_scale = speed
        return self


class AnimatedPolyhedraSphere(SphericalPolyhedraSphere):
    """
    带有额外动画效果的球面多面体
    可以控制旋转、缩放等动画参数
    """
    
    def __init__(
        self,
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        brightness: float = 1.8,
        time_scale: float = 1.0,
        auto_rotate: bool = True,
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
        if auto_rotate:
            # 添加自动旋转
            self.add_updater(self.auto_rotation_updater)
    
    def auto_rotation_updater(self, mobject, dt):
        """自动旋转更新器"""
        rotation_speed = 0.5  # 调整旋转速度
        mobject.rotate(rotation_speed * dt, axis=UP)
        mobject.rotate(rotation_speed * dt * 0.7, axis=RIGHT)
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


class StaticPolyhedraSphere(SphericalPolyhedraSphere):
    """
    静态的球面多面体，可以固定显示某种特定的多面体类型
    """
    
    def __init__(
        self,
        polyhedron_type: str = "dodecahedron",
        radius: float = 1.0,
        center: Iterable[float] = [0, 0, 0],
        brightness: float = 1.5,
        **kwargs
    ):
        super().__init__(
            radius=radius,
            center=center,
            brightness=brightness,
            time_scale=0.0,  # 停止时间更新
            **kwargs
        )
        
        # 根据类型名称设置对应的多面体
        type_map = {
            "dodecahedron": 0,
            "icosahedron": 1, 
            "cube": 2,
            "octahedron": 3
        }
        
        if polyhedron_type in type_map:
            self.set_polyhedron_type(type_map[polyhedron_type])
        else:
            raise ValueError(f"Unknown polyhedron type: {polyhedron_type}")
    
    def increment_time(self, dt):
        """静态模式下不更新时间"""
        return self


class ComparativePolyhedraGroup(VGroup):
    """
    比较展示组，同时显示四种不同的多面体
    """
    
    def __init__(
        self,
        radius: float = 0.8,
        spacing: float = 3.0,
        brightness: float = 1.5,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # 创建四种不同的多面体
        polyhedra_types = ["dodecahedron", "icosahedron", "cube", "octahedron"]
        positions = [
            [-spacing, spacing, 0],    # 左上
            [spacing, spacing, 0],     # 右上
            [-spacing, -spacing, 0],   # 左下
            [spacing, -spacing, 0]     # 右下
        ]
        
        for i, (poly_type, pos) in enumerate(zip(polyhedra_types, positions)):
            sphere = StaticPolyhedraSphere(
                polyhedron_type=poly_type,
                radius=radius,
                center=pos,
                brightness=brightness
            )
            
            # 添加标签
            label = Text(poly_type.capitalize(), font_size=24)
            label.next_to(sphere, DOWN, buff=0.3)
            
            self.add(sphere, label)


# 便捷的创建函数
def create_dodecahedron_sphere(radius=1.0, **kwargs):
    """创建十二面体球面"""
    return StaticPolyhedraSphere("dodecahedron", radius=radius, **kwargs)

def create_icosahedron_sphere(radius=1.0, **kwargs):
    """创建二十面体球面"""
    return StaticPolyhedraSphere("icosahedron", radius=radius, **kwargs)

def create_cube_sphere(radius=1.0, **kwargs):
    """创建立方体球面"""
    return StaticPolyhedraSphere("cube", radius=radius, **kwargs)

def create_octahedron_sphere(radius=1.0, **kwargs):
    """创建八面体球面"""
    return StaticPolyhedraSphere("octahedron", radius=radius, **kwargs)

def create_animated_polyhedra_sphere(radius=1.0, **kwargs):
    """创建动画球面多面体（自动循环切换）"""
    return SphericalPolyhedraSphere(radius=radius, **kwargs)
