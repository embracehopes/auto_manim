import os
import sys
import numpy as np

# 添加父目录到路径以便导入MultiTracingTails
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from manimlib import *
from mobject.TracingTailPMobject import *


def calculate_dark_rainbow_color(index, total_points):
    """计算深色彩虹渐变色 - 参考rainbow.py但使用更深色调"""
    # 将点索引线性映射到色相值 (0-100%)
    progress = index / total_points
    
    # 使用深色彩虹色调（比rainbow.py更深）
    dark_rainbow_colors = [
        "#2D1B69",  # 深紫色
        "#4A0E4E",  # 深洋红
        "#8B0000",  # 深红色  
        "#B8860B",  # 深金色
        "#006400",  # 深绿色
        "#191970",  # 深蓝色
        "#4B0082",  # 深靛色
        "#2D1B69"   # 回到起始颜色形成循环
    ]
    
    # 计算所在的颜色段
    num_segments = len(dark_rainbow_colors) - 1
    segment_idx = int(progress * num_segments)
    segment_idx = min(segment_idx, num_segments - 1)  # 确保索引有效
    
    # 计算在当前段内的进度 (0-1)
    segment_progress = (progress * num_segments) - segment_idx
    
    # 在两个相邻颜色之间进行插值
    color1 = dark_rainbow_colors[segment_idx]
    color2 = dark_rainbow_colors[segment_idx + 1]
    
    # 使用ManimGL的颜色插值
    base_color = interpolate_color(color1, color2, segment_progress)
    
    return base_color


class myglowdashborder(Scene):
    def construct(self):
        # 先创建形状

        def glowborder(width, height, corner_radius, dashnum, dot_radius=0.03):
            rect = RoundedRectangle(width=width, height=height, corner_radius=corner_radius)
        
            # 让多个点沿着rect移动，每个点从不同的起始位置开始
            dots = []
            anims = []
            traces = []
            
            # 创建辅助函数来避免闭包问题
            def create_dot_and_trace(index):
                start_t = index / dashnum  
                start_point = rect.point_from_proportion(start_t)
                
                # 使用深色彩虹配色方案
                current_color = calculate_dark_rainbow_color(index, dashnum)
                
                print(f"Point {index}: start_t={start_t:.3f}, color={current_color}")
                
                # 创建更小的点
                dot = Dot(radius=dot_radius, color=current_color).move_to(start_point)
                
                # 创建动画
                anim = MoveAlongPath(
                    dot, 
                    rect,
                    rate_func=lambda t, st=start_t: (overshoot(t) + st) % 1,  # 显式捕获start_t
                    run_time=6  # 增加运行时间让动画更平滑
                )
                
                # 创建轨迹追踪，使用更长的轨迹
                trace = TracingTailPMobject(
                    traced_point_func=lambda d=dot: d.get_center(),  # 显式捕获dot
                    base_color=current_color,                         # 使用深色彩虹颜色
                    max_tail_length=40,                               # 增加轨迹长度
                    tail_lifetime=3.0,                                # 增加生命周期
                    opacity_fade=(0.9, 0.0),                         # 调整透明度渐变
                    width_fade=(0.08, 0.02),                         # 调整宽度渐变
                    glow_factor=3.0                                   # 增加辉光效果
                )
                
                # 添加更新器
                trace.add_updater(lambda mob, dt: mob.update_tail(dt))
                
                return dot, anim, trace
            
            # 使用循环创建所有对象
            for i in range(dashnum):
                dot, anim, trace = create_dot_and_trace(i)
                dots.append(dot)
                anims.append(anim)
                traces.append(trace)
                
            return dots, anims, traces

        # 参数：宽度, 高度, 圆角半径, 点的数量, 点的半径
        dots, anims, traces = glowborder(8, 5, 0.8, 8, 0.02)
        
        # 先添加轨迹追踪对象
        self.add(*traces)
        
        # 再添加点（这样点会在轨迹之上）
        self.add(*dots)
        
        # 创建无限循环动画
        while True:
            # 播放所有动画
            self.play(*anims)
            
            # 可选：添加短暂暂停让循环更平滑
            self.wait(0.1)

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py")