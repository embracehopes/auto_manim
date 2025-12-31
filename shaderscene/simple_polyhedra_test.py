"""
球面多面体简单测试

快速测试新创建的 SphericalPolyhedraSphere mobject
"""
# 添加父目录到路径

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manimlib import *
from mobject.spherical_polyhedra_sphere import *

class SimplePolyhedraTest(Scene):
    def construct(self):
        self.camera.frame.set_height(5.5)
        # 创建一个简单的自动循环球面多面体
        sphere = SphericalPolyhedraSphere(
            radius=2.0,
            brightness=40,
            resolution=(80, 80)  # 使用适中的分辨率
        ).move_to(UP*2)
        sphere.set_opacity(0.5)
        sphere2 = SphericalPolyhedraSphere(
            radius=2.0,
            center=OUT*2,
            brightness=2,
            resolution=(80, 80)  # 使用适中的分辨率
        )

        
        self.add(sphere,sphere2)
        self.wait(25)  # 等待25秒观察所有四种多面体效果

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")