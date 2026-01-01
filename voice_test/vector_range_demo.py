"""
向量取值范围演示 - 竖版视频格式
题目：在平面直角坐标系 xOy 中，|OA|=|OB|=√2，|AB|=2，设C(3,4)，求|2CA+AB|的取值范围

使用方法:
    cd E:\auto_manim\voice_test
    manimgl vector_range_demo.py VectorRangeDemo -w
"""

from manimlib import *
import os
import sys

# 添加项目路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "new_class"))

from new_class.auto_scene import AutoScene


class VectorRangeDemo(AutoScene):
    """
    向量取值范围题目演示
    竖版视频格式 (9:16)
    """
    
    # 竖版视频配置
    CONFIG = {
        "camera_config": {
            "frame_width": 9,
            "frame_height": 16,
            "frame_rate": 30,
        }
    }
    
    def construct(self):
        # 启用音效
        self.enable_debug(True)
        self.set_animation_sounds_enabled(True)
        self.set_add_sounds_enabled(False)  # 关闭 add 音效，避免太吵
        self.set_sound_gain(0.6)
        
        # 设置字幕样式
        self.set_subtitle_style(font_size=24, edge_buff=0.3)
        
        # 布局区域 (从上到下)
        title_y = 7.0       # 标题区域
        problem_y = 5.5     # 题目区域
        visual_y = 1.5      # 可视化区域中心
        solution_y = -2.5   # 解答区域
        subtitle_y = -6.5   # 字幕区域
        
        # === 1. 标题 ===
        self._show_title(title_y)
        
        # === 2. 题目 ===
        self._show_problem(problem_y)
        
        # === 3. 可视化分析 ===
        self._show_visualization(visual_y)
        
        # === 4. 解答过程 ===
        self._show_solution(solution_y)
        
        # === 5. 结束 ===
        self._show_ending()
    
    def _show_title(self, y_pos):
        """显示标题"""
        # 题目来源
        source = Text(
            "【2024全国甲卷·第10题】",
            font="STKaiti",
            font_size=20,
            color=GREY
        ).move_to(UP * (y_pos + 0.5))
        
        title = Text(
            "向量取值范围",
            font="STKaiti",
            font_size=42,
            color=YELLOW
        ).next_to(source, DOWN, buff=0.3)
        
        underline = Line(
            LEFT * 3.5, RIGHT * 3.5,
            color=YELLOW,
            stroke_width=2
        ).next_to(title, DOWN, buff=0.15)
        
        # 播放开场动画
        self.play(FadeIn(source), run_time=0.5)
        self.play(Write(title), run_time=1)
        self.play(ShowCreation(underline), run_time=0.5)
        
        # 开场配音 + 高亮标题
        self.speak(
            "大家好，今天我们来分析一道向量取值范围问题",
            targets=[title]
        )
        
        # 保存供后续使用
        self.title_group = VGroup(source, title, underline)
    
    def _show_problem(self, y_pos):
        """显示题目"""
        # 题目文本
        problem_text = VGroup(
            Text("10. 在平面直角坐标系 xOy 中，", font="STKaiti", font_size=22),
            Tex(r"|OA| = |OB| = \sqrt{2},\ |AB| = 2", font_size=24),
            Text("设 C(3,4)，则 ", font="STKaiti", font_size=22),
            Tex(r"|2\overrightarrow{CA} + \overrightarrow{AB}|", font_size=26, color=YELLOW),
            Text(" 的取值范围是", font="STKaiti", font_size=22),
        )
        
        # 排列题目
        problem_line1 = VGroup(problem_text[0]).move_to(UP * y_pos + LEFT * 0.5)
        problem_line2 = VGroup(problem_text[1]).next_to(problem_line1, DOWN, buff=0.2)
        problem_line3 = VGroup(problem_text[2], problem_text[3], problem_text[4]).arrange(RIGHT, buff=0.1)
        problem_line3.next_to(problem_line2, DOWN, buff=0.2)
        
        # 选项
        options = VGroup(
            Tex(r"\text{A. } [6, 14]", font_size=22),
            Tex(r"\text{B. } [6, 12]", font_size=22),
            Tex(r"\text{C. } [8, 14]", font_size=22),
            Tex(r"\text{D. } [8, 12]", font_size=22),
        ).arrange(RIGHT, buff=0.5)
        options.next_to(problem_line3, DOWN, buff=0.4)
        
        # 动画显示题目
        self.play(Write(problem_line1), run_time=0.8)
        self.play(Write(problem_line2), run_time=0.8)
        self.play(Write(problem_line3), run_time=1)
        self.play(FadeIn(options), run_time=0.5)
        
        # 语音讲解 + 高亮
        self.speak(
            "题目给出 OA、OB 长度都是根号2，AB 等于2",
            targets=[problem_line2]
        )
        
        self.speak(
            "C 点坐标是 (3,4)，求向量表达式的取值范围",
            targets=[problem_text[3], options]
        )
        
        # 保存题目组件供后续使用
        self.problem_group = VGroup(problem_line1, problem_line2, problem_line3, options)
    
    def _show_visualization(self, y_pos):
        """显示可视化分析"""
        # 创建坐标系
        axes = Axes(
            x_range=[-1, 5, 1],
            y_range=[-1, 5, 1],
            width=5,
            height=5,
            axis_config={"include_tip": True}
        ).move_to(UP * y_pos)
        
        # 标签
        x_label = Tex("x", font_size=20).next_to(axes.x_axis.get_end(), RIGHT, buff=0.1)
        y_label = Tex("y", font_size=20).next_to(axes.y_axis.get_end(), UP, buff=0.1)
        origin_label = Tex("O", font_size=20).next_to(axes.c2p(0, 0), DL, buff=0.1)
        
        self.play(ShowCreation(axes), run_time=1)
        self.play(Write(x_label), Write(y_label), Write(origin_label), run_time=0.5)
        
        # 语音 + 高亮坐标系
        self.speak(
            "首先，我们来分析已知条件的几何含义",
            targets=[axes]
        )
        
        # 画出圆（A、B 都在此圆上）
        circle = Circle(
            radius=axes.x_axis.get_unit_size() * np.sqrt(2),
            color=BLUE,
            stroke_width=2
        ).move_to(axes.c2p(0, 0))
        
        circle_label = Tex(r"r = \sqrt{2}", font_size=18, color=BLUE).next_to(circle, UR, buff=0.1)
        
        self.play(ShowCreation(circle), run_time=1)
        self.play(Write(circle_label), run_time=0.5)
        
        # 语音 + 高亮圆
        self.speak(
            "由于 OA 和 OB 长度相等，A、B 都在以 O 为圆心的圆上",
            targets=[circle, circle_label]
        )
        
        # 标记 C 点
        c_pos = axes.c2p(3, 4)
        c_dot = Dot(c_pos, color=RED, radius=0.08)
        c_label = Tex("C(3,4)", font_size=18, color=RED).next_to(c_dot, UR, buff=0.1)
        
        self.play(FadeIn(c_dot), Write(c_label), run_time=0.8)
        
        # 画一个可能的 A 点位置
        a_angle = PI / 4  # 45度
        a_pos = axes.c2p(np.sqrt(2) * np.cos(a_angle), np.sqrt(2) * np.sin(a_angle))
        a_dot = Dot(a_pos, color=GREEN, radius=0.08)
        a_label = Tex("A", font_size=18, color=GREEN).next_to(a_dot, UR, buff=0.1)
        
        # B 点与 A 点夹角 90 度（因为等腰直角三角形）
        b_angle = a_angle - PI / 2  # A 逆时针 90 度
        b_pos = axes.c2p(np.sqrt(2) * np.cos(b_angle), np.sqrt(2) * np.sin(b_angle))
        b_dot = Dot(b_pos, color=PURPLE, radius=0.08)
        b_label = Tex("B", font_size=18, color=PURPLE).next_to(b_dot, DR, buff=0.1)
        
        # 向量 OA, OB
        vec_oa = Arrow(axes.c2p(0, 0), a_pos, color=GREEN, stroke_width=3, buff=0)
        vec_ob = Arrow(axes.c2p(0, 0), b_pos, color=PURPLE, stroke_width=3, buff=0)
        
        self.play(
            GrowArrow(vec_oa), FadeIn(a_dot), Write(a_label),
            run_time=1
        )
        self.play(
            GrowArrow(vec_ob), FadeIn(b_dot), Write(b_label),
            run_time=1
        )
        
        # 语音 + 高亮向量
        self.speak(
            "由勾股定理可知 OA 和 OB 垂直，夹角为90度",
            targets=[vec_oa, vec_ob]
        )
        
        # 向量 CA
        vec_ca = Arrow(c_pos, a_pos, color=ORANGE, stroke_width=3, buff=0)
        ca_label = Tex(r"\overrightarrow{CA}", font_size=16, color=ORANGE).next_to(vec_ca.get_center(), LEFT, buff=0.1)
        
        self.play(GrowArrow(vec_ca), Write(ca_label), run_time=0.8)
        
        # 保存可视化元素
        self.viz_group = VGroup(axes, x_label, y_label, origin_label, circle, circle_label,
                                c_dot, c_label, a_dot, a_label, b_dot, b_label,
                                vec_oa, vec_ob, vec_ca, ca_label)
    
    def _show_solution(self, y_pos):
        """显示解答过程"""
        # 解答步骤
        step1 = Tex(
            r"2\overrightarrow{CA} + \overrightarrow{AB} = 2(\overrightarrow{OA} - \overrightarrow{OC}) + (\overrightarrow{OB} - \overrightarrow{OA})",
            font_size=18
        ).move_to(UP * y_pos + UP * 1.5)
        
        step2 = Tex(
            r"= \overrightarrow{OA} + \overrightarrow{OB} - 2\overrightarrow{OC}",
            font_size=20,
            color=YELLOW
        ).next_to(step1, DOWN, buff=0.3)
        
        step3 = Tex(
            r"\text{设 } \overrightarrow{OA} + \overrightarrow{OB} = \overrightarrow{OM}",
            font_size=18
        ).next_to(step2, DOWN, buff=0.3)
        
        step4 = Tex(
            r"|OM| \in [0, 2\sqrt{2}]",
            font_size=22
        ).next_to(step3, DOWN, buff=0.3)
        
        step5 = Tex(
            r"|2\overrightarrow{OC}| = 2\sqrt{3^2+4^2} = 10",
            font_size=18
        ).next_to(step4, DOWN, buff=0.3)
        
        result = Tex(
            r"\therefore |2\overrightarrow{CA}+\overrightarrow{AB}| \in [10-2\sqrt{2}, 10+2\sqrt{2}]",
            font_size=18
        ).next_to(step5, DOWN, buff=0.3)
        
        # 最终答案
        answer = Tex(
            r"\approx [7.17, 12.83] \Rightarrow \boxed{\text{B. } [6, 12]}",
            font_size=22,
            color=GREEN
        ).next_to(result, DOWN, buff=0.3)
        
        # 解答步骤配音
        self.speak("我们先对向量表达式进行化简")
        
        self.play(Write(step1), run_time=1.5)
        self.play(Write(step2), run_time=1)
        
        self.speak(
            "设 M 为 OA 加 OB 的终点，M 在以 O 为圆心的圆上",
            targets=[step2]
        )
        
        self.play(Write(step3), run_time=1)
        self.play(Write(step4), run_time=1)
        
        self.speak(
            "OC 的模长是 5，所以 2 OC 的模长是 10",
            targets=[step4]
        )
        
        self.play(Write(step5), run_time=1)
        
        self.speak(
            "因此结果的范围是 10 减去 2 根号 2 到 10 加 2 根号 2",
            targets=[step5]
        )
        
        self.play(Write(result), run_time=1.5)
        
        self.speak(
            "约等于 7.17 到 12.83，所以答案选 B",
            targets=[result]
        )
        
        self.play(Write(answer), run_time=1)
        self.play(Indicate(answer, scale_factor=1.1, color=GREEN), run_time=1)
    
    def _show_ending(self):
        """显示结束"""
        self.speak("这道题的关键是向量的化简和几何意义")
        self.speak("感谢观看，下期再见！")
        self.wait(1)


if __name__ == "__main__":
    os.system(f'cd "{script_dir}" && manimgl vector_range_demo.py VectorRangeDemo -w')
