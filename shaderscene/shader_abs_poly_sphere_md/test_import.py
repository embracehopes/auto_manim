#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# 打印当前工作目录
print(f"当前工作目录: {os.getcwd()}")
print(f"Python 路径: {sys.path[:3]}")  # 只打印前几个路径

try:
    print("尝试导入 manimlib...")
    import manimlib
    print("manimlib 导入成功!")
except Exception as e:
    print(f"manimlib 导入失败: {e}")

try:
    print("尝试导入 fixed_spherical_polyhedra...")
    from shadersence.mobject.fixed_spherical_polyhedra import FixedSphericalPolyhedraSphere
    print("fixed_spherical_polyhedra 导入成功!")
    
    # 尝试创建一个简单的实例
    print("尝试创建球体...")
    sphere = FixedSphericalPolyhedraSphere(radius=1.0)
    print("创建球体成功!")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
