"""
牛顿冷却定律 - 凶杀案作案时间推断

运行方法:
    cd E:/auto_manim/xianyu
    manimgl newton_cooling_demo.py NewtonCoolingDemo -w
"""

from manimlib import *
import os
import sys
import numpy as np

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
    create_glowing_curved_arrow,
    is_gpu_glow_available,
)

# 引入 Table 类
from utils.table import Table, MathTable


class NewtonCoolingDemo(AutoScene):
    """
    牛顿冷却定律动画 - 凶杀案作案时间推断
    16:9 横版视频 (frame_height=8)
    """
    
    # === 配置 ===
    CONFIG = {
        "camera_config": {
            "frame_width": 14.22,  # 16:9 ratio with height=8
            "frame_height": 8,
            "frame_rate": 30,
        }
    }
    
    # 字体大小
    TITLE_FONT_SIZE = 32
    PROBLEM_FONT_SIZE = 22
    FORMULA_FONT_SIZE = 26
    SOLUTION_FONT_SIZE = 24
    
    # 颜色
    HIGHLIGHT_COLOR = YELLOW
    ANSWER_COLOR = GREEN
    TEMP_COLOR = RED
    TIME_COLOR = BLUE
    
    def construct(self):
        """主流程调度"""
        self.setup_scene()

        self.phase1_intro()           # 问题引入 (30s)
        self.phase2_modeling()        # 建模过程 (60s)
        self.phase3_solving()         # 求解动画 (90s)
        self.phase4_result()          # 结果演示 (60s)
        self.phase5_conclusion()      # 实际意义 (30s)
    
    def setup_scene(self):
        """场景初始化"""
        self.enable_debug(True)
        self.set_animation_sounds_enabled(False)  # 禁用音效
        self.set_add_sounds_enabled(False)
        self.set_subtitle_style(font_size=26, edge_buff=0.4, max_chars=999)  # 字幕不换行
        
        # 添加低透明度方格背景
        grid = self.add_grid_background(
            step=0.5,
            stroke_opacity=0.15,
            stroke_width=0.5,
        )
        self.add(grid)
        
        # 保存相机初始状态
        self.camera.frame.save_state()
        
        # 跨阶段共享对象
        self.shared_objects = {}
    
    # ==================== Phase 1: 问题引入 (30s) ====================
    
    def phase1_intro(self):
        """问题引入 - 展示凶杀案场景"""
        # 标题
        title = Text(
            "【数学建模】牛顿冷却定律应用",
            font="STKaiti",
            font_size=self.TITLE_FONT_SIZE,
            color=WHITE
        ).to_edge(UP, buff=0.4)
        
        # 辉光下划线 - 使用 AutoScene API 自动定位
        underline = self.create_glow_underline(
            title,
            color=self.HIGHLIGHT_COLOR,
            offset_ratio=0.3,
            glow_width=0.06,
            glow_factor=2.0,
        )
        
        # 问题描述
        problem_lines = [
            "某天在一住宅发生一起凶杀案，下午16:00法医赶到现场，",
            "立即测得尸体温度为30度，室内环境温度为20度。",
            "已知在环境温度20度状况下，尸体在最初2小时温度下降2度。",
            "若假定室内环境基本上为恒温，试推断凶杀案作案时间。"
        ]
        
        problem_group = VGroup()
        for line in problem_lines:
            text = Text(line, font="STKaiti", font_size=self.PROBLEM_FONT_SIZE)
            problem_group.add(text)
        problem_group.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        problem_group.next_to(underline, DOWN, buff=0.4)
        
        # 动画展示
        self.play(Write(title), run_time=0.8)
        self.play(FadeIn(underline, shift=RIGHT * 2), run_time=0.5)
        self.speak(
            text="大家好，今天我们来看一道牛顿冷却定律的应用题",
            targets=[title],
            subtitle="牛顿冷却定律应用题",
            color_map={"牛顿冷却定律": BLUE},
            min_duration=2.0
        )
        
        for i, line in enumerate(problem_group):
            self.play(FadeIn(line, shift=UP*0.2), run_time=0.4)
            if i == 0:
                self.speak(
                    text="某天发生了一起凶杀案，下午4点法医到达现场",
                    targets=[line],
                    subtitle="下午16:00法医到达现场",
                    color_map={"4点": self.TIME_COLOR},
                    min_duration=2.0
                )
            elif i == 1:
                self.speak(
                    text="测得尸体温度30度，室内温度20度",
                    targets=[line],
                    subtitle="尸体30度 室内20度",
                    color_map={"30度": self.TEMP_COLOR, "20度": self.TIME_COLOR},
                    min_duration=2.0
                )
        
        self.wait(0.3)
        
        # 标注关键数据 - 使用辉光方框
        key_data = VGroup(
            Tex(r"T_0 = 20^\circ C", font_size=self.FORMULA_FONT_SIZE, color=self.TIME_COLOR),
            Tex(r"T(0) = 30^\circ C", font_size=self.FORMULA_FONT_SIZE, color=self.TEMP_COLOR),
            Tex(r"T(2) = 28^\circ C", font_size=self.FORMULA_FONT_SIZE, color=self.TEMP_COLOR),
            Tex(r"T_{body} = 37^\circ C", font_size=self.FORMULA_FONT_SIZE, color=self.HIGHLIGHT_COLOR),
        ).arrange(RIGHT, buff=0.6)
        key_data.next_to(problem_group, DOWN, buff=0.5)
        
        # 为关键数据添加辉光方框
        key_data_boxes = VGroup()
        for item in key_data:
            box = create_glow_surrounding_rect(
                item, color=item.get_color(), buff=0.08,
                stroke_width=2, n_glow_layers=3, base_opacity=0.2
            )
            key_data_boxes.add(box)
        
        # 逐个显示关键数据并配音
        # T_0 = 20°C
        self.play(FadeIn(key_data_boxes[0]), FadeIn(key_data[0]), run_time=0.5)
        arrow_t0 = self.add_curved_annotation(
            key_data[0], "环境恒温", direction="dr",
            text_font_size=16, arrow_color=self.TIME_COLOR
        )
        self.speak(
            text="首先是环境温度20摄氏度，这是恒定不变的",
            targets=[key_data[0]],
            subtitle="环境温度T0=20度 保持恒定",
            color_map={"环境温度": self.TIME_COLOR},
            min_duration=2.0
        )
        self.play(FadeOut(arrow_t0), run_time=0.3)
        
        # T(0) = 30°C
        self.play(FadeIn(key_data_boxes[1]), FadeIn(key_data[1]), run_time=0.5)
        arrow_t1 = self.add_curved_annotation(
            key_data[1], "发现时温度", direction="dr",
            text_font_size=16, arrow_color=self.TEMP_COLOR
        )
        self.speak(
            text="法医到达时测得尸体温度30度，记为T零等于30",
            targets=[key_data[1]],
            subtitle="发现时尸体温度 T(0)=30度",
            color_map={"30度": self.TEMP_COLOR},
            min_duration=2.0
        )
        self.play(FadeOut(arrow_t1), run_time=0.3)
        
        # T(2) = 28°C
        self.play(FadeIn(key_data_boxes[2]), FadeIn(key_data[2]), run_time=0.5)
        arrow_t2 = self.add_curved_annotation(
            key_data[2], "2小时后温度", direction="dl",
            text_font_size=16, arrow_color=self.TEMP_COLOR
        )
        self.speak(
            text="两小时后温度下降到28度，记为T二等于28",
            targets=[key_data[2]],
            subtitle="2小时后温度 T(2)=28度",
            color_map={"28度": self.TEMP_COLOR},
            min_duration=2.0
        )
        self.play(FadeOut(arrow_t2), run_time=0.3)
        
        # T_body = 37°C
        self.play(FadeIn(key_data_boxes[3]), FadeIn(key_data[3]), run_time=0.5)
        arrow_body = self.add_curved_annotation(
            key_data[3], "正常体温", direction="dl",
            text_font_size=16, arrow_color=self.HIGHLIGHT_COLOR
        )
        self.speak(
            text="人的正常体温是37度，死亡时即为此温度",
            targets=[key_data[3]],
            subtitle="正常体温 Tbody=37度 即死亡时刻温度",
            color_map={"37度": ORANGE},
            min_duration=2.0
        )
        self.play(FadeOut(arrow_body), run_time=0.3)
        
        self.shared_objects["title"] = title
        self.shared_objects["underline"] = underline
        self.shared_objects["problem"] = problem_group
        self.shared_objects["key_data"] = key_data
        self.shared_objects["key_data_boxes"] = key_data_boxes
    
    # ==================== Phase 2: 建模过程 (60s) ====================
    
    def phase2_modeling(self):
        """建模过程 - 展示牛顿冷却定律"""
        # 淡出问题文字，保留标题
        self.play(
            FadeOut(self.shared_objects.get("problem", VGroup())),
            FadeOut(self.shared_objects.get("key_data", VGroup())),
            FadeOut(self.shared_objects.get("key_data_boxes", VGroup())),
            run_time=0.5
        )
        
        title = self.shared_objects.get("title")
        underline = self.shared_objects.get("underline")
        
        # 牛顿冷却定律标题
        law_title = Text(
            "牛顿冷却定律",
            font="STKaiti",
            font_size=self.TITLE_FONT_SIZE,
            color=self.HIGHLIGHT_COLOR
        ).next_to(underline, DOWN, buff=0.5)
        
        law_desc = Text(
            "物体在介质中的冷却速度同该物体温度与介质温度之差成正比",
            font="STKaiti",
            font_size=self.PROBLEM_FONT_SIZE,
        ).next_to(law_title, DOWN, buff=0.3)
        
        # 微分方程
        diff_eq = Tex(
            r"\frac{dT}{dt} = -k(T - T_0)",
            font_size=self.FORMULA_FONT_SIZE + 6
        ).next_to(law_desc, DOWN, buff=0.5)
        
        # 为微分方程添加辉光方框
        diff_eq_box = create_glow_surrounding_rect(
            diff_eq, color=BLUE, buff=0.15,
            stroke_width=2, n_glow_layers=4, base_opacity=0.25
        )
        
        # 变量说明
        vars_explain = VGroup(
            VGroup(Tex(r"T", color=self.TEMP_COLOR, font_size=22), 
                   Text("：物体温度", font="STKaiti", font_size=18)).arrange(RIGHT, buff=0.05),
            VGroup(Tex(r"T_0", color=self.TIME_COLOR, font_size=22), 
                   Text("：环境温度", font="STKaiti", font_size=18)).arrange(RIGHT, buff=0.05),
            VGroup(Tex(r"k", color=self.HIGHLIGHT_COLOR, font_size=22), 
                   Text("：冷却系数", font="STKaiti", font_size=18)).arrange(RIGHT, buff=0.05),
        ).arrange(RIGHT, buff=0.5)
        vars_explain.next_to(diff_eq, DOWN, buff=0.5)
        
        self.play(Write(law_title), run_time=0.6)
        self.speak(
            text="牛顿冷却定律告诉我们",
            targets=[law_title],
            subtitle="牛顿冷却定律",
            color_map={"牛顿冷却定律": ORANGE},
            min_duration=2.0
        )
        
        self.play(FadeIn(law_desc), run_time=0.6)
        self.speak(
            text="冷却速度与温差成正比",
            targets=[law_desc],
            subtitle="冷却速度与温差成正比",
            color_map={"冷却速度": self.TEMP_COLOR, "温差": self.TIME_COLOR},
            min_duration=2.0
        )
        
        self.play(FadeIn(diff_eq_box), Write(diff_eq), run_time=1.0)
        self.speak(
            text="写成微分方程就是 d T d t 等于负 k 乘以 T 减 T0",
            targets=[diff_eq],
            subtitle="微分方程 dT/dt = -k(T - T0)",
            color_map={"微分方程": BLUE},
            min_duration=2.0
        )
        
        # 使用 focus_guide 高亮微分方程
        self.focus_guide([diff_eq], hold_time=0.8)
        
        self.play(FadeIn(vars_explain), run_time=0.6)
        self.speak(
            text="其中 T 是物体温度，T0 是环境温度，k 是冷却系数",
            targets=[vars_explain],
            subtitle="T物体温度 T0环境温度 k冷却系数",
            color_map={"T": self.TEMP_COLOR, "T0": self.TIME_COLOR, "k": ORANGE},
            min_duration=2.0
        )
        
        self.shared_objects["law_title"] = law_title
        self.shared_objects["law_desc"] = law_desc
        self.shared_objects["diff_eq"] = diff_eq
        self.shared_objects["diff_eq_box"] = diff_eq_box
        self.shared_objects["vars_explain"] = vars_explain
    
    # ==================== Phase 3: 求解动画 (90s) ====================
    
    def phase3_solving(self):
        """求解微分方程"""
        # 清理上一阶段，保留微分方程
        title = self.shared_objects.get("title")
        underline = self.shared_objects.get("underline")
        diff_eq = self.shared_objects.get("diff_eq")
        diff_eq_box = self.shared_objects.get("diff_eq_box")
        
        self.play(
            FadeOut(self.shared_objects.get("law_title", VGroup())),
            FadeOut(self.shared_objects.get("law_desc", VGroup())),
            FadeOut(self.shared_objects.get("vars_explain", VGroup())),
            diff_eq.animate.next_to(underline, DOWN, buff=0.4),
            diff_eq_box.animate.next_to(underline, DOWN, buff=0.4),
            run_time=0.6
        )
        
        # 重新定位 diff_eq_box
        diff_eq_box_new = create_glow_surrounding_rect(
            diff_eq, color=BLUE, buff=0.1,
            stroke_width=2, n_glow_layers=3, base_opacity=0.2
        )
        self.remove(diff_eq_box)
        self.add(diff_eq_box_new)
        
        # 求解步骤
        step1 = Tex(
            r"\text{令 } u = T - T_0, \text{ 则 } \frac{du}{dt} = -ku",
            font_size=self.SOLUTION_FONT_SIZE
        ).next_to(diff_eq, DOWN, buff=0.4)
        
        step2 = Tex(
            r"\frac{du}{u} = -k \, dt",
            font_size=self.SOLUTION_FONT_SIZE
        ).next_to(step1, DOWN, buff=0.25)
        
        step3 = Tex(
            r"\ln|u| = -kt + C",
            font_size=self.SOLUTION_FONT_SIZE
        ).next_to(step2, DOWN, buff=0.25)
        
        step4 = Tex(
            r"u = Ae^{-kt}, \text{ 即 } T - T_0 = Ae^{-kt}",
            font_size=self.SOLUTION_FONT_SIZE
        ).next_to(step3, DOWN, buff=0.25)
        
        solution = Tex(
            r"T(t) = T_0 + Ae^{-kt}",
            font_size=self.SOLUTION_FONT_SIZE + 4,
            color=self.HIGHLIGHT_COLOR
        ).next_to(step4, DOWN, buff=0.4)
        
        # 动画演示
        self.speak(
            text="现在我们来求解这个微分方程",
            targets=[diff_eq],
            subtitle="求解微分方程",
            color_map={"微分方程": BLUE},
            min_duration=2.0
        )
        
        self.play(Write(step1), run_time=0.8)
        self.speak(
            text="令 u 等于 T 减 T0",
            targets=[step1],
            subtitle="令 u = T - T0",
            color_map={"u": TEAL},
            min_duration=2.0
        )
        
        # 使用 highlight_text 强调
        hl = self.highlight_text(step1, effect="box", color=YELLOW)
        self.wait(0.3)
        if hl:
            self.remove_highlight(hl)
        
        self.play(Write(step2), run_time=0.6)
        self.speak(
            text="分离变量",
            targets=[step2],
            subtitle="分离变量",
            color_map={"分离变量": BLUE},
            min_duration=2.0
        )
        
        self.play(Write(step3), run_time=0.6)
        self.speak(
            text="两边积分",
            targets=[step3],
            subtitle="两边积分",
            color_map={"积分": BLUE},
            min_duration=2.0
        )
        
        self.play(Write(step4), run_time=0.8)
        self.speak(
            text="得到指数形式的解",
            targets=[step4],
            subtitle="得到指数形式的解",
            color_map={"指数形式": TEAL},
            min_duration=2.0
        )
        
        # 通解添加辉光方框
        solution_box = create_glow_surrounding_rect(
            solution, color=self.HIGHLIGHT_COLOR, buff=0.1,
            stroke_width=2, n_glow_layers=4, base_opacity=0.3
        )
        
        self.play(FadeIn(solution_box), Write(solution), run_time=0.8)
        self.speak(
            text="通解为 T t 等于 T0 加 A 乘以 e 的负 kt 次方",
            targets=[solution],
            subtitle="通解 T(t) = T0 + Ae^(-kt)",
            color_map={"通解": ORANGE},
            min_duration=2.0
        )
        
        # 使用相机聚焦
        self.focus_guide_with_camera([solution], zoom_factor=1.3, hold_time=1.0, auto_remove=True)
        
        # 清理并展示代入过程
        self.wait(0.3)
        solving_group = VGroup(step1, step2, step3, step4)
        self.play(
            FadeOut(solving_group), 
            FadeOut(diff_eq_box_new),
            solution.animate.next_to(diff_eq, DOWN, buff=0.4),
            solution_box.animate.next_to(diff_eq, DOWN, buff=0.4),
            run_time=0.5
        )
        
        # 重建 solution_box
        solution_box_new = create_glow_surrounding_rect(
            solution, color=self.HIGHLIGHT_COLOR, buff=0.1,
            stroke_width=2, n_glow_layers=3, base_opacity=0.2
        )
        self.remove(solution_box)
        self.add(solution_box_new)
        
        # 条件和代入
        conditions = Tex(
            r"T_0 = 20, \quad T(0) = 30, \quad T(2) = 28", 
            font_size=self.SOLUTION_FONT_SIZE
        ).next_to(solution, DOWN, buff=0.4)
        
        sub1 = Tex(
            r"T(0) = 30: \quad 20 + A = 30 \Rightarrow A = 10",
            font_size=self.SOLUTION_FONT_SIZE
        ).next_to(conditions, DOWN, buff=0.3)
        
        sub2 = Tex(
            r"T(2) = 28: \quad 20 + 10e^{-2k} = 28",
            font_size=self.SOLUTION_FONT_SIZE
        ).next_to(sub1, DOWN, buff=0.25)
        
        sub3 = Tex(
            r"e^{-2k} = 0.8 \Rightarrow k = \frac{\ln 1.25}{2}",
            font_size=self.SOLUTION_FONT_SIZE
        ).next_to(sub2, DOWN, buff=0.25)
        
        final_eq = Tex(
            r"T(t) = 20 + 10 \cdot (0.8)^{t/2}",
            font_size=self.SOLUTION_FONT_SIZE + 4,
            color=self.ANSWER_COLOR
        ).next_to(sub3, DOWN, buff=0.4)
        
        self.play(FadeIn(conditions), run_time=0.6)
        self.speak(
            text="代入已知条件：环境温度20度，初始30度，2小时后28度",
            targets=[conditions],
            subtitle="代入 T0=20 T(0)=30 T(2)=28",
            color_map={"20度": self.TIME_COLOR, "30度": self.TEMP_COLOR, "28度": self.TEMP_COLOR},
            min_duration=2.0
        )
        
        self.play(Write(sub1), run_time=0.8)
        self.speak(
            text="由 T 0 等于 30 得 A 等于 10",
            targets=[sub1],
            subtitle="由 T(0)=30 得 A=10",
            color_map={"A": TEAL},
            min_duration=2.0
        )
        
        self.play(Write(sub2), run_time=0.8)
        self.play(Write(sub3), run_time=0.8)
        self.speak(
            text="由 T 2 等于 28 得 e 的负 2k 等于 0.8",
            targets=[sub2, sub3],
            subtitle="由 T(2)=28 得 e^(-2k)=0.8",
            color_map={"k": TEAL},
            min_duration=2.0
        )
        
        # 最终结果添加辉光
        final_eq_box = create_glow_surrounding_rect(
            final_eq, color=self.ANSWER_COLOR, buff=0.1,
            stroke_width=2, n_glow_layers=4, base_opacity=0.3
        )
        
        self.play(FadeIn(final_eq_box), Write(final_eq), run_time=0.8)
        self.speak(
            text="最终得到温度随时间的函数",
            targets=[final_eq],
            subtitle="温度函数 T(t)=20+10x0.8^(t/2)",
            color_map={"温度": self.TEMP_COLOR, "时间": self.TIME_COLOR},
            min_duration=2.0
        )
        
        # 使用 focus_guide_with_camera 强调结果
        self.focus_guide_with_camera([final_eq], zoom_factor=1.4, hold_time=1.2, auto_remove=True)
        
        self.shared_objects["solution"] = solution
        self.shared_objects["solution_box"] = solution_box_new
        self.shared_objects["final_eq"] = final_eq
        self.shared_objects["final_eq_box"] = final_eq_box
        self.shared_objects["solve_steps"] = VGroup(conditions, sub1, sub2, sub3)
    
    # ==================== Phase 4: 结果演示 (60s) ====================
    
    def phase4_result(self):
        """结果演示 - 图表可视化"""
        # === 清理前面阶段的对象（如果存在） ===
        self.safe_fadeout("diff_eq", "solution", "solution_box", "solve_steps", "title", "underline")
        
        # === 获取或创建 final_eq（支持独立运行） ===
        def create_final_eq():
            """factory 函数：创建完整的公式对象并添加到场景"""
            eq = Tex(
                r"T(t) = 20 + 10 \cdot (0.8)^{t/2}",
                font_size=self.SOLUTION_FONT_SIZE + 4,
                color=self.ANSWER_COLOR
            ).to_edge(UP, buff=0.5)
            self.add(eq)  # 自动添加到场景
            return eq
        
        final_eq = self.get_shared("final_eq", factory=create_final_eq)
        
        # 如果已存在（从前序阶段传来），移动到顶部
        if final_eq in self.mobjects:
            self.play(final_eq.animate.to_edge(UP, buff=0.5), run_time=0.3)
        
        # === 重建 final_eq_box ===
        old_box = self.shared_objects.get("final_eq_box")
        if old_box:
            self.remove(old_box)
        
        final_eq_box = create_glow_surrounding_rect(
            final_eq, color=self.ANSWER_COLOR, buff=0.1,
            stroke_width=2, n_glow_layers=3, base_opacity=0.2
        )
        self.add(final_eq_box)
        self.set_shared("final_eq_box", final_eq_box)
        
        # 创建坐标系 - 使用标准配置，y从15到40
        # 注意：y_range从15开始，所以x轴自然在y=15处
        axes = create_stealth_axes(
            x_range=[0, 10, 2],
            y_range=[15, 40, 5],
            width=6,
            height=4,
            axis_config={"stroke_width": 1.5, "color": WHITE},
            tip_config={"tip_length": 0.15, "tip_width": 0.1},
        )
        
        # ❗重要：先移动坐标系到最终位置，再创建曲线
        # 这样 c2p 返回的坐标才是正确的
        axes.move_to(LEFT * 3 + DOWN * 0.3)
        
        # 添加轴标签
        x_label = Tex("t", font_size=18).next_to(axes.x_tip, RIGHT, buff=0.08)
        y_label = Tex("T", font_size=18).next_to(axes.y_tip, UP, buff=0.08)
        x_gr=Group(axes.x_axis, x_label,axes.x_tip).shift(UP*(axes.c2p(0,1)-axes.c2p(0,0))[1]*15)
        
        # 温度曲线 T(t) = 20 + 10 * 0.8^(t/2)
        def temp_func(t):
            return 20 + 10 * (0.8 ** (t / 2))
        
        # 绘制曲线 - 现在 axes 已经在最终位置，c2p 会返回正确坐标
        if is_gpu_glow_available():
            curve = axes.get_glow_graph(
                function=temp_func,
                x_range=[0, 10],
                color=self.TEMP_COLOR,
                n_samples=200,
            )
        else:
            curve = axes.axes.get_graph(temp_func, x_range=[0, 10], color=self.TEMP_COLOR, stroke_width=2)
        
        # ===== 创建数值表格（增加数据点） =====
        t_values = [0, 2, 4, 6, 8]
        temp_values = [temp_func(t) for t in t_values]
        
        table_data = [
            [Tex(r"t=0", font_size=18), Tex(r"20+10\times0.8^0", font_size=16), Tex(r"=30", font_size=16, color=self.TEMP_COLOR)],
            [Tex(r"t=2", font_size=18), Tex(r"20+10\times0.8^1", font_size=16), Tex(r"=28", font_size=16, color=self.TEMP_COLOR)],
            [Tex(r"t=4", font_size=18), Tex(r"20+10\times0.8^2", font_size=16), Tex(r"=26.4", font_size=16, color=self.TEMP_COLOR)],
            [Tex(r"t=6", font_size=18), Tex(r"20+10\times0.8^3", font_size=16), Tex(r"\approx 25.1", font_size=16, color=self.TEMP_COLOR)],
            [Tex(r"t=8", font_size=18), Tex(r"20+10\times0.8^4", font_size=16), Tex(r"\approx 24.1", font_size=16, color=self.TEMP_COLOR)],
        ]
        
        calc_table = Table(
            table_data,
            col_labels=[
                Text("时间", font="STKaiti", font_size=16, color=self.TIME_COLOR),
                Text("代入公式", font="STKaiti", font_size=16),
                Text("结果", font="STKaiti", font_size=16, color=self.ANSWER_COLOR),
            ],
            include_outer_lines=True,
            v_buff=0.25,
            h_buff=0.3,
            line_config={"stroke_width": 1.5, "color": GREY_B},
        )
        
        # 表格宽度设为5.5
        target_width = 5.5
        if calc_table.get_width() != target_width:
            calc_table.scale(target_width / calc_table.get_width())
        
        # ===== 左右布局 =====
        # 坐标系已经在上面移动到位，更新标签位置
        x_label.next_to(axes.x_tip, RIGHT, buff=0.08)
        y_label.next_to(axes.y_tip, UP, buff=0.08)
        
        # 表格居右
        calc_table.move_to(RIGHT * 3.5)
        calc_table.align_to(axes, UP)
        
        # 显示坐标系和表格框架
        self.play(ShowCreation(axes), Write(x_label), Write(y_label), run_time=1.0)
        self.play(FadeIn(calc_table.lines), run_time=0.5)
        self.speak(
            text="让我们用图像和表格来展示温度变化",
            targets=[axes],
            subtitle="用图像和表格展示温度变化",
            color_map={"图像": BLUE, "表格": GREEN},
            min_duration=2.0
        )
        
        # 显示表头
        if hasattr(calc_table, 'col_labels_mobjects') and calc_table.col_labels_mobjects:
            self.play(FadeIn(calc_table.col_labels_mobjects), run_time=0.5)
        
        # 同步显示表格行和图上的点
        points = []
        for i, t in enumerate(t_values):
            row = calc_table.get_row(i)
            if row is None:
                continue
            if isinstance(row, list):
                row = VGroup(*row)
            
            point = Dot(axes.axes.c2p(t, temp_values[i]), color=self.ANSWER_COLOR, radius=0.05)
            points.append(point)
            
            self.play(FadeIn(row), FadeIn(point), run_time=0.6)
            
            if i == 0:
                self.speak(
                    text="t等于0时，温度是30度",
                    targets=[row, point],
                    subtitle="t=0 时温度 30度",
                    color_map={"30度": self.TEMP_COLOR},
                    min_duration=1.5
                )
            elif i == 1:
                self.speak(
                    text="t等于2时，温度28度，与题目一致",
                    targets=[row, point],
                    subtitle="t=2 时温度 28度 验证正确",
                    color_map={"28度": self.TEMP_COLOR},
                    min_duration=1.5
                )
            elif i == 2:
                self.speak(
                    text="t等于4时，温度降到26点4度",
                    targets=[row, point],
                    subtitle="t=4 时温度 26.4度",
                    color_map={"26点4度": self.TEMP_COLOR},
                    min_duration=1.5
                )
            elif i == 3:
                self.speak(
                    text="t等于6时，温度约25点1度",
                    targets=[row, point],
                    subtitle="t=6 时温度约25.1度",
                    color_map={"25点1度": self.TEMP_COLOR},
                    min_duration=1.5
                )
            else:
                self.speak(
                    text="t等于8时，温度约24点1度，越来越接近20度",
                    targets=[row, point],
                    subtitle="t=8 时温度约24.1度 趋近环境温度",
                    color_map={"24点1度": self.TEMP_COLOR, "20度": self.TIME_COLOR},
                    min_duration=1.5
                )
        
        # 显示完整曲线
        self.add(curve)
        self.play(ShowCreation(curve), run_time=1.0)
        self.speak(
            text="这就是完整的温度变化曲线",
            targets=[curve],
            subtitle="完整的温度变化曲线",
            color_map={"温度": self.TEMP_COLOR},
            min_duration=1.5
        )
        
        self.wait(0.5)
        
        # 只淡出点，保留表格
        self.play(*[FadeOut(p) for p in points], run_time=0.5)
        
        # 标注关键水平线（延伸到x轴最右端 x=10）
        # y=37 体温线
        line_37 = DashedLine(
            axes.axes.c2p(0, 37), axes.axes.c2p(10, 37),
            color=self.HIGHLIGHT_COLOR, stroke_width=1.2
        )
        # y=30 发现时温度线  
        line_30 = DashedLine(
            axes.axes.c2p(0, 30), axes.axes.c2p(10, 30),
            color=self.TEMP_COLOR, stroke_width=1.2
        )
        # y=20 环境温度线（在x轴最右端）
        line_20 = DashedLine(
            axes.axes.c2p(0, 20), axes.axes.c2p(10, 20),
            color=self.TIME_COLOR, stroke_width=1.2
        )
        
        label_37 = Tex(r"37", font_size=14, color=self.HIGHLIGHT_COLOR).next_to(axes.axes.c2p(0, 37), LEFT, buff=0.08)
        label_30 = Tex(r"30", font_size=14, color=self.TEMP_COLOR).next_to(axes.axes.c2p(0, 30), LEFT, buff=0.08)
        label_20 = Tex(r"20", font_size=14, color=self.TIME_COLOR).next_to(axes.axes.c2p(0, 20), LEFT, buff=0.08)
        
        self.play(
            ShowCreation(line_37), ShowCreation(line_30), ShowCreation(line_20),
            Write(label_37), Write(label_30), Write(label_20),
            run_time=1.0
        )
        self.speak(
            text="37度是正常体温，30度是发现时的温度，20度是环境温度",
            targets=[label_37, label_30, label_20],
            subtitle="37度体温 30度发现时 20度环境",
            color_map={"37度": ORANGE, "30度": self.TEMP_COLOR, "20度": self.TIME_COLOR},
            min_duration=2.0
        )
        
        # 使用弧形箭头标注关键点
        key_point = Dot(axes.axes.c2p(0, 30), color=self.TEMP_COLOR, radius=0.08)
        self.play(FadeIn(key_point), run_time=0.3)
        
        arrow_key = self.add_curved_annotation(
            key_point, "发现时刻", direction="ur",
            text_font_size=16, arrow_color=self.TEMP_COLOR
        )
        self.wait(0.5)
        self.play(FadeOut(arrow_key), run_time=0.3)
        
        # 计算结果
        result_text = VGroup(
            Text("推断结果：", font="STKaiti", font_size=self.SOLUTION_FONT_SIZE, color=WHITE),
            Tex(r"t \approx 4.76 \text{ 小时}", font_size=self.SOLUTION_FONT_SIZE, color=self.ANSWER_COLOR),
        ).arrange(RIGHT, buff=0.3)
        result_text.next_to(axes, DOWN, buff=0.4)
        
        answer_text = Text(
            "作案时间约为 11:15 左右",
            font="STKaiti",
            font_size=self.SOLUTION_FONT_SIZE + 2,
            color=self.ANSWER_COLOR
        ).next_to(result_text, DOWN, buff=0.25)
        
        # 为答案添加辉光方框
        answer_box = create_glow_surrounding_rect(
            answer_text, color=self.ANSWER_COLOR, buff=0.1,
            stroke_width=2, n_glow_layers=4, base_opacity=0.3
        )
        
        self.play(FadeIn(result_text), run_time=0.8)
        self.speak(
            text="根据计算，从37度冷却到30度需要约4点76小时",
            targets=[result_text],
            subtitle="计算得出冷却时间约4.76小时",
            color_map={"4点76小时": self.ANSWER_COLOR},
            min_duration=2.0
        )
        
        self.play(FadeIn(answer_box), Write(answer_text), run_time=0.8)
        self.speak(
            text="因此作案时间大约是中午11点15分左右",
            targets=[answer_text],
            subtitle="作案时间约 11:15 左右",
            color_map={"11点15分": self.ANSWER_COLOR},
            min_duration=2.0
        )
        
        # 相机聚焦答案
        self.focus_guide_with_camera([answer_text], zoom_factor=1.5, hold_time=1.5, auto_remove=True)
        
        # === 保存所有对象到 shared_objects ===
        self.set_shared("final_eq", final_eq)
        self.set_shared("axes", axes)
        self.set_shared("curve", curve)
        self.set_shared("x_label", x_label)
        self.set_shared("y_label", y_label)
        self.set_shared("calc_table", calc_table)
        self.set_shared("result_text", result_text)
        self.set_shared("answer", answer_text)
        self.set_shared("answer_box", answer_box)
    
    # ==================== Phase 5: 实际意义 (30s) ====================
    
    def phase5_conclusion(self):
        """总结和结束语 - 保留坐标系和结果，添加总结标题"""
        self.wait(0.5)
        
        # === 只淡出顶部的公式，为标题腾出空间 ===
        self.safe_fadeout("final_eq", "final_eq_box")
        
        # === 添加总结标题（在最上方） ===
        summary = Text(
            "牛顿冷却定律在法医学中的重要应用",
            font="STKaiti",
            font_size=self.TITLE_FONT_SIZE,
            color=self.HIGHLIGHT_COLOR
        ).to_edge(UP, buff=0.3)
        
        summary_underline = self.create_glow_underline(
            summary,
            color=self.HIGHLIGHT_COLOR,
            offset_ratio=0.3,
            glow_width=0.06,
            glow_factor=2.0,
        )
        
        self.play(FadeIn(summary), FadeIn(summary_underline), run_time=0.8)
        
        self.speak(
            text="这就是牛顿冷却定律在法医学中的重要应用",
            targets=[summary],
            subtitle="牛顿冷却定律在法医学中的应用",
            color_map={"牛顿冷却定律": ORANGE, "法医学": self.ANSWER_COLOR},
            min_duration=2.0
        )
        
        self.speak(
            text="通过数学建模，我们可以科学地推断作案时间",
            targets=[summary],
            subtitle="数学建模科学推断作案时间",
            color_map={"数学建模": BLUE, "科学": self.ANSWER_COLOR},
            min_duration=2.0
        )
        
        self.speak(
            text="感谢观看，下期再见！",
            targets=[summary],
            subtitle="感谢观看 下期再见",
            color_map={"感谢观看": TEAL},
            min_duration=2.0
        )
        self.wait(1)
  


if __name__ == "__main__":
    os.system(f'cd "{script_dir}" && manimgl newton_cooling_demo.py NewtonCoolingDemo -w')
