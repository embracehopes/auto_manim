#!/usr/bin/env python3

import numpy as np
from manimlib import *
from pathlib import Path

# 先导入现有的shader基类
from mobject.sphere_surface import ShaderSurface

class GlassCubeComplexSquare(ShaderSurface):
    """显示复杂3D玻璃立方体效果的正方形面，确保所有面都能正确显示"""
    shader_folder: str = str(Path(Path(__file__).parent.parent / "glass_cube_complex_shader"))
    
    def __init__(self, **kwargs):
        """
        创建一个显示复杂3D玻璃立方体效果的正方形面
        使用简化的参数方程确保每个面都能正确渲染
        """
        
        def square_func(u, v):
            """简化的正方形参数方程，确保法向量正确"""
            return [u, v, 0]
        
        # 设置Surface的基本参数，增加分辨率以确保渲染质量
        kwargs.setdefault("u_range", (-1, 1))
        kwargs.setdefault("v_range", (-1, 1))
        kwargs.setdefault("resolution", (32, 32))  # 增加分辨率
        kwargs.setdefault("brightness", 1.5)
        
        super().__init__(
            uv_func=square_func,
            **kwargs
        )
        
        # 强制设置双面渲染，确保所有角度都能看到效果
        self.always_update = True
        
        # 设置shader uniforms
        self.set_uniforms({
            "resolution": [1080.0, 1080.0],  # 使用正方形分辨率
            "use_orthographic": 1
        })
