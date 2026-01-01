"""
鸡兔同笼问题详解 - AutoScene 完整增强版
竖版视频格式 (9:16) - 1080x1920

【六块布局】Title / Divider / Problem / Viz / Derivation / Subtitle
使用 layout_content_blocks() 均匀分布三区

使用方法:
    cd E:\auto_manim\voice_test
    manimgl ji.py ChickenRabbitScene -w
"""

from manimlib import *
import os
import sys

# 添加项目路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "new_class"))

from new_class.auto_scene import AutoScene, create_glow_surrounding_rect
from new_class.auto_wrap import AutoWrap


class ChickenRabbitScene(AutoScene):
    """鸡兔同笼问题 - 六块布局 + layout_content_blocks 均匀分布"""
    
    CONFIG = {
        "camera_config": {
            "frame_width": 27/4,
            "frame_height": 12,
            "frame_rate": 30,
        }
    }
    
    FRAME_WIDTH = 27/4
    FRAME_HEIGHT = 12
    
    # 边距
    TITLE_BUFF = 0.4
    DIVIDER_BUFF = 0.2
    EDGE_BUFF = 0.2
    
    # 可视化区域目标宽度：88% 屏幕宽度
    VIZ_WIDTH_RATIO = 0.88
    TEXT_WIDTH_RATIO = 0.85
    SAFE_WIDTH = FRAME_WIDTH * 0.85
    
    # 字体（公式最小默认字号 42）
    TITLE_FONT_SIZE = 24
    PROBLEM_FONT_SIZE = 22
    METHOD_FONT_SIZE = 22
    STEP_FONT_SIZE = 42       # 公式最小默认字号
    ANSWER_FONT_SIZE = 44     # 答案字号
    
    # 颜色
    TEXT_COLOR = WHITE
    EMPHASIS_COLOR = RED
    ANSWER_COLOR = GREEN
    CHICKEN_COLOR = YELLOW_C
    RABBIT_COLOR = GREY_B
    LEG_COLOR = ORANGE
    
    def construct(self):
        self.setup_scene()
        self.create_all_content()    # 先创建所有内容
        self.do_layout()             # 使用 layout_content_blocks 均匀分布
        self.animate_all()           # 动画展示
    
    def setup_scene(self):
        self.enable_debug(True)
        self.set_animation_sounds_enabled(True)
        self.set_add_sounds_enabled(False)
        self.set_sound_gain(0.6)
        self.set_subtitle_style(font_size=20, edge_buff=0.25)
        
        grid = self.add_grid_background(step=0.5, stroke_opacity=0.15, stroke_width=0.5)
        self.add(grid)
        
        lights = self.add_traffic_lights(buff=0.2)
        self.add(lights)
        
        self.wrapper = AutoWrap(
            max_width_ratio=self.TEXT_WIDTH_RATIO,
            frame_width=self.FRAME_WIDTH,
            font_size=self.PROBLEM_FONT_SIZE,
            font="STKaiti",
            line_buff=0.1,
        )
        
        self.shared_objects = {}
        print("="*50)
        print("🎬 鸡兔同笼问题详解 - layout_content_blocks 均匀分布")
        print("="*50)
    
    def create_all_content(self):
        """创建所有内容块（不设置位置）"""
        # === Title + Divider ===
        self.title = Text(
            "【小学奥数·经典题】",
            font="STKaiti",
            font_size=self.TITLE_FONT_SIZE,
            color=self.TEXT_COLOR,
        ).to_edge(UP, buff=self.TITLE_BUFF)
        self.title.fix_in_frame()
        
        self.divider = Line(
            LEFT * (self.SAFE_WIDTH / 2),
            RIGHT * (self.SAFE_WIDTH / 2),
            stroke_width=1.5,
            color=GREY_A,
        ).next_to(self.title, DOWN, buff=self.DIVIDER_BUFF)
        self.divider.fix_in_frame()
        
        # === Problem 区 ===
        problem_text = "鸡兔同笼，共有10只动物，共32条腿，问鸡与兔各有多少只？"
        self.problem = self.wrapper.create_wrapped_text(
            problem_text, align="left",
            font="STKaiti", font_size=self.PROBLEM_FONT_SIZE, color=self.TEXT_COLOR,
        )
        
        # 添加解法标题
        method_title = Text(
            "假设法：假全鸡", font="STKaiti",
            font_size=self.METHOD_FONT_SIZE, color=self.EMPHASIS_COLOR,
        )
        self.problem_group = VGroup(self.problem, method_title).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        
        # === Viz 可视化区 ===
        self.viz_group = self._create_viz_content()
        # 注意：scale_viz_to_fit 已集成到 layout_content_blocks 中，无需手动调用
        
        # === Derivation 推导区 ===
        self.derivation_group = self._create_derivation_content()
        
        self.shared_objects["title"] = self.title
        self.shared_objects["divider"] = self.divider
    
    def _create_viz_content(self):
        """创建可视化内容（鸡兔图标+腿+数值）"""
        def create_chicken():
            body = Circle(radius=0.12, fill_color=self.CHICKEN_COLOR, fill_opacity=0.9, stroke_width=1)
            beak = Triangle(fill_color=ORANGE, fill_opacity=1, stroke_width=0).scale(0.03)
            beak.rotate(-PI/6).next_to(body, RIGHT, buff=-0.01)
            leg1 = Line(body.get_bottom(), body.get_bottom() + DOWN * 0.08 + LEFT * 0.02, stroke_width=2, color=self.LEG_COLOR)
            leg2 = Line(body.get_bottom(), body.get_bottom() + DOWN * 0.08 + RIGHT * 0.02, stroke_width=2, color=self.LEG_COLOR)
            return VGroup(body, beak, leg1, leg2)
        
        def create_rabbit():
            body = Ellipse(width=0.2, height=0.15, fill_color=self.RABBIT_COLOR, fill_opacity=0.9, stroke_width=1)
            ear1 = Ellipse(width=0.03, height=0.1, fill_color=PINK, fill_opacity=0.8, stroke_width=0)
            ear2 = ear1.copy()
            ear1.next_to(body, UP, buff=-0.02).shift(LEFT * 0.03).rotate(0.15)
            ear2.next_to(body, UP, buff=-0.02).shift(RIGHT * 0.03).rotate(-0.15)
            legs = VGroup()
            for dx in [-0.05, -0.02, 0.02, 0.05]:
                leg = Line(body.get_bottom() + RIGHT * dx, body.get_bottom() + DOWN * 0.08 + RIGHT * dx, stroke_width=2, color=self.LEG_COLOR)
                legs.add(leg)
            return VGroup(ear1, ear2, body, *legs)
        
        # 4只鸡 + 6只兔
        chickens = VGroup(*[create_chicken() for _ in range(4)])
        rabbits = VGroup(*[create_rabbit() for _ in range(6)])
        
        # 排列
        chickens.arrange(RIGHT, buff=0.15)
        rabbits.arrange(RIGHT, buff=0.15)
        
        animals = VGroup(chickens, rabbits).arrange(DOWN, buff=0.2)
        
        # 数值显示
        info_row = VGroup(
            VGroup(Tex(r"\text{鸡}", font_size=14, color=self.CHICKEN_COLOR), Tex(r"4", font_size=14, color=self.CHICKEN_COLOR)).arrange(RIGHT, buff=0.05),
            VGroup(Tex(r"\text{兔}", font_size=14, color=self.RABBIT_COLOR), Tex(r"6", font_size=14, color=self.RABBIT_COLOR)).arrange(RIGHT, buff=0.05),
            VGroup(Tex(r"\text{腿}", font_size=14, color=self.LEG_COLOR), Tex(r"32", font_size=14, color=self.LEG_COLOR)).arrange(RIGHT, buff=0.05),
        ).arrange(RIGHT, buff=0.4)
        
        target_hint = Tex(r"\text{目标：} 32 \text{ 腿}", font_size=12, color=GREY)
        
        viz = VGroup(animals, info_row, target_hint).arrange(DOWN, buff=0.15)
        return viz
    
    def _create_derivation_content(self):
        """创建推导内容"""
        steps = [
            r"10 \times 2 = 20",
            r"32 - 20 = 12",
            r"4 - 2 = 2",
            r"12 ÷ 2 = 6",
            r"10 - 6 = 4",
        ]
        derivation = VGroup(*[
            Tex(s, font_size=self.STEP_FONT_SIZE, color=self.TEXT_COLOR)
            for s in steps
        ]).arrange(DOWN, buff=0.12)
        
        # 答案
        answer = Tex(
            r"\text{答：鸡 } 4 \text{ 只，兔 } 6 \text{ 只}",
            font_size=self.ANSWER_FONT_SIZE, color=self.ANSWER_COLOR,
        )
        
        deriv_group = VGroup(derivation, answer).arrange(DOWN, buff=0.2)
        return deriv_group
    
    def do_layout(self):
        """使用 layout_content_blocks API 均匀分布三区"""
        # 使用 AutoScene 的 layout_content_blocks 方法
        layout_info = self.layout_content_blocks(
            problem=self.problem_group,
            viz=self.viz_group,
            derivation=self.derivation_group,
            divider=self.divider,
            align_left=False,  # 居中对齐
        )
        
        # 调整 problem 左对齐
        self.problem_group.to_edge(LEFT, buff=self.EDGE_BUFF)
        
        print(f"📐 布局信息: {layout_info}")
    
    def animate_all(self):
        """动画展示"""
        # Title + Divider
        self.play(FadeIn(self.title, shift=DOWN * 0.3), run_time=1)
        self.play(ShowCreation(self.divider), run_time=0.8)
        self.speak(text="大家好，今天我们来解一道经典的鸡兔同笼问题", subtitle="经典的鸡兔同笼问题")
        
        # Problem
        self.play(Write(self.problem_group[0]), run_time=1.5)
        self.speak(text="共有 10 只动物，32 条腿", subtitle="共10只动物，32条腿")
        self.speak(text="问鸡与兔各有多少只", subtitle="问鸡与兔各有多少只？")
        
        self.play(Write(self.problem_group[1]), run_time=1)
        self.speak(text="我们用假设法来解题", subtitle="假设法：假全鸡")
        
        # Viz + 辉光箭头测试
        self.play(FadeIn(self.viz_group), run_time=1)
        
        # 【测试】添加辉光箭头标注
        # 标注鸡（自动选择方向）
        arrow_chicken = self.add_curved_annotation(
            self.viz_group[0][0],  # 第一只鸡
            "鸡(2腿)",
            direction="auto",
            text_font_size=16,
            arrow_color=self.CHICKEN_COLOR,
            use_glow=True,
        )
        
        # 标注兔
        arrow_rabbit = self.add_curved_annotation(
            self.viz_group[0][1],  # 第一只兔
            "兔(4腿)",
            direction="auto",
            text_font_size=16,
            arrow_color=self.RABBIT_COLOR,
            use_glow=True,
        )
        
        self.speak(text="最终结果是 4 只鸡和 6 只兔，正好 32 条腿", subtitle="4只鸡+6只兔=32条腿")
        
        # 清除箭头
        self.play(FadeOut(arrow_chicken), FadeOut(arrow_rabbit), run_time=0.5)
        
        # Derivation
        derivation = self.derivation_group[0]
        answer_tex = self.derivation_group[1]
        
        step_tts = [
            ("10 乘 2 等于 20", "10×2=20"),
            ("32 减 20 等于 12", "32-20=12"),
            ("每只兔多 2 条腿", "4-2=2"),
            ("12 除以 2 等于 6 只兔", "12÷2=6"),
            ("10 减 6 等于 4 只鸡", "10-6=4"),
        ]
        
        for i, (step, (tts, sub)) in enumerate(zip(derivation, step_tts)):
            if i == 0:
                self.play(Write(step), run_time=1)
            else:
                self.play(TransformMatchingShapes(derivation[i-1].copy(), step), run_time=0.8)
                self.add(step)
            self.speak(text=tts, subtitle=sub)
        
        # Answer
        answer_bg = create_glow_surrounding_rect(
            answer_tex, color=self.ANSWER_COLOR, buff=0.08,
            stroke_width=2, fill_opacity=0.2, n_glow_layers=2,
        )
        self.play(Write(answer_tex), run_time=0.8)
        self.play(FadeIn(answer_bg), run_time=0.5)
        self.speak(text="最终得出，鸡有 4 只，兔有 6 只", subtitle="答：鸡4只，兔6只")
        
        self.camera_focus(answer_tex, zoom_factor=1.3, hold_time=1.5)
        
        # Ending - 添加黑色背景避免遮挡
        summary = Tex(r"\text{假设法} \Rightarrow \text{假全鸡/假全兔}", font_size=18, color=GREY_B)
        # 添加黑色背景
        summary_bg = BackgroundRectangle(summary, fill_opacity=0.9, buff=0.15)
        summary_with_bg = VGroup(summary_bg, summary).to_edge(DOWN, buff=1.5)
        summary_with_bg.fix_in_frame()
        
        self.speak(text="本题使用假设法，难度一颗星", subtitle="假设法 ★☆☆☆☆")
        self.play(FadeIn(summary_with_bg), run_time=0.8)
        self.speak(text="感谢观看，下期再见", subtitle="感谢观看！")
        self.wait(2)
        
        print("="*50)
        print(f"✅ 完成 @ {self._current_time:.2f}s")
        print("="*50)


if __name__ == "__main__":
    os.system(f'manimgl "{script_dir}\\ji.py" ChickenRabbitScene')
