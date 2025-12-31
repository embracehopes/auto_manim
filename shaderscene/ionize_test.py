"""
电离效果(Ionize)shader测试
基于XorDev的Ionize效果：https://x.com/XorDev/status/1921224922166104360
"""

from manimlib import *
import sys
import os
import numpy as np

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mobject.ionize_surface import create_ionize_surface, create_animated_ionize_surface

class IonizeTest(Scene):
    """电离效果测试"""
    
    def construct(self):
        # 创建电离表面
        ionize_surface = create_ionize_surface(
            u_range=(-3, 3),
            v_range=(-2, 2),
            resolution=(80, 60),
            brightness=1.2
        )
        
        # 添加到场景
        self.add(ionize_surface)
        
        # 让电离动画播放
        self.wait(8)


class AnimatedIonizeTest(Scene):
    """动画电离效果测试"""
    
    def construct(self):
        # 创建动画电离表面
        animated_ionize = create_animated_ionize_surface(
            u_range=(-3, 3),
            v_range=(-2, 2),
            resolution=(80, 60),
            brightness=1.5
        )
        
        # 添加到场景
        self.add(animated_ionize)
        
        # 等待动画播放
        self.wait(10)
        
        # 测试变换：旋转
        self.play(
            Rotate(animated_ionize, PI/6, axis=UP),
            run_time=3
        )
        
        # 测试变换：缩放
        self.play(
            animated_ionize.animate.scale(1.5),
            run_time=3
        )
        
        # 测试变换：移动
        self.play(
            animated_ionize.animate.shift(RIGHT * 2),
            run_time=3
        )
        
        self.wait(5)


class MinimalIonizeTest(Scene):
    """最小化的电离测试"""
    
    def construct(self):
        # 创建最简单的电离效果
        ionize = create_ionize_surface(
            u_range=(-2, 2),
            v_range=(-2, 2),
            resolution=(32, 32),
            brightness=1.0
        )
        
        # 缩放到适当大小
        ionize.scale(2)
        
        # 添加到场景
        self.add(ionize)
        
        # 播放动画
        self.wait(6)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py AnimatedIonizeTest ")