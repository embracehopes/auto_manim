"""
奇函数综合题演示 - 竖版视频格式 (增强版)
题目：已知函数 f(x) 是定义在 (-∞,0)∪(0,+∞) 上的奇函数，点 (2,4) 在函数 f(x) 的图象上。
当 x<0 时，f(x)=x²+bx。求 b 的值、f(x) 解析式、若 f(a)=5 求 a 的值。

使用新增 AutoScene 增强方法:
- highlight_text(): 随机高亮效果
- camera_focus(): 动态相机聚焦
- annotate_region(): 区域标注覆盖

使用方法:
    cd E:\auto_manim\voice_test
    manimgl odd_function_demo.py OddFunctionDemo -w
"""

from manimlib import *
import os
import sys

# 添加项目路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "new_class"))

from new_class.auto_scene import (
    AutoScene, 
    create_stealth_axes, 
    create_glow_surrounding_rect,
    create_glow_function_graph,
    create_glow_wrapper,
    create_glow_point_cloud,
    is_gpu_glow_available,
    GlowFunctionGraph,
    GlowWrapperEffect,
)


class OddFunctionDemo(AutoScene):
    """
    奇函数综合题演示
    竖版视频格式 (9:16)
    """
    
    # === 常量区（便于调试） ===
    
    # 竖版视频配置 (27/4 x 12)
    CONFIG = {
        "camera_config": {
            "frame_width": 27/4,   # 6.75
            "frame_height": 12,
            "frame_rate": 30,
        }
    }
    
    # 布局位置 (从上到下，y范围 [-6, 6])
    # 上下布局：可视化在上，解题在下
    TITLE_Y = 5.5           # 标题区域（顶部）
    PROBLEM_Y = 3.5         # 题目区域
    VIZ_Y = 0.8             # 可视化区域中心（中上部）
    SOLUTION_Y = -2.2       # 解答区域（下方，确保不与字幕重叠）
    # 字幕区域约在 y=-5.2（由 AutoScene 控制）
    TransformMatchingShapes
    
    # 屏幕宽度限制
    SCREEN_WIDTH = 27/4     # 竖版安全宽度
    
    # 字体大小
    TITLE_FONT_SIZE = 24
    SOURCE_FONT_SIZE = 24
    PROBLEM_FONT_SIZE = 24  
    SOLUTION_FONT_SIZE = 24
    
    # 可视化参数 (缩小，给解题留空间)
    VIZ_WIDTH = 4.0
    VIZ_HEIGHT = 4.0
    VIZ_X_RANGE = [-6, 6, 1]
    VIZ_Y_RANGE = [-6, 6, 1]
    
    # 颜色
    HIGHLIGHT_COLOR = YELLOW
    ANSWER_COLOR = GREEN
    FUNC_COLOR_NEG = BLUE    # x < 0 部分
    FUNC_COLOR_POS = RED     # x > 0 部分
    
    def construct(self):
        """主流程调度"""
        self.setup_scene()
        
        # === 阶段调用 ===
        # self.phase1_title()
        # self.phase2_problem()
        self.phase3_visualization_with_part1()  # 可视化 + 第1问
        # self.phase4_part2()  # 第2问
        # self.phase5_part3()  # 第3问
        # self.phase6_ending()

    def setup_scene(self):
        """场景初始化"""
        self.enable_debug(True)
        self.set_animation_sounds_enabled(True)
        self.set_add_sounds_enabled(False)
        self.set_sound_gain(0.6)
        self.set_subtitle_style(font_size=22, edge_buff=0.3)
        # self.camera.frame.save_state()
        
        # self.camera.frame.reorient(-22, 39, 0, (np.float32(-0.74), np.float32(0.05), np.float32(-0.12)), 9.56)
        # self.play(Restore(self.camera.frame), run_time=2, rate_func=lambda t: smooth(smooth(t)))
        
        # 添加低透明度方格背景
        grid = self.add_grid_background(
            step=0.5,
            stroke_opacity=0.3,
            stroke_width=0.5,
        )
        self.add(grid)
        
        # 添加右上角红黄绿圆点
        lights = self.add_traffic_lights(buff=0.1)
        self.add(lights)
        
        # 跨阶段共享对象
        self.shared_objects = {}
    
    # ==================== Phase 1: 标题 ====================
    
    def phase1_title(self):
        """显示标题和题目来源"""
        # 导入辉光线条
        from shaderscene.mobject.glow_line import GlowLine
        
        source = Text(
            "【高考真题·函数综合】",
            font="STKaiti",
            font_size=self.SOURCE_FONT_SIZE,
            color=GREY
        ).move_to(UP * (self.TITLE_Y + 0.3))
        
        # 辉光下划线
        underline = GlowLine(
            start=LEFT * 3.2,
            end=RIGHT * 3.2,
            color=self.HIGHLIGHT_COLOR,
            glow_width=0.08,
            glow_factor=2.0,
        ).next_to(source, DOWN, buff=0.1)
        
        self.play(FadeIn(source), rate_func=smooth, run_time=0.5)
        self.play(FadeIn(underline, shift=LEFT * 10), rate_func=smooth, run_time=0.8)
        
        self.speak("大家好，今天我们来解一道奇函数综合题")
        
        self.shared_objects["title_group"] = Group(source, underline)
    
    # ==================== Phase 2: 题目展示 ====================
    
    def phase2_problem(self):
        """展示题目内容 - 使用 Tex 排版，自适应屏幕宽度"""
        # 使用 Tex 排版题目（更紧凑）
        problem_tex = Tex(
            r"\text{17. (10分) 已知函数 } f(x) \text{ 是定义在 }", 
            r"(-\infty,0) \cup (0,+\infty)",
            r"\text{ 上的奇函数，}",
            font_size=self.PROBLEM_FONT_SIZE
        )
        problem_tex.arrange(RIGHT, buff=0.05)
        
        line2 = Tex(
            r"\text{点 } (2,4) \text{ 在函数 } f(x) \text{ 的图象上。}",
            font_size=self.PROBLEM_FONT_SIZE
        )
        line2[1:6].set_color(self.HIGHLIGHT_COLOR)  # (2,4) 高亮
        
        line3 = Tex(
            r"\text{当 } x < 0 \text{ 时，} f(x) = x^2 + bx",
            font_size=self.PROBLEM_FONT_SIZE
        )
        line3[-10:].set_color(self.HIGHLIGHT_COLOR)  # 公式高亮
        
        # 小问
        questions = Group(
            Tex(r"\text{(1) 求实数 } b \text{ 的值}", font_size=self.PROBLEM_FONT_SIZE),
            Tex(r"\text{(2) 求函数 } f(x) \text{ 的解析式}", font_size=self.PROBLEM_FONT_SIZE),
            Tex(r"\text{(3) 若 } f(a) = 5 \text{，求 } a \text{ 的值}", font_size=self.PROBLEM_FONT_SIZE),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        
        # 组合并排列
        problem_group = Group(problem_tex, line2, line3, questions)
        problem_group.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        problem_group.move_to(UP * self.PROBLEM_Y)
        
        problem_group.stretch_to_fit_width(self.SCREEN_WIDTH*0.95)
        # 题目不 fix，跟随相机
        
        # 动画
        self.play(Write(problem_tex), rate_func=smooth, run_time=1)
        self.play(Write(line2), rate_func=smooth, run_time=0.8)
        
        self.speak_with_highlight(
            text="f x 是奇函数，坐标 2 4 在图像上",
            subtitle="f(x) 是奇函数，坐标 (2,4) 在图像上",
            targets=[line2]
        )
        
        # 添加弯曲箭头指示关键点 (2,4)
        arrow_24 = self.add_curved_annotation(
            line2[1:6],  # (2,4) 部分
            "关键条件",
            direction="dr",
            text_font_size=18,
            arrow_color=self.HIGHLIGHT_COLOR,
        )
        self.wait(0.5)
        self.play(FadeOut(arrow_24), run_time=0.3)
        
        self.play(Write(line3), rate_func=smooth, run_time=0.8)
        
        # 使用新方法：随机高亮公式部分
        hl = self.highlight_text(line3[-10:], effect="random")
        self.wait(0.3)
        if hl:
            self.remove_highlight(hl)
        
        self.play(FadeIn(questions), rate_func=smooth, run_time=0.8)
        
        self.speak_with_highlight(
            text="当 x 小于 0 时，f x 等于 x 平方加 b x",
            subtitle="当 x < 0 时，f(x) = x² + bx",
            targets=[line3]
        )
        
        # 添加弯曲箭头指示公式中的 b
        arrow_b = self.add_curved_annotation(
            line3[-2:],  # bx 部分
            "待求参数",
            direction="dr",
            text_font_size=18,
            arrow_color=BLUE,
        )
        self.wait(0.5)
        self.play(FadeOut(arrow_b), run_time=0.3)
        
        self.shared_objects["problem_group"] = problem_group
    
    # ==================== Phase 3: 可视化 + 第1问 ====================
    
    def phase3_visualization_with_part1(self):
        """同时显示可视化图像和第1问解答"""
        # --- 创建坐标系 (使用 StealthTip 箭头，无刻度) ---
        stealth_axes = create_stealth_axes(
            x_range=self.VIZ_X_RANGE,
            y_range=self.VIZ_Y_RANGE,
            axis_config={
                "stroke_width": 1.5,
                "color": WHITE,
            },
            tip_config={
                "tip_length": 0.25,
                "tip_width": 0.2,
                "back_indent": 0.3,
            },
            width=self.VIZ_WIDTH,
            height=self.VIZ_HEIGHT,
        ).move_to(UP * self.VIZ_Y)
        
        # 使用 stealth_axes 的内部 axes 对象
        axes = stealth_axes.axes
        
        x_label = Tex("x", font_size=16).next_to(stealth_axes.x_tip, RIGHT, buff=0.1)
        y_label = Tex("y", font_size=16).next_to(stealth_axes.y_tip, UP, buff=0.1)
        origin_label = Tex("O", font_size=14).next_to(axes.c2p(0, 0), DL, buff=0.08)
        
        self.play(ShowCreation(stealth_axes), rate_func=smooth, run_time=1)
        self.play(Write(x_label), Write(y_label), Write(origin_label), run_time=0.5)
        
        # ========== 动态展示 b 参数变化 ==========
        # 使用 ValueTracker 控制 b 参数
        b_tracker = ValueTracker(0)  # 初始 b=0
        
        # 动态曲线（随 b 变化实时更新）
        def get_dynamic_curve_neg():
            b = b_tracker.get_value()
            return axes.get_graph(
                lambda x: x**2 + b*x,
                x_range=[-5.5, -0.1],
                color=self.FUNC_COLOR_NEG,
                stroke_width=2
            )
        
        def get_dynamic_curve_pos():
            b = b_tracker.get_value()
            return axes.get_graph(
                lambda x: -x**2 + b*x,
                x_range=[0.1, 5.5],
                color=self.FUNC_COLOR_POS,
                stroke_width=2
            )
        
        # 使用 always_redraw 创建动态曲线
        dynamic_curve_neg = always_redraw(get_dynamic_curve_neg)
        dynamic_curve_pos = always_redraw(get_dynamic_curve_pos)
        
        # b 值显示标签（随 b 变化实时更新）
        def get_b_label():
            b = b_tracker.get_value()
            label = Tex(f"b = {b:.1f}", font_size=20, color=YELLOW)
            label.to_corner(UR, buff=0.3)
            return label
        
        b_label = always_redraw(get_b_label)
        
        # 关键点标签（不使用 Dot），直接使用坐标定位标签并添加辉光方框
        p24_pos = axes.c2p(2, 4)
        point_24_label = Tex("(2,4)", font_size=14, color=WHITE)
        point_24_label.move_to(p24_pos + UR * 0.2)
        # 使用辉光方框 API
        point_24_bg = create_glow_surrounding_rect(
            point_24_label,
            color=self.FUNC_COLOR_POS,
            buff=0.03,
            stroke_width=1,
            fill_opacity=0.6,
            n_glow_layers=2,
            max_glow_width=8,
            base_opacity=0.2,
        )

        p_n2n4_pos = axes.c2p(-2, -4)
        point_n2n4_label = Tex("(-2,-4)", font_size=14, color=WHITE)
        point_n2n4_label.move_to(p_n2n4_pos + DL * 0.2)
        # 使用辉光方框 API
        point_n2n4_bg = create_glow_surrounding_rect(
            point_n2n4_label,
            color=self.FUNC_COLOR_NEG,
            buff=0.03,
            stroke_width=1,
            fill_opacity=0.6,
            n_glow_layers=2,
            max_glow_width=8,
            base_opacity=0.2,
        )
        
        self.speak("让我们先看函数图像，观察参数 b 的变化")
        
        # 添加动态曲线和 b 值标签
        self.add(dynamic_curve_neg, dynamic_curve_pos, b_label)
        
        # 动画：b 从 0 变化到 4
        self.play(
            b_tracker.animate.set_value(4),
            run_time=3,
            rate_func=smooth
        )
        
        # 显示关键点（先背景再标签）
        self.play(
            FadeIn(point_24_bg), Write(point_24_label),
            FadeIn(point_n2n4_bg), Write(point_n2n4_label),
            run_time=1
        )
        
        self.speak_with_highlight(
            text="当 b 等于 4 时，坐标 2 4 和 负 2 负 4 关于原点对称",
            subtitle="当 b = 4 时，(2,4) 和 (-2,-4) 关于原点对称",
            targets=[point_24_label, point_n2n4_label]
        )
        
        # 添加弯曲箭头指示对称性
        arrow_sym_1 = self.add_curved_annotation(
            point_24_label,
            "x > 0",
            direction="ur",
            text_font_size=16,
            arrow_color=self.FUNC_COLOR_POS,
        )
        arrow_sym_2 = self.add_curved_annotation(
            point_n2n4_label,
            "x < 0",
            direction="dl",
            text_font_size=16,
            arrow_color=self.FUNC_COLOR_NEG,
        )
        self.speak("这两个点关于原点对称，说明函数是奇函数")
        self.wait(0.8)
        self.play(FadeOut(arrow_sym_1), FadeOut(arrow_sym_2), run_time=0.4)
        
        # 移除动态曲线，使用坐标系的 get_glow_graph 方法
        self.remove(dynamic_curve_neg, dynamic_curve_pos, b_label)
        
        # 使用 stealth_axes.get_glow_graph 创建与坐标系对齐的辉光曲线
        if is_gpu_glow_available():
            # x < 0 部分: f(x) = x² + 4x
                curve_neg = stealth_axes.get_glow_graph(
                    function=lambda x: x**2 + 4*x,
                    x_range=[-5.5, -0.1],
                    color=self.FUNC_COLOR_NEG,
                    n_samples=500,
                )
            
            # x > 0 部分: f(x) = -x² + 4x
                curve_pos = stealth_axes.get_glow_graph(
                    function=lambda x: -x**2 + 4*x,
                    x_range=[0.1, 5.5],
                    color=self.FUNC_COLOR_POS,
                    n_samples=500,
                )
        else:
            # 回退到普通曲线
            curve_neg = axes.get_graph(lambda x: x**2 + 4*x, x_range=[-5.5, -0.1], color=self.FUNC_COLOR_NEG, stroke_width=2)
            curve_pos = axes.get_graph(lambda x: -x**2 + 4*x, x_range=[0.1, 5.5], color=self.FUNC_COLOR_POS, stroke_width=2)
        
        self.add(curve_neg, curve_pos)
        
        # 为关键点添加 GPU 辉光效果 (使用 get_glow_dots)
        if is_gpu_glow_available():
            # 使用 stealth_axes.get_glow_dots 创建辉光点
            glow_points = stealth_axes.get_glow_dots(
                coords=[(2, 4), (-2, -4)],
                colors=[self.HIGHLIGHT_COLOR, self.HIGHLIGHT_COLOR],
                glow_width=0.3,
                glow_factor=0.5,
            )
            self.add(glow_points)
        
        # --- 第1问解答 (可视化下方) ---
        step_y = self.SOLUTION_Y
        
        step1 = Tex(r"f(2) = 4", font_size=self.SOLUTION_FONT_SIZE).move_to(UP * step_y)
        # 解题步骤不 fix，跟随相机
        step2 = Tex(r"f(-2) = -f(2) = -4", font_size=self.SOLUTION_FONT_SIZE, color=self.HIGHLIGHT_COLOR)
        step2.next_to(step1, DOWN, buff=0.12)
        step3 = Tex(r"f(-2) = 4 - 2b = -4", font_size=self.SOLUTION_FONT_SIZE)
        step3.next_to(step2, DOWN, buff=0.12)
        step4 = Tex(r"\therefore b = 4", font_size=self.SOLUTION_FONT_SIZE + 2, color=self.ANSWER_COLOR)
        step4.next_to(step3, DOWN, buff=0.12)
        
        self.speak("首先求 b 的值")
        
        # 第一行：直接 Write
        self.play(Write(step1), run_time=0.8)
        
        # step1 -> step2：f(2)=4 转换到 f(-2)=-f(2)=-4
        step1_copy = step1.copy()
        self.play(TransformMatchingShapes(step1_copy, step2), run_time=0.8)
        self.add(step2)
        
        # step2 -> step3
        step2_copy = step2.copy()
        self.play(TransformMatchingShapes(step2_copy, step3), run_time=0.8)
        self.add(step3)
        
        # step4：结论
        self.play(Write(step4), run_time=0.8)
        
        # 方框引导 + 配音同步 + 相机跟随
        self.speak(text="由 f 2 等于 4", subtitle="由 f(2) = 4")
        self.focus_guide_with_camera([step1], zoom_factor=1.2, hold_time=1.0, auto_remove=True)
        
        self.speak(text="利用奇函数性质，f 负 2 等于 负 4", subtitle="利用奇函数性质，f(-2) = -4")
        self.focus_guide_with_camera([step2], zoom_factor=1.2, hold_time=1.0, auto_remove=True)
        
        self.speak(text="代入解析式 f 负 2 等于 4 减 2b 等于 负 4", subtitle="代入解析式 f(-2) = 4 - 2b = -4")
        self.focus_guide_with_camera([step3], zoom_factor=1.2, hold_time=1.0, auto_remove=True)
        
        self.speak(text="解得 b 等于 4", subtitle="解得 b = 4")
        self.focus_guide_with_camera([step4], zoom_factor=1.2, hold_time=1.5, auto_remove=True)
        
        # 保存
        self.shared_objects["axes"] = axes
        self.shared_objects["stealth_axes"] = stealth_axes  # 保存以便后续使用 get_glow_dot
        self.shared_objects["viz_group"] = Group(
            stealth_axes, x_label, y_label, origin_label,
            curve_neg, curve_pos,
            point_24_label, point_n2n4_label
        )
        self.shared_objects["part1_steps"] = Group(step1, step2, step3, step4)
    
    # ==================== Phase 4: 第2问 ====================
    
    def phase4_part2(self):
        """求 f(x) 解析式"""
        # 清理第1问步骤
        if "part1_steps" in self.shared_objects:
            self.play(FadeOut(self.shared_objects["part1_steps"]), run_time=0.5)
        
        step_y = self.SOLUTION_Y
        
        step1 = Tex(r"x < 0: f(x) = x^2 + 4x", font_size=self.SOLUTION_FONT_SIZE)
        step1.move_to(UP * step_y)
        # 解题步骤不 fix
        
        step2 = Tex(r"x > 0: -x < 0", font_size=self.SOLUTION_FONT_SIZE)
        step2.next_to(step1, DOWN, buff=0.12)
        
        step3 = Tex(r"f(-x) = x^2 - 4x", font_size=self.SOLUTION_FONT_SIZE)
        step3.next_to(step2, DOWN, buff=0.12)
        
        step4 = Tex(r"f(x) = -x^2 + 4x", font_size=self.SOLUTION_FONT_SIZE, color=self.HIGHLIGHT_COLOR)
        step4.next_to(step3, DOWN, buff=0.12)
        
        result = Tex(
            r"f(x) = \begin{cases} x^2 + 4x, & x < 0 \\ -x^2 + 4x, & x > 0 \end{cases}",
            font_size=self.SOLUTION_FONT_SIZE,
            color=self.ANSWER_COLOR
        ).next_to(step4, DOWN, buff=0.2)
        
        self.speak("接下来求解析式")
        
        # step1, step2：独立条件，直接 Write
        self.play(Write(step1), run_time=0.8)
        self.play(Write(step2), run_time=0.6)
        
        # step2 -> step3
        step2_copy = step2.copy()
        self.play(TransformMatchingShapes(step2_copy, step3), run_time=0.8)
        self.add(step3)
        
        # step3 -> step4
        step3_copy = step3.copy()
        self.play(TransformMatchingShapes(step3_copy, step4), run_time=0.8)
        self.add(step4)
        
        # result
        self.play(Write(result), run_time=1)
        
        # 方框引导 + 配音同步 + 相机跟随
        self.speak(text="当 x 小于 0 时，f x 等于 x 平方 加 4 x", subtitle="当 x < 0 时，f(x) = x² + 4x")
        self.focus_guide_with_camera([step1], zoom_factor=1.2, hold_time=1.0, auto_remove=True)
        
        self.speak("利用奇函数性质进行转化")
        self.focus_guide_with_camera([step3, step4], zoom_factor=1.2, hold_time=1.2, auto_remove=True)
        
        self.speak("得到分段函数的解析式")
        self.focus_guide_with_camera([result], zoom_factor=1.2, hold_time=1.5, auto_remove=True)
        
        self.shared_objects["part2_steps"] = Group(step1, step2, step3, step4, result)
    
    # ==================== Phase 5: 第3问 ====================
    
    def phase5_part3(self):
        """求 a 的值"""
        # 清理第2问
        if "part2_steps" in self.shared_objects:
            self.play(FadeOut(self.shared_objects["part2_steps"]), run_time=0.5)
        
        # 在图上标注 f(a)=5 的点（使用 GPU 辉光点）
        axes = self.shared_objects.get("axes")
        stealth_axes = self.shared_objects.get("stealth_axes")
        point_n5_5 = None
        point_n5_5_glow = None
        
        
        if axes:
            # 不使用 Dot：仅创建标签与可选 GPU 辉光点
            p_n5_pos = axes.c2p(-5, 5)
            # 坐标标注使用辉光方框
            point_n5_5_label = Tex("(-5,5)", font_size=14, color=WHITE)
            point_n5_5_label.move_to(p_n5_pos + UP * 0.2)
            point_n5_5_bg = create_glow_surrounding_rect(
                point_n5_5_label,
                color=GREEN,
                buff=0.03,
                stroke_width=1,
                fill_opacity=0.6,
                n_glow_layers=2,
                max_glow_width=10,
                base_opacity=0.25,
            )

            # 使用 stealth_axes.get_glow_dot 创建辉光点（不创建普通 Dot）
            if stealth_axes and is_gpu_glow_available():
                point_n5_5_glow = stealth_axes.get_glow_dot(
                    x=-5, y=5,
                    color=GREEN,
                    glow_width=0.15,
                    glow_factor=1.5,
                )
                self.play(
                    FadeIn(point_n5_5_glow), 
                    FadeIn(point_n5_5_bg), Write(point_n5_5_label), 
                    run_time=0.8
                )
            else:
                self.play(FadeIn(point_n5_5_bg), Write(point_n5_5_label), run_time=0.8)
        
        step_y = self.SOLUTION_Y
        
        title = Tex(r"f(a) = 5", font_size=self.SOLUTION_FONT_SIZE)
        title.move_to(UP * step_y)
        # 解题步骤不 fix
        
        case1 = Tex(r"a > 0: \Delta < 0, \text{无解}", font_size=self.SOLUTION_FONT_SIZE, color=RED)
        case1.next_to(title, DOWN, buff=0.12)
        
        case2 = Tex(r"a < 0: a^2 + 4a = 5", font_size=self.SOLUTION_FONT_SIZE)
        case2.next_to(case1, DOWN, buff=0.12)
        
        case2_solve = Tex(r"(a+5)(a-1) = 0", font_size=self.SOLUTION_FONT_SIZE)
        case2_solve.next_to(case2, DOWN, buff=0.1)
        
        answer = Tex(r"\therefore a = -5", font_size=self.SOLUTION_FONT_SIZE + 3, color=self.ANSWER_COLOR)
        answer.next_to(case2_solve, DOWN, buff=0.12)
        
        self.speak("最后求 a 的值")
        
        self.play(Write(title), run_time=0.6)
        self.play(Write(case1), run_time=0.8)
        self.play(Write(case2), run_time=0.8)
        self.play(Write(case2_solve), run_time=0.8)
        self.play(Write(answer), run_time=0.8)
        
        # 方框引导 + 配音同步 + 相机跟随
        self.speak(text="设 f a 等于 5", subtitle="设 f(a) = 5")
        self.focus_guide_with_camera([title], zoom_factor=1.2, hold_time=0.8, auto_remove=True)
        
        self.speak(text="当 a 大于 0 时，判别式小于 0，无解", subtitle="当 a > 0 时，Δ < 0，无解")
        self.focus_guide_with_camera([case1], zoom_factor=1.2, hold_time=1.0, auto_remove=True)
        
        self.speak(text="当 a 小于 0 时，代入解析式", subtitle="当 a < 0 时，代入解析式")
        self.focus_guide_with_camera([case2], zoom_factor=1.2, hold_time=1.0, auto_remove=True)
        
        self.speak(text="因式分解得 a 等于 负 5 或 a 等于 1", subtitle="因式分解得 a = -5 或 a = 1")
        self.focus_guide_with_camera([case2_solve], zoom_factor=1.2, hold_time=1.0, auto_remove=True)
        
        self.speak(text="由于 a 小于 0，所以 a 等于 负 5", subtitle="由于 a < 0，所以 a = -5")
        self.focus_guide_with_camera([answer], zoom_factor=1.2, hold_time=1.5, auto_remove=True)
        
        if axes:
            # 相机聚焦到图上的关键点（优先使用 GPU 辉光点）
            focus_target = None
            if 'point_n5_5_glow' in locals() and point_n5_5_glow is not None:
                focus_target = point_n5_5_glow
            else:
                focus_target = point_n5_5_label

            self.camera_focus(focus_target, zoom_factor=2.0, hold_time=2.0)

            # 添加弯曲箭头指示最终答案点
            arrow_answer = self.add_curved_annotation(
                point_n5_5_label,
                "答案",
                direction="ur",
                text_font_size=18,
                arrow_color=self.ANSWER_COLOR,
            )

            self.speak_with_highlight(
                "在图上就是这个点",
                targets=[focus_target]
            )
            
            self.wait(0.5)
            self.play(FadeOut(arrow_answer), run_time=0.3)
    
    # ==================== Phase 6: 结束 ====================
    
    def phase6_ending(self):
        """总结和结束语"""
        # 显示辉光总结文字
        summary = self.create_glow_text(
            "奇函数性质",
            font="STKaiti",
            font_size=32,
            color=YELLOW,
            glow_color=YELLOW,
            glow_size=0.35,
        ).move_to(UP * 1)
        
        # 关键公式（辉光 TeX，不指定颜色自动轮询色盘）
        key_formula = self.create_glow_tex(
            r"f(-x) = -f(x)",
            font_size=36,
            # 不指定颜色，自动使用轮询色盘
            glow_size=0.3,
        ).next_to(summary, DOWN, buff=0.5)
        
        self.speak("这道题的关键是利用奇函数性质进行转化")
        self.play(FadeIn(summary), run_time=0.8)
        
        self.speak("记住 f(-x) 等于负 f(x)")
        self.play(FadeIn(key_formula), run_time=0.8)
        
        self.wait(2)
        
        self.speak("感谢观看，下期再见！")
        self.wait(1)


if __name__ == "__main__":
    os.system(f'cd "{script_dir}" && manimgl odd_function_demo.py OddFunctionDemo -s' )
