"""
TextGlow - 使用已验证的 GlowWrapperEffect 为文字添加辉光

这是对 GlowWrapperEffect 的简单封装，专门用于文字辉光

使用示例：
    from text_glow import create_glow_text
    
    text = create_glow_text("你好", glow_size=0.1)
    self.add(text)
"""

from __future__ import annotations
from manimlib import *

import os
import sys

# 确保能导入 glow_wrapper
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from mobject.glow_wrapper import GlowWrapperEffect


__all__ = [
    "create_glow_text",
    "create_glow_tex",
    "TextGlow",
]


class TextGlow(Group):
    """
    文字辉光效果 - 基于 GlowWrapperEffect
    
    自动为 Text/Tex 添加辉光效果
    """
    
    def __init__(
        self,
        text_obj,
        glow_color=WHITE,
        glow_size: float = 0.4,         # 大半径
        glow_factor: float = 2.5,       # 中等衰减
        white_core_ratio: float = 0.08, # 很低的白色核心强度
        white_glow_ratio: float = 0.15, # 很低的白色辉光
        alpha: float = 0.35,            # 低透明度避免模糊
        render_mode: str = "point",     # 使用点模式
        **kwargs,
    ):
        super().__init__(**kwargs)
        
        # 创建辉光 - 减少采样密度，使用点模式
        self.glow = GlowWrapperEffect(
            text_obj,
            color=glow_color,
            alpha=alpha,
            size=glow_size,
            glow_factor=glow_factor,
            white_core_ratio=white_core_ratio,
            white_glow_ratio=white_glow_ratio,
            render_mode=render_mode,
            curve_sample_factor=30,      # 减少采样密度
            min_curve_samples=150,       # 降低最小采样数
            core_width_ratio=0.15,       # 小过渡区域
        )
        
        # 关闭深度测试，避免重叠辉光四边形产生棱刺
        self.glow.deactivate_depth_test()
        
        self.text = text_obj
        
        # 先添加辉光，再添加文字（确保文字在上层）
        self.add(self.glow, self.text)
    
    def set_glow_color(self, color):
        self.glow.set(color=color)
        return self
    
    def set_glow_size(self, size: float):
        self.glow.set(size=size)
        return self


def create_glow_text(
    text: str,
    font: str = "STKaiti",
    font_size: int = 36,
    color=WHITE,
    glow_color=WHITE,
    glow_size: float = 0.4,         # 大半径
    glow_factor: float = 2.5,       # 中等衰减
    white_core_ratio: float = 0.08, # 很低强度
    white_glow_ratio: float = 0.15,
    alpha: float = 0.35,
    **kwargs,
) -> TextGlow:
    """
    创建带辉光的文字
    
    参数：
    - text: 文字内容
    - glow_size: 辉光半径 (0.4 = 大范围)
    - alpha: 辉光透明度 (0.35 = 避免模糊)
    """
    text_obj = Text(text, font=font, font_size=font_size, color=color)
    
    return TextGlow(
        text_obj,
        glow_color=glow_color,
        glow_size=glow_size,
        glow_factor=glow_factor,
        white_core_ratio=white_core_ratio,
        white_glow_ratio=white_glow_ratio,
        alpha=alpha,
        **kwargs,
    )


def create_glow_tex(
    tex_string: str,
    font_size: int = 36,
    color=WHITE,
    glow_color=WHITE,
    glow_size: float = 0.12,
    glow_factor: float = 3.5,
    **kwargs,
) -> TextGlow:
    """
    创建带辉光的 LaTeX 公式
    """
    tex_obj = Tex(tex_string, font_size=font_size, color=color)
    
    return TextGlow(
        tex_obj,
        glow_color=glow_color,
        glow_size=glow_size,
        glow_factor=glow_factor,
        **kwargs,
    )
