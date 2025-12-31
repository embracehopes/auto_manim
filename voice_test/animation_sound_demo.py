"""
动画音效演示 Demo
展示所有动画类型及其对应的音效，配有语音讲解

使用方法:
    cd E:\auto_manim\voice_test
    manimgl animation_sound_demo.py AnimationSoundDemo -w
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


class AnimationSoundDemo(AutoScene):
    """
    动画音效演示场景
    
    展示所有动画类型及其音效:
    - 创建类: ShowCreation, Write, DrawBorderThenFill
    - 淡入淡出类: FadeIn, FadeOut
    - 生长类: GrowFromCenter, GrowArrow
    - 指示类: Flash, Indicate, CircleIndicate
    - 移动类: MoveAlongPath
    - 旋转类: Rotate
    - 变换类: Transform, ReplacementTransform
    - 数字类: ChangingDecimal
    """
    
    def construct(self):
        # 启用调试和音效
        self.enable_debug(True)
        self.set_animation_sounds_enabled(True)
        self.set_add_sounds_enabled(True)
        
        # 定义时间轴（语音讲解）
        timeline = [
            {"start": 0.0, "end": 3.0, "text": "欢迎观看 ManimGL 动画音效演示"},
            {"start": 3.0, "end": 5.0, "text": "每种动画都会播放对应的音效"},
        ]
        
        # 运行开场白
        self.run_timeline(timeline)
        self.clear_subtitle()
        self.wait(0.5)
        
        # === 创建类动画 ===
        self._demo_creation_animations()
        
        # === 淡入淡出类动画 ===
        self._demo_fade_animations()
        
        # === 生长类动画 ===
        self._demo_grow_animations()
        
        # === 指示类动画 ===
        self._demo_indicate_animations()
        
        # === 移动类动画 ===
        self._demo_movement_animations()
        
        # === 旋转类动画 ===
        self._demo_rotation_animations()
        
        # === 变换类动画 ===
        self._demo_transform_animations()
        
        # === 数字类动画 ===
        self._demo_number_animations()
        
        # === add() 音效演示 ===
        self._demo_add_sound()
        
        # 结束语
        self._show_ending()
    
    def _show_section_title(self, title: str, color=YELLOW):
        """显示章节标题"""
        title_text = Text(
            title,
            font="STKaiti",
            font_size=48,
            color=color
        )
        
        self.play(Write(title_text), run_time=0.8)
        self.wait(0.5)
        self.play(FadeOut(title_text), run_time=0.3)
    
    def _demo_creation_animations(self):
        """演示创建类动画"""
        self._show_section_title("创建类动画", BLUE)
        
        # ShowCreation
        self.subtitle(self._current_time, self._current_time + 3, 
                     "ShowCreation - 绘制路径动画",
                     {"ShowCreation": YELLOW})
        circle = Circle(radius=1.5, color=BLUE)
        self.play(ShowCreation(circle), run_time=2)
        self.wait(0.5)
        self.play(FadeOut(circle), run_time=0.3)
        
        # Write
        self.subtitle(self._current_time, self._current_time + 3,
                     "Write - 书写文字动画",
                     {"Write": YELLOW})
        text = Text("Hello World!", font_size=64, color=GREEN)
        self.play(Write(text), run_time=2)
        self.wait(0.5)
        self.play(FadeOut(text), run_time=0.3)
        
        # DrawBorderThenFill
        self.subtitle(self._current_time, self._current_time + 3,
                     "DrawBorderThenFill - 先描边后填充",
                     {"DrawBorderThenFill": YELLOW})
        square = Square(side_length=2, fill_opacity=0.8, color=RED)
        self.play(DrawBorderThenFill(square), run_time=2)
        self.wait(0.5)
        self.play(FadeOut(square), run_time=0.3)
        
        self.clear_subtitle()
        self.wait(0.3)
    
    def _demo_fade_animations(self):
        """演示淡入淡出类动画"""
        self._show_section_title("淡入淡出类动画", TEAL)
        
        # FadeIn
        self.subtitle(self._current_time, self._current_time + 2.5,
                     "FadeIn - 淡入显现",
                     {"FadeIn": YELLOW})
        star = RegularPolygon(n=5, color=YELLOW, fill_opacity=0.8).scale(1.5)
        self.play(FadeIn(star), run_time=1.5)
        self.wait(0.5)
        
        # FadeOut
        self.subtitle(self._current_time, self._current_time + 2.5,
                     "FadeOut - 淡出消失",
                     {"FadeOut": YELLOW})
        self.play(FadeOut(star), run_time=1.5)
        self.wait(0.5)
        
        # FadeIn 方向变体
        self.subtitle(self._current_time, self._current_time + 3,
                     "FadeIn 支持方向参数",
                     {"方向": YELLOW})
        
        arrows = VGroup(
            Arrow(LEFT * 3, ORIGIN, color=RED),
            Arrow(RIGHT * 3, ORIGIN, color=GREEN),
            Arrow(UP * 2, ORIGIN, color=BLUE),
            Arrow(DOWN * 2, ORIGIN, color=PURPLE),
        )
        self.play(
            FadeIn(arrows[0], shift=RIGHT),
            FadeIn(arrows[1], shift=LEFT),
            FadeIn(arrows[2], shift=DOWN),
            FadeIn(arrows[3], shift=UP),
            run_time=1.5
        )
        self.wait(0.5)
        self.play(FadeOut(arrows), run_time=0.3)
        
        self.clear_subtitle()
        self.wait(0.3)
    
    def _demo_grow_animations(self):
        """演示生长类动画"""
        self._show_section_title("生长类动画", GREEN)
        
        # GrowFromCenter
        self.subtitle(self._current_time, self._current_time + 2.5,
                     "GrowFromCenter - 从中心放大",
                     {"GrowFromCenter": YELLOW})
        circle = Circle(radius=1.5, color=ORANGE, fill_opacity=0.6)
        self.play(GrowFromCenter(circle), run_time=1.5)
        self.wait(0.5)
        self.play(FadeOut(circle), run_time=0.3)
        
        # GrowFromEdge
        self.subtitle(self._current_time, self._current_time + 2.5,
                     "GrowFromEdge - 从边缘生长",
                     {"GrowFromEdge": YELLOW})
        rect = Rectangle(width=3, height=2, color=PURPLE, fill_opacity=0.6)
        self.play(GrowFromEdge(rect, LEFT), run_time=1.5)
        self.wait(0.5)
        self.play(FadeOut(rect), run_time=0.3)
        
        # GrowArrow
        self.subtitle(self._current_time, self._current_time + 2.5,
                     "GrowArrow - 箭头生长",
                     {"GrowArrow": YELLOW})
        arrow = Arrow(LEFT * 2, RIGHT * 2, color=RED, stroke_width=6)
        self.play(GrowArrow(arrow), run_time=1.5)
        self.wait(0.5)
        self.play(FadeOut(arrow), run_time=0.3)
        
        self.clear_subtitle()
        self.wait(0.3)
    
    def _demo_indicate_animations(self):
        """演示指示类动画"""
        self._show_section_title("指示类动画", PINK)
        
        # 创建示例对象
        text = Text("重点内容", font="STKaiti", font_size=56, color=WHITE)
        self.add(text)
        
        # Flash
        self.subtitle(self._current_time, self._current_time + 2.5,
                     "Flash - 闪光效果",
                     {"Flash": YELLOW})
        self.play(Flash(text, color=YELLOW, flash_radius=0.5), run_time=1)
        self.wait(1)
        
        # Indicate
        self.subtitle(self._current_time, self._current_time + 2.5,
                     "Indicate - 强调突出",
                     {"Indicate": YELLOW})
        self.play(Indicate(text, scale_factor=1.3), run_time=1.5)
        self.wait(0.5)
        
        # CircleIndicate
        self.subtitle(self._current_time, self._current_time + 2.5,
                     "CircleIndicate - 圆圈强调",
                     {"CircleIndicate": YELLOW})
        self.play(CircleIndicate(text), run_time=1.5)
        self.wait(0.5)
        
        # ShowPassingFlash
        self.subtitle(self._current_time, self._current_time + 2.5,
                     "ShowPassingFlash - 流光效果",
                     {"ShowPassingFlash": YELLOW})
        line = Line(LEFT * 3, RIGHT * 3, color=BLUE, stroke_width=4).shift(DOWN)
        self.add(line)
        self.play(ShowPassingFlash(line.copy().set_color(YELLOW), time_width=0.5), run_time=1.5)
        self.wait(0.5)
        
        self.play(FadeOut(text), FadeOut(line), run_time=0.3)
        self.clear_subtitle()
        self.wait(0.3)
    
    def _demo_movement_animations(self):
        """演示移动类动画"""
        self._show_section_title("移动类动画", MAROON)
        
        # MoveAlongPath
        self.subtitle(self._current_time, self._current_time + 4,
                     "MoveAlongPath - 沿路径移动",
                     {"MoveAlongPath": YELLOW})
        
        # 创建路径和移动对象
        path = Arc(radius=2, start_angle=0, angle=TAU, color=GREY)
        dot = Dot(color=RED, radius=0.15)
        dot.move_to(path.get_start())
        
        self.add(path, dot)
        self.play(MoveAlongPath(dot, path), run_time=3)
        self.wait(0.5)
        self.play(FadeOut(path), FadeOut(dot), run_time=0.3)
        
        self.clear_subtitle()
        self.wait(0.3)
    
    def _demo_rotation_animations(self):
        """演示旋转类动画"""
        self._show_section_title("旋转类动画", GOLD)
        
        # Rotate
        self.subtitle(self._current_time, self._current_time + 3,
                     "Rotate - 旋转动画",
                     {"Rotate": YELLOW})
        
        square = Square(side_length=2, color=BLUE, fill_opacity=0.5)
        self.add(square)
        self.play(Rotate(square, angle=TAU), run_time=2)
        self.wait(0.5)
        self.play(FadeOut(square), run_time=0.3)
        
        self.clear_subtitle()
        self.wait(0.3)
    
    def _demo_transform_animations(self):
        """演示变换类动画"""
        self._show_section_title("变换类动画", PURPLE)
        
        # Transform
        self.subtitle(self._current_time, self._current_time + 3,
                     "Transform - 形状变换",
                     {"Transform": YELLOW})
        
        circle = Circle(radius=1.5, color=BLUE, fill_opacity=0.5)
        square = Square(side_length=2.5, color=RED, fill_opacity=0.5)
        
        self.add(circle)
        self.play(Transform(circle, square), run_time=2)
        self.wait(0.5)
        self.play(FadeOut(circle), run_time=0.3)
        
        # ReplacementTransform
        self.subtitle(self._current_time, self._current_time + 3,
                     "ReplacementTransform - 替换变换",
                     {"ReplacementTransform": YELLOW})
        
        text1 = Text("Hello", font_size=64, color=GREEN)
        text2 = Text("World", font_size=64, color=YELLOW)
        
        self.add(text1)
        self.play(ReplacementTransform(text1, text2), run_time=1.5)
        self.wait(0.5)
        self.play(FadeOut(text2), run_time=0.3)
        
        self.clear_subtitle()
        self.wait(0.3)
    
    def _demo_number_animations(self):
        """演示数字类动画"""
        self._show_section_title("数字类动画", ORANGE)
        
        # ChangingDecimal
        self.subtitle(self._current_time, self._current_time + 4,
                     "ChangingDecimal - 数字变化动画",
                     {"ChangingDecimal": YELLOW})
        
        # 创建数字显示
        number = DecimalNumber(
            0,
            num_decimal_places=1,
            font_size=72,
            color=WHITE
        )
        
        self.add(number)
        
        # 数字从 0 变化到 100
        self.play(
            ChangeDecimalToValue(number, 100),
            run_time=3
        )
        self.wait(0.5)
        self.play(FadeOut(number), run_time=0.3)
        
        self.clear_subtitle()
        self.wait(0.3)
    
    def _demo_add_sound(self):
        """演示 add() 音效"""
        self._show_section_title("self.add() 音效", TEAL)
        
        self.subtitle(self._current_time, self._current_time + 4,
                     "self.add() 直接添加对象时也会播放音效",
                     {"add": YELLOW})
        
        # 依次添加多个对象
        objects = [
            Circle(radius=0.5, color=RED).shift(LEFT * 3),
            Square(side_length=1, color=GREEN).shift(LEFT * 1),
            Triangle(color=BLUE).shift(RIGHT * 1),
            RegularPolygon(n=5, color=YELLOW).scale(0.5).shift(RIGHT * 3),
        ]
        
        for i, obj in enumerate(objects):
            self.add(obj)  # 这里会触发音效
            self.wait(0.5)
        
        self.wait(0.5)
        self.play(*[FadeOut(obj) for obj in objects], run_time=0.5)
        
        self.clear_subtitle()
        self.wait(0.3)
    
    def _show_ending(self):
        """显示结束语"""
        ending_timeline = [
            {"start": self._current_time, "end": self._current_time + 3,
             "text": "演示完毕！所有动画都已展示音效"},
            {"start": self._current_time + 3, "end": self._current_time + 5,
             "text": "感谢观看！"},
        ]
        
        self.run_timeline(ending_timeline)
        self.clear_subtitle()
        
        # 结束动画
        end_text = Text(
            "🎬 完",
            font="STKaiti",
            font_size=72,
            color=GOLD
        )
        self.play(Write(end_text), run_time=1)
        self.wait(1)
        self.play(FadeOut(end_text), run_time=0.5)


# ==================== 简化版演示 ====================

class SimpleAnimationDemo(AutoScene):
    """
    简化版动画音效演示
    不包含语音讲解，仅展示核心动画
    """
    
    def construct(self):
        self.enable_debug(True)
        self.set_animation_sounds_enabled(True)
        self.set_add_sounds_enabled(True)
        
        # 标题
        title = Text("动画音效演示", font="STKaiti", font_size=56, color=YELLOW)
        self.play(Write(title), run_time=1)
        self.wait(0.5)
        self.play(FadeOut(title), run_time=0.3)
        
        # 快速演示各类动画
        
        # 1. ShowCreation
        circle = Circle(radius=1.5, color=BLUE)
        self.play(ShowCreation(circle), run_time=1)
        self.wait(0.3)
        
        # 2. Transform
        square = Square(side_length=2.5, color=RED)
        self.play(Transform(circle, square), run_time=1)
        self.wait(0.3)
        
        # 3. Indicate
        self.play(Indicate(circle), run_time=0.8)
        self.wait(0.3)
        
        # 4. Rotate
        self.play(Rotate(circle, angle=PI), run_time=1)
        self.wait(0.3)
        
        # 5. FadeOut
        self.play(FadeOut(circle), run_time=0.5)
        self.wait(0.3)
        
        # 6. GrowFromCenter
        text = Text("Hello!", font_size=64, color=GREEN)
        self.play(GrowFromCenter(text), run_time=1)
        self.wait(0.3)
        
        # 7. Flash
        self.play(Flash(text, flash_radius=0.3), run_time=0.5)
        self.wait(0.3)
        
        # 8. FadeOut
        self.play(FadeOut(text), run_time=0.5)
        
        # 结束
        end = Text("完", font="STKaiti", font_size=72, color=GOLD)
        self.play(Write(end), run_time=0.8)
        self.wait(1)


if __name__ == "__main__":
    # 默认运行完整演示
    os.system(f'cd "{script_dir}" && manimgl animation_sound_demo.py AnimationSoundDemo -w')
