#!/usr/bin/env python3
"""
复变函数 Domain Coloring 可视化 - 基于 Shader 实现

相比原始 Python 实现的优势：
1. GPU 并行计算，性能大幅提升
2. 实时交互和动画
3. 高分辨率渲染无延迟

使用方法:
    manimgl complex_domain_demo.py ComplexDomainDemo
    manimgl complex_domain_demo.py ComplexDomainAnimation
    manimgl complex_domain_demo.py ComplexDomainInteractive
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from manimlib import *


class ComplexDomainShader(Mobject):
    """基于 Shader 的复变函数 Domain Coloring 可视化"""
    
    # Shader 文件夹路径
    shader_folder = os.path.join(os.path.dirname(__file__), "complex_domain_shader")
    
    # 函数类型映射
    FUNC_TYPES = {
        "z": 0,
        "z^2": 1,
        "z^3": 2,
        "1/z": 3,
        "exp(z)": 4,
        "sin(z)": 5,
        "cos(z)": 6,
        "z^n": 7,
        "(z^2-1)/(z^2+1)": 8,
        "sin(1/z)": 9,
        "exp(1/z)": 10,
        "z*sin(1/z)": 11,
        "polynomial": 12,
        "z^(1+10i)*cos(...)": 13,
        "ln(sin(z))+cos(z)": 14,
        "exp(z)*sin(z)": 15,
        "z^8+15z^4-16": 16,
        "(z+z^2/sin(z^4-1))^2": 17,
        "animated": 18,
    }
    
    def __init__(
        self,
        func_type: str = "z",
        scale_factor: float = 3.0,
        offset: np.ndarray = None,
        power: float = 2.0,
        brightness_scale: float = 0.8,
        saturation_scale: float = 1.5,
        opacity: float = 1.0,
        height: float = FRAME_HEIGHT,
        aspect_ratio: float = 16 / 9,
        root_a: np.ndarray = None,
        root_b: np.ndarray = None,
        root_c: np.ndarray = None,
        **kwargs,
    ):
        self.func_type = func_type
        self.scale_factor = scale_factor
        self.offset = offset if offset is not None else np.array([0.0, 0.0, 0.0])
        self.power = power
        self.brightness_scale = brightness_scale
        self.saturation_scale = saturation_scale
        self._opacity = opacity
        self.aspect_ratio = aspect_ratio
        self.root_a = root_a if root_a is not None else np.array([1.0, 0.0])
        self.root_b = root_b if root_b is not None else np.array([-1.0, 0.0])
        self.root_c = root_c if root_c is not None else np.array([0.0, 1.0])
        
        # 设置顶点数据类型：只需要 point 属性（不使用 rgba，避免 KeyError）
        self.data_dtype = [("point", np.float32, (3,))]
        
        super().__init__(**kwargs)
        self.set_height(height, stretch=True)
        self.set_width(height * aspect_ratio, stretch=True)
    
    def init_data(self, length: int = 4) -> None:
        super().init_data(length=length)
        self.data["point"][:] = [UL, DL, UR, DR]
    
    def init_uniforms(self):
        super().init_uniforms()
        
        # 设置 uniforms
        func_index = self.FUNC_TYPES.get(self.func_type, 0)
        self.uniforms["func_type"] = float(func_index)
        self.uniforms["scale_factor"] = float(self.scale_factor)
        self.uniforms["offset"] = np.array(self.offset, dtype=np.float32)
        self.uniforms["power"] = float(self.power)
        self.uniforms["brightness_scale"] = float(self.brightness_scale)
        self.uniforms["saturation_scale"] = float(self.saturation_scale)
        self.uniforms["opacity"] = float(self._opacity)
        self.uniforms["time"] = 0.0
        self.uniforms["root_a"] = np.array(self.root_a, dtype=np.float32)
        self.uniforms["root_b"] = np.array(self.root_b, dtype=np.float32)
        self.uniforms["root_c"] = np.array(self.root_c, dtype=np.float32)
    
    def set_func_type(self, func_type: str):
        """设置函数类型"""
        self.func_type = func_type
        func_index = self.FUNC_TYPES.get(func_type, 0)
        self.uniforms["func_type"] = float(func_index)
        return self
    
    def set_scale(self, scale_factor: float):
        """设置缩放"""
        self.scale_factor = scale_factor
        self.uniforms["scale_factor"] = float(scale_factor)
        return self
    
    def set_offset(self, offset: np.ndarray):
        """设置偏移（复平面中心）"""
        self.offset = offset
        self.uniforms["offset"] = np.array(offset, dtype=np.float32)
        return self
    
    def set_power(self, power: float):
        """设置幂次"""
        self.power = power
        self.uniforms["power"] = float(power)
        return self
    
    def set_brightness(self, brightness: float):
        """设置亮度"""
        self.brightness_scale = brightness
        self.uniforms["brightness_scale"] = float(brightness)
        return self
    
    def set_saturation(self, saturation: float):
        """设置饱和度"""
        self.saturation_scale = saturation
        self.uniforms["saturation_scale"] = float(saturation)
        return self
    
    def set_roots(self, root_a=None, root_b=None, root_c=None):
        """设置多项式根"""
        if root_a is not None:
            self.root_a = root_a
            self.uniforms["root_a"] = np.array(root_a, dtype=np.float32)
        if root_b is not None:
            self.root_b = root_b
            self.uniforms["root_b"] = np.array(root_b, dtype=np.float32)
        if root_c is not None:
            self.root_c = root_c
            self.uniforms["root_c"] = np.array(root_c, dtype=np.float32)
        return self
    
    def increment_time(self, dt):
        """更新时间（用于动画）"""
        self.uniforms["time"] += dt
        return self
    
    def set_color(self, *args, **kwargs):
        return self


# ==================== 演示场景 ====================

class ComplexDomainDemo(Scene):
    """复变函数 Domain Coloring 演示 - 展示多个函数"""
    
    def construct(self):
        # 标题
        title = Text("Domain Coloring: 复变函数可视化 (GPU Shader)", font="STSong")
        title.scale(0.6).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # 函数列表
        functions = [
            ("z", r"f(z) = z"),
            ("z^2", r"f(z) = z^2"),
            ("z^3", r"f(z) = z^3"),
            ("1/z", r"f(z) = 1/z"),
            ("exp(z)", r"f(z) = e^z"),
            ("sin(z)", r"f(z) = \sin(z)"),
            ("cos(z)", r"f(z) = \cos(z)"),
            ("(z^2-1)/(z^2+1)", r"f(z) = \frac{z^2-1}{z^2+1}"),
            ("sin(1/z)", r"f(z) = \sin(1/z)"),
            ("exp(1/z)", r"f(z) = e^{1/z}"),
            ("z*sin(1/z)", r"f(z) = z\sin(1/z)"),
            ("exp(z)*sin(z)", r"f(z) = e^z \sin(z)"),
            ("z^8+15z^4-16", r"f(z) = z^8 + 15z^4 - 16"),
            ("ln(sin(z))+cos(z)", r"f(z) = \ln(\sin z) + \cos z"),
        ]
        
        # 创建 shader mobject
        domain = ComplexDomainShader(
            func_type="z",
            scale_factor=3.0,
            brightness_scale=1,
            saturation_scale=3.0,
            height=6.0,
        )
        domain.shift(DOWN * 0.3)
        
        # 公式标签
        label = Tex(r"f(z) = z", font_size=36)
        label.next_to(domain, DOWN, buff=0.3)
        
        # 显示第一个函数
        self.add(domain)
        self.add(label)
        self.wait(0.5)
        
        # 遍历展示所有函数
        for func_type, formula in functions[1:]:
            new_label = Tex(formula, font_size=36)
            new_label.next_to(domain, DOWN, buff=0.3)
            
            # 更新函数
            domain.set_func_type(func_type)
            
            self.play(
                Transform(label, new_label),
                run_time=0.3
            )
            self.wait(0.8)
        
        # 结束
        self.play(FadeOut(label), FadeOut(title))
        self.remove(domain)
        self.wait(0.5)


class ComplexDomainAnimation(Scene):
    """复变函数动画 - z^n 连续变化"""
    
    def construct(self):
        # 标题
        title = Text("连续幂次变换: z → z^n", font="STSong")
        title.scale(0.6).to_edge(UP)
        self.add(title)
        
        # 创建 shader mobject
        domain = ComplexDomainShader(
            func_type="z^n",
            scale_factor=2.5,
            power=1.0,
            brightness_scale=0.8,
            saturation_scale=1.5,
            height=5.0,
        )
        domain.shift(DOWN * 0.2)
        self.add(domain)
        
        # 幂次显示
        power_tracker = ValueTracker(1.0)
        power_label = DecimalNumber(1.0, num_decimal_places=2)
        power_label.add_updater(lambda m: m.set_value(power_tracker.get_value()))
        power_text = Text("n = ", font="Consolas")
        power_display = VGroup(power_text, power_label).arrange(RIGHT)
        power_display.to_corner(UL, buff=0.5).shift(DOWN * 0.5)
        self.add(power_display)
        
        # 更新 shader 的 power uniform
        def update_power(mob):
            mob.set_power(power_tracker.get_value())
        domain.add_updater(update_power)
        
        # 动画：n 从 1 变化到 6
        self.play(
            power_tracker.animate.set_value(6.0),
            run_time=10,
            rate_func=smooth
        )
        
        domain.remove_updater(update_power)
        self.wait(2)


class ComplexDomainZoom(Scene):
    """复变函数缩放动画 - 放大查看细节"""
    
    def construct(self):
        title = Text("sin(1/z) - 本性奇点", font="STSong")
        title.scale(0.6).to_edge(UP)
        self.add(title)
        
        # 创建 shader mobject
        domain = ComplexDomainShader(
            func_type="sin(1/z)",
            scale_factor=3.0,
            brightness_scale=0.8,
            saturation_scale=1.5,
            height=5.0,
        )
        domain.shift(DOWN * 0.2)
        self.add(domain)
        
        # 缩放 tracker
        scale_tracker = ValueTracker(3.0)
        
        def update_scale(mob):
            mob.set_scale(scale_tracker.get_value())
        domain.add_updater(update_scale)
        
        # 缩放显示
        scale_label = DecimalNumber(3.0, num_decimal_places=3)
        scale_label.add_updater(lambda m: m.set_value(scale_tracker.get_value()))
        scale_text = Text("scale = ", font="Consolas")
        scale_display = VGroup(scale_text, scale_label).arrange(RIGHT)
        scale_display.to_corner(UL, buff=0.5).shift(DOWN * 0.5)
        self.add(scale_display)
        
        # 放大动画
        self.play(
            scale_tracker.animate.set_value(0.1),
            run_time=8,
            rate_func=smooth
        )
        
        domain.remove_updater(update_scale)
        self.wait(2)


class ComplexDomainPolynomialRoots(Scene):
    """多项式根的可视化 - 动态移动根"""
    
    def construct(self):
        title = Text("多项式 (z-a)(z-b)(z-c) - 根的位置", font="STSong")
        title.scale(0.5).to_edge(UP)
        self.add(title)
        
        # 创建 shader mobject
        domain = ComplexDomainShader(
            func_type="polynomial",
            scale_factor=3.0,
            root_a=[1.0, 0.0],
            root_b=[-1.0, 0.0],
            root_c=[0.0, 1.0],
            brightness_scale=0.8,
            saturation_scale=1.5,
            height=5.0,
        )
        domain.shift(DOWN * 0.2)
        self.add(domain)
        
        # 动画：旋转根
        angle_tracker = ValueTracker(0.0)
        
        def update_roots(mob):
            angle = angle_tracker.get_value()
            r = 1.5
            mob.set_roots(
                root_a=[r * np.cos(angle), r * np.sin(angle)],
                root_b=[r * np.cos(angle + 2*PI/3), r * np.sin(angle + 2*PI/3)],
                root_c=[r * np.cos(angle + 4*PI/3), r * np.sin(angle + 4*PI/3)],
            )
        domain.add_updater(update_roots)
        
        # 旋转动画
        self.play(
            angle_tracker.animate.set_value(2 * PI),
            run_time=8,
            rate_func=linear
        )
        
        domain.remove_updater(update_roots)
        self.wait(2)


class ComplexDomainComparison(Scene):
    """对比：同时展示多个函数"""
    
    def construct(self):
        title = Text("复变函数对比", font="STSong")
        title.scale(0.6).to_edge(UP)
        self.add(title)
        
        # 创建 4 个 shader mobject，排列成 2x2
        functions = [
            ("z^2", r"z^2"),
            ("z^3", r"z^3"),
            ("sin(z)", r"\sin(z)"),
            ("exp(z)", r"e^z"),
        ]
        
        domains = []
        labels = []
        
        for i, (func_type, formula) in enumerate(functions):
            domain = ComplexDomainShader(
                func_type=func_type,
                scale_factor=2.5,
                brightness_scale=0.8,
                saturation_scale=1.5,
                height=4.0,
                aspect_ratio=1.0,
            )

            label = Tex(formula, font_size=28)

            # 2x2 布局
            row = i // 2
            col = i % 2
            x = -2.5 + col * 5.0
            y = 0.8 - row * 3.5

            domain.move_to([x, y, 0])
            label.next_to(domain, DOWN, buff=0.15)

            domains.append(domain)
            labels.append(label)
        
        # 显示所有
        for d in domains:
            self.add(d)
        for l in labels:
            self.add(l)
        
        self.wait(3)


# ==================== 入口 ====================

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    os.system(f"cd {script_dir} && manimgl {script_name}.py ComplexDomainDemo")
