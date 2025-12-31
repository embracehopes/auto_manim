import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from manimlib import *
import numpy as np

class SimpleGeodesicTest(Scene):
    """简单的测地线球面测试"""
    
    def construct(self):
        # 导入球面表面类
        from mobject.sphere_surface import SphereSurface
        
        # 创建球面
        sphere = SphereSurface(
            radius=1.5,
            resolution=(60, 60),
            brightness=1.8
        )
        
        # 添加到场景
        self.add(sphere)
        
        # 简单的旋转动画
        self.play(
            Rotate(sphere, TAU, axis=OUT),
            run_time=6,
            rate_func=linear
        )

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")