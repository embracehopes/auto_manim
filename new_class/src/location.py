"""
屏幕坐标网格演示
在屏幕上显示坐标网格和每个节点的坐标标注
用于调试和定位
"""

from manimlib import *
import numpy as np


class CoordinateGridOverlay(Scene):
    """
    显示布满屏幕的坐标网格
    格子精度 0.2，坐标标注在整数位置
    """
    
    def construct(self):
        # ========== 配置参数 ==========
        grid_step = 0.2  # 格子精度
        label_step = 1   # 坐标标注精度（整数）
        label_font_size = 3  # 小字体
        
        # 网格范围
        try:
            frame_width = self.camera.frame.get_width()
            frame_height = self.camera.frame.get_height()
        except:
            frame_width = 16
            frame_height = 9
        
        x_min = -frame_width / 2 - grid_step
        x_max = frame_width / 2 + grid_step
        y_min = -frame_height / 2 - grid_step
        y_max = frame_height / 2 + grid_step
        
        # ========== 创建网格线 ==========
        grid_lines = VGroup()
        
        # 垂直线（0.2精度）
        x = x_min
        while x <= x_max:
            is_integer = abs(x - round(x)) < 0.01
            sw = 1.0 if is_integer else 0.5
            op = 0.5 if is_integer else 0.3  # 更明显
            color = GREY_B if is_integer else GREY_C
            line = Line(
                start=np.array([x, y_min, 0]),
                end=np.array([x, y_max, 0]),
                stroke_width=sw,
                color=color,
            )
            line.set_stroke(opacity=0.9)
            grid_lines.add(line)
            x += grid_step
        
        # 水平线（0.2精度）
        y = y_min
        while y <= y_max:
            is_integer = abs(y - round(y)) < 0.01
            sw = 1.0 if is_integer else 0.5
            op = 0.5 if is_integer else 0.3  # 更明显
            color = GREY_B if is_integer else GREY_C
            line = Line(
                start=np.array([x_min, y, 0]),
                end=np.array([x_max, y, 0]),
                stroke_width=sw,
                color=color,
            )
            line.set_stroke(opacity=0.9)
            grid_lines.add(line)
            y += grid_step
        
        # 原点坐标轴（加粗显示）
        x_axis = Line(
            start=np.array([x_min, 0, 0]),
            end=np.array([x_max, 0, 0]),
            stroke_width=2,
            color=RED,
        )
        x_axis.set_stroke(opacity=0.7)
        
        y_axis = Line(
            start=np.array([0, y_min, 0]),
            end=np.array([0, y_max, 0]),
            stroke_width=2,
            color=GREEN,
        )
        y_axis.set_stroke(opacity=0.7)
        
        self.add(grid_lines)
        self.add(x_axis, y_axis)
        
        # ========== 创建坐标标注（仅整数位置）==========
        labels = VGroup()
        
        x_int_min = int(x_min)
        x_int_max = int(x_max) + 1
        y_int_min = int(y_min)
        y_int_max = int(y_max) + 1
        
        for x in range(x_int_min, x_int_max):
            for y in range(y_int_min, y_int_max):
                coord_text = f"({x},{y})"
                
                # 原点特殊标记
                if x == 0 and y == 0:
                    label = Text(
                        coord_text,
                        font="Consolas",
                        font_size=5,
                        color=YELLOW,
                    )
                else:
                    label = Text(
                        coord_text,
                        font="Consolas",
                        font_size=label_font_size,
                        color=WHITE,
                    )
                
                # 将标签放置在对应坐标位置
                label.move_to(np.array([x, y, 0]))
                labels.add(label)
        
        self.add(labels)
        
        # ========== 添加frame信息 ==========
        info_text = Text(
            f"Frame: {frame_width:.1f} x {frame_height:.1f} | Grid: {grid_step} | Labels: {label_step}",
            font="Consolas",
            font_size=16,
            color=YELLOW,
        )
        info_text.to_corner(UL, buff=0.2)
        info_bg = BackgroundRectangle(info_text, fill_opacity=0.8, buff=0.1)
        self.add(info_bg, info_text)
        
        # ========== 等待 ==========
        self.wait(10)


class CoordinateGridOverlayVertical(Scene):
    """
    竖版屏幕坐标网格（9:16 比例）
    格子精度 0.2，坐标标注在整数位置
    """
    
    CONFIG = {
        "camera_config": {
            "frame_width": 9,
            "frame_height": 16,
        }
    }
    
    def construct(self):
        grid_step = 0.2
        label_font_size = 2
        
        frame_width = 9
        frame_height = 16
        
        x_min, x_max = -frame_width / 2 - grid_step, frame_width / 2 + grid_step
        y_min, y_max = -frame_height / 2 - grid_step, frame_height / 2 + grid_step
        
        grid_lines = VGroup()
        labels = VGroup()
        
        # 网格线（0.2精度）
        x = x_min
        while x <= x_max:
            is_integer = abs(x - round(x)) < 0.01
            sw = 0.8 if is_integer else 0.3
            op = 0.5 if is_integer else 0.3
            line = Line(np.array([x, y_min, 0]), np.array([x, y_max, 0]), stroke_width=sw, color=GREY_B if is_integer else GREY_C)
            line.set_stroke(opacity=0.9)
            grid_lines.add(line)
            x += grid_step
        
        y = y_min
        while y <= y_max:
            is_integer = abs(y - round(y)) < 0.01
            sw = 0.8 if is_integer else 0.3
            op = 0.5 if is_integer else 0.3
            line = Line(np.array([x_min, y, 0]), np.array([x_max, y, 0]), stroke_width=sw, color=GREY_B if is_integer else GREY_C)
            line.set_stroke(opacity=0.9)
            grid_lines.add(line)
            y += grid_step
        
        # 坐标轴
        x_axis = Line(np.array([x_min, 0, 0]), np.array([x_max, 0, 0]), stroke_width=2, color=RED)
        y_axis = Line(np.array([0, y_min, 0]), np.array([0, y_max, 0]), stroke_width=2, color=GREEN)
        x_axis.set_stroke(opacity=0.7)
        y_axis.set_stroke(opacity=0.7)
        
        self.add(grid_lines, x_axis, y_axis)
        
        # 坐标标注（仅整数位置）
        for x in range(int(x_min), int(x_max) + 1):
            for y in range(int(y_min), int(y_max) + 1):
                coord_text = f"({x},{y})"
                
                if x == 0 and y == 0:
                    label = Text(coord_text, font="Consolas", font_size=4, color=YELLOW)
                else:
                    label = Text(coord_text, font="Consolas", font_size=label_font_size, color=WHITE)
                
                label.move_to(np.array([x, y, 0]))
                labels.add(label)
        
        self.add(labels)
        self.wait(5)


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    os.system(f'cd "{script_dir}" && manimgl {script_name}.py CoordinateGridOverlay')
