"""
位置无关的球面多面体 Shader 实现

解决 SphericalPolyhedraSphere 类中 shader 效果随位置变化的问题
通过使用本地坐标系替代世界坐标系来实现位置无关的 shader 效果
"""

import sys
import os
import numpy as np
from pathlib import Path

from manimlib import *


class FixedShaderSurface(Surface):
    """修复版的着色器表面基类"""
    shader_folder: str = str(Path(Path(__file__).parent.parent / "fixed_spherical_polyhedra_shader"))

    def __init__(
            self,
            uv_func,
            u_range=(0, 1),
            v_range=(0, 1),
            brightness=1.5,
            **kwargs
    ):
        self.passed_uv_func = uv_func
        super().__init__(u_range=u_range, v_range=v_range, **kwargs)

        # 初始化shader uniforms - 修复：使用字典方式
        self.uniforms.update({
            "time": 0.0,
            "brightness": float(brightness)
        })

        # 添加时间更新器
        self.add_updater(lambda m, dt: m.increment_time(dt))

    def uv_func(self, u, v):
        return self.passed_uv_func(u, v)

    def increment_time(self, dt):
        if "time" in self.uniforms:
            self.uniforms["time"] += 1 * dt
        return self


class FixedSphericalPolyhedraSphere(FixedShaderSurface):
    """
    修复版本的球面多面体，解决 shader 效果随位置变化的问题
    
    主要改进：
    1. 使用本地坐标系进行 shader 计算
    2. 自动更新球体中心位置的 uniform 变量
    3. 确保移动球体时 shader 效果保持一致
    """
    
    def __init__(
            self,
            radius: float = 1.0,
            center=None,
            u_range: tuple = (0, TAU),
            v_range: tuple = (0, PI),
            resolution: tuple = (64, 64),
            brightness: float = 1.5,
            time_scale: float = 1.0,
            **kwargs
    ):
        if center is None:
            center = [0, 0, 0]
            
        self.radius = radius
        self.center = np.array(center)
        self.time_scale = time_scale
        
        def sphere_func(u, v):
            # 球面参数方程
            x = self.radius * np.sin(v) * np.cos(u) + self.center[0]
            y = self.radius * np.sin(v) * np.sin(u) + self.center[1]
            z = self.radius * np.cos(v) + self.center[2]
            return np.array([x, y, z])
        
        super().__init__(
            uv_func=sphere_func,
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            brightness=brightness,
            **kwargs
        )
        
        # 设置初始 uniforms（关键修复：添加球体中心）- 修复：使用字典方式
        self.uniforms.update({
            "time": 0.0,
            "brightness": float(brightness),
            "sphere_center": self.center.astype(np.float32),
            "resolution": np.array([1920.0, 1080.0], dtype=np.float32)
        })
        
        # 添加时间更新器
        self.add_updater(lambda m, dt: m.increment_time(dt))
    
    def increment_time(self, dt):
        """重写时间增量方法以支持时间缩放"""
        if "time" in self.uniforms:
            self.uniforms["time"] += self.time_scale * dt
        return self
    
    def move_to(self, point):
        """重写 move_to 方法，确保更新球体中心的 uniform 变量"""
        result = super().move_to(point)
        # 更新球体中心位置 - 修复：使用字典方式
        self.center = np.array(self.get_center())
        self.uniforms.update({
            "sphere_center": self.center.astype(np.float32)
        })
        return result
    
    def shift(self, vector):
        """重写 shift 方法，确保更新球体中心的 uniform 变量"""
        result = super().shift(vector)
        # 更新球体中心位置 - 修复：使用字典方式
        self.center = np.array(self.get_center())
        self.uniforms.update({
            "sphere_center": self.center.astype(np.float32)
        })
        return result
    
    def set_polyhedron_type(self, poly_type: int):
        """
        手动设置多面体类型 (0-3)
        0: 十二面体 (Dodecahedron)
        1: 二十面体 (Icosahedron) 
        2: 立方体 (Cube)
        3: 八面体 (Octahedron)
        """
        # 通过修改时间来控制显示的多面体类型 - 修复：使用字典方式
        target_time = (poly_type / 0.2) - 10.0
        self.uniforms.update({
            "time": target_time
        })
        return self
    
    def set_animation_speed(self, speed: float):
        """设置动画速度"""
        self.time_scale = speed
        return self


class FixedAnimatedPolyhedraSphere(FixedSphericalPolyhedraSphere):
    """
    修复版本的动画球面多面体，包含自动旋转功能
    """
    
    def __init__(
        self,
        radius: float = 1.0,
        center=None,
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


class FixedStaticPolyhedraSphere(FixedSphericalPolyhedraSphere):
    """
    修复版本的静态球面多面体，可以固定显示某种特定的多面体类型
    """
    
    def __init__(
        self,
        polyhedron_type: str = "dodecahedron",
        radius: float = 1.0,
        center=None,
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


# 便捷的创建函数
def create_fixed_dodecahedron_sphere(radius=1.0, **kwargs):
    """创建修复版本的十二面体球面"""
    return FixedStaticPolyhedraSphere("dodecahedron", radius=radius, **kwargs)

def create_fixed_icosahedron_sphere(radius=1.0, **kwargs):
    """创建修复版本的二十面体球面"""
    return FixedStaticPolyhedraSphere("icosahedron", radius=radius, **kwargs)

def create_fixed_cube_sphere(radius=1.0, **kwargs):
    """创建修复版本的立方体球面"""
    return FixedStaticPolyhedraSphere("cube", radius=radius, **kwargs)

def create_fixed_octahedron_sphere(radius=1.0, **kwargs):
    """创建修复版本的八面体球面"""
    return FixedStaticPolyhedraSphere("octahedron", radius=radius, **kwargs)

def create_fixed_animated_polyhedra_sphere(radius=1.0, **kwargs):
    """创建修复版本的动画球面多面体（自动循环切换）"""
    return FixedSphericalPolyhedraSphere(radius=radius, **kwargs)
