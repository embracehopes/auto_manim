#!/usr/bin/env python3

import numpy as np
from manimlib import *
from pathlib import Path

from .sphere_surface import ShaderSurface
class CubeEnjoyerSquare(Surface):
    """显示cube enjoyer效果的正方形面 - 所有面都显示相同的正视效果"""
    shader_folder: str = str(Path(Path(__file__).parent.parent / "cube_enjoyer_shader"))
    
    def __init__(self, **kwargs):
        """
        创建一个显示cube enjoyer效果的正方形面
        所有面都显示相同的正视角度效果
        """
        
        # 设置Surface的基本参数
        kwargs.setdefault("u_range", (-1, 1))
        kwargs.setdefault("v_range", (-1, 1))
        kwargs.setdefault("resolution", (51, 51))
        
        super().__init__(**kwargs)
        
        # 设置shader uniforms - 使用正交投影
        self.set_uniforms({
            "time": 0.0,
            "brightness": 1.5,
            "resolution": [1920.0, 1080.0],
            "use_orthographic": 1  # 启用正交投影
        })
        
        # 添加时间更新器
        self.add_updater(lambda m, dt: m.increment_time(dt))
    
    def uv_func(self, u, v):
        """正方形参数方程 - Surface类要求的方法"""
        return [u, v, 0]
    
    def increment_time(self, dt):
        """更新时间uniform"""
        self.uniforms["time"] += dt
        return self
