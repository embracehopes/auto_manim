"""
辉光扫描下划线效果演示
使用 GlowDot + TracingTailPMobject 实现辉光点沿路径移动并留下彗尾
"""

from manimlib import *
import numpy as np
import sys
from pathlib import Path

# 添加 TracingTailPMobject 路径
_shader_path = str(Path(__file__).resolve().parent.parent.parent / "shaderscene" / "mobject")
if _shader_path not in sys.path:
    sys.path.insert(0, _shader_path)

from TracingTailPMobject import TracingTailPMobject


class GlowSweepUnderlineDemo(Scene):
    """
    辉光扫描下划线效果演示
    一个辉光点沿着下划线路径左右移动，并留下彗尾
    """
    
    def construct(self):
        # ========== 创建目标文字 ==========
        text = Text(
            "GlowDot 扫描效果",
            font="Microsoft YaHei",
            font_size=48,
            color=WHITE,
        )
        text.move_to(ORIGIN)
        self.add(text)
        
        # ========== 创建下划线路径 ==========
        # 获取文字底部的左右端点
        left_point = text.get_corner(DL) + DOWN * 0.1
        right_point = text.get_corner(DR) + DOWN * 0.1
        
        # 下划线长度和中点
        line_length = right_point[0] - left_point[0]
        line_center = (left_point + right_point) / 2
        
        # 创建一条下划线（作为参考，可以不显示）
        underline = Line(left_point, right_point, color=GREY, stroke_width=2)
        underline.set_stroke(opacity=0.3)
        self.add(underline)
        
        # ========== 创建辉光点 ==========
        glow_dot = GlowDot(
            center=left_point,
            radius=0.15,
            color=YELLOW,
            glow_factor=2.0,
        )
        self.add(glow_dot)
        
        # ========== 左右来回移动的位置追踪器 ==========
        # 使用 ValueTracker 控制位置
        progress_tracker = ValueTracker(0)  # 0 = 左端, 1 = 右端
        
        def get_current_position():
            """获取辉光点当前位置（用于彗尾追踪）"""
            t = progress_tracker.get_value()
            # 使用正弦函数让点左右来回移动
            # t 从 0 -> 1 -> 0 循环
            x = interpolate(left_point[0], right_point[0], t)
            y = left_point[1]
            z = 0
            return np.array([x, y, z])
        
        # 让辉光点跟随 tracker
        def update_dot(dot):
            dot.move_to(get_current_position())
        
        glow_dot.add_updater(update_dot)
        
        # ========== 创建彗尾效果 ==========
        tail = TracingTailPMobject(
            traced_point_func=get_current_position,
            max_tail_length=60,
            tail_lifetime=0.8,
            base_color=YELLOW,
            opacity_fade=(1.0, 0.0),
            width_fade=(0.08, 0.02),
            glow_factor=2.0,
        )
        self.add(tail)
        
        # 彗尾更新器
        def update_tail(mob, dt):
            mob.update_tail(dt)
        
        tail.add_updater(update_tail)
        
        # ========== 动画：来回扫描 ==========
        # 使用循环让辉光点来回移动
        
        # 第一次：从左到右
        self.play(
            progress_tracker.animate.set_value(1),
            run_time=1.5,
            rate_func=smooth,
        )
        
        # 第二次：从右到左
        self.play(
            progress_tracker.animate.set_value(0),
            run_time=1.5,
            rate_func=smooth,
        )
        
        # 第三次：快速来回几次
        for _ in range(3):
            self.play(
                progress_tracker.animate.set_value(1),
                run_time=0.8,
                rate_func=smooth,
            )
            self.play(
                progress_tracker.animate.set_value(0),
                run_time=0.8,
                rate_func=smooth,
            )
        
        # 停留展示
        self.wait(2)
        
        # 清理更新器
        glow_dot.clear_updaters()
        tail.clear_updaters()


class MultiTextSweepDemo(Scene):
    """
    多行文字扫描效果演示
    """
    
    def construct(self):
        # 创建多行文字
        texts = VGroup(
            Text("第一行文字", font="Microsoft YaHei", font_size=36),
            Text("第二行内容", font="Microsoft YaHei", font_size=36),
            Text("第三行展示", font="Microsoft YaHei", font_size=36),
        )
        texts.arrange(DOWN, buff=0.8)
        texts.move_to(ORIGIN)
        self.add(texts)
        
        # 为每行文字创建扫描效果
        for i, text in enumerate(texts):
            # 获取左右端点
            left_point = text.get_corner(DL) + DOWN * 0.1
            right_point = text.get_corner(DR) + DOWN * 0.1
            
            # 下划线
            underline = Line(left_point, right_point, color=GREY, stroke_width=1)
            underline.set_stroke(opacity=0.2)
            self.add(underline)
            
            # 颜色循环
            colors = [YELLOW, TEAL, PINK]
            color = colors[i % len(colors)]
            
            # 辉光点
            glow_dot = GlowDot(
                center=left_point,
                radius=0.12,
                color=color,
                glow_factor=1.5,
            )
            self.add(glow_dot)
            
            # 位置追踪器
            tracker = ValueTracker(0)
            
            def make_position_func(lp, rp, trk):
                def get_pos():
                    t = trk.get_value()
                    x = interpolate(lp[0], rp[0], t)
                    return np.array([x, lp[1], 0])
                return get_pos
            
            get_pos = make_position_func(left_point, right_point, tracker)
            
            def make_dot_updater(pos_func):
                def updater(dot):
                    dot.move_to(pos_func())
                return updater
            
            glow_dot.add_updater(make_dot_updater(get_pos))
            
            # 彗尾
            tail = TracingTailPMobject(
                traced_point_func=get_pos,
                max_tail_length=40,
                tail_lifetime=0.5,
                base_color=color,
                opacity_fade=(0.8, 0.0),
                width_fade=(0.06, 0.01),
                glow_factor=1.5,
            )
            self.add(tail)
            
            def make_tail_updater():
                def updater(mob, dt):
                    mob.update_tail(dt)
                return updater
            
            tail.add_updater(make_tail_updater())
            
            # 动画：扫过去
            self.play(
                tracker.animate.set_value(1),
                run_time=0.8,
                rate_func=smooth,
            )
        
        # 等待展示
        self.wait(2)


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__).replace(".py", "")
    os.system(f"cd {script_dir} && manimgl {script_name}.py GlowSweepUnderlineDemo")
