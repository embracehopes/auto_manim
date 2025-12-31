#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最小化测试：验证修复后的球面多面体能否正常创建和显示
"""

import sys
import os

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from manimlib import *

try:
    from shadersence.mobject.fixed_spherical_polyhedra import FixedSphericalPolyhedraSphere
    print("✓ 成功导入 FixedSphericalPolyhedraSphere")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)


class MinimalTest(Scene):
    """最简单的测试场景"""
    def construct(self):
        # 创建一个简单的球体
        try:
            sphere = FixedSphericalPolyhedraSphere(
                radius=1.5,
                brightness=20,
                resolution=(40, 40)  # 降低分辨率加快渲染
            )
            print("✓ 成功创建球体")
            
            # 添加到场景
            self.add(sphere)
            print("✓ 成功添加球体到场景")
            
            # 简单等待
            self.wait(2)
            
            # 测试移动
            self.play(sphere.animate.shift(UP), run_time=1)
            print("✓ 成功移动球体")
            
            self.wait(2)
            
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("开始最小化测试...")
    print("运行命令: manimgl minimal_test.py MinimalTest")
