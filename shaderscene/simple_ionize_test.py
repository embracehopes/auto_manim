"""
简单电离效果测试 - 直接继承Surface
"""

from manimlib import *
import sys
import os
import numpy as np

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mobject.ionize_surface import create_ionize_surface

class SimpleIonizeTest(ThreeDScene):
    """简单电离效果测试"""
    
    def construct(self):
        # 创建简单电离表面
        ionize = create_ionize_surface(
            u_range=(-2, 2),
            v_range=(-2, 2),
            resolution=(32, 32),
            brightness=1.2,
            animated=True
        )
        
        # 缩放到适当大小
        ionize.scale(2)
        
        # 添加到场景
        self.add(ionize)
        
        # 播放动画
        self.wait(8)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")
