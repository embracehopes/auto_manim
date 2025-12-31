"""
辉光虚线动态边框 - 基于MultiTracingTails的实现
"""

import os
import sys
import numpy as np

# 添加父目录到路径以便导入MultiTracingTails
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from manimlib import *
from mobject.TracingTailPMobject import MultiTracingTails


class GlowDashBorder(VMobject):
    """
    辉光虚线动态边框 - 基于MultiTracingTails的实现
    
    Parameters
    ----------
    width : float
        边框宽度
    height : float  
        边框高度
    corner_radius : float
        圆角半径，默认0.2
    num_dashes : int
        虚线段数量，默认20
    dashed_ratio : float
        虚线占空比，默认0.6
    dash_offset : float
        虚线偏移量，默认0
    glow_factor : float
        辉光强度，默认2.0
    tail_length : int
        轨迹长度，默认50
    tail_lifetime : float
        轨迹生命周期，默认1.5
    color : ManimColor
        边框颜色，默认BLUE
    """
    
    def __init__(
        self,
        width: float = 6.0,
        height: float = 4.0,
        corner_radius: float = 0.2,
        num_dashes: int = 20,
        dashed_ratio: float = 0.6,
        dash_offset: float = 0,
        glow_factor: float = 2.0,
        tail_length: int = 50,
        tail_lifetime: float = 1.5,
        color: str = "WHITE",
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # 存储参数
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.num_dashes = num_dashes
        self.dashed_ratio = dashed_ratio
        self.dash_offset = dash_offset
        self.glow_factor = glow_factor
        self.tail_length = tail_length
        self.tail_lifetime = tail_lifetime
        self.border_color = color
        
        # 创建边框路径
        self.border_path = self._create_border_path()
        
        # 创建虚线段
        self.dash_segments = self._create_dash_segments()
        print(f"创建了 {len(self.dash_segments)} 个虚线段")
        
        # 先添加边框路径作为参考（调试用）
        self.add(self.border_path.copy().set_stroke(width=1, opacity=0.3))
        
        # 添加虚线段作为静态显示（调试用）
        for segment in self.dash_segments:
            segment_copy = segment.copy().set_stroke(color=RED, width=2)
            self.add(segment_copy)
        
        # 创建MultiTracingTails系统
        self.tracing_tails = self._create_tracing_tails()
        print(f"创建了MultiTracingTails，类型: {type(self.tracing_tails)}")
        
        # 不直接添加tracing_tails，因为它可能不是VMobject
        # 将在Scene中手动添加
    
    def _create_border_path(self):
        """创建带圆角的矩形边框路径"""
        # 创建带圆角的矩形
        if self.corner_radius > 0:
            border = RoundedRectangle(
                width=self.width,
                height=self.height,
                corner_radius=self.corner_radius,
                color=self.border_color
            )
        else:
            border = Rectangle(
                width=self.width,
                height=self.height,
                color=self.border_color
            )
        
        return border
    
    def _create_dash_segments(self):
        """创建虚线段"""
        r = self.dashed_ratio
        n = self.num_dashes
        
        if n <= 0:
            return []
        
        # 计算虚线和空白的长度
        dash_len = r / n
        void_len = (1 - r) / n  # 封闭曲线
        
        period = dash_len + void_len
        phase_shift = (self.dash_offset % 1) * period
        
        # 计算虚线起始和结束位置
        dash_starts = [((i * period + phase_shift) % 1) for i in range(n)]
        dash_ends = [((i * period + dash_len + phase_shift) % 1) for i in range(n)]
        
        # 创建虚线段
        dash_segments = []
        for i in range(len(dash_starts)):
            start_t = dash_starts[i]
            end_t = dash_ends[i]
            
            # 处理跨越边界的情况
            if start_t <= end_t:
                # 正常情况
                segment = self.border_path.get_subcurve(start_t, end_t)
                dash_segments.append(segment)
            else:
                # 跨越边界的情况，分成两段
                segment1 = self.border_path.get_subcurve(start_t, 1.0)
                segment2 = self.border_path.get_subcurve(0.0, end_t)
                dash_segments.extend([segment1, segment2])
        
        return dash_segments
    
    def _create_tracing_tails(self):
        """创建MultiTracingTails系统"""
        if not self.dash_segments:
            print("警告: 没有虚线段可以追踪")
            return None
            
        # 为每个虚线段创建追踪函数
        tracer_functions = []
        colors = []
        
        for i, segment in enumerate(self.dash_segments):
            # 创建追踪函数 - 追踪段的中心点
            def create_tracer(seg, idx=i):
                def tracer():
                    try:
                        points = seg.get_points()
                        if len(points) > 0:
                            # 返回段的中心点
                            center = np.mean(points[::3], axis=0)  # 只取控制点
                            # 添加一些动态偏移
                            time_offset = time.time() * 2 + idx * 0.5
                            center[0] += 0.1 * np.cos(time_offset)
                            center[1] += 0.1 * np.sin(time_offset)
                            return center
                    except Exception as e:
                        print(f"追踪函数错误: {e}")
                    return ORIGIN
                return tracer
            
            tracer_functions.append(create_tracer(segment, i))
            
            # 为每个段分配颜色（可以是渐变色）
            hue = (i / len(self.dash_segments)) * 360
            segment_color = self._hue_to_rgb(hue)
            colors.append(segment_color)
        
        print(f"创建了 {len(tracer_functions)} 个追踪函数")
        
        try:
            # 创建MultiTracingTails
            multi_tails = MultiTracingTails(
                traced_functions=tracer_functions,
                colors=colors,
                max_tail_length=self.tail_length,
                tail_lifetime=self.tail_lifetime,
                opacity_fade=(0.8, 0.0),
                width_fade=(0.06, 0.02),
                glow_factor=self.glow_factor
            )
            print("MultiTracingTails创建成功")
            return multi_tails
        except Exception as e:
            print(f"创建MultiTracingTails失败: {e}")
            return None
    
    def _hue_to_rgb(self, hue):
        """将色相转换为RGB"""
        # 简化的HSV到RGB转换
        hue = hue % 360
        if hue < 60:
            t = hue / 60
            return np.array([1.0, t, 0.0])
        elif hue < 120:
            t = (hue - 60) / 60
            return np.array([1.0 - t, 1.0, 0.0])
        elif hue < 180:
            t = (hue - 120) / 60
            return np.array([0.0, 1.0, t])
        elif hue < 240:
            t = (hue - 180) / 60
            return np.array([0.0, 1.0 - t, 1.0])
        elif hue < 300:
            t = (hue - 240) / 60
            return np.array([t, 0.0, 1.0])
        else:
            t = (hue - 300) / 60
            return np.array([1.0, 0.0, 1.0 - t])
    
    def update_dash_offset(self, new_offset):
        """更新虚线偏移量"""
        self.dash_offset = new_offset
        
        # 重新创建虚线段
        self.dash_segments = self._create_dash_segments()
        
        # 重新创建追踪系统（不在这里添加到自身，由Scene管理）
        self.tracing_tails = self._create_tracing_tails()
    
    def set_corner_radius(self, radius):
        """设置圆角半径"""
        self.corner_radius = radius
        self.border_path = self._create_border_path()
        
        # 重新创建虚线段和追踪系统（不在这里添加到自身，由Scene管理）
        self.dash_segments = self._create_dash_segments()
        self.tracing_tails = self._create_tracing_tails()


class GlowDashBorderDemo(Scene):
    """演示GlowDashBorder的使用"""
    
    def construct(self):
    
        # 创建辉光虚线边框
        glow_border = GlowDashBorder(
            width=8,
            height=5,
            corner_radius=0.5,
            num_dashes=24,
            dashed_ratio=0.7,
            glow_factor=2.5,
            tail_length=60,
            tail_lifetime=2.0,
            color=BLUE
        )
        
        # 添加标题
        title = Text("辉光虚线动态边框演示", font_size=36, color=WHITE)
        title.next_to(glow_border, UP, buff=0.8)
        
        # 分别添加边框和轨迹系统
        self.add(glow_border, title)
        
        # 单独添加MultiTracingTails系统
        if hasattr(glow_border, 'tracing_tails') and glow_border.tracing_tails is not None:
            print("添加MultiTracingTails到场景")
            self.add(glow_border.tracing_tails)
        else:
            print("警告: tracing_tails不存在或为空")
        
        # 创建动态偏移值
        offset_tracker = ValueTracker(0)
        
        # 添加更新器 - 让虚线动态移动
        def update_border(border, dt):
            offset_tracker.increment_value(dt * 0.5)  # 控制移动速度
            new_offset = offset_tracker.get_value() % 1
            border.update_dash_offset(new_offset)
        
        glow_border.add_updater(update_border)
        
        # 演示不同的圆角半径
        self.wait(3)
        
        # 动态改变圆角半径
        self.play(
            AnimationGroup(
                *[ApplyMethod(glow_border.set_corner_radius, 0.8) for _ in range(1)],
                run_time=2
            )
        )
        
        self.wait(2)
        
        self.play(
            AnimationGroup(
                *[ApplyMethod(glow_border.set_corner_radius, 0.2) for _ in range(1)],
                run_time=2
            )
        )
        
        self.wait(3)
        
        # 清理更新器
        glow_border.clear_updaters()


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    os.system(f"cd {script_dir} && manimgl {script_name}.py")
