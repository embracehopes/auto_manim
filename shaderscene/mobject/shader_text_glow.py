"""
ShaderTextGlow - 基于 GLSL Shader 的文字辉光效果

使用 GPU shader 实现真正的高斯模糊辉光，而非多层模拟

使用示例：
    from shader_text_glow import ShaderTextGlow, create_glowing_text
    
    # 方法1: 使用 ShaderTextGlow 包装现有文字
    text = Text("Hello", font="STKaiti")
    glow = ShaderTextGlow(text, glow_radius=0.1, glow_intensity=1.5)
    self.add(glow, text)
    
    # 方法2: 使用便捷函数创建辉光文字
    glowing_text = create_glowing_text("你好", glow_radius=0.1)
    self.add(glowing_text)
"""

from __future__ import annotations
import numpy as np
import moderngl
from pathlib import Path

from manimlib import *
from manimlib.mobject.types.point_cloud_mobject import PMobject
from manimlib.utils.color import color_to_rgba


__all__ = [
    "TextBloomPointCloud",
    "ShaderTextGlow",
    "create_glowing_text",
    "create_glowing_tex",
]


class TextBloomPointCloud(PMobject):
    """
    使用 GPU Shader 渲染辉光的点云
    
    每个点会被几何着色器扩展为一个辉光四边形，
    片段着色器使用多重高斯模糊实现柔和的辉光效果
    """
    
    shader_folder: str = str(Path(Path(__file__).parent.parent, "text_bloom_shader"))
    render_primitive: int = moderngl.POINTS
    
    data_dtype = [
        ("point", np.float32, (3,)),
        ("rgba", np.float32, (4,)),
        ("glow_radius", np.float32, (1,)),
    ]
    
    def __init__(
        self,
        points: np.ndarray,
        colors: np.ndarray = None,
        glow_radius: float = 0.08,
        glow_intensity: float = 1.2,
        glow_softness: float = 0.5,
        white_core_strength: float = 0.3,
        falloff_power: float = 1.5,
        **kwargs,
    ) -> None:
        """
        参数：
        - points: (N, 3) 点坐标数组
        - colors: (N, 4) RGBA 颜色数组，默认白色
        - glow_radius: 辉光半径（扩散范围）
        - glow_intensity: 辉光强度
        - glow_softness: 辉光柔和度 (0.3-0.8)
        - white_core_strength: 白色核心强度 (0.2-0.6)
        - falloff_power: 边缘衰减指数 (1.0-3.0)
        """
        self._glow_radius = glow_radius
        self._glow_intensity = glow_intensity
        self._glow_softness = glow_softness
        self._white_core_strength = white_core_strength
        self._falloff_power = falloff_power
        
        super().__init__(**kwargs)
        
        # 设置点数据
        self.set_points(points)
        
        # 设置颜色
        if colors is None:
            colors = np.tile([1.0, 1.0, 1.0, 1.0], (len(points), 1)).astype(np.float32)
        self.data["rgba"][:] = colors
        
        # 设置辉光半径
        self.data["glow_radius"][:, 0] = glow_radius
    
    def init_uniforms(self) -> None:
        super().init_uniforms()
        self.uniforms["glow_intensity"] = float(self._glow_intensity)
        self.uniforms["glow_softness"] = float(self._glow_softness)
        self.uniforms["white_core_strength"] = float(self._white_core_strength)
        self.uniforms["falloff_power"] = float(self._falloff_power)
    
    def set_glow_intensity(self, value: float) -> "TextBloomPointCloud":
        self._glow_intensity = value
        self.uniforms["glow_intensity"] = float(value)
        return self
    
    def set_glow_softness(self, value: float) -> "TextBloomPointCloud":
        self._glow_softness = value
        self.uniforms["glow_softness"] = float(value)
        return self
    
    def set_glow_radius(self, value: float) -> "TextBloomPointCloud":
        self._glow_radius = value
        self.data["glow_radius"][:, 0] = value
        return self
    
    def set_white_core_strength(self, value: float) -> "TextBloomPointCloud":
        self._white_core_strength = value
        self.uniforms["white_core_strength"] = float(value)
        return self
    
    def set_colors(self, colors: np.ndarray) -> "TextBloomPointCloud":
        if len(colors) == len(self.data["rgba"]):
            self.data["rgba"][:] = colors
        return self


class ShaderTextGlow(Group):
    """
    为 Text/Tex 对象添加基于 Shader 的辉光效果
    
    从文字轮廓采样点，使用 GPU shader 渲染柔和辉光
    """
    
    def __init__(
        self,
        mobject: "Mobject",
        glow_color=WHITE,
        glow_radius: float = 0.08,
        glow_intensity: float = 1.2,
        glow_softness: float = 0.5,
        white_core_strength: float = 0.35,
        falloff_power: float = 1.5,
        sample_rate: float = 30.0,  # 每单位长度采样点数
        min_samples: int = 100,
        max_samples: int = 2000,
        **kwargs,
    ):
        """
        参数：
        - mobject: 要添加辉光的对象 (Text, Tex, VMobject)
        - glow_color: 辉光颜色
        - glow_radius: 辉光半径
        - glow_intensity: 辉光强度
        - glow_softness: 辉光柔和度
        - white_core_strength: 白色核心强度
        - falloff_power: 边缘衰减
        - sample_rate: 采样密度
        """
        super().__init__(**kwargs)
        
        self.target = mobject
        self._glow_color = color_to_rgba(glow_color)
        self._glow_radius = glow_radius
        self._glow_intensity = glow_intensity
        self._glow_softness = glow_softness
        self._white_core_strength = white_core_strength
        self._falloff_power = falloff_power
        self._sample_rate = sample_rate
        self._min_samples = min_samples
        self._max_samples = max_samples
        
        self._build_glow()
    
    def _sample_mobject(self) -> np.ndarray:
        """从 mobject 轮廓采样点"""
        points_list = []
        
        for member in self.target.get_family():
            if not hasattr(member, "get_points") or not member.has_points():
                continue
            
            if hasattr(member, "get_num_curves"):
                # VMobject: 沿曲线均匀采样
                num_curves = member.get_num_curves()
                if num_curves > 0:
                    # 计算采样数量
                    perimeter = sum(
                        np.linalg.norm(member.get_nth_curve_points(i)[-1] - member.get_nth_curve_points(i)[0])
                        for i in range(min(num_curves, 50))
                    )
                    num_samples = int(perimeter * self._sample_rate)
                    num_samples = max(self._min_samples, min(num_samples, self._max_samples))
                    
                    # 采样
                    alphas = np.linspace(0, 1, num_samples, endpoint=False)
                    sampled = [member.point_from_proportion(a) for a in alphas]
                    points_list.extend(sampled)
            else:
                # 其他类型：使用原始点
                pts = member.get_points()
                stride = max(1, len(pts) // self._max_samples)
                points_list.extend(pts[::stride])
        
        if not points_list:
            return np.array([[0, 0, 0]], dtype=np.float32)
        
        return np.array(points_list, dtype=np.float32)
    
    def _build_glow(self):
        """构建辉光层"""
        points = self._sample_mobject()
        
        # 创建颜色数组
        colors = np.tile(self._glow_color, (len(points), 1)).astype(np.float32)
        
        # 创建辉光点云
        self.glow = TextBloomPointCloud(
            points=points,
            colors=colors,
            glow_radius=self._glow_radius,
            glow_intensity=self._glow_intensity,
            glow_softness=self._glow_softness,
            white_core_strength=self._white_core_strength,
            falloff_power=self._falloff_power,
        )
        
        self.add(self.glow)
    
    def set_glow_intensity(self, value: float) -> "ShaderTextGlow":
        self.glow.set_glow_intensity(value)
        return self
    
    def set_glow_radius(self, value: float) -> "ShaderTextGlow":
        self.glow.set_glow_radius(value)
        return self
    
    def set_glow_color(self, color) -> "ShaderTextGlow":
        self._glow_color = color_to_rgba(color)
        colors = np.tile(self._glow_color, (len(self.glow.data["rgba"]), 1)).astype(np.float32)
        self.glow.set_colors(colors)
        return self


def create_glowing_text(
    text: str,
    font: str = "STKaiti",
    font_size: int = 36,
    color=WHITE,
    glow_color=WHITE,
    glow_radius: float = 0.08,
    glow_intensity: float = 1.2,
    glow_softness: float = 0.5,
    **kwargs,
) -> Group:
    """
    创建带辉光的文字（便捷函数）
    
    返回 Group 包含辉光层和文字
    """
    text_obj = Text(text, font=font, font_size=font_size, color=color)
    
    glow = ShaderTextGlow(
        text_obj,
        glow_color=glow_color,
        glow_radius=glow_radius,
        glow_intensity=glow_intensity,
        glow_softness=glow_softness,
        **kwargs,
    )
    
    result = Group(glow, text_obj)
    return result


def create_glowing_tex(
    tex_string: str,
    font_size: int = 36,
    color=WHITE,
    glow_color=WHITE,
    glow_radius: float = 0.08,
    glow_intensity: float = 1.2,
    **kwargs,
) -> Group:
    """
    创建带辉光的 LaTeX 公式（便捷函数）
    """
    tex_obj = Tex(tex_string, font_size=font_size, color=color)
    
    glow = ShaderTextGlow(
        tex_obj,
        glow_color=glow_color,
        glow_radius=glow_radius,
        glow_intensity=glow_intensity,
        **kwargs,
    )
    
    result = Group(glow, tex_obj)
    return result
