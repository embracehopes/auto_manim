#!/usr/bin/env python3
"""
复数解集可视化 - 二元二次方程组

误差函数: F(x, y) = [x² + 5y² - 5] + i·[x² + (y-1)² - r²]

可视化策略:
- 固定 y 为实数参数
- 在 x 的复平面上绘图
- 解集: 颜色极暗(接近黑)的点, 即 F(x, y) = 0 的解

使用方法:
    manimgl complex_solution_set.py ComplexSolutionSetAnimation
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from manimlib import *


class SolutionSetShader(Mobject):
    """复数解集可视化 Shader Mobject"""
    
    # Shader 文件夹路径
    shader_folder = os.path.join(os.path.dirname(__file__), "solution_set_shader")
    
    def __init__(
        self,
        y_param: float = 0.0,
        y_imag: float = 0.02,  # 虚部扰动，打破 Re(F)=Im(F) 退化
        r_param: float = 2.0,
        scale_factor: float = 3.0,
        offset: np.ndarray = None,
        brightness_scale: float = 1.0,
        saturation_scale: float = 1.5,
        opacity: float = 1.0,
        height: float = FRAME_HEIGHT,
        aspect_ratio: float = 16 / 9,
        **kwargs,
    ):
        self.y_param = y_param
        self.y_imag = y_imag
        self.r_param = r_param
        self.scale_factor = scale_factor
        self.offset = offset if offset is not None else np.array([0.0, 0.0, 0.0])
        self.brightness_scale = brightness_scale
        self.saturation_scale = saturation_scale
        self._opacity = opacity
        self.aspect_ratio = aspect_ratio
        
        # 设置顶点数据类型
        self.data_dtype = [("point", np.float32, (3,))]
        
        super().__init__(**kwargs)
        self.set_height(height, stretch=True)
        self.set_width(height * aspect_ratio, stretch=True)
    
    def init_data(self, length: int = 4) -> None:
        super().init_data(length=length)
        self.data["point"][:] = [UL, DL, UR, DR]
    
    def init_uniforms(self):
        super().init_uniforms()
        
        self.uniforms["y_param"] = float(self.y_param)
        self.uniforms["y_imag"] = float(self.y_imag)
        self.uniforms["r_param"] = float(self.r_param)
        self.uniforms["scale_factor"] = float(self.scale_factor)
        self.uniforms["offset"] = np.array(self.offset, dtype=np.float32)
        self.uniforms["brightness_scale"] = float(self.brightness_scale)
        self.uniforms["saturation_scale"] = float(self.saturation_scale)
        self.uniforms["opacity"] = float(self._opacity)
    
    def set_y_param(self, y: float):
        """设置 y 参数 (实部)"""
        self.y_param = y
        self.uniforms["y_param"] = float(y)
        return self
    
    def set_y_imag(self, y_imag: float):
        """设置 y 参数的虚部扰动"""
        self.y_imag = y_imag
        self.uniforms["y_imag"] = float(y_imag)
        return self
    
    def set_r_param(self, r: float):
        """设置 r 参数"""
        self.r_param = r
        self.uniforms["r_param"] = float(r)
        return self
    
    def set_scale(self, scale_factor: float):
        """设置缩放"""
        self.scale_factor = scale_factor
        self.uniforms["scale_factor"] = float(scale_factor)
        return self
    
    def set_offset(self, offset: np.ndarray):
        """设置偏移"""
        self.offset = offset
        self.uniforms["offset"] = np.array(offset, dtype=np.float32)
        return self
    
    def set_color(self, *args, **kwargs):
        return self


class ComplexSolutionSetAnimation(Scene):
    """复数解集可视化动画 - y 参数实时变化"""
    
    def compute_solutions(self, y, r, scale_factor):
        """
        计算解的位置
        对于 F(x, y) = 0:
        - Re(x²) = 5(1-y²)
        当 |y| ≤ 1: x = ±√(5(1-y²)) 在实轴
        当 |y| > 1: x = ±i√(5(y²-1)) 在虚轴
        """
        solutions = []
        val = 5 * (1 - y**2)
        
        if val >= 0:
            # 解在实轴上
            x_real = np.sqrt(val)
            solutions = [
                np.array([x_real * scale_factor, 0, 0]),
                np.array([-x_real * scale_factor, 0, 0]),
            ]
        else:
            # 解在虚轴上
            x_imag = np.sqrt(-val)
            solutions = [
                np.array([0, x_imag * scale_factor, 0]),
                np.array([0, -x_imag * scale_factor, 0]),
            ]
        
        return solutions
    
    def construct(self):
        # ========== 统一字体设置 ==========
        TITLE_FONT = "Microsoft YaHei"  # 中文标题
        MONO_FONT = "Arial"              # 好看的等宽字体
        
        # ========== 上方公式 ==========
        title = Text("复数解集可视化 (二元二次方程组)", font=TITLE_FONT, font_size=32)
        title.to_edge(UP, buff=0.3)
        
        # 方程组
        equations = Tex(
            r"\frac{x^2}{5} + \frac{y^2}{1} = 1 \quad \text{和} \quad x^2 + (y-1)^2 = r^2",
            font_size=28
        )
        equations.next_to(title, DOWN, buff=0.2)
        
        # ========== 参数 ==========
        scale_factor = 1.0  # 缩小以显示更多复平面范围 (原来的 1/3)
        r_value = 2.0
        y_imag_perturbation = 0.0  # 去掉扰动
        domain_center = DOWN * 0.3
        
        # ========== 创建 Shader Mobject ==========
        domain = SolutionSetShader(
            y_param=0.0,
            y_imag=y_imag_perturbation,
            r_param=r_value,
            scale_factor=scale_factor,
            brightness_scale=1.2,
            saturation_scale=1.5,
            height=5.0,
        )
        domain.shift(domain_center)
        
        # ========== 下方公式 ==========
        error_func = Tex(
            r"F(x, y) = [x^2 + 5y^2 - 5] + i \cdot [x^2 + (y-1)^2 - r^2]",
            font_size=26
        )
        error_func.to_edge(DOWN, buff=0.6)
        
        condition = Tex(
            r"\text{解集: } F(x, y) = 0 \text{ (暗色区域)}",
            font_size=24
        )
        condition.next_to(error_func, DOWN, buff=0.15)
        
        # ========== 右上角 y 值显示 ==========
        y_tracker = ValueTracker(0.0)
        
        y_text = Text("y = ", font=MONO_FONT, font_size=26)
        y_number = DecimalNumber(
            0.0, 
            num_decimal_places=2, 
            font_size=26,
            color=WHITE,
            text_config=dict(
                font="Times New Roman",  # 好看的衬线字体
                slant="NORMAL",
                weight="NORMAL",
            )
        )
        y_label = VGroup(y_text, y_number).arrange(RIGHT, buff=0.1)
        y_label.to_corner(UR, buff=0.5)
        
        # 更新 y 值显示
        y_number.add_updater(lambda m: m.set_value(y_tracker.get_value()))
        
        # 更新 shader 的 y_param
        def update_y_param(mob):
            mob.set_y_param(y_tracker.get_value())
        domain.add_updater(update_y_param)
        
        # ========== 右上角 r 值显示 ==========
        r_text = Text("r = ", font=MONO_FONT, font_size=26)
        r_number = Text("2.00", font="Times New Roman", font_size=26)
        r_label = VGroup(r_text, r_number).arrange(RIGHT, buff=0.1)
        r_label.next_to(y_label, DOWN, buff=0.2)
        
        # ========== 解的标记 (箭头指向解 + x值) ==========
        solution_arrows = VGroup()
        solution_labels = VGroup()
        solution_values = VGroup()  # x 的数值标注
        
        colors = [RED_C, BLUE_C]  # 只用2种颜色，更简洁
        labels_text = [r"x_1", r"x_2"]
        
        for i in range(2):  # 只显示2个解
            # 创建箭头 (从上方或下方指向解的位置)
            arrow = Arrow(
                start=ORIGIN, 
                end=ORIGIN + DOWN * 0.5,  # 临时方向，会在 updater 中更新
                color=colors[i],
                stroke_width=3,
                buff=0.05,
                max_tip_length_to_length_ratio=0.3,
            )
            label = Tex(labels_text[i], font_size=18, color=colors[i])
            
            # x 值的数值标注，使用好看的字体
            x_value = DecimalNumber(
                0.0, 
                num_decimal_places=2, 
                font_size=16,
                color=colors[i],
                text_config=dict(
                    font="Arial",
                    weight="NORMAL",
                )
            )
            
            solution_arrows.add(arrow)
            solution_labels.add(label)
            solution_values.add(x_value)
        
        # 更新解的位置和数值
        def update_solutions(mob_group):
            y = y_tracker.get_value()
            solutions = self.compute_solutions(y, r_value, 1.0)  # 返回复平面坐标
            
            # 复平面坐标到屏幕坐标的转换
            # height=5.0, scale_factor决定复平面范围
            # 屏幕坐标 = 复平面坐标 * (height / 2) / (complex_range / 2)
            # complex_range = height / scale_factor 约为 5.0/1.0 = 5.0
            screen_scale = 5.0 / (5.0 / scale_factor)  # = scale_factor
            
            for i, (arrow, label, x_val) in enumerate(
                zip(solution_arrows, solution_labels, solution_values)
            ):
                if i < len(solutions):
                    pos = solutions[i] * screen_scale + domain_center
                    
                    # 计算实际的 x 值 (复数)
                    val = 5 * (1 - y**2)
                    if val >= 0:
                        # 解在实轴上，箭头从上方指向
                        x_real = np.sqrt(val) * (1 if i == 0 else -1)
                        x_val.set_value(x_real)
                        
                        # 箭头从上方指向解 (增加 buff)
                        arrow_start = pos + UP * 1.0
                        arrow.put_start_and_end_on(arrow_start, pos + UP * 0.2)
                        label.next_to(arrow, UP, buff=0.08)
                        x_val.next_to(label, RIGHT, buff=0.1)
                    else:
                        # 解在虚轴上，箭头从侧面指向 (增加 buff)
                        x_imag = np.sqrt(-val) * (1 if i == 0 else -1)
                        x_val.set_value(x_imag)
                        
                        # 箭头从侧面指向解
                        side_dir = RIGHT if i == 0 else LEFT
                        arrow_start = pos + side_dir * 1.0
                        arrow.put_start_and_end_on(arrow_start, pos + side_dir * 0.2)
                        label.next_to(arrow, side_dir, buff=0.08)
                        x_val.next_to(label, UP, buff=0.05)
                    
                    arrow.set_opacity(1)
                    label.set_opacity(1)
                    x_val.set_opacity(1)
                else:
                    arrow.set_opacity(0)
                    label.set_opacity(0)
                    x_val.set_opacity(0)
        
        solution_group = VGroup(solution_arrows, solution_labels, solution_values)
        solution_group.add_updater(update_solutions)
        
        # ========== 坐标轴标签 ==========
        # x 轴 (实部)
        re_axis_label = Tex(r"\mathrm{Re}(x)", font_size=22, color=WHITE)
        re_axis_label.move_to(domain_center + RIGHT * 4.2 + DOWN * 0.1)
        
        # y 轴 (虚部)
        im_axis_label = Tex(r"\mathrm{Im}(x)", font_size=22, color=WHITE)
        im_axis_label.move_to(domain_center + UP * 2.2 + LEFT * 0.1)
        
        # ========== 颜色说明 ==========
        color_legend = VGroup(
            Text("颜色含义:", font=TITLE_FONT, font_size=18),
            Tex(r"\bullet\ \text{色相} = \arg(F)", font_size=16).set_color(YELLOW),
            Tex(r"\bullet\ \text{亮度} \propto |F|", font_size=16).set_color(YELLOW),
            Tex(r"\bullet\ \text{黑色} = F = 0\ (\text{解})", font_size=16).set_color(GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        color_legend.to_corner(UL, buff=0.4).shift(DOWN * 0.8)
        
        # ========== 添加所有元素 ==========
        self.add(title, equations)
        self.add(domain)
        self.add(error_func, condition)
        self.add(y_label, r_label)
        self.add(solution_group)
        self.add(re_axis_label, im_axis_label)
        self.add(color_legend)
        
        self.wait(1)
        
        # ========== 解析解公式 (在特殊y值时显示) ==========
        # y = 1/2 时的解析解
        solution_formula_y1 = Tex(
            r"y_1 = \frac{1}{2}:\ x = \pm\frac{\sqrt{15}}{2} \approx \pm 1.94",
            font_size=24,
            color=GREEN_C
        )
        solution_formula_y1.next_to(equations, DOWN, buff=0.15)
        
        # y = -1 时的解析解
        solution_formula_y2 = Tex(
            r"y_2 = -1:\ x = 0",
            font_size=24,
            color=TEAL_C
        )
        solution_formula_y2.next_to(equations, DOWN, buff=0.15)
        a=Axes()
        
        # ========== 动画: 在特殊点停留 ==========
        
        # 1. 先到 y = -1 (第二个解)
        self.play(
            y_tracker.animate.set_value(-1.0),
            run_time=3,
            rate_func=smooth
        )
        # 显示解析解
        self.play(FadeIn(solution_formula_y2), run_time=0.5)
        self.wait(2)  # 在 y = -1 停留
        self.play(FadeOut(solution_formula_y2), run_time=0.5)
        
        # 2. 过渡到 y = 0.5 (第一个解)
        self.play(
            y_tracker.animate.set_value(0.5),
            run_time=4,
            rate_func=smooth
        )
        # 显示解析解
        self.play(FadeIn(solution_formula_y1), run_time=0.5)
        self.wait(2)  # 在 y = 0.5 停留
        self.play(FadeOut(solution_formula_y1), run_time=0.5)
        
        # 3. 继续到 y = 1 (最大值)
        self.play(
            y_tracker.animate.set_value(1.0),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.5)
        
        # 4. 回到 y = 0.5 再次展示
        self.play(
            y_tracker.animate.set_value(0.5),
            run_time=3,
            rate_func=smooth
        )
        self.play(FadeIn(solution_formula_y1), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(solution_formula_y1), run_time=0.5)
        
        # 5. 回到 y = -1 再次展示
        self.play(
            y_tracker.animate.set_value(-1.0),
            run_time=3,
            rate_func=smooth
        )
        self.play(FadeIn(solution_formula_y2), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(solution_formula_y2), run_time=0.5)
        
        # 6. 回到 y = 0
        self.play(
            y_tracker.animate.set_value(0.0),
            run_time=2,
            rate_func=smooth
        )
        
        domain.remove_updater(update_y_param)
        solution_group.remove_updater(update_solutions)
        self.wait(2)





# ==================== 入口 ====================

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    os.system(f'cd "{script_dir}" && manimgl {script_name}.py ComplexSolutionSetAnimation -w')
