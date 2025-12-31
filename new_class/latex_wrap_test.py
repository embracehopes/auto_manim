"""
LaTeX 侧自动换行测试 - 使用 \parbox / minipage

探索 Manim 坐标单位与 LaTeX 长度单位的换算关系

原理：
1. 在 LaTeX 中使用 \parbox{宽度}{内容} 来实现自动换行
2. 需要找到 Manim 单位 -> TeX pt 的换算比例
3. 通过实验测量确定换算系数

使用方法：
    cd E:\auto_manim\new_class
    manimgl latex_wrap_test.py LatexWrapTest
"""

from manimlib import *
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))


class LatexWrapTest(Scene):
    """
    测试 LaTeX \parbox 自动换行
    """
    
    CONFIG = {
        "camera_config": {
            "frame_width": 27/4,  # 6.75 - 竖版
            "frame_height": 12,
        }
    }
    
    def construct(self):
        frame_width = self.camera.frame.get_width()
        safe_width = frame_width * 0.95
        margin = 0.05 * frame_width
        
        print(f"\n屏幕尺寸: {frame_width:.3f} x 12")
        print(f"目标宽度 (95%): {safe_width:.3f} Manim 单位")
        
        # 标题
        title = Text(
            "LaTeX \\parbox 自动换行测试",
            font="STKaiti",
            font_size=22,
            color=YELLOW
        ).to_edge(UP, buff=0.3)
        self.play(Write(title))
        
        # 显示边界线
        left_line = Line(
            UP * 5 + LEFT * (frame_width/2 - margin),
            DOWN * 5 + LEFT * (frame_width/2 - margin),
            color=RED, stroke_width=1, stroke_opacity=0.5
        )
        right_line = Line(
            UP * 5 + RIGHT * (frame_width/2 - margin),
            DOWN * 5 + RIGHT * (frame_width/2 - margin),
            color=RED, stroke_width=1, stroke_opacity=0.5
        )
        self.play(ShowCreation(left_line), ShowCreation(right_line), run_time=0.3)
        
        # ==================== 步骤1：测量换算系数 ====================
        
        print("\n=== 步骤1: 测量 Manim 单位 -> TeX pt 换算系数 ===")
        
        # 创建一个已知 TeX 宽度的参考对象
        # 使用 \rule{100pt}{1pt} 创建一个精确 100pt 宽的线
        ref_tex = Tex(r"\rule{100pt}{1pt}", font_size=24)
        ref_manim_width = ref_tex.get_width()
        
        # 换算：100 TeX pt = ref_manim_width Manim 单位
        pt_per_manim = 100 / ref_manim_width
        
        print(f"参考线 (100pt) 的 Manim 宽度: {ref_manim_width:.4f}")
        print(f"换算系数: 1 Manim 单位 = {pt_per_manim:.2f} TeX pt")
        
        # 显示参考线
        ref_label = Text(
            f"100pt 参考线 → {ref_manim_width:.2f} Manim 单位",
            font="STKaiti",
            font_size=14,
            color=BLUE
        ).move_to(UP * 3.5)
        ref_tex.next_to(ref_label, DOWN, buff=0.2)
        
        self.play(Write(ref_label), FadeIn(ref_tex), run_time=0.5)
        self.wait(0.5)
        
        # ==================== 步骤2：计算目标宽度的 TeX pt 值 ====================
        
        target_pt = safe_width * pt_per_manim
        print(f"\n目标宽度: {safe_width:.3f} Manim 单位 = {target_pt:.1f} TeX pt")
        
        # ==================== 步骤3：使用 \parbox 实现自动换行 ====================
        
        print("\n=== 步骤3: 使用 \\parbox 自动换行 ===")
        
        # 测试文本（中文需要用 \text{} 包裹）
        # 使用 \parbox{宽度pt}{内容}
        parbox_width = int(target_pt)  # 取整
        
        # 简单英文测试
        test_text_en = "This is a long English text that should automatically wrap when it exceeds the specified width using LaTeX parbox."
        
        parbox_tex_en = Tex(
            rf"\parbox{{{parbox_width}pt}}{{{test_text_en}}}",
            font_size=20
        )
        parbox_tex_en.move_to(UP * 1.5)
        parbox_tex_en.to_edge(LEFT, buff=margin)
        
        label_en = Text("英文 \\parbox 测试:", font="STKaiti", font_size=14, color=GREEN)
        label_en.next_to(parbox_tex_en, UP, buff=0.15, aligned_edge=LEFT)
        
        self.play(Write(label_en), run_time=0.3)
        self.play(FadeIn(parbox_tex_en), run_time=0.8)
        
        actual_width_en = parbox_tex_en.get_width()
        print(f"英文 parbox 实际宽度: {actual_width_en:.3f} Manim 单位 "
              f"({actual_width_en/safe_width*100:.1f}%)")
        
        self.wait(1)
        
        # ==================== 步骤4：中文测试（需要 CJK 支持）====================
        
        print("\n=== 步骤4: 中文 \\parbox 测试 ===")
        
        # 注意：LaTeX 中的中文需要特殊处理
        # ManimGL 的 Tex 默认可能不支持直接中文换行
        # 可以尝试使用 \text{} + CJK 包
        
        try:
            # 尝试使用 minipage + \text
            test_text_cn = r"\text{这是一段很长的中文文本，用于测试 LaTeX parbox 的自动换行功能。}"
            
            parbox_tex_cn = Tex(
                rf"\parbox{{{parbox_width}pt}}{{{test_text_cn}}}",
                font_size=20
            )
            parbox_tex_cn.move_to(DOWN * 1)
            parbox_tex_cn.to_edge(LEFT, buff=margin)
            
            label_cn = Text("中文 \\parbox 测试:", font="STKaiti", font_size=14, color=GREEN)
            label_cn.next_to(parbox_tex_cn, UP, buff=0.15, aligned_edge=LEFT)
            
            self.play(Write(label_cn), run_time=0.3)
            self.play(FadeIn(parbox_tex_cn), run_time=0.8)
            
            actual_width_cn = parbox_tex_cn.get_width()
            print(f"中文 parbox 实际宽度: {actual_width_cn:.3f} Manim 单位 "
                  f"({actual_width_cn/safe_width*100:.1f}%)")
            
        except Exception as e:
            print(f"中文 parbox 失败: {e}")
            
            # 备选方案：显示说明
            note = Text(
                "⚠️ 中文 \\parbox 需要 CJK 支持",
                font="STKaiti",
                font_size=16,
                color=ORANGE
            ).move_to(DOWN * 1)
            self.play(Write(note), run_time=0.5)
        
        self.wait(1)
        
        # ==================== 总结 ====================
        
        summary = VGroup(
            Text("📌 LaTeX parbox 换行总结", font="STKaiti", font_size=18, color=YELLOW),
            Text(f"换算: 1 Manim ≈ {pt_per_manim:.1f} pt", font="STKaiti", font_size=14),
            Text(f"目标宽度: {safe_width:.2f} Manim = {target_pt:.0f} pt", font="STKaiti", font_size=14),
            Text("✓ 英文自动换行效果较好", font="STKaiti", font_size=14, color=GREEN),
            Text("⚠️ 中文需要额外 CJK 配置", font="STKaiti", font_size=14, color=ORANGE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        summary.move_to(DOWN * 4)
        
        self.play(FadeIn(summary), run_time=0.8)
        self.wait(2)


class ParboxMathTest(Scene):
    """
    测试数学公式在 parbox 中的表现
    """
    
    CONFIG = {
        "camera_config": {
            "frame_width": 27/4,
            "frame_height": 12,
        }
    }
    
    def construct(self):
        frame_width = self.camera.frame.get_width()
        safe_width = frame_width * 0.95
        margin = 0.05 * frame_width
        
        # 计算换算系数
        ref_tex = Tex(r"\rule{100pt}{1pt}", font_size=24)
        pt_per_manim = 100 / ref_tex.get_width()
        target_pt = int(safe_width * pt_per_manim)
        
        print(f"\n目标宽度: {target_pt} pt")
        
        # 标题
        title = Text(
            "数学公式 + parbox 测试",
            font="STKaiti",
            font_size=22,
            color=YELLOW
        ).to_edge(UP, buff=0.3)
        self.play(Write(title))
        
        # 边界线
        left_line = Line(
            UP * 5 + LEFT * (frame_width/2 - margin),
            DOWN * 5 + LEFT * (frame_width/2 - margin),
            color=RED, stroke_width=1, stroke_opacity=0.5
        )
        right_line = Line(
            UP * 5 + RIGHT * (frame_width/2 - margin),
            DOWN * 5 + RIGHT * (frame_width/2 - margin),
            color=RED, stroke_width=1, stroke_opacity=0.5
        )
        self.play(ShowCreation(left_line), ShowCreation(right_line), run_time=0.3)
        
        # ==================== 测试1：简单文本公式混合 ====================
        
        print("\n=== 测试: 文本 + 公式混合 ===")
        
        # 使用 minipage 环境，可以包含多行和公式
        # 注意：$ $ 内的公式会自动调整
        mixed_content = (
            r"Given the quadratic equation $ax^2 + bx + c = 0$, "
            r"the solutions are $x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$. "
            r"This is called the quadratic formula."
        )
        
        parbox_mixed = Tex(
            rf"\parbox{{{target_pt}pt}}{{{mixed_content}}}",
            font_size=18
        )
        parbox_mixed.move_to(UP * 2)
        parbox_mixed.to_edge(LEFT, buff=margin)
        
        label1 = Text("文本+公式混合:", font="STKaiti", font_size=14, color=GREEN)
        label1.next_to(parbox_mixed, UP, buff=0.15, aligned_edge=LEFT)
        
        self.play(Write(label1), run_time=0.3)
        self.play(FadeIn(parbox_mixed), run_time=1)
        
        w = parbox_mixed.get_width()
        print(f"混合 parbox 宽度: {w:.3f} ({w/safe_width*100:.1f}%)")
        
        self.wait(1)
        
        # ==================== 测试2：多行公式推导 ====================
        
        print("\n=== 测试: 多行公式 (align 环境) ===")
        
        # 使用 aligned 环境实现多行对齐公式
        # 这是更推荐的公式换行方式
        align_content = (
            r"\begin{aligned}"
            r"e &= \sqrt{1 + \frac{b^2}{a^2}} \geq \sqrt{5} \\"
            r"1 + \frac{b^2}{a^2} &\geq 5 \\"
            r"b^2 &\geq 4a^2 \\"
            r"|b| &\geq 2|a|"
            r"\end{aligned}"
        )
        
        align_tex = Tex(align_content, font_size=20)
        align_tex.move_to(DOWN * 1.5)
        align_tex.to_edge(LEFT, buff=margin)
        
        label2 = Text("推荐方式: aligned 环境", font="STKaiti", font_size=14, color=GREEN)
        label2.next_to(align_tex, UP, buff=0.15, aligned_edge=LEFT)
        
        self.play(Write(label2), run_time=0.3)
        self.play(Write(align_tex), run_time=1.5)
        
        w2 = align_tex.get_width()
        print(f"aligned 环境宽度: {w2:.3f} ({w2/safe_width*100:.1f}%)")
        
        self.wait(1)
        
        # ==================== 总结 ====================
        
        summary = VGroup(
            Text("📌 数学公式换行最佳实践", font="STKaiti", font_size=18, color=YELLOW),
            Text("1. 简单公式: 使用 $...$ 内嵌", font="STKaiti", font_size=14),
            Text("2. 多行推导: 使用 aligned 环境", font="STKaiti", font_size=14, color=GREEN),
            Text("3. 长公式: 手动在 \\Rightarrow 处断行", font="STKaiti", font_size=14),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        summary.move_to(DOWN * 4.5)
        
        self.play(FadeIn(summary), run_time=0.8)
        self.wait(2)


if __name__ == "__main__":
    os.system(f'cd "{script_dir}" && manimgl latex_wrap_test.py LatexWrapTest')
