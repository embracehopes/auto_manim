"""
简单的特殊测地线球面测试
验证新着色器的基本功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manimlib import *
from mobject.special_geodesic_sphere import SpecialGeodesicSphere

class SimpleSpecialGeodesicTest(Scene):
    """简单的特殊测地线球面测试"""
    
    def construct(self):
        # 创建特殊测地线球面
        sphere = SpecialGeodesicSphere(
            radius=2.0,
            resolution=(80, 80),
            brightness=1.6
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