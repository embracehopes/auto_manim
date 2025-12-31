"""
完整的球面电离效果测试
包含原始平面版本和新的球面版本的对比
演示shader效果如何在绝对坐标中保持固定
"""

from manimlib import *
import sys
import os
import numpy as np

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mobject.ionize_surface import create_ionize_surface
from mobject.ionize_sphere import create_ionize_sphere
from mobject.fixed_ionize_sphere import create_fixed_ionize_sphere

class ComprehensiveIonizeTest(Scene):
    """综合电离效果测试"""
    
    def construct(self):
        # 创建原始平面电离效果作为参考
        plane_ionize = create_ionize_surface(
            u_range=(-1.5, 1.5),
            v_range=(-1.5, 1.5),
            resolution=(40, 40),
            brightness=1.0
        )
        plane_ionize.shift(LEFT * 3)
        
        # 创建球面电离效果
        sphere_ionize = create_ionize_sphere(
            radius=1.2,
            center=[0, 0, 0],
            resolution=(60, 45),
            brightness=1.2
        )
        
        # 创建固定位置的球面电离效果
        fixed_sphere_ionize = create_fixed_ionize_sphere(
            radius=1.2,
            center=[3, 0, 0],
            resolution=(60, 45),
            brightness=1.2
        )
        
        # 添加到场景
        self.add(plane_ionize, sphere_ionize, fixed_sphere_ionize)
        
        # 播放基础动画
        self.wait(5)
        
        # 测试移动 - 观察shader效果的不同行为
        self.play(
            plane_ionize.animate.shift(UP * 1.5),
            sphere_ionize.animate.shift(UP * 1.5),
            fixed_sphere_ionize.animate.shift(UP * 1.5),
            run_time=4
        )
        
        self.wait(3)
        
        # 测试旋转
        self.play(
            Rotate(plane_ionize, PI/4, axis=OUT),
            Rotate(sphere_ionize, PI/3, axis=UP),
            Rotate(fixed_sphere_ionize, PI/3, axis=UP),
            run_time=4
        )
        
        self.wait(5)


class MovingSpheresTest(Scene):
    """移动球体测试 - 重点演示固定shader效果"""
    
    def construct(self):
        # 创建多个球体在不同位置
        spheres = []
        positions = [
            [-3, -1.5, 0],
            [0, -1.5, 0], 
            [3, -1.5, 0]
        ]
        
        for i, pos in enumerate(positions):
            sphere = create_fixed_ionize_sphere(
                radius=1.0,
                center=pos,
                resolution=(50, 40),
                brightness=4
            )
            spheres.append(sphere)
            self.add(sphere)
        
        # 等待基础动画
        self.wait(3)
        
        # 让球体在场景中移动，观察shader效果是否保持固定
        animations = []
        for i, sphere in enumerate(spheres):
            # 创建圆形运动路径
            center_x = positions[i][0]
            animations.append(
                sphere.animate.shift(UP * 2 + RIGHT * np.sin(i * PI/3))
            )
        
        self.play(*animations, run_time=4)
        
        # 继续移动
        animations = []
        for i, sphere in enumerate(spheres):
            animations.append(
                sphere.animate.shift(DOWN * 1 + LEFT * 1.5)
            )
        
        self.play(*animations, run_time=4)
        
        self.wait(5)


class RotatingSpheresTest(Scene):
    """旋转球体测试"""
    
    def construct(self):
        # 创建一个中心球体
        center_sphere = create_fixed_ionize_sphere(
            radius=1.5,
            center=[0, 0, 0],
            resolution=(80, 60),
            brightness=1.5
        )
        
        self.add(center_sphere)
        self.wait(3)
        
        # 连续旋转测试
        self.play(
            Rotate(center_sphere, PI, axis=UP),
            run_time=4
        )
        
        self.play(
            Rotate(center_sphere, PI, axis=RIGHT),
            run_time=4
        )
        
        # 同时旋转和移动
        self.play(
            Rotate(center_sphere, TAU, axis=OUT),
            center_sphere.animate.shift(RIGHT * 2),
            run_time=6
        )
        
        self.wait(3)


class ScalingTest(Scene):
    """缩放测试"""
    
    def construct(self):
        # 创建球体
        scaling_sphere = create_fixed_ionize_sphere(
            radius=1.0,
            center=[0, 0, 0],
            resolution=(60, 45),
            brightness=4
        )
        
        self.add(scaling_sphere)
        self.wait(3)
        
        # 缩放测试
        self.play(
            scaling_sphere.animate.scale(2),
            run_time=3
        )
        
        self.wait(2)
        
        self.play(
            scaling_sphere.animate.scale(0.5),
            run_time=3
        )
        
        self.wait(2)
        
        # 同时缩放和移动
        self.play(
            scaling_sphere.animate.scale(1.5).shift(UP * 2),
            run_time=4
        )
        
        self.wait(3)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ScalingTest")
