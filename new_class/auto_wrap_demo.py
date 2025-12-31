"""
自动换行演示场景 - 测试 AutoWrap 工具

演示内容：
1. 中文文本自动换行
2. 英文文本自动换行
3. 中英混合文本换行
4. 数学公式换行
5. 宽度比例调试可视化

使用方法：
    cd E:\auto_manim\new_class
    manimgl auto_wrap_demo.py AutoWrapDemo
"""

from manimlib import *
import os
import sys

# 添加项目路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, script_dir)

from auto_wrap import AutoWrap, wrap_text_to_width


class AutoWrapDemo(Scene):
    """
    自动换行演示场景
    """
    
    CONFIG = {
        "camera_config": {
            "frame_width": 27/4,   # 6.75 - 竖版
            "frame_height": 12,
            "frame_rate": 30,
        }
    }
    
    def construct(self):
        # 获取屏幕尺寸
        frame_width = self.camera.frame.get_width()
        frame_height = self.camera.frame.get_height()
        
        print(f"\n屏幕尺寸: {frame_width:.3f} x {frame_height:.3f}")
        print(f"95% 宽度: {frame_width * 0.95:.3f}")
        
        # 显示标题
        title = Text(
            "AutoWrap 自动换行演示",
            font="STKaiti",
            font_size=28,
            color=YELLOW
        ).to_edge(UP, buff=0.3)
        self.play(Write(title))
        
        # 显示边界参考线
        margin = 0.05 * frame_width
        safe_width = frame_width * 0.95
        
        # 左右边界线
        left_line = Line(
            UP * 5 + LEFT * (frame_width/2 - margin),
            DOWN * 5 + LEFT * (frame_width/2 - margin),
            color=RED,
            stroke_width=1,
            stroke_opacity=0.5
        )
        right_line = Line(
            UP * 5 + RIGHT * (frame_width/2 - margin),
            DOWN * 5 + RIGHT * (frame_width/2 - margin),
            color=RED,
            stroke_width=1,
            stroke_opacity=0.5
        )
        
        # 95% 标签
        width_label = Text(
            f"← 95% = {safe_width:.2f} →",
            font="STKaiti",
            font_size=14,
            color=RED
        ).to_edge(UP, buff=0.8)
        
        self.play(
            ShowCreation(left_line),
            ShowCreation(right_line),
            Write(width_label),
            run_time=0.5
        )
        
        # ==================== 测试用例 ====================
        
        test_cases = [
            {
                "title": "测试1: 中文长文本",
                "text": "这是一个很长的中文文本示例，用于测试超过屏幕宽度95%之后自动换行的逻辑。我们来看看效果如何。",
                "font_size": 22,
            },
            {
                "title": "测试2: 英文文本",
                "text": "This is a long English text example to test automatic line wrapping when exceeding 95% screen width.",
                "font_size": 22,
            },
            {
                "title": "测试3: 中英混合",
                "text": "设集合P={-1,0,1,2,3,4}，从P取整数a，从Q={-2,-1,0,1,2,3}取整数b，求概率。",
                "font_size": 22,
            },
        ]
        
        y_position = 2.5
        
        for case in test_cases:
            # 清除上一个测试
            if y_position < 2.5:
                self.wait(1.5)
                self.play(*[FadeOut(m) for m in self.mobjects[4:]], run_time=0.5)
            
            # 显示测试标题
            case_title = Text(
                case["title"],
                font="STKaiti",
                font_size=18,
                color=BLUE
            ).move_to(UP * y_position)
            
            self.play(Write(case_title), run_time=0.3)
            
            # 创建自动换行工具
            wrapper = AutoWrap(
                max_width_ratio=0.95,
                frame_width=frame_width,
                font_size=case["font_size"],
                font="STKaiti",
                debug=True,  # 开启调试输出
            )
            
            # 执行换行
            print(f"\n{'='*50}")
            print(f"处理: {case['title']}")
            print(f"原文: {case['text']}")
            
            wrapped_group = wrapper.create_wrapped_text(
                case["text"],
                align="left",
                font_size=case["font_size"],
            )
            
            # 定位
            wrapped_group.next_to(case_title, DOWN, buff=0.3)
            wrapped_group.to_edge(LEFT, buff=margin)
            
            # 显示每行的宽度信息 - 先保存原始行列表避免遍历时修改
            original_lines = list(wrapped_group.submobjects)
            width_notes = []
            
            for i, line_mob in enumerate(original_lines):
                line_width = line_mob.get_width()
                fill_ratio = line_width / safe_width * 100
                print(f"  行{i+1}: 宽度={line_width:.3f}, 填充={fill_ratio:.1f}%")
                
                # 在行末添加宽度标注
                width_note = Text(
                    f"{fill_ratio:.0f}%",
                    font="Arial",
                    font_size=12,
                    color=GREEN if fill_ratio > 80 else YELLOW
                ).next_to(line_mob, RIGHT, buff=0.1)
                width_notes.append(width_note)
            
            # 添加所有宽度标注
            for note in width_notes:
                wrapped_group.add(note)
            
            # 动画显示
            self.play(FadeIn(wrapped_group), run_time=0.8)
            
            # 显示总宽度对比
            total_width = wrapped_group.get_width()
            info_text = Text(
                f"总宽度: {total_width:.2f} / {safe_width:.2f} ({total_width/safe_width*100:.1f}%)",
                font="STKaiti",
                font_size=14,
                color=WHITE
            ).next_to(wrapped_group, DOWN, buff=0.3)
            
            self.play(Write(info_text), run_time=0.3)
            
            y_position -= 3
        
        # 结束
        self.wait(2)
        
        # 总结
        summary = Text(
            "自动换行测试完成！",
            font="STKaiti",
            font_size=24,
            color=YELLOW
        ).move_to(ORIGIN)
        
        self.play(
            *[FadeOut(m) for m in self.mobjects],
            run_time=0.5
        )
        self.play(Write(summary))
        self.wait(1)


class SimpleWrapTest(Scene):
    """
    简化测试 - 单个文本换行
    """
    
    CONFIG = {
        "camera_config": {
            "frame_width": 27/4,
            "frame_height": 12,
        }
    }
    
    def construct(self):
        frame_width = self.camera.frame.get_width()
        
        # 测试文本
        text = "设集合P={-1,0,1,2,3,4}，Q={-2,-1,0,1,2,3}，从P取整数a，从Q取整数b，求y=ax^b为奇函数的概率。"
        
        print(f"\n测试文本: {text}")
        print(f"屏幕宽度: {frame_width}")
        print(f"95%宽度: {frame_width * 0.95}")
        
        # 创建换行工具
        wrapper = AutoWrap(
            max_width_ratio=0.95,
            frame_width=frame_width,
            font_size=24,
            font="STKaiti",
            debug=True,
        )
        
        # 生成换行文本
        wrapped = wrapper.create_wrapped_text(text, align="left")
        wrapped.to_edge(LEFT, buff=0.2)
        wrapped.move_to(ORIGIN)
        
        # 显示
        self.play(Write(wrapped))
        
        # 打印每行信息
        for i, line in enumerate(wrapped):
            if isinstance(line, Text):
                print(f"行{i+1}: 宽度={line.get_width():.3f}")
        
        self.wait(2)


if __name__ == "__main__":
    # 默认运行 AutoWrapDemo，可以改为 SimpleWrapTest 或 TexWrapTest
    os.system(f'cd "{script_dir}" && manimgl auto_wrap_demo.py TexWrapTest')


class TexWrapTest(Scene):
    """
    Tex 数学公式断行测试
    
    重要结论：
    - 数学公式不适合自动 tokenize 断行（会破坏 LaTeX 语法）
    - 推荐使用手动断行方式
    - 或者将公式转换为多个独立 Tex 对象
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
        
        print(f"\n屏幕尺寸: {frame_width:.3f} x 12")
        print(f"95% 宽度: {safe_width:.3f}")
        
        # 标题
        title = Text(
            "Tex 数学公式 - 推荐断行方式",
            font="STKaiti",
            font_size=24,
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
        
        # ==================== 说明 ====================
        
        note1 = Text(
            "⚠️ 数学公式不适合自动断行",
            font="STKaiti",
            font_size=18,
            color=ORANGE
        ).move_to(UP * 4)
        
        note2 = Text(
            "原因：tokenize 会破坏 LaTeX 语法",
            font="STKaiti",
            font_size=16,
            color=WHITE
        ).next_to(note1, DOWN, buff=0.2)
        
        self.play(Write(note1), run_time=0.5)
        self.play(Write(note2), run_time=0.5)
        
        self.wait(1)
        
        # ==================== 推荐方式1：VGroup 手动分行 ====================
        
        print("\n=== 推荐方式1: VGroup 手动分行 ===")
        
        label1 = Text(
            "✓ 方式1: 手动分行 + VGroup",
            font="STKaiti",
            font_size=16,
            color=GREEN
        ).move_to(UP * 2)
        
        # 手动分行的公式组
        formula1 = VGroup(
            Tex(r"\text{设集合 } P = \{-1, 0, 1, 2, 3, 4\}", font_size=22),
            Tex(r"Q = \{-2, -1, 0, 1, 2, 3\}", font_size=22),
            Tex(r"\text{从 } P \text{ 取整数 } a \text{，从 } Q \text{ 取整数 } b", font_size=22),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        formula1.next_to(label1, DOWN, buff=0.2)
        formula1.to_edge(LEFT, buff=margin)
        
        self.play(Write(label1), run_time=0.3)
        self.play(FadeIn(formula1), run_time=0.8)
        
        for i, line in enumerate(formula1):
            w = line.get_width()
            print(f"  行{i+1}: 宽度={w:.3f}, 填充={w/safe_width*100:.1f}%")
        
        self.wait(1)
        
        # ==================== 推荐方式2：公式推导链 ====================
        
        print("\n=== 推荐方式2: 公式推导链 ===")
        
        label2 = Text(
            "✓ 方式2: 推导链分步显示",
            font="STKaiti",
            font_size=16,
            color=GREEN
        ).move_to(DOWN * 1)
        
        # 推导链
        formula2 = VGroup(
            Tex(r"e = \sqrt{1 + \frac{b^2}{a^2}} \geq \sqrt{5}", font_size=22),
            Tex(r"\Rightarrow b^2 \geq 4a^2", font_size=22),
            Tex(r"\Rightarrow |b| \geq 2|a|", font_size=22, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        formula2.next_to(label2, DOWN, buff=0.2)
        formula2.to_edge(LEFT, buff=margin)
        
        self.play(Write(label2), run_time=0.3)
        
        # 逐行显示推导过程
        for i, line in enumerate(formula2):
            self.play(Write(line), run_time=0.5)
            w = line.get_width()
            print(f"  行{i+1}: 宽度={w:.3f}, 填充={w/safe_width*100:.1f}%")
        
        self.wait(1)
        
        # ==================== 总结 ====================
        
        summary = VGroup(
            Text("📌 Tex 公式断行总结", font="STKaiti", font_size=18, color=YELLOW),
            Text("1. 手动拆分为多个 Tex 对象", font="STKaiti", font_size=14),
            Text("2. 使用 VGroup + arrange 排列", font="STKaiti", font_size=14),
            Text("3. 推导过程逐步 Write 动画", font="STKaiti", font_size=14),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        summary.move_to(DOWN * 4.5)
        
        self.play(FadeIn(summary), run_time=0.8)
        self.wait(2)

