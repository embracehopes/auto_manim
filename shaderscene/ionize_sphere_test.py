"""
球面电离效果(IonizeSphere)shader测试
基于原始的Ionize效果，将shader效果映射到球面上
shader效果基于绝对世界坐标，不会因为球体移动而改变
"""

from manimlib import *
import sys
import os
import numpy as np

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mobject.ionize_sphere import create_ionize_sphere, create_animated_ionize_sphere

class IonizeSphereTest(Scene):
    """电离球体效果测试"""
    
    def construct(self):
        # 创建电离球体
        ionize_sphere = create_ionize_sphere(
            radius=1.5,
            center=[0, 0, 0],
            resolution=(80, 60),
            brightness=1.2
        )
        
        # 添加到场景
        self.add(ionize_sphere)
        
        # 让电离动画播放
        self.wait(8)


class AnimatedIonizeSphereTest(Scene):
    """动画电离球体效果测试"""
    
    def construct(self):
        # 创建动画电离球体
        animated_ionize_sphere = create_animated_ionize_sphere(
            radius=1.5,
            center=[0, 0, 0],
            resolution=(80, 60),
            brightness=4
        )
        
        # 添加到场景
        self.add(animated_ionize_sphere)
        
        # 等待动画播放
        self.wait(5)
        
        # 测试变换：旋转 - shader效果不应该改变
        self.play(
            Rotate(animated_ionize_sphere, PI/3, axis=UP),
            run_time=3
        )
        
        # 测试变换：缩放
        self.play(
            animated_ionize_sphere.animate.scale(1.5),
            run_time=3
        )
        
        # 测试变换：移动 - 关键测试！shader效果应该保持在绝对位置
        self.play(
            animated_ionize_sphere.animate.shift(RIGHT * 2),
            run_time=3
        )
        
        # 再移动回来
        self.play(
            animated_ionize_sphere.animate.shift(LEFT * 2),
            run_time=3
        )
        
        # 向上移动
        self.play(
            animated_ionize_sphere.animate.shift(UP * 1.5),
            run_time=3
        )
        
        self.wait(5)


class ComparisonTest(Scene):
    """对比测试：显示多个电离球体"""
    
    def construct(self):
        # 创建三个不同位置的电离球体
        sphere1 = create_animated_ionize_sphere(
            radius=1.0,
            center=[-2.5, 0, 0],
            resolution=(60, 45),
            brightness=1.2
        )
        
        sphere2 = create_animated_ionize_sphere(
            radius=1.0,
            center=[0, 0, 0],
            resolution=(60, 45),
            brightness=1.2
        )
        
        sphere3 = create_animated_ionize_sphere(
            radius=1.0,
            center=[2.5, 0, 0],
            resolution=(60, 45),
            brightness=1.2
        )
        
        # 添加到场景
        self.add(sphere1, sphere2, sphere3)
        
        # 播放动画，观察shader效果是否基于绝对坐标
        self.wait(8)
        
        # 同时移动所有球体，shader效果应该保持在原位置
        self.play(
            sphere1.animate.shift(UP * 1.5),
            sphere2.animate.shift(UP * 1.5),
            sphere3.animate.shift(UP * 1.5),
            run_time=4
        )
        
        self.wait(5)


class MinimalIonizeSphereTest(Scene):
    """最小化的电离球体测试"""
    
    def construct(self):
        # 创建最简单的电离球体效果
        ionize_sphere = create_ionize_sphere(
            radius=1.2,
            center=[0, 0, 0],
            resolution=(32, 24),
            brightness=1.0
        )
        
        # 添加到场景
        self.add(ionize_sphere)
        
        # 播放动画
        self.wait(6)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  MinimalIonizeSphereTest")
