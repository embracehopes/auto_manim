"""
特殊测地线球面着色器演示
基于高级 Shadertoy 代码的复杂几何效果
包含：
- 20面体域镜像技术
- 测地线三角化平铺
- 动态六边形细分
- 光谱颜色调色板
- 复杂的边缘检测
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manimlib import *
from mobject.special_geodesic_sphere import (
    SpecialGeodesicSphere,
    AnimatedGeodesicSphere,
    MultiScaleGeodesicSphere,
    create_special_geodesic_sphere,
    create_animated_geodesic_sphere,
    create_multiscale_geodesic_sphere
)


class SpecialGeodesicDemo(Scene):
    """展示特殊测地线球面的基本效果"""
    
    def construct(self):
        # 创建特殊测地线球面
        sphere = create_special_geodesic_sphere(
            radius=2.5,
            resolution=(120, 120),
            brightness=1.6
        )
        
        # 添加到场景
        self.add(sphere)
        
        # 简单的旋转展示
        self.play(
            Rotate(sphere, TAU, axis=OUT),
            run_time=8,
            rate_func=linear
        )
        
        # 缩放动画
        self.play(
            sphere.animate.scale(1.3),
            run_time=2
        )
        
        self.play(
            sphere.animate.scale(0.8),
            run_time=2
        )


class AnimatedGeodesicDemo(Scene):
    """展示动画测地线球面"""
    
    def construct(self):
        # 创建动画球面
        sphere = create_animated_geodesic_sphere(
            radius=2.2,
            animation_speed=1.5,
            resolution=(100, 100),
            brightness=1.8
        )
        
        self.add(sphere)
        
        # 让球面自己动画，同时进行旋转
        self.play(
            Rotate(sphere, TAU * 2, axis=UP),
            run_time=12,
            rate_func=linear
        )


class MultiScaleGeodesicDemo(Scene):
    """展示多尺度测地线球面"""
    
    def construct(self):
        # 创建多尺度球面
        sphere = create_multiscale_geodesic_sphere(
            radius=2.0,
            subdivision_range=(1.5, 5.0),
            subdivision_speed=0.6,
            resolution=(140, 140),
            brightness=1.7
        )
        
        self.add(sphere)
        
        # 复杂的运动轨迹
        self.play(
            sphere.animate.shift(LEFT * 2),
            run_time=3
        )
        
        self.play(
            sphere.animate.shift(RIGHT * 4),
            run_time=3
        )
        
        self.play(
            sphere.animate.shift(LEFT * 2),
            Rotate(sphere, TAU, axis=RIGHT),
            run_time=4
        )


class ComparisonDemo(Scene):
    """对比不同类型的测地线球面"""
    
    def construct(self):
        # 创建三个不同的球面
        sphere1 = create_special_geodesic_sphere(
            radius=1.3,
            center=[-3, 0, 0],
            resolution=(80, 80),
            brightness=1.4
        )
        
        sphere2 = create_animated_geodesic_sphere(
            radius=1.3,
            center=[0, 0, 0],
            animation_speed=2.0,
            resolution=(80, 80),
            brightness=1.6
        )
        
        sphere3 = create_multiscale_geodesic_sphere(
            radius=1.3,
            center=[3, 0, 0],
            subdivision_range=(2.0, 4.5),
            subdivision_speed=1.0,
            resolution=(80, 80),
            brightness=1.8
        )
        
        spheres = Group(sphere1, sphere2, sphere3)
        
        # 依次显示
        self.play(
            FadeIn(sphere1),
            run_time=1
        )
        self.wait(1)
        
        self.play(
            FadeIn(sphere2),
            run_time=1
        )
        self.wait(1)
        
        self.play(
            FadeIn(sphere3),
            run_time=1
        )
        self.wait(2)
        
        # 同时旋转所有球面
        self.play(
            Rotate(spheres, TAU, axis=UP),
            run_time=8,
            rate_func=linear
        )


class ComplexGeodesicShowcase(Scene):
    """复杂的测地线球面展示"""
    
    def construct(self):
        # 创建一个大的中心球面
        main_sphere = create_multiscale_geodesic_sphere(
            radius=2.5,
            subdivision_range=(2.0, 6.0),
            subdivision_speed=0.8,
            resolution=(150, 150),
            brightness=2.0
        )
        
        # 创建围绕的小球面
        small_spheres = Group()
        positions = [
            [3.5, 0, 0],
            [-3.5, 0, 0],
            [0, 3.5, 0],
            [0, -3.5, 0],
            [2.5, 2.5, 0],
            [-2.5, -2.5, 0]
        ]
        
        for i, pos in enumerate(positions):
            small_sphere = create_animated_geodesic_sphere(
                radius=0.8,
                center=pos,
                animation_speed=1.5 + i * 0.3,
                resolution=(60, 60),
                brightness=1.5
            )
            small_spheres.add(small_sphere)
        
        # 组合所有元素
        all_spheres = Group(main_sphere, small_spheres)
        
        # 动画序列
        self.play(
            FadeIn(main_sphere),
            run_time=2
        )
        
        self.play(
            FadeIn(small_spheres),
            run_time=2
        )
        
        # 复杂的组合运动
        self.play(
            Rotate(main_sphere, TAU, axis=OUT),
            Rotate(small_spheres, -TAU, axis=IN),
            run_time=10,
            rate_func=linear
        )
        
        # 缩放效果
        self.play(
            all_spheres.animate.scale(1.2),
            run_time=2
        )
        
        self.play(
            all_spheres.animate.scale(0.8),
            run_time=2
        )

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")