"""
最简单的等离子球测试
"""

from manimlib import *
import sys
import os
import numpy as np

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mobject.sphere_surface import SphereSurface

class BasicSphereTest(ThreeDScene):
    """最基础的球体测试"""
    
    def construct(self):
        # 设置3D场景

        
        # 创建基础球体
        sphere = SphereSurface(
            radius=2.0,
            center=[0, 0, 0],
            brightness=1.5
        )
        sphere.set_color(BLUE)
        
        self.add(sphere)
        self.wait(5)
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")