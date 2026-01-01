"""
AutoScene API 全面测试脚本

测试 auto_scene.py 中的所有主要 API：
- 字幕与配音：make_subtitle, speak, clear_subtitle
- 文本高亮：highlight_text, _add_highlight_animation
- 布局工具：create_title_divider, layout_content_blocks, get_subtitle_top_y
- 相机聚焦：focus_guide, focus_guide_with_camera, camera_focus
- 辉光效果：create_glow_surrounding_rect, create_glow_underline, create_glow_text, 
             create_glowing_curved_arrow, create_glowing_circle
- 3D 标注：add_fixed_annotation, add_fixed_annotation_dynamic
- 工具方法：add_fixed_formula, add_fixed_grid, add_curved_annotation
- 调试工具：enable_debug, enable_time_hud, mark, get_current_time

运行命令:
    manimgl test_auto_scene_api.py TestAutoSceneAPI
"""

import sys
import os

# 确保可以导入 auto_scene
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auto_scene import AutoScene, create_glow_surrounding_rect, is_gpu_glow_available
from manimlib import (
    Text, Tex, Circle, Square, Line, VGroup, 
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    WHITE, YELLOW, RED, BLUE, GREEN, GREY,
    Write, FadeIn, FadeOut, ShowCreation,
)


class TestAutoSceneAPI(AutoScene):
    """测试 AutoScene 所有 API 的场景"""
    
    def construct(self):
        # 启用调试模式
        self.enable_debug(True)
        self.enable_time_hud()
        
        # ==================== 第1部分：字幕与配音 ====================
        self.test_subtitle_api()
        
        # ==================== 第2部分：高亮效果 ====================
        self.test_highlight_api()
        
        # ==================== 第3部分：布局工具 ====================
        self.test_layout_api()
        
        # ==================== 第4部分：辉光效果 ====================
        self.test_glow_api()
        
        # ==================== 第5部分：相机聚焦 ====================
        self.test_focus_api()
        
        # ==================== 第6部分：曲线标注 ====================
        self.test_annotation_api()
        
        # ==================== 第7部分：3D 标注 (如适用) ====================
        # self.test_3d_annotation_api()  # 需要 3D 相机
        
        # 结束
        self.wait(1)
        self.mark("测试完成")
        print(f"📊 标记列表: {self.get_markers()}")
    
    # ==================== 字幕与配音测试 ====================
    
    def test_subtitle_api(self):
        """测试字幕相关 API"""
        self.mark("字幕测试开始")
        
        # 1. make_subtitle - 创建字幕
        sub1 = self.make_subtitle("这是 make_subtitle 创建的字幕")
        self.play(FadeIn(sub1))
        self.wait(1)
        self.play(FadeOut(sub1))
        
        # 2. speak - 带配音的字幕（禁用配音以加速测试）
        self._enable_voice = False
        
        # 创建一个目标对象供高亮
        demo_text = Text("高亮目标", font=self.SUBTITLE_FONT, font_size=48)
        self.play(Write(demo_text))
        
        # speak 会自动创建字幕并高亮目标
        self.speak("这是 speak 方法，会自动高亮目标", targets=[demo_text])
        self.wait(0.5)
        
        # 3. clear_subtitle - 清除字幕
        self.clear_subtitle()
        self.play(FadeOut(demo_text))
        
        self.mark("字幕测试结束")
    
    # ==================== 高亮效果测试 ====================
    
    def test_highlight_api(self):
        """测试高亮相关 API"""
        self.mark("高亮测试开始")
        
        # 创建测试对象
        formula = Tex(r"E = mc^2", font_size=72)
        self.play(Write(formula))
        self.wait(0.5)
        
        # 测试不同高亮效果
        effects = ["box", "underline", "indicate", "focus", "wave", "flash", "circumscribe", "grow"]
        
        last_decoration = None
        for i, effect in enumerate(effects[:4]):  # 测试前4种
            self.speak(f"高亮效果: {effect}")
            
            # 清理上一个装饰（避免重叠）- 使用 remove 而非 FadeOut
            if last_decoration is not None:
                self.remove(last_decoration)
                
            last_decoration = self.highlight_text(formula, effect=effect, color=YELLOW, run_time=0.8)
            self.wait(0.3)
        
        # 清理最后一个装饰
        if last_decoration is not None:
            self.remove(last_decoration)
        
        self.clear_subtitle()
        self.play(FadeOut(formula))
        
        self.mark("高亮测试结束")
    
    # ==================== 布局工具测试 ====================
    
    def test_layout_api(self):
        """测试布局相关 API"""
        self.mark("布局测试开始")
        
        # 1. create_title_divider - 标题和分割线
        title, divider = self.create_title_divider(
            "【API 测试】布局工具",
            title_font_size=28,
            use_glow_divider=True
        )
        self.play(Write(title), ShowCreation(divider))
        self.wait(0.5)
        
        # 2. get_subtitle_top_y - 获取字幕顶部位置
        sub_top_y = self.get_subtitle_top_y()
        print(f"📏 字幕顶部 Y: {sub_top_y:.2f}")
        
        # 3. layout_content_blocks - 内容块布局
        problem = Text("问题区域", font=self.SUBTITLE_FONT, font_size=24)
        viz = Circle(radius=0.8, color=BLUE)
        derivation = Tex(r"\int f(x) dx", font_size=36)
        
        layout_info = self.layout_content_blocks(
            problem, viz, derivation, 
            divider=divider
        )
        print(f"📐 布局信息: {layout_info}")
        
        self.play(Write(problem), ShowCreation(viz), Write(derivation))
        self.wait(1)
        
        # 清理
        self.play(
            FadeOut(title), FadeOut(divider),
            FadeOut(problem), FadeOut(viz), FadeOut(derivation)
        )
        
        self.mark("布局测试结束")
    
    # ==================== 辉光效果测试 ====================
    
    def test_glow_api(self):
        """测试辉光相关 API"""
        self.mark("辉光测试开始")
        
        # 检查 GPU 辉光可用性
        glow_available = is_gpu_glow_available()
        print(f"🎮 GPU 辉光可用: {glow_available}")
        
        # 1. create_glow_surrounding_rect - 辉光方框
        target = Text("辉光方框", font=self.SUBTITLE_FONT, font_size=36)
        self.play(Write(target))
        
        glow_rect = create_glow_surrounding_rect(
            target, color=YELLOW, buff=0.15, 
            n_glow_layers=4, base_opacity=0.2
        )
        self.play(FadeIn(glow_rect))
        self.wait(0.5)
        self.play(FadeOut(glow_rect), FadeOut(target))
        
        # 2. create_glow_text - 辉光文字
        glow_text = self.create_glow_text(
            "辉光文字效果", 
            font_size=42, 
            color=BLUE,
            glow_size=0.4
        )
        self.play(FadeIn(glow_text))
        self.wait(0.5)
        self.play(FadeOut(glow_text))
        
        # 3. create_glow_underline - 辉光下划线
        title = Text("带下划线的标题", font=self.SUBTITLE_FONT, font_size=36)
        self.play(Write(title))
        
        underline = self.create_glow_underline(title, color=RED)
        self.play(ShowCreation(underline))
        self.wait(0.5)
        self.play(FadeOut(title), FadeOut(underline))
        
        self.mark("辉光测试结束")
    
    # ==================== 相机聚焦测试 ====================
    
    def test_focus_api(self):
        """测试相机聚焦相关 API"""
        self.mark("聚焦测试开始")
        
        # 创建多个目标
        objs = VGroup(
            Circle(radius=0.5, color=RED).shift(LEFT * 3),
            Square(side_length=1, color=GREEN),
            Circle(radius=0.5, color=BLUE).shift(RIGHT * 3),
        )
        self.play(ShowCreation(objs))
        self.wait(0.5)
        
        # 1. focus_guide - 聚焦引导（不移动相机）
        boxes = self.focus_guide(
            targets=[objs[0], objs[2]], 
            box_buff=0.15, 
            run_time=0.6,
            auto_remove=False
        )
        self.wait(0.5)
        
        # 手动移除方框
        for box in boxes:
            self.play(FadeOut(box), run_time=0.3)
        
        # 2. camera_focus - 相机聚焦
        self.camera_focus(objs[1], zoom_factor=1.5, focus_time=0.8, hold_time=0.5, restore_time=0.5)
        self.camera_focus(objs, zoom_factor=1.0, focus_time=0.5, hold_time=0.3, restore_time=0.5)  # 恢复
        
        self.play(FadeOut(objs))
        
        self.mark("聚焦测试结束")
    
    # ==================== 曲线标注测试 ====================
    
    def test_annotation_api(self):
        """测试曲线标注相关 API"""
        self.mark("标注测试开始")
        
        # 创建目标
        target = Circle(radius=0.6, color=YELLOW).shift(LEFT * 2)
        self.play(ShowCreation(target))
        
        # 1. add_curved_annotation - 曲线标注
        annotation = self.add_curved_annotation(
            target,
            annotation="这是一个圆",
            direction="right",
            text_font_size=20,
            use_glow=True
        )
        self.wait(1)
        
        # 2. create_glow_arc_arrow - 辉光弧形箭头
        arrow = self.create_glow_arc_arrow(
            start_angle=0, angle=1.0, radius=2.0, side="right"
        )
        arrow.shift(RIGHT * 2)
        self.play(ShowCreation(arrow))
        self.wait(0.5)
        
        # 清理
        self.play(FadeOut(target), FadeOut(annotation), FadeOut(arrow))
        
        self.mark("标注测试结束")
    
    # ==================== 3D 标注测试（可选） ====================
    
    def test_3d_annotation_api(self):
        """测试 3D 标注 API（需要 3D 相机模式）"""
        # 注意：此测试需要 3D 场景，默认跳过
        pass


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #获取文件名
    script_name = os.path.basename(__file__).replace(".py", "")
    # 使用 manimgl 运行此脚本
    os.system(f"cd {script_dir} && manimgl {script_name}.py  ")